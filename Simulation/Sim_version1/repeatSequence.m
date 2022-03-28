function [y]= repeatSequence(x,N)
%Repeat a given sequence x of arbitrary length to match the given
%length N. This function is useful to repeat any sequence
%(say PRBS) to match the length of another sequence
x=x(:); %serialize
xLen = length(x); %length of sequence x
%truncate or extend sequence x to suite the given length N
if xLen >= N %Truncate x when sequencelength less than N
    y = x(1:N);
else
temp = repmat(x,fix(N/xLen),1); %repeat sequence integer times
residue = mod(N,xLen); %reminder when dividing N by xLen
%append reminder times
if residue ~=0, temp = [temp; x(1:residue)]; end
    y = temp; %repeating sequence matching length N
end