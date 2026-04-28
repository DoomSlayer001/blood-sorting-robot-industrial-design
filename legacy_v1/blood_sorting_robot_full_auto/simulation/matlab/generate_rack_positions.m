function pos = generate_rack_positions(origin, cfg)
pos = zeros(cfg.rack_rows * cfg.rack_cols, 3);
k = 1;
for r = 1:cfg.rack_rows
    for c = 1:cfg.rack_cols
        pos(k,:) = [origin(1) + cfg.rack_margin + (c-1)*cfg.tube_pitch, ...
                    origin(2) + cfg.rack_margin + (r-1)*cfg.tube_pitch, cfg.z_pick];
        k = k + 1;
    end
end
end
