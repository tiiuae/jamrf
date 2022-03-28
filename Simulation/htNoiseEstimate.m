function [nest,sigest] = htNoiseEstimate(x,chanEst,cfgHT,varargin)
%htNoiseEstimate Estimate noise power using HT data field pilots
%
%   NEST = htNoiseEstimate(X,CHANEST,CFGHT) estimates the mean noise power
%   in watts using the demodulated pilot symbols in the HT data field and
%   estimated channel at pilot subcarriers location. The noise estimate is
%   averaged over the number of symbols and receive antennas.
%
%   X is the received time-domain HT-Data field signal. It is a Ns-by-Nr
%   matrix of real or complex values, where Ns represents the number of
%   time-domain samples in the HT-Data field and Nr represents the number
%   of receive antennas.
%
%   CHANEST is a complex Nst-by-(Nsts+Ness)-by-Nr array containing the
%   estimated channel at data and pilot subcarriers, where Nst is the
%   number of subcarriers, Nsts is the number of space-time streams, Ness
%   is the number of extension streams.
%
%   CFGHT is the format configuration object of type <a
%   href="matlab:help('wlanHTConfig')">wlanHTConfig</a>.
%   
%   NEST = htNoiseEstimate(...,SYMOFFSET) specifies the sampling offset as
%   a fraction of the cyclic prefix (CP) length for every OFDM symbol, as a
%   double precision, real scalar between 0 and 1, inclusive. The OFDM
%   demodulation is performed based on Nfft samples following the offset
%   position, where Nfft denotes the FFT length. The default value of this
%   property is 0.75, which means the offset is three quarters of the CP
%   length.
%
%   [NEST,SIGEST] = htNoiseEstimate(...) additionally returns an estimate
%   of the signal power.

%   Copyright 2018 The MathWorks, Inc.

%#codegen

% Validate inputs
validateattributes(x, {'double'}, {'2d','finite'}, mfilename, 'HT-Data field input'); 
validateattributes(chanEst, {'double'}, {'3d','finite'}, mfilename, 'Channel estimate input'); 
validateattributes(cfgHT,{'wlanHTConfig'},{'scalar'}, mfilename,'HT format configuration object');

if nargin == 4
    symOffset = varargin{1};
    % Validate symbol offset
    validateattributes(symOffset, {'double'},{'real','scalar','>=',0,'<=',1}, mfilename,'OFDM sampling offset');
else
    symOffset = 0.75;
end

numSTS = cfgHT.NumSpaceTimeStreams;
[cfgOFDM,~,pilotInd] = wlan.internal.wlanGetOFDMConfig(cfgHT.ChannelBandwidth, cfgHT.GuardInterval, 'HT', numSTS);

% Ensure at least 1 OFDM symbol in the input
numSamples = size(x,1);
minMultipleLength = cfgOFDM.FFTLength+cfgOFDM.CyclicPrefixLength;
numOFDMSym = floor(numSamples/minMultipleLength);
minInputLength = minMultipleLength;
coder.internal.errorIf(numSamples<minInputLength, 'wlan:shared:ShortDataInput', minInputLength);

% Extract pilot subcarriers from channel estimate
chanEstPilots = chanEst(pilotInd,:,:);

% OFDM demodulate
minInputLength = minMultipleLength*numOFDMSym;
[~,ofdmDemodPilots] = wlan.internal.wlanOFDMDemodulate(x(1:minInputLength,:), cfgOFDM, symOffset);

% Get reference pilots, from IEEE Std 802.11-2012, Eqn 20-58/59
% For HT-MF, offset by 3 to allow for L-SIG and HT-SIG pilot symbols
z = 3; 
refPilots = wlan.internal.htPilots(numOFDMSym, z, cfgHT.ChannelBandwidth, numSTS);

% Estimate CPE and phase correct symbols
[cpe,estRxPilots] = wlan.internal.commonPhaseErrorEstimate(ofdmDemodPilots, chanEstPilots, refPilots);
ofdmPilotsData = wlan.internal.commonPhaseErrorCorrect(ofdmDemodPilots,cpe);

% Estimate noise
pilotError = estRxPilots-ofdmPilotsData;
nest = mean(real(pilotError(:).*conj(pilotError(:))));

if nargout>1
    % Get power of channel estimate at pilot locations
   sigest =  mean(estRxPilots(:).*conj(estRxPilots(:)));
end

end