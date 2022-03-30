% In this script, we simulate the performance of 802.11n 
clc
clear
close
%% Waveform Configuration
% Create a format configuration object for a 1-by-1 HT transmission
cfgHT = wlanHTConfig;
cfgHT.ChannelBandwidth = 'CBW20'; % 20 MHz channel bandwidth
cfgHT.NumTransmitAntennas = 1;    % 1 transmit antennas
cfgHT.NumSpaceTimeStreams = 1;    % 1 space-time streams
cfgHT.PSDULength = 1000;          % PSDU length in bytes
cfgHT.MCS = 4;                    % 1 spatial streams, 16-QAM rate-3/4
cfgHT.ChannelCoding = 'BCC';      % BCC channel coding
%% Channel Configuration
% Create and configure the tranmit channel
tgnChannel = wlanTGnChannel;
tgnChannel.DelayProfile = 'Model-A';
tgnChannel.NumTransmitAntennas = cfgHT.NumTransmitAntennas;
tgnChannel.NumReceiveAntennas = 1;
tgnChannel.TransmitReceiveDistance = 10; % Distance in meters for NLOS
tgnChannel.LargeScaleFadingEffect = 'None';
tgnChannel.NormalizeChannelOutputs = false;

%% Simulation Parameters
snr = 0:5:45;
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
%% Processing SNR Points
S = numel(snr);
%parpool(S);
packetErrorRate = zeros(S,1);
bitErrorRate = zeros(S,1);
%parfor i = 1:S % Use 'parfor' to speed up the simulation
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

        % Pass the waveform through the TGn channel model
        reset(tgnChannel); % Reset channel for different realization
        rx = tgnChannel(tx);

        % Add noise
        rx = awgn(rx,packetSNR);
        
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
    bitErrorRate(i) = ber/(count*1000*8);
    % Calculate packet error rate (PER) at SNR point
    packetErrorRate(i) = numPacketErrors/(n-1);
    disp(['SNR ' num2str(snr(i))...
          ' completed after '  num2str(n-1) ' packets,'...
          ' PER: ' num2str(packetErrorRate(i))]);
end
perfile = sprintf('PER_noJamming.mat');
save(perfile,'packetErrorRate');
berfile = sprintf('BER_noJamming.mat');
save(berfile,'bitErrorRate');
%% Plot Packet Error Rate vs SNR Results
figure (1);
semilogy(snr,packetErrorRate,'k-O');
xlabel('snr (dB)');
ylabel('Packet Error Rate (PER)');
ylim([10^-5 1]);
grid on;
hold off

figure(2)
semilogy(snr,bitErrorRate,'k-O');
xlabel('snr (dB)');
ylabel('Bit Error Rate (BER)');
ylim([10^-5 1]);
grid on;
hold off
