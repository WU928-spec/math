"""a2_transfer_falsifier.py — 高端 junior 转移引理候选的即时证伪器（(P) 第三条攻击线基建）。

输入：候选引理 = a2_candidate_spec.py 的 candidate_rows（或 --spec 指定模块）。
输出判决（按 (m,k) × t 网格）：
  BLOCKED      —— LP 不可行：候选把角落多面体砍空，引理若成立则 (P) 平凡成立（候选有戏）；
  ALIVE-UNPACK —— LP 可行但全部采样点不可装箱（与 (P) 一致，候选不添反例）；
  COUNTEREXAMPLE——发现可装箱点：候选引理或 (P) 本身有洞（打印完整物品多重集）。
Π* = build_close 去掉装箱行（SS/SJ/JJ/JJJ）——角落全部合法约束（含保序 mon2），装箱另测。
装箱判定：子集和 + memoized DFS（精确，n=2m≤24 快；m>12 自动跳过并标注）。
采样：LP 顶点（多随机方向最优）+ 零目标可行点 + 历史鬼影族（分层有理点重构）。
用法：python a2_transfer_falsifier.py [--spec a2_candidate_spec] [--m 6,8,12] [--dfs] [--once]
"""
import numpy as np
from scipy.optimize import linprog
from functools import lru_cache
from fractions import Fraction as F
import sys, os, importlib, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hole_close import build_close

MG = F(1, 10000)


def polytope(m, k, extra_rows):
    """Π*(m,k) + 候选行。返回 (A, b)（浮点，t 固定网格在调用处代入）——
    行形式 A x <= bc + bt*t；此处保留符号 t，固定 t 由调用者代入。"""
    A, bc, bt, names, nv = build_close(m, (1, m - 3, 0, 1, 0, 0), k, use_ammin=True)  # cnt 只影响装箱行；ammin=a_m=s₀ 已登记合法
    keep = [i for i, nm in enumerate(names) if nm not in ('SS', 'SJ', 'JJJ', 'JJ')]
    A = [A[i] for i in keep]
    bc = [bc[i] for i in keep]
    bt = [bt[i] for i in keep]
    return A, bc, bt, nv


def apply_candidate(A, bc, bt, nv, cand):
    nS = (nv - 6) // 2

    def vidx(v):
        if v == 'p': return 0
        if v == 't': return 1
        if v == 'am': return 2 + 2 * nS
        if v == 'q1': return 2 + 2 * nS + 1
        if v[0] == 's': return 2 + int(v[1:])
        if v[0] == 'j': return 2 + nS + int(v[1:])
        raise ValueError(v)
    for coef, bcx, btx, nm in cand:
        row = [F(0)] * nv
        for v, c in coef.items():
            row[vidx(v)] = F(c).limit_denominator(10**6)
        A.append(row); bc.append(F(bcx)); bt.append(F(btx))
    return A, bc, bt


def feasible_at(A, bc, bt, t0, nv, direction=None):
    """A x <= bc + bt*t（t=x[1]）在 t=t0 的可行性：变形 (A − bt·e1ᵀ)x <= bc，x[1] 固定。"""
    Af = np.array([[float(x) for x in row] for row in A])
    bcf = np.array([float(x) for x in bc]); btf = np.array([float(x) for x in bt])
    A2 = Af.copy(); A2[:, 1] -= btf
    bounds = [(None, None)] * nv
    bounds[1] = (t0, t0)
    c = np.zeros(nv) if direction is None else direction
    res = linprog(c=c, A_ub=A2, b_ub=bcf, bounds=bounds, method='highs')
    return (res.status == 0), (res.x if res.status == 0 else None)


def can_pack(items, m, cap=1.0):
    n = len(items)
    if n > 26:
        return None  # 太大跳过（m>12）
    subsum = [0.0] * (1 << n)
    for mask in range(1, 1 << n):
        lsb = mask & (-mask)
        subsum[mask] = subsum[mask ^ lsb] + items[lsb.bit_length() - 1]

    @lru_cache(maxsize=None)
    def dfs(mask, k):
        if mask == 0:
            return True
        if k == 0:
            return False
        if subsum[mask] > k * cap + 1e-9:
            return False
        sub = mask
        while sub:
            if subsum[sub] <= cap + 1e-9 and dfs(mask ^ sub, k - 1):
                return True
            sub = (sub - 1) & mask
        return False
    return dfs((1 << n) - 1, m)


def points_of(x, m):
    nS = m - 1
    p, t = x[0], x[1]
    s = list(x[2:2 + nS]); j = list(x[2 + nS:2 + 2 * nS])
    return [p, t] + s + j


def ghost_point(m, k):
    """历史洞族的分层有理鬼影（t=1/3 顶窗、三层 senior、两级 junior）——最锋利测试点。"""
    nS = m - 1
    t = 1 / 3
    p = 11 / 12
    a = max(1, round(nS * 4 / 11))  # 分层比例粗配
    b = max(0, round(nS * 4 / 11))
    s = [0.5] * a + [7 / 12] * b + [2 / 3] * (nS - a - b)
    j = [5 / 12] * a + [1 / 3] * (nS - a)
    return [p, t] + s + j + [0.45, 5 / 12]


def main():
    args = sys.argv[1:]
    spec = 'a2_candidate_spec'
    ms = [6, 8, 12]
    do_dfs = '--dfs' in args
    if '--spec' in args:
        spec = args[args.index('--spec') + 1]
    if '--m' in args:
        ms = [int(x) for x in args[args.index('--m') + 1].split(',')]
    mod = importlib.import_module(spec)
    cand_fn = mod.candidate_rows
    t0_all = time.time()
    print(f'=== 转移引理证伪器：spec={spec} m={ms} ===')
    summary = {}
    for m in ms:
        nS = m - 1
        tl = (m - 1) / (4 * (m - 2))
        for k in range(1, m):
            cand = cand_fn(m, k, {'nS': nS, 'jj': k - 1})
            A, bc, bt, nv = polytope(m, k, cand)
            if cand:
                A, bc, bt = apply_candidate(A, bc, bt, nv, cand)
            verdict = 'BLOCKED'
            pack_hits = 0
            pts_tested = 0
            for t0 in np.linspace(tl + 0.002, 1 / 3, 5):
                feas, x = feasible_at(A, bc, bt, t0, nv)
                if not feas:
                    continue
                verdict = 'ALIVE-UNPACK'  # 暂记；若 DFS 发现可装则翻 COUNTEREXAMPLE
                if do_dfs and m <= 12:
                    # 采样：该可行点 + 两个随机方向顶点 + 鬼影点（若满足 Π*）
                    pts = [x]
                    rng = np.random.default_rng(0)
                    for _ in range(2):
                        d = rng.normal(size=nv)
                        f2, x2 = feasible_at(A, bc, bt, t0, nv, direction=d)
                        if f2:
                            pts.append(x2)
                    g = np.array(ghost_point(m, k))
                    Afix = np.array([[float(v) for v in row] for row in A])
                    bfix = np.array([float(c0) + float(c1) * t0 for c0, c1 in zip(bc, bt)])
                    if np.all(Afix[:, [0] + list(range(2, nv))] @ g[[0] + list(range(2, nv))] <= bfix + 1e-9) and abs(g[1] - t0) < 1e-6:
                        pts.append(g)
                    for pt in pts:
                        items = points_of(pt, m)
                        pts_tested += 1
                        if can_pack(items, m):
                            pack_hits += 1
                            verdict = 'COUNTEREXAMPLE'
                            print(f'  ✗✗ 可装箱反例 m={m} k={k} t={t0:.4f}: items={np.round(items,4).tolist()}', flush=True)
            summary[(m, k)] = verdict
            tag = {'BLOCKED': 'BLOCKED', 'ALIVE-UNPACK': 'ALIVE(未装)', 'COUNTEREXAMPLE': '✗COUNTEREXAMPLE'}[verdict]
            print(f'  m={m} k={k}: {tag}' + (f'（DFS 测 {pts_tested} 点，可装 {pack_hits}）' if do_dfs else ''), flush=True)
    nb = sum(1 for v in summary.values() if v == 'BLOCKED')
    na = sum(1 for v in summary.values() if v == 'ALIVE-UNPACK')
    nc = sum(1 for v in summary.values() if v == 'COUNTEREXAMPLE')
    print(f'=== 汇总：BLOCKED {nb} / ALIVE-UNPACK {na} / COUNTEREXAMPLE {nc}（{time.time()-t0_all:.0f}s）===')


if __name__ == '__main__':
    main()
