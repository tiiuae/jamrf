
% In this script, we simulate the performance of 802.11n in the presence of
% jammer
clc
clear
close
%% Waveform Configuration
% Create a format configuration object for a 2-by-2 HT transmission
cfgHT = wlanHTConfig;
cfgHT.ChannelBandwidth = 'CBW20'; % 20 MHz channel bandwidth
cfgHT.NumTransmitAntennas = 2;    % 2 transmit antennas
cfgHT.NumSpaceTimeStreams = 2;    % 2 space-time streams
cfgHT.PSDULength = 1000;          % PSDU length in bytes
cfgHT.MCS = 15;                   % 2 spatial streams, 64-QAM rate-5/6
cfgHT.ChannelCoding = 'BCC';      % BCC channel coding
%% Channel Configuration
% Create and configure the tranmit channel
tgnChannel = wlanTGnChannel;
tgnChannel.DelayProfile = 'Model-B';
tgnChannel.NumTransmitAntennas = cfgHT.NumTransmitAntennas;
tgnChannel.NumReceiveAntennas = 2;
tgnChannel.TransmitReceiveDistance = 10; % Distance in meters for NLOS
tgnChannel.LargeScaleFadingEffect = 'None';
tgnChannel.NormalizeChannelOutputs = false;

% Create and configure the jamming channel
tgnChannel1 = wlanTGnChannel;
tgnChannel1.DelayProfile = 'Model-B';
tgnChannel1.NumTransmitAntennas = 1;
tgnChannel1.NumReceiveAntennas = 1;
tgnChannel1.TransmitReceiveDistance = 5; % Distance in meters for NLOS
tgnChannel1.LargeScaleFadingEffect = 'None';
tgnChannel1.NormalizeChannelOutputs = false;
%% Simulation Parameters
snr = 25:5:45;
maxNumPEs = 200; % The maximum number of packet errors at an SNR point
maxNumPackets = 10000; % The maximum number of packets at an SNR point
% Get the baseband sampling rate
fs = wlanSampleRate(cfgHT);
% Get the OFDM info
ofdmInfo = wlanHTOFDMInfo('HT-Data',cfgHT);
% Set the sampling rate of the channel
tgnChannel.SampleRate = fs;
% Indices for accessing each field within the time-domain packet
ind = wlanFieldIndices(cfgHT);
JSR_dB = [-100, -10,-5, 0, 2]; %Jammer to Signal ratios (dB)
n_jammers = 3;
Fj = 0.0001; %Jamming tone - normalized frequency (-0.5 < F < 0.5)
Thetaj = rand(1,1)*2*pi;%random jammer phase(0 to 2*pi radians)
%% Processing SNR Points
S = numel(snr);
%parpool(S);
packetErrorRate = zeros(length(JSR_dB),S);
bitErrorRate = zeros(length(JSR_dB),S);
%parfor i = 1:S % Use 'parfor' to speed up the simulation
for jammer = 1:n_jammers
for k=1:length(JSR_dB)%loop for each given JSR
    for i = 1:S % Use 'for' to debug the simulation
        % Set random substream index per iteration to ensure that each
        % iteration uses a repeatable set of random numbers
        stream = RandStream('combRecursive','Seed',0);
        stream.Substream = i;
        RandStream.setGlobalStream(stream);
    
        % Account for noise energy in nulls so the SNR is defined per
        % active subcarrier
        packetSNR = snr(i)-10*log10(ofdmInfo.FFTLength/ofdmInfo.NumTones);
    
        % Loop to simulate multiple packets
        numPacketErrors = 0;
        n = 1; % Index of packet transmitted
        ber = 0;
        count = 1;
        while numPacketErrors<=maxNumPEs && n<=maxNumPackets
            % Generate a packet waveform
            txPSDU = randi([0 1],cfgHT.PSDULength*8,1); % PSDULength in bytes
            tx = wlanWaveformGenerator(txPSDU,cfgHT);
            
            % Add trailing zeros to allow for channel filter delay
            tx = [tx; zeros(15,cfgHT.NumTransmitAntennas)]; %#ok<AGROW>
            
            %Generate single tone jammer for each given JSR
            [L,j] = size(tx);
            Eb = sum(sum(abs(tx).^2))/(L*j);
            if jammer == 1
                J = tone_jammer(JSR_dB(k),Fj,Thetaj,Eb,L);%generate a tone jammer
            elseif jammer == 2
                J = noise_jammer(JSR_dB(k),Fj,Thetaj,Eb,L);%generate a noise jammer
            else
                J = QPSK_jammer(JSR_dB(k),Fj,Thetaj,Eb,L);%generate a QPSK jammer
            end

            % Pass the waveform through the TGn channel model
            reset(tgnChannel); % Reset channel for different realization
            rx = tgnChannel(tx);
            reset(tgnChannel1);
            J = tgnChannel1(J);
    
            % Add noise
            rx = awgn(rx,packetSNR);
    
            % Add Jamming Signal
            rx = rx + J;
            
            % Packet detect and determine coarse packet offset
            coarsePktOffset = wlanPacketDetect(rx,cfgHT.ChannelBandwidth);
            if isempty(coarsePktOffset) % If empty no L-STF detected; packet error
                numPacketErrors = numPacketErrors+1;
                n = n+1;
                continue; % Go to next loop iteration
            end
    
            % Extract L-STF and perform coarse frequency offset correction
            lstf = rx(coarsePktOffset+(ind.LSTF(1):ind.LSTF(2)),:);
            coarseFreqOff = wlanCoarseCFOEstimate(lstf,cfgHT.ChannelBandwidth);
            rx = helperFrequencyOffset(rx,fs,-coarseFreqOff);
    
            % Extract the non-HT fields and determine fine packet offset
            nonhtfields = rx(coarsePktOffset+(ind.LSTF(1):ind.LSIG(2)),:);
            finePktOffset = wlanSymbolTimingEstimate(nonhtfields,...
                cfgHT.ChannelBandwidth);
    
            % Determine final packet offset
            pktOffset = coarsePktOffset+finePktOffset;
    
            % If packet detected outwith the range of expected delays from the
            % channel modeling; packet error
            if pktOffset>15
                numPacketErrors = numPacketErrors+1;
                n = n+1;
                continue; % Go to next loop iteration
            end
    
            % Extract L-LTF and perform fine frequency offset correction
            lltf = rx(pktOffset+(ind.LLTF(1):ind.LLTF(2)),:);
            fineFreqOff = wlanFineCFOEstimate(lltf,cfgHT.ChannelBandwidth);
            rx = helperFrequencyOffset(rx,fs,-fineFreqOff);
    
            % Extract HT-LTF samples from the waveform, demodulate and perform
            % channel estimation
            htltf = rx(pktOffset+(ind.HTLTF(1):ind.HTLTF(2)),:);
            htltfDemod = wlanHTLTFDemodulate(htltf,cfgHT);
            chanEst = wlanHTLTFChannelEstimate(htltfDemod,cfgHT);
    
            % Extract HT Data samples from the waveform
            htdata = rx(pktOffset+(ind.HTData(1):ind.HTData(2)),:);
    
            % Estimate the noise power in HT data field
            nVarHT = htNoiseEstimate(htdata,chanEst,cfgHT);
    
            % Recover the transmitted PSDU in HT Data
            rxPSDU = wlanHTDataRecover(htdata,chanEst,nVarHT,cfgHT);
    
            % Determine if any bits are in error, i.e. a packet error
            ber = ber + biterr(txPSDU,rxPSDU);
            packetError = any(biterr(txPSDU,rxPSDU));
            numPacketErrors = numPacketErrors+packetError;
            count=count+1;
            n = n+1;
        end
        bitErrorRate(k,i) = ber/((n-1)*1000*8);
        % Calculate packet error rate (PER) at SNR point
        packetErrorRate(k,i) = numPacketErrors/(n-1);
        disp(['SNR ' num2str(snr(i))...
              ' completed after '  num2str(n-1) ' packets,'...
              ' PER: ' num2str(packetErrorRate(k,i))]);
    end
end
% Save Results
if jammer == 1
    perfile = sprintf('PER_toneJamming.mat');
    save(perfile,'packetErrorRate');
    berfile = sprintf('BER_toneJamming.mat');
    save(berfile,'bitErrorRate');
elseif jammer == 2
    perfile = sprintf('PER_noiseJamming.mat');
    save(perfile,'packetErrorRate');
    berfile = sprintf('BER_noiseJamming.mat');
    save(berfile,'bitErrorRate');
else
    perfile = sprintf('PER_QPSKJamming.mat');
    save(perfile,'packetErrorRate');
    berfile = sprintf('BER_QPSKJamming.mat');
    save(berfile,'bitErrorRate');
end
end
%%

%% Plot Packet Error Rate vs SNR Results
figure (1);
semilogy(snr,packetErrorRate(1,:),'k-O');
hold on 
semilogy(snr,packetErrorRate(2,:),'r-*');
hold on 
semilogy(snr,packetErrorRate(3,:),'b-*');
hold on 
semilogy(snr,packetErrorRate(4,:),'m-*');
hold on 
semilogy(snr,packetErrorRate(5,:),'g-*');
xlabel('snr (dB)');
ylabel('Packet Error Rate (PER)');
legend('JSR = -100dB','JSR = -10dB','JSR = -5dB',...
    'JSR = 0dB','JSR = 2dB','Location','southwest');
ylim([10^-5 1]);
grid on;
%title('802.11n 20MHz, MCS15, Direct Mapping, 2x2 Channel Model B-NLOS');
hold off

figure(2)
semilogy(snr,bitErrorRate(1,:),'k-O');
hold on 
semilogy(snr,bitErrorRate(2,:),'r-*');
hold on 
semilogy(snr,bitErrorRate(3,:),'b-*');
hold on 
semilogy(snr,bitErrorRate(4,:),'m-*');
hold on 
semilogy(snr,bitErrorRate(5,:),'g-*');
xlabel('snr (dB)');
ylabel('Bit Error Rate (BER)');
legend('JSR = -100dB','JSR = -10dB','JSR = -5dB',...
    'JSR = 0dB','JSR = 2dB','Location','southwest');
ylim([10^-5 1]);
grid on;
%title('802.11n 20MHz, MCS15, Direct Mapping, 2x2 Channel Model B-NLOS');
hold off
