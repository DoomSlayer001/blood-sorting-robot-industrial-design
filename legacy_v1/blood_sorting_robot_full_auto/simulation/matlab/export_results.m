function export_results(result, cfg)
datadir = fullfile(cfg.root, 'results', 'data'); if ~exist(datadir,'dir'), mkdir(datadir); end
T = array2table([result.t result.ref result.actual result.vel result.u], ...
    'VariableNames', {'t','x_ref','y_ref','z_ref','x','y','z','vx','vy','vz','ux','uy','uz'});
writetable(T, fullfile(datadir,'matlab_pid_simulation.csv'));
err = result.ref - result.actual;
metrics = [max(abs(err)); mean(abs(err)); sqrt(mean(err.^2))];
writematrix(metrics, fullfile(datadir,'matlab_error_metrics.csv'));
end
