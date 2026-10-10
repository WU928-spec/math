"""m=4 候选"值坐标"（C* 下界）筛选：在 4 台机器、每台 <=3 件、负载 <=1、所有工件 > alpha 的
全体非增实例上，最大化各候选表达式。最大值 <= 1 表示该表达式是恒成立的 C* 下界（可用作 cap 坐标）。"""
import math, sys
import numpy as np
from scipy.optimize import linprog

c = (1 + math.sqrt(37)) / 6
ALPHA = 1.5 * (c - 1)          # (3/2)(c-1) = 0.27069...（O3 的工件下界）
M = 4                          # 机器数
N = int(sys.argv[1]) if len(sys.argv) > 1 else 12


def partitions(n, maxb=3, nblocks=M):
    """{0..n-1} 分到 <=nblocks 块、每块 <=maxb 个（规范枚举：新块只从最小剩余元素开始）"""
    def rec(rest, blocks):
        if not rest:
            yield blocks
            return
        e = rest[0]
        for i, b in enumerate(blocks):
            if len(b) < maxb:
                yield from rec(rest[1:], blocks[:i] + [b + [e]] + blocks[i + 1:])
        if len(blocks) < nblocks:
            yield from rec(rest[1:], blocks + [[e]])
    yield from rec(list(range(n)), [])


PARTS = list(partitions(N))
print(f"n={N}, 机器数={M}, 结构数={len(PARTS)}", flush=True)


def max_of(obj_terms):
    """maximize min over terms（每个 term 是 (下标列表, 系数) 的线性式）；返回 (最大值, 见证 p)"""
    nt = len(obj_terms)
    best = None
    for blocks in PARTS:
        A, B = [], []
        for blk in blocks:                       # 每台负载 <= 1
            row = [0.0] * (N + nt)
            for i in blk:
                row[i] = 1.0
            A.append(row); B.append(1.0)
        for i in range(N - 1):                   # p_i >= p_{i+1}
            row = [0.0] * (N + nt); row[i] = -1.0; row[i + 1] = 1.0
            A.append(row); B.append(0.0)
        for k, term in enumerate(obj_terms):     # t_k - term <= 0
            row = [0.0] * (N + nt)
            for idx, coef in term:
                row[idx] += -coef
            row[N + k] = 1.0
            A.append(row); B.append(0.0)
        obj = [0.0] * N + [1.0] * nt             # 最大化 sum t_k（对单 term 即最大化该项）
        r = linprog(c=[-x for x in obj], A_ub=A, b_ub=B,
                    bounds=[(ALPHA, None)] * N + [(None, None)] * nt, method="highs")
        if r.status == 0 and (best is None or -r.fun > best[0] + 1e-12):
            best = (-r.fun, tuple(r.x[:N]))
    return best


def T(*specs):
    """specs: 每个是 [(下标,系数), ...]"""
    return list(specs)


tests = [
    ("p1", T([(0, 1)])),
    ("p4+p5", T([(3, 1), (4, 1)])),
    ("p2+p5", T([(1, 1), (4, 1)])),
    ("p2+p6", T([(1, 1), (5, 1)])),
    ("p5+p6", T([(4, 1), (5, 1)])),
    ("p3+p4+p5", T([(2, 1), (3, 1), (4, 1)])),
    ("p2+p5+p6", T([(1, 1), (4, 1), (5, 1)])),
    ("min{p2+p5, p3+p4+p5}", T([(1, 1), (4, 1)], [(2, 1), (3, 1), (4, 1)])),
    ("min{p2+p6, p3+p5+p6}", T([(1, 1), (5, 1)], [(2, 1), (4, 1), (5, 1)])),
    ("min{p2+p6, p4+p5+p6}", T([(1, 1), (5, 1)], [(3, 1), (4, 1), (5, 1)])),
    ("min{p5+p6, p3+p4+p5}", T([(4, 1), (5, 1)], [(2, 1), (3, 1), (4, 1)])),
    ("p7+p8+p9", T([(6, 1), (7, 1), (8, 1)])),
    ("p10+p11+p12", T([(9, 1), (10, 1), (11, 1)])),
]

print("%-26s %10s   %s" % ("候选表达式", "LP 最大值", "是否恒 <= C*（可作坐标）"))
for name, terms in tests:
    b = max_of(terms)
    if b is None:
        print("%-26s %10s   LP 异常" % (name, "-")); continue
    val, p = b
    ok = "是" if val <= 1 + 1e-9 else "**否**"
    print("%-26s %10.4f   %s" % (name, val, ok), flush=True)
