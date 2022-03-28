function [y,states] = lfsr(G,X)
%Galois LFSR for m-sequence generation
% G - polynomial (primitive for m-sequence) arranged as vector
% X - initial state of the delay elements arranged as vector
% y - output of LFSR
% states - gives the states through which the LFSR has sequenced.
%This is particularly helpful in frequency hopping applications
%The function outputs the m-sequence for a single period
%Sample call:
%3rd order LFSR polynomial:xˆ5+xˆ2+1=>g5=1,g4=0,g3=0,g2=1,g1=0,g0=1
%with intial states [0 0 0 0 1]: lfsr([1 0 0 1 0 1],[0 0 0 0 1])
g=G(:); x=X(:); %serialize G and X as column vectors
if length(g)-length(x)~=1
    error('Length of initial seed X0 should be equal to the number of delay elements (length(g)-1)');
end
%LFSR state-transistion matrix construction
L = length(g)-1; %order of polynomial
A0 = [zeros(1,L-1); eye(L-1)]; %A-matrix construction
g=g(1:end-1);
A = [A0 g]; %LFSR state-transistion matrix
N = 2^L-1; %period of maximal length sequence
y = zeros(1,length(N));%array to store output
states=zeros(1,length(N));%LFSR states(useful for Frequeny Hopping)
for i=1:N %repeate for each clock period
    states(i)=bin2dec(char(x.'+'0'));%convert LFSR states to a number
    y(i) = x(end); %output the last bit
    x = mod(A*x,2); %LFSR equation
end