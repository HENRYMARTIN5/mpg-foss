function varargout = tfestimate(x,y,varargin) % Defines a function named tfestimate that accepts an input x, an input y, and a variable number of additional inputs. It returns a variable number of outputs.

%TFESTIMATE   Transfer Function Estimate. % Comment describing the function.

%   Txy = TFESTIMATE(X,Y) estimates the transfer function of the system % Comment.
%   with input X and output Y using Welch's averaged, modified periodogram % Comment.
%   method. Txy is the quotient of the Cross Power Spectral Density (CPSD) % Comment.
%   of X and Y, Pxy, and the Power Spectral Density (PSD) of X, Pxx. % Comment.
%   ... % Comments describing the function usage and parameters.

%#codegen % Directive for MATLAB Coder to generate C/C++ code from MATLAB code.

narginchk(2,10) % Checks the number of input arguments and errors if not between 2 and 10.

inpArgs = cell(1,length(varargin)); % Initializes inpArgs as a cell array with the same length as varargin.

if nargin > 2 % Checks if the number of input arguments is greater than 2.
    % Use explicit loops to preserve constants in Coder % Comment.
    for i = 1:numel(inpArgs) % Loops through each element in inpArgs.
        inpArgs{i} = convertStringsToChars(varargin{i}); % Converts strings in varargin to character arrays and stores them in inpArgs.
    end
else % If nargin is not greater than 2.
    inpArgs = varargin; % Directly assigns varargin to inpArgs without conversion.
end

[funcName,idx] = signal.internal.tefstimate.parseEstimator(inpArgs{:}); % Parses the estimator from the input arguments and returns the name and index.

if idx == 0 % Checks if the index is 0.
    args = inpArgs; % Directly assigns inpArgs to args.
else % If idx is not 0.
    args = {inpArgs{1:idx-1},inpArgs{idx+2:end}}; % Removes the estimator and its value from inpArgs and assigns the result to args.
end

% Possible outputs are: % Comment.
%       Plot % Comment.
%       Txy % Comment.
%       Txy, freq % Comment.
[varargout{1:nargout}] = welch({x,y},funcName,args{:}); % Calls the welch function with the processed arguments and assigns its outputs to varargout.

if nargout == 0 % Checks if no output arguments were requested.
    coder.internal.assert(coder.target('MATLAB'),'signal:tfestimate:PlottingNotSupported'); % Asserts that plotting is not supported in non-MATLAB targets.
    title(getString(message('signal:dspdata:dspdata:WelchTransferFunctionEstimate'))); % Sets the title of the plot.
end
end % Ends the function.

function [funcName,idx] = parseEstimator(varargin)
    % Parse the estimator n-v pair and return the flag for welch in esttype.
    % Remove the pair and return the remaining arguments for welch in args.
    %
    % For internal use only.
    
    %   Copyright 2023 The MathWorks, Inc.
    %#codegen
    idx = 0;
    coder.unroll();
    for i = 1:length(varargin)
        if ischar(varargin{i})
            validatestring(varargin{i},{'mimo','onesided','twosided','centered','Estimator','h1','h2'},'tfestimate');
            coder.internal.assert(coder.internal.isConst(varargin{i}),'signal:tfestimate:CharParamNotConstant');
            if strncmpi(varargin{i},'estimator',length(varargin{i}))
                coder.internal.errorIf(idx > 0,'signal:tfestimate:MultipleEstimatorOptions');
                coder.internal.errorIf(isempty({varargin{i+1:end}}),'signal:tfestimate:MissingEstimatorOption');
                est = validatestring(varargin{i+1},{'H1','H2'},'tfestimate','EST');
                idx = i;
            end
        end
    end
    
    if idx == 0
        est = 'H1';
    end
    
    % Return the function name for welch.
    if strcmp(est,'H2')
        funcName = 'tfeh2';
    else
        funcName = 'tfe';
    end
    
    % LocalWords:  Txy Welch's Pxy Pxx periodograms NOVERLAP NFFT Fs mimo
    % LocalWords:  FREQRANGE txy htool esttype freqrange Estimatorvalue tfeh