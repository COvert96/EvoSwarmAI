function plotGrid(state,state0,numExplored,numSteps,mapgrid,sz,obstacles)
% Plot area coverage environment

% Copyright 2024 The MathWorks, Inc.

persistent ax cells robots

if isempty(ax) || ~isvalid(ax)
    % build figure
    f = figure;
    f.Position = [195 120 400 300];
    %f.Visible = 'on';  % force external figure
    ax = gca(f);
    hold(ax,'on');
    if ~isequal(obstacles,-1)
        cmap = [255 255 255; ...    % white  (unexplored)
            255 140 105; ...    % light red (explored by A)
            152 251 152; ...    % light green (explored by B)
            176 226 255; ...    % light blue (explored by C)
            0 0 0]./255;        % black (obstacles)
    else
        cmap = [255 255 255;...     % white  (unexplored)
            255 140 105; ...    % light red (explored by A)
            152 251 152; ...    % light green (explored by B)
            176 226 255; ...    % light blue (explored by C)
            ]./255;
    end
    colormap(ax,cmap);

    % plot cells
    cdata = mapgrid;
    cells = imagesc(ax,[0.5 sz(1)-0.5],[0.5 sz(2)-0.5],cdata);

    % plot grid lines
    x = 0:1:sz(2);
    y = 0:1:sz(1);
    [X,Y] = meshgrid(x,y);
    plot(ax,X,Y,'Color',[0.94 0.94 0.94]);
    plot(ax,Y,X,'Color',[0.94 0.94 0.94]);

    % plot robots
    sA = state0(1,:);
    sB = state0(2,:);
    sC = state0(3,:);
    robots    = gobjects(1,2);
    robots(1) = rectangle(ax,'Position',[sA(2)-1 sA(1)-1 1 1],'FaceColor','r','Curvature',1);
    robots(2) = rectangle(ax,'Position',[sB(2)-1 sB(1)-1 1 1],'FaceColor','g','Curvature',1);
    robots(3) = rectangle(ax,'Position',[sC(2)-1 sC(1)-1 1 1],'FaceColor','b','Curvature',1);

    % time text
    totalExploredCells = sum(numExplored);
    totalCells = sz(1) * sz(2) - sum(mapgrid==1,'all');
    coverage = totalExploredCells / totalCells * 100;
    title(ax,sprintf('Steps = %d, Coverage = %.1f%%',numSteps,coverage));

    ax.XTick = 0:1:sz(1);
    ax.YTick = 0:1:sz(2);
    ax.XTickLabel = {};
    ax.YTickLabel = {};
    axis(ax,'equal');
    grid(ax,'on');
    ax.XLim = [0 sz(1)];
    ax.YLim = [0 sz(2)];
    ax.Box = 'on';
end

% update color map
cmap = [255 255 255; ...    % white  (unexplored)
    255 140 105; ...    % light red (explored by A)
    152 251 152; ...    % light green (explored by B)
    176 226 255; ...    % light blue (explored by C)
    0 0 0]./255;        % black (obstacles)
if all(mapgrid~=0,'all')
    cmap = cmap(2:end,:);   % no unexplored cells
end
if isequal(obstacles,-1)
    cmap = cmap(1:end-1,:); % no obstacles
end
colormap(ax,cmap);

% update cell colors
cdata = mapgrid;
cells.CData = cdata;

% update robot positions
for idx = 1:3
    s = state(idx,:);
    robots(idx).Position = [s(2)-1 s(1)-1 1 1];
end

% update info text
totalExploredCells = sum(numExplored);
totalCells = sz(1) * sz(2) - sum(mapgrid==1,'all');
coverage = totalExploredCells / totalCells * 100;
ax.Title.String = sprintf('Steps = %d, Coverage = %.1f%%',numSteps,coverage);

ax.XLim = [0 sz(1)];
ax.YLim = [0 sz(2)];

drawnow();
