function plot_results(result, cfg)
figdir = fullfile(cfg.root, 'results', 'figures'); if ~exist(figdir,'dir'), mkdir(figdir); end
names = {'X','Y','Z'};
f = figure('Visible','off'); tiledlayout(3,1);
for i=1:3
    nexttile; plot(result.t,result.ref(:,i),'k--'); hold on; plot(result.t,result.actual(:,i));
    grid on; ylabel([names{i} ' mm']); legend('ref','actual');
end
xlabel('Time s'); saveas(f, fullfile(figdir,'matlab_position_tracking.png')); close(f);
f = figure('Visible','off'); plot3(result.actual(:,1),result.actual(:,2),result.actual(:,3),'r'); hold on;
plot3(result.ref(:,1),result.ref(:,2),result.ref(:,3),'k--'); grid on; xlabel('X'); ylabel('Y'); zlabel('Z');
saveas(f, fullfile(figdir,'matlab_end_effector_3d.png')); close(f);
end
