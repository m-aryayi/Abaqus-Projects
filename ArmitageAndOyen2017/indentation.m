clc;clear;close all;

%% WorDir is the working directory of the program
WorDir = pwd;
AbqDir = ['cd ' WorDir];
system(AbqDir); %Make WorDir ABAQUS working directory
subroutineBas = 'USDFLD_Base';
subroutineRun = 'USDFLD_Run';
inputFileBas = 'Job-Base';
inputFileRun = 'Job-Run';

%% Parameters
Ec = 19;
Es = 3;
W = 12;

interfaceDistance = linspace(-20,20,20);

% in inp file this parameters considered:
% posion ratio : 0.4 , R : 1 , h : 0.0625

%% Run loop

% Update InputFile
fidin = fopen([inputFileBas '.inp'],'r');
fidout = fopen([inputFileRun '.inp'],'w+');

while feof(fidin) == 0
    tline = fgetl(fidin);
    
    specialString = '*Elastic, dependencies=1'; %This exsits in inp file
    header = strfind(tline,specialString);
    if ~isempty(header)
        fprintf(fidout,'%s\n',tline);
        text1 = [num2str(Ec) ', 0.4, ,  0.'];
        text2 = [num2str(Es) ', 0.4, ,  1.'];
        fprintf(fidout,'%s\n%s\n', text1,text2);
        fgetl(fidin);fgetl(fidin); % Skip base lines
        continue;
    end
    
    fprintf(fidout,'%s\n',tline);
end

fclose('all');

indentorForce = zeros(1,length(interfaceDistance));

for ii = 1:length(interfaceDistance)
    
    % Update Subroutine
    fidin = fopen([subroutineBas '.for'],'r');
    fidout = fopen([subroutineRun '.for'],'w+');
    
    while feof(fidin) == 0
        tline = fgetl(fidin);
        
        specialString = 'c		for matlab'; %This is added in subroutine
        header = strfind(tline,specialString);
        if ~isempty(header)
            fprintf(fidout,'%s\n',tline);
            text1 = ['        a = -5.89/' num2str(W)];
            text2 = ['        c = a*(x+(' num2str(interfaceDistance(ii)) '))'];
            fprintf(fidout,'%s\n%s\n', text1,text2);
            fgetl(fidin);fgetl(fidin); % Skip base lines
            continue;
        end
        
        fprintf(fidout,'%s\n',tline);
    end
    
    fclose('all');
    
    Itr0Cmd = ['abaqus job=' inputFileRun ' input=' inputFileRun ' user=' subroutineRun '.for' ];
    system(Itr0Cmd);
    
    %%% Check lck (Run Start)
    A = 0;
    while A == 0
        A = exist([inputFileRun '.lck'],'file');
    end
    
    %%% Check lck (Run Finish)
    A = 2;
    while A == 2
        A = exist([inputFileRun '.lck'],'file');
    end
    
    %%% Get Force
    fid = fopen([inputFileRun '.dat'],'r');
    lineCounter = 0;
    
    while feof(fid) == 0
        
        tline = fgetl(fid);
        lineCounter = lineCounter + 1;
        
        removedSpaces = strrep(tline,' ',''); % Replace space with null.
        % Upper lines has been used to code work in differnet abaqus version
        specialString = 'NODEFOOT-RF2'; %This exsits in dat file
        header = strfind(removedSpaces,specialString);
        if ~isempty(header)
            Header_Line = lineCounter+2;
            NodeData = importdata([inputFileRun '.dat'],' ',Header_Line);
            indentorForce(ii) = -NodeData.data(1,2); %negetive is for direction
        end
        
    end
    fclose('all');
end

E = 3*indentorForce*(1-0.4^2)/(4*sqrt(1*0.0625^3));