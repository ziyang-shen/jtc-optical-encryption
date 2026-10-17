"""Verify archived MATLAB figure data without executing MATLAB callbacks."""
from pathlib import Path
import numpy as np
from scipy.io import loadmat

ROOT = Path(__file__).resolve().parents[1]

def panels(filename):
    figure = loadmat(ROOT / 'results' / filename, simplify_cells=True)['hgS_070000']
    result = []
    for axis in figure['children']:
        children = axis.get('children', [])
        if isinstance(children, dict):
            children = [children]
        for child in children:
            if child.get('type') == 'image':
                result.append(np.asarray(child['properties']['CData']))
    return result

def normalize(x):
    return (x-x.min()) / (x.max()-x.min())

def blocks(x):
    return [x[i:i+32, j:j+32] for j in range(0,256,32) for i in range(0,256,32)]

def main():
    original, scrambled, p1, p2, joint_display, cipher_display, correlation, decoded = panels('figure1.fig')
    other_decoded, recovered, comparison = panels('result5.12.fig')
    np.testing.assert_array_equal(decoded, other_decoded)
    np.testing.assert_array_equal(np.sort(original.ravel()), np.sort(scrambled.ravel()))
    joint = np.zeros((512,512), dtype=complex)
    joint[:256,:256] = scrambled * np.exp(2j*np.pi*p1)
    joint[256:,256:] = np.exp(2j*np.pi*p2)
    np.testing.assert_allclose(np.abs(joint), joint_display, atol=1e-12)
    power = np.abs(np.fft.fft2(joint))**2
    np.testing.assert_allclose(normalize(np.log1p(power)), cipher_display, atol=1e-11)
    key = np.zeros_like(joint)
    key[256:,256:] = np.exp(2j*np.pi*p2)
    rebuilt = np.abs(np.fft.fftshift(np.fft.ifft2(power*np.conj(np.fft.fft2(key)))))
    np.testing.assert_allclose(rebuilt, correlation, rtol=1e-10, atol=1e-8)
    np.testing.assert_allclose(normalize(correlation[128:384,128:384]), decoded, atol=1e-12)
    # Repeated uniform input blocks make the original permutation ambiguous.
    # Match both input and recovered blocks, enforcing a one-to-one assignment.
    source, target, out, before = map(blocks, [original, scrambled, recovered, decoded])
    from scipy.optimize import linear_sum_assignment
    compatible = np.array([[np.array_equal(target[i], source[k]) and
                            np.allclose(before[i], out[k], rtol=0, atol=1e-12)
                            for k in range(64)] for i in range(64)])
    rows, cols = linear_sum_assignment(~compatible)
    if not compatible[rows, cols].all():
        raise AssertionError('Inverse block arrangement does not match')
    mse = np.mean((original-recovered)**2)
    print('Verified: shared decoded image, block permutation, joint magnitude,')
    print('log-power display, raw-power correlation, central crop, inverse blocks.')
    print(f'MSE: {mse:.10f}')
    print(f'PSNR (nominal peak=1): {-10*np.log10(mse):.10f} dB')
    print(f'Pearson correlation: {np.corrcoef(original.ravel(), recovered.ravel())[0,1]:.10f}')
    print(f'Original range: [{original.min():.10f}, {original.max():.10f}]')
    print(f'Raw correlation maximum: {correlation.max():.10f}')
    print(f'Distinct phase values: {np.unique(p1).size}, {np.unique(p2).size}')
    print('No original simulation source or attack-trial data is included.')

if __name__ == '__main__':
    main()
