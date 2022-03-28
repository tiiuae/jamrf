function [prbs] = generatePRBS(prbsType,G1,G2,X1,X2)
%Generate PRBS sequence - choose from either msequence or gold code
%prbsType - type of PRBS generator - 'MSEQUENCE' or 'GOLD'
% If prbsType == 'MSEQUENCE' G1 is the generator poly for LFSR
% and X1 its seed. G2 and X2 are not used
% If prbsType == 'GOLD' G1,G2 are the generator polynomials
% for LFSR1/LFSR2 and X1,X2 are their initial seeds.
%G1,G2 - Generator polynomials for PRBS generation
%X1,X2 - Initial states of LFSRs
%The PRBS generators results in 1 period PRBS,
%need to repeat it to suit the data length
if strcmpi(prbsType,'MSEQUENCE')
    prbs=lfsr( G1, X1);%use only one poly and initial state vector
elseif strcmpi(prbsType,'GOLD')
    prbs=gold_code_generator(G1,G2,X1,X2);%full length Gold sequence
else %Gold codes as default
    G1=[1 1 1 1 0 1]; G2 = [1 0 0 1 0 1]; %LFSR polynomials
    X1 = [ 0 0 0 0 1]; X2=[ 0 0 0 0 1] ; %initial state of LFSR
    prbs = gold_code_generator(G1,G2,X1,X2);
end