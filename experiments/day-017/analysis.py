import sys
sys.path.insert(0, "installed-skills/statistical-analysis/scripts")

import numpy as np
import pandas as pd
import pingouin as pg
from assumption_checks import comprehensive_assumption_check, detect_outliers

group_a = np.array([12, 15, 14, 13, 55, 14])
group_b = np.array([10, 11, 9, 12, 10, 11, 9, 10, 12])

print("=== Descriptives ===")
for name, g in [("A", group_a), ("B", group_b)]:
    print(f"Group {name}: n={len(g)}, mean={g.mean():.2f}, sd={g.std(ddof=1):.2f}, "
          f"median={np.median(g):.2f}, min={g.min()}, max={g.max()}")

df = pd.DataFrame({
    "value": np.concatenate([group_a, group_b]),
    "group": ["A"] * len(group_a) + ["B"] * len(group_b),
})

print("\n=== Outlier detection (Group A) ===")
out_a = detect_outliers(group_a, method="iqr")
print(out_a)

print("\n=== Outlier detection (Group B) ===")
out_b = detect_outliers(group_b, method="iqr")
print(out_b)

print("\n=== Comprehensive assumption check ===")
results = comprehensive_assumption_check(data=df, value_col="value", group_col="group", alpha=0.05)
for k, v in results.items():
    print(f"--- {k} ---")
    print(v)

print("\n=== Welch's t-test (prespecified, as if no outlier concern) ===")
res = pg.ttest(group_a, group_b, correction=True)
print(res)
d = pg.compute_effsize(group_a, group_b, eftype="cohen")
print(f"Cohen's d (signed, A-B) = {d:.3f}")

print("\n=== Mann-Whitney U (rank-based alternative) ===")
mwu = pg.mwu(group_a, group_b)
print(mwu)

print("\n=== Sensitivity: t-test with the outlier (55) removed from Group A ===")
group_a_no_outlier = np.array([12, 15, 14, 13, 14])
res2 = pg.ttest(group_a_no_outlier, group_b, correction=True)
print(res2)
d2 = pg.compute_effsize(group_a_no_outlier, group_b, eftype="cohen")
print(f"Cohen's d (signed, A-B) without outlier = {d2:.3f}")
