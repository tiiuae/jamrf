
% In this script, we simulate the performance of 802.11n in the presence of
% jammer
clc
clear
close
%% Simulation Parameters
snr_dB = 0:5:45;
JSR_dB = [-100, -10,-5, 0, 5, 10]; %Jammer to Signal ratios (dB)
n_jammers = 1;
Fj = 0.0001; %Jamming tone - normalized frequency (-0.5 < F < 0.5)
Thetaj = rand(1,1)*2*pi;%random jammer phase(0 to 2*pi radians)
%% Processing SNR Points
S = numel(snr_dB);
bitErrorRate = zeros(length(JSR_dB),S);
%parfor i = 1:S % Use 'parfor' to speed up the simulation
for jammer = 1:n_jammers
for k=1:length(JSR_dB)%loop for each given JSR
    for i = 1:S % Use 'for' to debug the simulation    
        % Loop to simulate multiple packets
        SNR = 10.^(snr_dB(i)/10); %Signal-to-noise ratio in linear scale
        JSR = 10.^(JSR_dB(k)/10); %Jammer-to-Signal ratio in linear scale
        if jammer == 1
            d = sqrt(SNR/(10*(1+SNR*JSR)));
            bitErrorRate(k,i) =1-0.25*(erf(d)^2+2*erf(d)*(1-2*erfc(d))+(1-2*erfc(d))^2);
        else
            JNR = 2*JSR*SNR;
            bitErrorRate(k,i) = 3/8 * (erfc(sqrt(SNR)+sqrt(0.5*JNR))+erfc(sqrt(SNR)-sqrt(0.5*JNR))); 
        end
    end
end
% Save Results
if jammer == 1
    berfile = sprintf('BER_noiseJamming.mat');
    save(berfile,'bitErrorRate');
else
    berfile = sprintf('BER_QPSKJamming.mat');
    save(berfile,'bitErrorRate');
end
end
%%

%% Plot Bit Error Rate vs SNR Results

figure(1)
semilogy(snr_dB,bitErrorRate(1,:),'k--','LineWidth',1,'MarkerSize',7);
hold on 
semilogy(snr_dB,bitErrorRate(2,:),'r-*','LineWidth',1,'MarkerSize',7);
hold on 
semilogy(snr_dB,bitErrorRate(3,:),'b-d','LineWidth',1,'MarkerSize',7);
hold on 
semilogy(snr_dB,bitErrorRate(4,:),'m-s','LineWidth',1,'MarkerSize',7);
hold on 
semilogy(snr_dB,bitErrorRate(5,:),'g-h','LineWidth',1,'MarkerSize',7);
hold on 
semilogy(snr_dB,bitErrorRate(6,:),'c-<','LineWidth',1,'MarkerSize',7);
xlabel('snr (dB)');
ylabel('Bit Error Rate (BER)');
legend('JSR = -100dB','JSR = -10dB','JSR = -5dB',...
    'JSR = 0dB','JSR = 5dB','JSR = 10dB','Location','southwest');
ylim([10^-5 1]);
hold off
