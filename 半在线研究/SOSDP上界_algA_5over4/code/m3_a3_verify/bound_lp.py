import itertools, math
import numpy as np
from scipy.optimize import linprog

c = (1 + math.sqrt(37)) / 6
LOW = 1.5 * (c - 1)   # (3/2)(c-1) = 0.27069...  all jobs strictly greater than this

def partitions(n, maxb=3, nblocks=3):
    """all ways to split {0..n-1} into <=nblocks nonempty blocks of size<=maxb"""
    idx = list(range(n))
    def rec(rest, blocks):
        if not rest:
            yield blocks
            return
        # take the smallest remaining element, place it
        e = rest[0]
        for i, b in enumerate(blocks):
            if len(b) < maxb:
                yield from rec(rest[1:], blocks[:i] + [b + [e]] + blocks[i+1:])
        if len(blocks) < nblocks:
            yield from rec(rest[1:], blocks + [[e]])
    for b in rec(idx, []):
        yield b

def solve(n, obj, extra=()):
    """max obj . p  over p1>=..>=pn>=LOW (strict, use LOW+eps*0) and some packing with load<=1"""
    best = None
    for blocks in partitions(n):
        A, B = [], []
        for blk in blocks:
            row = [0.0] * n
            for i in blk:
                row[i] = 1.0
            A.append(row); B.append(1.0)
        for i in range(n - 1):          # p_i - p_{i+1} >= 0
            row = [0.0] * n; row[i] = -1.0; row[i + 1] = 1.0
            A.append(row); B.append(0.0)
        for row, val in extra:
            A.append(row); B.append(val)
        res = linprog(c=[-x for x in obj], A_ub=A, b_ub=B,
                      bounds=[(LOW, None)] * n, method="highs")
        if res.status == 0 and (best is None or -res.fun > best[0] + 1e-12):
            best = (-res.fun, tuple(res.x), blocks)
    return best

def vec(n, spec):
    v = [0.0] * n
    for i in spec:
        v[i - 1] = 1.0
    return v

def main():
    print("c =", c, " (3/2)(c-1) =", LOW)
    print()
    for n in (7, 8, 9):
        for name, spec in [("p3", [3]), ("p4", [4]), ("p5", [5]), ("p6", [6]), ("p7", [7]),
                           ("p6+p7", [6, 7]), ("p5+p8", [5, 8]), ("p2", [2]),
                           ("p4+p9", [4, 9]), ("p3+p4+p9", [3, 4, 9]),
                           ("p1+p4+p9", [1, 4, 9]), ("p1+p8+p9", [1, 8, 9]),
                           ("p2+p5+p8", [2, 5, 8]), ("p2+p6", [2, 6]),
                           ("p2+p5+p6", [2, 5, 6]), ("p3+p6+p7", [3, 6, 7])]:
            if max(spec) > n:
                continue
            b = solve(n, vec(n, spec))
            print("n=%d  max(%-9s) = %.4f   p=%s" % (n, name, b[0], " ".join("%.4f" % v for v in b[1])))
        print()


if __name__ == "__main__":
    main()
