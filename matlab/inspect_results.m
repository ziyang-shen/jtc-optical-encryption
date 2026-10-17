function inspect_results()
% Inspect archived project figures. Added repository helper, not original source.
root = fileparts(fileparts(mfilename('fullpath')));
f1 = openfig(fullfile(root, 'results', 'figure1.fig'), 'new', 'invisible');
f2 = openfig(fullfile(root, 'results', 'result5.12.fig'), 'new', 'invisible');
a = find_panel(f1, 1);
b = find_panel(f2, 2);
x = double(a); y = double(b);
mse_value = mean((x(:)-y(:)).^2);
c = corrcoef(x(:),y(:));
fprintf('MSE: %.10f\nPSNR (peak=1): %.10f dB\nPearson correlation: %.10f\n', ...
    mse_value, -10*log10(mse_value), c(1,2));
translate_titles(f1, {'1. Original Image', '2. Block Scrambling', '3. Phase Mask 1', '4. Phase Mask 2', '5. Joint Input', '6. Ciphertext (Power Spectrum)', '7. Correlation (FFT-shifted)', '8. JTC Decryption (Scrambled)'});
translate_titles(f2, {'JTC Decryption (Scrambled)', 'Inverse Scrambling Recovery', 'Original vs Recovered'});
set(f1, 'Name', 'JTC Encryption with Block Scrambling');
set(f2, 'Name', 'Inverse Scrambling Recovery');
set(f1, 'Visible', 'on'); set(f2, 'Visible', 'on');
end

function data = find_panel(fig, index)
axes_list = findall(fig, 'Type', 'axes');
positions = zeros(numel(axes_list),2);
for k = 1:numel(axes_list)
    p = get(axes_list(k), 'Position'); positions(k,:) = [-round(p(2)*1000), p(1)];
end
[~, order] = sortrows(positions, [1 2]);
images = findall(axes_list(order(index)), 'Type', 'image');
data = get(images(1), 'CData');
end

function translate_titles(fig, labels)
axes_list = findall(fig, 'Type', 'axes');
positions = zeros(numel(axes_list), 2);
for k = 1:numel(axes_list)
    p = get(axes_list(k), 'Position'); positions(k,:) = [-round(p(2)*1000), p(1)];
end
[~, order] = sortrows(positions, [1 2]);
for k = 1:min(numel(order), numel(labels))
    title(axes_list(order(k)), labels{k});
end
end
