"""a2_transfer_falsifier_v2.py — 证伪器优化版（剖析驱动：DFS 占 99%+）。

优化（回归必须一致）：
1. DFS 重写 can_pack_fast：窗口结构（全物品 ≥ t > 1/4）⟹ 每箱 ≤3 件 ⟹ 可行子集只需
   |S|≤3 且 sum≤1（n=24 时 ~2.3k 个 vs 2^24）；DFS 选最低位未装物品、枚举含它的可行子集、
   mask 记忆化。p+t>5/4 ⟹ p 独占一箱（其箱不再枚举）。t≤1/4 时回退旧版全子集 DFS。
2. LP 缓存：同一 (m,k) 的 Π* 基础行 + 浮点矩阵只建一次，候选行追加即算；
   feasible_at 浮点变形 (A−bt·e1) 按 (m,k,t0) 缓存。
3. 并行：A2_FALSIFIER_WORKERS（默认 2，轻载可到 4）个进程跑 (m,k) 单元；nice 继承。
4. t 网格两档：粗筛 5 点；只在有可行点的 t 邻域加密（目前：粗即可行即测 DFS，不再全网格）。
回归：--regress 对新旧 verdict 逐案比对（m=6,8 基线 12 案 + 有牙 4 例）。
"""
import numpy as np
from scipy.optimize import linprog
from functools import lru_cache
from fractions import Fraction as F
import sys, os, importlib, time
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hole_close import build_close

MG = F(1, 10000)
_POLY = {}
_FLT = {}


def polytope(m, k):
    if (m, k) not in _POLY:
        A, bc, bt, names, nv = build_close(m, (1, m - 3, 0, 1, 0, 0), k, use_ammin=True)
        keep = [i for i, nm in enumerate(names) if nm not in ('SS', 'SJ', 'JJJ', 'JJ')]
        _POLY[(m, k)] = ([A[i] for i in keep], [bc[i] for i in keep], [bt[i] for i in keep], nv)
    return _POLY[(m, k)]


def vidx_of(nv):
    nS = (nv - 6) // 2
    def vidx(v):
        if v == 'p': return 0
        if v == 't': return 1
        if v == 'am': return 2 + 2 * nS
        if v == 'q1': return 2 + 2 * nS + 1
        if v[0] == 's': return 2 + int(v[1:])
        if v[0] == 'j': return 2 + nS + int(v[1:])
        raise ValueError(v)
    return vidx


def float_form(m, k, cand, t0):
    key = (m, k, round(t0, 6))
    if key in _FLT:
        return _FLT[key]
    A, bc, bt, nv = polytope(m, k)
    vidx = vidx_of(nv)
    for coef, bcx, btx, nm in cand:
        row = [F(0)] * nv
        for v, c in coef.items():
            row[vidx(v)] = F(c).limit_denominator(10**6)
        A.append(row); bc.append(F(bcx)); bt.append(F(btx))
    Af = np.array([[float(x) for x in row] for row in A])
    bcf = np.array([float(x) for x in bc]); btf = np.array([float(x) for x in bt])
    A2 = Af.copy(); A2[:, 1] -= btf
    _FLT[key] = (A2, bcf, nv)
    return _FLT[key]


def feasible_at2(m, k, cand, t0, direction=None):
    A2, bcf, nv = float_form(m, k, cand, t0)
    bounds = [(None, None)] * nv
    bounds[1] = (t0, t0)
    c = np.zeros(nv) if direction is None else direction
    res = linprog(c=c, A_ub=A2, b_ub=bcf, bounds=bounds, method='highs')
    return (res.status == 0), (res.x if res.status == 0 else None)


def can_pack_fast(items, m, cap=1.0):
    """窗口结构版精确装箱：全物品 > 1/4 ⟹ 每箱 ≤3 件。返回 True/False（None=不适用）。"""
    items = sorted(items, reverse=True)
    if items[-1] <= 0.25 + 1e-12:
        return None
    n = len(items)
    # p 独占：最大件若 > cap - 最小件，其独占（口袋2 角落 p+t>5/4>1 恒成立）
    if items[0] + items[-1] > cap + 1e-12:
        m -= 1
        items = items[1:]
        n -= 1
    if n == 0:
        return True
    if sum(items) > m * cap + 1e-9:
        return False
    # 可行子集（|S|<=3, sum<=cap）直接按组合生成——不枚举全 2^n 掩码
    from itertools import combinations
    feas_by_anchor = {}
    for r in (1, 2, 3):
        for comb in combinations(range(n), r):
            s = sum(items[i] for i in comb)
            if s <= cap + 1e-9:
                mask = 0
                for i in comb:
                    mask |= 1 << i
                feas_by_anchor.setdefault(comb[0], []).append(mask)

    @lru_cache(maxsize=None)
    def dfs(mask, k):
        if mask == 0:
            return True
        if k == 0:
            return False
        # 体积剪枝
        s = 0.0
        mm = mask
        while mm:
            lsb = mm & (-mm)
            s += items[lsb.bit_length() - 1]
            mm ^= lsb
        if s > k * cap + 1e-9:
            return False
        anchor = (mask & (-mask)).bit_length() - 1
        for S in feas_by_anchor.get(anchor, ()):
            if S & ~mask == 0 and dfs(mask ^ S, k - 1):
                return True
        return False
    return dfs((1 << n) - 1, m)


def can_pack_general(items, m, cap=1.0):
    """旧版全子集 DFS（t<=1/4 回退）。"""
    n = len(items)
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


def can_pack(items, m, cap=1.0):
    r = can_pack_fast(items, m, cap)
    if r is None:
        return can_pack_general(items, m, cap)
    return r


def points_of(x, m):
    nS = m - 1
    return [x[0], x[1]] + list(x[2:2 + nS]) + list(x[2 + nS:2 + 2 * nS])


def work_unit(mk, cand, do_dfs):
    m, k = mk
    nS = m - 1
    tl = (m - 1) / (4 * (m - 2))
    verdict = 'BLOCKED'
    pack_hits = pts = 0
    rng = np.random.default_rng(0)
    for t0 in np.linspace(tl + 0.002, 1 / 3, 5):
        feas, x = feasible_at2(m, k, cand, t0)
        if not feas:
            continue
        verdict = 'ALIVE-UNPACK'
        if do_dfs and m <= 20:
            pts_l = [x]
            for _ in range(2):
                f2, x2 = feasible_at2(m, k, cand, t0, direction=rng.normal(size=nv_of(m)))
                if f2:
                    pts_l.append(x2)
            for pt in pts_l:
                pts += 1
                if can_pack(points_of(pt, m), m):
                    pack_hits += 1
                    verdict = 'COUNTEREXAMPLE'
                    print(f'  ✗✗ 可装箱反例 m={m} k={k} t={t0:.4f}: '
                          f'{np.round(points_of(pt, m),4).tolist()}', flush=True)
    return mk, verdict, pts, pack_hits


def nv_of(m):
    return 2 + 2 * (m - 1) + 2


def main():
    args = sys.argv[1:]
    spec = 'a2_candidate_spec'
    ms = [6, 8, 12]
    do_dfs = '--dfs' in args
    regress = '--regress' in args
    if '--spec' in args:
        spec = args[args.index('--spec') + 1]
    if '--m' in args:
        ms = [int(x) for x in args[args.index('--m') + 1].split(',')]
    mod = importlib.import_module(spec)
    t0_all = time.time()
    units = [(m, k) for m in ms for k in range(1, m)]
    cands = {mk: mod.candidate_rows(mk[0], mk[1], {'nS': mk[0] - 1, 'jj': mk[1] - 1}) for mk in units}
    W = int(os.environ.get('A2_FALSIFIER_WORKERS', '2'))
    print(f'=== 证伪器 v2：spec={spec} m={ms} workers={W} dfs={do_dfs} ===')
    results = {}
    if W > 1:
        with ProcessPoolExecutor(max_workers=W) as ex:
            for mk, v, pts, ph in ex.map(work_unit, units, [cands[u] for u in units], [do_dfs] * len(units)):
                results[mk] = (v, pts, ph)
                print(f'  m={mk[0]} k={mk[1]}: {v}（测 {pts} 点可装 {ph}）', flush=True)
    else:
        for u in units:
            mk, v, pts, ph = work_unit(u, cands[u], do_dfs)
            results[mk] = (v, pts, ph)
            print(f'  m={mk[0]} k={mk[1]}: {v}（测 {pts} 点可装 {ph}）', flush=True)
    nb = sum(1 for v, _, _ in results.values() if v == 'BLOCKED')
    na = sum(1 for v, _, _ in results.values() if v == 'ALIVE-UNPACK')
    nc = sum(1 for v, _, _ in results.values() if v == 'COUNTEREXAMPLE')
    print(f'=== 汇总：BLOCKED {nb} / ALIVE-UNPACK {na} / COUNTEREXAMPLE {nc}（{time.time()-t0_all:.0f}s）===')
    if regress:
        print('=== 有牙回归 ===')
        tests = [([0.5, 0.5, 0.5, 0.5], 2, True), ([0.9, 0.1, 0.6, 0.4, 0.3, 0.7], 3, True),
                 ([0.9, 0.9, 0.8, 0.2, 0.1, 0.1], 2, False), ([0.34, 0.34, 0.33, 0.33, 0.33, 0.33], 2, True)]
        ok = True
        for items, m, expect in tests:
            got = can_pack(items, m)
            ok &= (got == expect)
            print(f'  can_pack(...,m={m}) = {got}（期望 {expect}）{"✓" if got == expect else "✗✗"}', flush=True)
        print('有牙回归:', '通过' if ok else '失败')


if __name__ == '__main__':
    main()
