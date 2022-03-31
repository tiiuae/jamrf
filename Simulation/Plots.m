clc
clear
close
%% Signal Detection With 1D CNN
snr = 0:5:45;
% Load Dataset
PER1 = load("PER_noJamming.mat");
BER1 = load("BER_noJamming.mat");
PER2 = load("PER_toneJamming.mat");
BER2 = load("BER_toneJamming.mat");
PER3 = load("PER_QPSKJamming.mat");
BER3 = load("BER_QPSKJamming.mat");
PER4 = load("PER_noiseJamming.mat");
BER4 = load("BER_noiseJamming.mat");
PER1 = PER1.packetErrorRate;
BER1 = BER1.bitErrorRate;
PER2 = PER2.packetErrorRate;
BER2 = BER2.bitErrorRate;
PER3 = PER3.packetErrorRate;
BER3 = BER3.bitErrorRate;
PER4 = PER4.packetErrorRate;
BER4 = BER4.bitErrorRate;
%% Plot Packet Error Rate vs SNR Results
figure(1)
semilogy(snr,BER3(1,:),'k--','LineWidth',1,'MarkerSize',7);
hold on 
semilogy(snr,BER3(2,:),'r-*','LineWidth',1,'MarkerSize',7);
hold on 
semilogy(snr,BER3(3,:),'b-d','LineWidth',1,'MarkerSize',7);
hold on 
semilogy(snr,BER3(4,:),'m-s','LineWidth',1,'MarkerSize',7);
xlabel('snr (dB)');
ylabel('Bit Error Rate (BER)');
legend('JSR = -100dB','JSR = -10dB','JSR = -5dB',...
    'JSR = 0dB','Location','southwest');
ylim([10^-5 1]);
hold off

figure(2)
semilogy(snr,BER4(1,:),'k--','LineWidth',1,'MarkerSize',7);
hold on 
semilogy(snr,BER4(2,:),'r-*','LineWidth',1,'MarkerSize',7);
hold on 
semilogy(snr,BER4(3,:),'b-d','LineWidth',1,'MarkerSize',7);
hold on 
semilogy(snr,BER4(4,:),'m-s','LineWidth',1,'MarkerSize',7);
xlabel('snr (dB)');
ylabel('Bit Error Rate (BER)');
legend('JSR = -100dB','JSR = -10dB','JSR = -5dB',...
    'JSR = 0dB','Location','southwest');
ylim([10^-5 1]);
hold off

figure (3);
semilogy(snr,PER1,'k-o','LineWidth',1,'MarkerSize',7);
hold on 
semilogy(snr,PER2(4,:),'r-*','LineWidth',1,'MarkerSize',7);
hold on 
semilogy(snr,PER3(4,:),'b-s','LineWidth',1,'MarkerSize',7);
hold on 
semilogy(snr,PER4(4,:),'m-d','LineWidth',1,'MarkerSize',7);
xlabel('snr (dB)');
ylabel('Packet Error Rate (PER)');
legend('No Jamming','Single-tone Jamming','QPSK Jamming',...
    'Noise Jamming','Location','southwest');
ylim([10^-3 1]);
hold off

figure(4)
semilogy(snr,BER1,'k-o','LineWidth',1,'MarkerSize',7);
hold on 
semilogy(snr,BER2(4,:),'r-*','LineWidth',1,'MarkerSize',7);
hold on 
semilogy(snr,BER3(4,:),'b-s','LineWidth',1,'MarkerSize',7);
hold on 
semilogy(snr,BER4(4,:),'m-d','LineWidth',1,'MarkerSize',7);
xlabel('snr (dB)');
ylabel('Bit Error Rate (BER)');
legend('No Jamming','Single-tone Jamming','QPSK Jamming',...
    'Noise Jamming','Location','southwest');
ylim([10^-4 1]);
hold off