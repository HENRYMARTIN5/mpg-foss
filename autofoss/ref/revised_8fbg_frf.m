% Written by Dr. Kevin Crosby, edited by Kevin Totts
% Creates a figure containing all possible FRFs for an 8-input system
% Best run as individual kernels
% In the command window, the code will prompt to enter the start time in seconds.
% The start time is where the code begins its calculations.

% Select CSV file
[file, path] = uigetfile('*.csv', 'Select a CSV file');
csvFile = fullfile(path, file);

% Read the CSV file into a table
data = readtable(csvFile);

% Split data in the first column
% splitData = split(data{:, 1}, ',');

% Convert split data into a table
%numColumns = size(splitData, 2);
%newColumns = array2table(splitData, 'VariableNames', cellstr(string(1:numColumns)));

% Concatenate new columns with the remaining original data
%newData = [newColumns, data(:, 2:end)];
newData = data; 

%% Read in Track Data
% Extract track data from specific columns
Track1 = newData{:, 3};
Track2 = newData{:, 4};
Track3 = newData{:, 5};
Track4 = newData{:, 6};
Track5 = newData{:, 7};
Track6 = newData{:, 8};
Track7 = newData{:, 9};
Track8 = newData{:, 10};
TrackW = newData{:, 2};

% Convert COG wavelength to microstrain
Tracks = {Track1, Track2, Track3, Track4, Track5, Track6, Track7, Track8};
for k = 1:8
    Tracks{k} = ((Tracks{k} - Tracks{k}(1)) / Tracks{k}(1)) * (1 / (1 - 0.22)) * 10^6;
end

%% Sample rate, time window and frequency limits
fs = 19320;  % samples/sec
T = 0.2;     % 0.2 seconds
f1 = 200;    % lower frequency limit (Hz)
f2 = 5000;   % upper frequency limit (Hz)

% Frequency vector in Hz
f = linspace(f1, f2, fs * T);  

% User input for start time (in seconds)
tStart = input('Enter the start time in seconds: ');
winStartIdx = floor(tStart * fs) + 1;

% Number of windows based on user input and window size
nWindows = floor((length(Track1) - winStartIdx + 1) / (fs * T));

% Figure initialization
figure;

% Iterate over all possible pairs of tracks
for i = 1:8
    for j = 1:8
        if i ~= j
            H_sum = 0;
            
            for w = 1:nWindows
                % Extract the windowed segments
                winStart = winStartIdx + (w-1) * fs * T;
                winEnd = winStart + fs * T - 1;
                segment1 = Tracks{i}(winStart:winEnd);
                segment2 = Tracks{j}(winStart:winEnd);
                
                % Compute transfer function
                [H, fVec] = tfestimate(segment1, segment2, [], [], [], fs);
                
                % Sum the transfer functions
                H_sum = H_sum + H;
            end
            
            % Average the transfer functions
            H_avg = H_sum / nWindows;
            
            % Compute the magnitude
            H_mag = abs(H_avg);
            
            % Select indices for desired frequency range
            freqIndices = (fVec >= f1) & (fVec <= f2);
            
            % Plot the magnitude of the averaged transfer function
            subplot(8, 8, (i-1) * 8 + j);
            plot(fVec(freqIndices), H_mag(freqIndices));
            title(['Track ', num2str(i), ' to Track ', num2str(j)]);
            xlabel('Frequency (Hz)');
            ylabel('Magnitude (\mu\epsilon / \mu\epsilon)');
        end
    end
end
fig = gcf;

% Add a title at the top of the figure
annotation(fig, 'textbox', [0.3 0.95 0.4 0.04], 'String', 'MPG-FOSS Transmittance Functions', ...
    'HorizontalAlignment', 'center', 'VerticalAlignment', 'middle', ...
    'FontWeight', 'bold', 'FontSize', 14, 'EdgeColor', 'none');