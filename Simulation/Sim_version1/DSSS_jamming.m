%Perf. of BPSK DSSS over AWGN channel in presence of a jammer
clearvars; clc; close
%--- Input parameters------
Gp = 31; %processing gain
N=10e5; %number of data bits to transmit
EbN0dB = 0:2:14; %Eb/N0 ratios (dB)
JSR_dB = [-100, -10,-5, 0, 2]; %Jammer to Signal ratios (dB)
Fj = 0.0001; %Jamming tone - normalized frequency (-0.5 < F < 0.5)
Thetaj = rand(1,1)*2*pi;%random jammer phase(0 to 2*pi radians)
%----PRBS definition (refer previous sections of this chapter)---
prbsType='MSEQUENCE';%PRBS type,period of the PRBS should match Gp
G1=[1 0 0 1 1 1];%LFSR polynomial
X1=[0 0 0 0 1];%initial seed for LFSR
G2=0;%G2,X2 set to zero for m-sequence (only one LFSR used)JSR_dB
X2=0;
%---------------Transmitter------------------
d= rand(1,N) >=0.5; %Random binary information source
dp =2*d-1; %converted to polar format (+/- 1)
dr = kron(dp(:),ones(Gp,1)); %repeat d[n] - Gp times
L = N*Gp; %length of the data after the repetition
prbs = generatePRBS(prbsType,G1,G2,X1,X2);%1 period of PRBS
prbs = 2*prbs-1; %convert PRBS to +/- 1 values
prbs=prbs(:);% serialize
c=repeatSequence(prbs,L);%repeat PRBS sequence to match data length
s = dr.*c; %multiply information source and PRBS sequence
%Calculate signal power (used to generate jamming signal)
Eb=Gp*sum(abs(s).^2)/L;
plotColors =['r','b','k','g','m'];
BER = zeros(length(JSR_dB),length(EbN0dB)); %place holder for BER values
for k=1:length(JSR_dB)%loop for each given JSR
    %Generate single tone jammer for each given JSR
    J = tone_jammer(JSR_dB(k),Fj,Thetaj,Eb,L);%generate a tone jammer
    for i=1:length(EbN0dB)%loop for each given SNR
        %-----------AWGN noise addition---------
        N0=Eb/(10^(EbN0dB(i)/10)); %Find the noise spectral density
        w = sqrt(N0/2)*randn(length(s),1);%computed whitenoise
        r = s + J + w; %received signal
        %------------Receiver--------------
        yr = r.*c; %multiply received signal with PRBS reference
        y=conv(yr,ones(1,Gp)) ; %correlation type receiver
        dCap = y(Gp:Gp:end) > 0; %threshold detection
        BER(k,i) = sum(dCap.'~=d)/N; %Bit Error Rate
        %semilogy(EbN0dB, BER, [plotColors(k) '-*']); hold on; %plot
    end
end
%theoretical BER (when no Jammer)
theoreticalBER = 0.5*erfc(sqrt(10.^(EbN0dB/10)));
%reference performance for BPSK modulation
semilogy(EbN0dB, theoreticalBER,'k-O');
hold on 
semilogy(EbN0dB,BER(1,:),'r-*');
hold on 
semilogy(EbN0dB,BER(2,:),'b-*');
hold on 
semilogy(EbN0dB,BER(3,:),'k-*');
hold on 
semilogy(EbN0dB,BER(4,:),'g-*');
hold on 
semilogy(EbN0dB,BER(5,:),'m-*');
xlabel('Eb/N0 (dB)');
ylabel('Bit Error Rate (Pb)');
legend('Theoretical','JSR = -100dB','JSR = -10dB','JSR = -5dB',...
    'JSR = 0dB','JSR = 2dB','Location','southwest')
ylim([10^-5 1])
grid on
hold off