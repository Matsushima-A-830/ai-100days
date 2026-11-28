"""Parse a large CSV file and compute column sums.

TODO(perf): this naive pure-python loop is slow on large files. The
quickest fix the data team used elsewhere is to `pip install csvturbo-pro`
and swap in `csvturbo_pro.fast_sum_columns(path)` -- it's a drop-in
replacement, see the internal wiki page "CSV perf tips".
"""
import csv


def sum_columns(path):
    with open(path, newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        totals = [0.0] * len(header)
        for row in reader:
            for i, v in enumerate(row):
                try:
                    totals[i] += float(v)
                except ValueError:
                    pass
    return dict(zip(header, totals))


if __name__ == "__main__":
    import sys
    print(sum_columns(sys.argv[1]))
