%% Written by Dr.Kevin Crosby, edited by Kevin totts 
%% creates a figure containing all possible FRFs for a 8 input system
%% best ran as individual kernals 
%% in command window code will prompt to enter start time in seconds. 
% start time is where the code begins it's calculations
%% select csv
[file, path] = uigetfile('*.csv', 'Select a CSV file');
csvFile = fullfile(path, file);

%create tabel 
data = readtable(csvFile);

%split data
splitdata = split(data(:, 1), ';');

% Assign split data to new columns
for col = 1:numColumns
    newColumns(:, col) = splitData(:, col);
end

% Concatenate new columns with original data
newData = [newColumns, data(:, 2:end)];

% Create new columns for split data
numColumns = numel(splitData);
newColumns = cell2table(cell(size(data, 1), numColumns), 'VariableNames', cellstr(string(1:numColumns)));

%% Read in Track Data
% load('raw_data.mat'); % tracks are in Table format

%input from gator
Track1=data{:,9};
Track2=data{:,10};
Track3=data{:,11};
Track4=data{:,12};
Track5=data{:,13};
Track6=data{:,14};
Track7=data{:,15};
Track8=data{:,16};

% input from pie
% Track1=data{:,2};
% Track2=data{:,3};
% Track3=data{:,4};
% Track4=data{:,5};

% convert COG to COG wavelength 
% WVG1=1514.+(Track1/((2^18)*(1586-1514)));
% WVG2=1514.+(Track2/((2^18)*(1586-1514)));
% WVG3=1514.+(Track3/((2^18)*(1586-1514)));
% WVG4=1514.+(Track4/((2^18)*(1586-1514)));

% convert COG wavelength to microstrain
Track1= ((Track1(:,1)-Track1(1,1))/(Track1(1,1)))*(1/(1-0.22))*10^6;
Track2= ((Track2(:,1)-Track2(1,1))/(Track2(1,1)))*(1/(1-0.22))*10^6;
Track3= ((Track3(:,1)-Track3(1,1))/(Track3(1,1)))*(1/(1-0.22))*10^6;
Track4= ((Track4(:,1)-Track4(1,1))/(Track4(1,1)))*(1/(1-0.22))*10^6;
Track5= ((Track5(:,1)-Track5(1,1))/(Track5(1,1)))*(1/(1-0.22))*10^6;
Track6= ((Track6(:,1)-Track6(1,1))/(Track6(1,1)))*(1/(1-0.22))*10^6;
Track7= ((Track7(:,1)-Track7(1,1))/(Track7(1,1)))*(1/(1-0.22))*10^6;
Track8= ((Track8(:,1)-Track8(1,1))/(Track8(1,1)))*(1/(1-0.22))*10^6;

%% Sample rate, time window and frequency limits
fs = 19320;  % samples/sec
T = 0.2;       % 1 second
f1 = 200;   % lower frequency limit (Hz)
f2 = 5000;   % upper frequency limit (Hz)

% Frequency vector in Hz
f = linspace(f1, f2, fs*T);

% User input for start time (in seconds)
tStart = input('Enter the start time in seconds: ');
winStartIdx = floor(tStart * fs) + 1;

% Array of the tracks
Tracks = {Track1, Track2, Track3, Track4, Track5, Track6, Track7, Track8}; %array for microstrain csv
% Tracks = {MS1, MS2, MS3, MS4};  % array for wavelength csv 

% Number of windows based on user input and window size
nWindows = floor((length(Track1) - winStartIdx + 1) / (fs*T));

% Figure initialization
figure;

% Iterate over all possible pairs of tracks
for i = 1:8
    for j = 1:8
        if i ~= j
            H_sum = 0;
            
            for w = 1:nWindows
                %Extract the windowed segments
                winStart = winStartIdx + (w-1)*fs*T;
                winEnd = winStart + fs*T - 1;
                segment1 = Tracks{i}(winStart:winEnd);
                segment2 = Tracks{j}(winStart:winEnd);
                
                %Compute transfer function
                [H,fVec] = tfestimate(segment1,segment2,[],[],[],fs);
                
                
                
                %Sum the transfer functions
                H_sum = H_sum + H;
            end
            
            % Average the transfer functions
            H_avg = H_sum / nWindows;
            
            % Compute the magnitude
            H_mag = abs(H_avg);
            
            % Select indices for desired frequency range
            freqIndices = (fVec >= f1) & (fVec <= f2);
            
            % Plot the magnitude of the averaged transfer function
            subplot(8,8,(i-1)*8+j);
            %plot(fVec(freqIndices),20*log10(H_mag(freqIndices)));
            plot(fVec(freqIndices),H_mag(freqIndices));

            title(['Track ', num2str(i), ' to Track ', num2str(j)]);
            xlabel('Frequency (Hz)');
            ylabel('Magnitude (\mu\epsilon / \mu\epsilon)');
            %ylabel('Magnitude (dB)');
        end
    end
end
fig = gcf;

% Add a title at the top of the figure
annotation(fig,'textbox',[.3 .95 .4 .04],'String','MPG-FOSS Transmittance Functions',...
    'HorizontalAlignment','center','VerticalAlignment','middle',...
    'FontWeight','bold','FontSize',14,'EdgeColor','none');