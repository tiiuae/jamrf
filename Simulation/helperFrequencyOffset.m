function out = helperFrequencyOffset(in, fs, foffset)
%helperFrequencyOffset Apply a frequency offset to the input signal
%
%   OUT = helperFrequencyOffset(IN, FS, FOFFSET) applies the specified
%   frequency offset to the input signal.
%
%   OUT is the frequency-offset output of the same size as IN.
%   IN is the complex 2D array input.
%   FS is the sampling rate in Hz (e.g. 80e6).
%   FOFFSET is the frequency offset to apply to the input in Hz.
%
%   See also comm.PhaseFrequencyOffset.

%   Copyright 2015-2019 The MathWorks, Inc.

%#codegen

% Initialize output
out = complex(zeros(size(in)));

% Create vector of time samples
t = ((0:size(in,1)-1)/fs).';

% For each antenna, apply the frequency offset
for i = 1:size(in,2)
    out(:,i) = in(:,i).*exp(1i*2*pi*foffset*t);
end