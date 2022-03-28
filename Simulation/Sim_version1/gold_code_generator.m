function [y] = gold_code_generator( G1,G2,X1,X2)
%Implementation of Gold code generator
%G1-preferred polynomial 1 for LFSR1 arranged as [g0 g1 g2 ... gL-1]
%G2-preferred polynomial 2 for LFSR2 arranged as [g0 g1 g2 ... gL-1]
%X1-initial seed for LFSR1 [x0 x1 x2 ... xL-1]
%X2-initial seed for LFSR2 [x0 x1 x2 ... xL-1]
%y-Gold code
%The function outputs the m-sequence for a single period
%Sample call:
% 7th order preferred polynomials [1,2,3,7] and [3,7] (polynomials : 1+x+xˆ2+xˆ3+xˆ7 and 1+xˆ3+xˆ7)
% i.e, G1 = [1,1,1,1,0,0,0,1] and G2=[1,0,0,1,0,0,0,1]
% with intial states X1=[0,0,0,0,0,0,0,1], X2=[0,0,0,0,0,0,0,1]:
%gold_code_generator(G1,G2,X1,X2)
g1=G1(:); x1=X1(:); %serialize G1 and X1 matrices
g2=G2(:); x2=X2(:); %serialize G2 and X2 matrices
if length(g1)~=length(g2) && length(x1)~=length(x2)
    error('Length mismatch between G1 & G2 or X1 & X2');
end
%LFSR state-transistion matrix construction
L = length(g1)-1; %order of polynomial
A0 = [zeros(1,L-1); eye(L-1)]; %A-matrix construction
g1=g1(1:end-1);g2=g2(1:end-1);
A1 = [A0 g1]; %LFSR1 state-transistion matrix
A2 = [A0 g2]; %LFSR2 state-transistion matrix
N = 2^L-1; %period of maximal length sequence
y = zeros(1,length(N));%array to store output
for i=1:N %repeate for each clock period
    y(i)= mod(x1(end)+x2(end),2);%XOR of outputs of LFSR1 & LFSR2
    x1 = mod(A1*x1,2); %LFSR equation
    x2 = mod(A2*x2,2); %LFSR equation
end