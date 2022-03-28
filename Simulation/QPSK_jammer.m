function [J,JSRmeas] = QPSK_jammer(JSR_dB,Fj,Thetaj,Esig,L)
%Generates a single tone jammer (J) for the following inputs
%JSR_dB - required Jammer to Signal Ratio for generating the jammer
%Fj- Jammer frequency offset from center frequency (-0.5 < Fj < 0.5)
%Thetaj - phase of the jammer tone (0 to 2*pi)
%Esig -transmitted signal power to which jammer needs to be added
%- length of the transmitter signal vector
%The output JSRmeas is the measured JSR from the generated samples
qpskmod = comm.QPSKModulator;
JSR = 10.^(JSR_dB/10); %Jammer-to-Signal ratio in linear scale
Pj= JSR*Esig; %required Jammer power for the given signal power
n=(0:1:L-1).';%indices for generating jammer samples
M = 4;
data = randi([0 M-1],L,1);
waveform = qpskmod(data);
J = sqrt(2*Pj).*waveform; %QPSK Jammer
%J = sqrt(2*Pj)*pskmod(data,M,pi/M);
% Add IQ imbalance with an amplitude imbalance of 8dB
%J = iqimbal(J, 8, (180/pi)*pi/5);
Ej=sum(abs(J).^2)/L; %computed jammer energy from generated samples
JSRmeas = 10*log10(Ej/Esig);%measured JSR
%disp(['Measured JSR from jammer & signal: ',num2str(JSRmeas),'dB']);