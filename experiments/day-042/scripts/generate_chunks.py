"""
検証に使った合成ログ(著作権的に無害なランダム単語+連番+乱数値)を生成する。
driver.py / continue_bili.py / continue_direct.py はこの出力(chunk_part_aa..af)を
scratch-run/ ディレクトリから読む想定。
"""
import random

WORDS = ['alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta',
          'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'omicron', 'pi', 'rho',
          'sigma', 'tau', 'upsilon']

# segment 1-4: seed=42, 1600 lines split into 4 (chunk_part_aa..ad, via `split -n l/4`)
random.seed(42)
lines = []
for i in range(1, 1601):
    row = ' '.join(random.choice(WORDS) for _ in range(12))
    lines.append(f'LOG-{i:05d}: {row} value={random.randint(1000, 9999)}')
with open('chunk.txt', 'w') as f:
    f.write('\n'.join(lines))
# 実際の分割は `split -n l/4 chunk.txt chunk_part_` で行った(各400行前後)

# segment 5-6: seed=99, 400 lines each (chunk_part_ae, chunk_part_af)
random.seed(99)
for part in range(5, 7):
    seg_lines = []
    for i in range(1, 401):
        row = ' '.join(random.choice(WORDS) for _ in range(12))
        seg_lines.append(f'LOG-{(part - 1) * 400 + i:05d}: {row} value={random.randint(1000, 9999)}')
    fname = 'chunk_part_a' + chr(ord('a') + part - 1)
    with open(fname, 'w') as f:
        f.write('\n'.join(seg_lines))
    print(fname, 'written')
