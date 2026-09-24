"""a3_a2_corner.py —— A2（反序负载帽 j_r + s_{nS+1-r} <= K = 5(am+q1)/4）角落域合法性复核。
背景：A2 在 main_cert154 支撑行 0/308，去 A2 精确证书仍 115/115 —— 不承重。
但合法性分类仍需定案（SEMANTICS 登记用）：
  agent-1 辩护词"真实机器负载<=K"在角落疑似为假（早段 fallback 可使小 senior 机超载 >K），
  agent-3 候选反例：s_max=0.95 + j_min=0.31，反序和 1.26 > K≈1.24。
测试（机 LP 角落域=fast_lp 去装箱帽，±B3 razor 值带）：
  ①r=1 精确 LP：max s_{nS-1} + w − 5/4(am+q1)，w<=j_u ∀u（w=min junior，最大化自动取等）。
  ②采样 30 方向/配置：值排序 juniors 后逐 r 计算 j_(r)+s_(nS+1-r)−K 的最大值。
判读：max<=0 ⟹ A2 在角落域成立（VALID，前提"负载<=K"在角落域意外为真）；
      max>0 ⟹ 角落域允许反序超载 ⟹ A2 过约束（SUSPECT/INVALID，但因不承重无害）。
"""
import numpy as np
from scipy.optimize import linprog
from fractions import Fraction as F
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fast_lp

TMESH = [0.27, 0.29, 0.30, 0.31, 0.32, 0.33, 1 / 3]
CAPNAMES = {'SS', 'SJ', 'JJJ', 'JJ'}
rng = np.random.default_rng(114514)


def corner_rows(m, cnt, k, use_b3):
    R, nv = fast_lp.rows_fixed(m, cnt, k, use_order=True)
    R = [r for r in R if r[3] not in CAPNAMES]
    if use_b3:
        nS = m - 1
        # B3: s_{nS-1} <= 1 - t（0-based 最大 senior）
        row = [0.0] * nv; row[2 + nS - 1] = 1.0
        R.append((row, F(1), F(-1), 'B3'))
    return R, nv


def test_config(m, cnt, k, use_b3):
    nS = m - 1
    R, nv = corner_rows(m, cnt, k, use_b3)
    Af = np.array([row for row, _, _, _ in R])
    bcf = np.array([float(c0) for _, c0, _, _ in R])
    btf = np.array([float(c1) for _, _, c1, _ in R])
    ip, it = 0, 1
    vs = lambda i: 2 + i
    vj = lambda i: 2 + nS + i
    iam, iq1 = 2 + 2 * nS, 2 + 2 * nS + 1
    out = dict(r1_max=None, samp_max=None)
    # ① r=1 精确：增广 w，w <= j_u，目标 max s_{nS-1} + w - 1.25(am+q1)
    A2 = [list(row) + [0.0] for row in Af]
    for u in range(nS):
        row = [0.0] * (nv + 1); row[vj(u)] = -1.0; row[nv] = 1.0   # w <= j_u（w=min junior 下界）
        A2.append(row)
    c = np.zeros(nv + 1)
    c[vs(nS - 1)] = -1.0; c[nv] = -1.0; c[iam] = 1.25; c[iq1] = 1.25
    best = None
    for t0 in TMESH:
        res = linprog(c=c, A_ub=np.array(A2), b_ub=np.append(bcf + btf * t0, np.zeros(nS)),
                      bounds=(None, None), method='highs')
        if res.status == 0:
            v = -res.fun
            if best is None or v > best[0]:
                x = res.x
                best = (v, t0, float(x[vs(nS - 1)]), float(min(x[vj(u)] for u in range(nS))),
                        float(1.25 * (x[iam] + x[iq1])))
    out['r1_max'] = best
    # ② 采样全 r
    smax = None
    for t0 in TMESH:
        r0 = linprog(c=np.zeros(nv), A_ub=Af, b_ub=bcf + btf * t0, bounds=(None, None), method='highs')
        if r0.status != 0:
            continue
        for _ in range(30):
            cc = rng.uniform(-1, 1, nv)
            res = linprog(c=cc, A_ub=Af, b_ub=bcf + btf * t0, bounds=(None, None), method='highs')
            if res.status != 0:
                continue
            x = res.x
            sj = sorted(float(x[vj(u)]) for u in range(nS))
            ss = [float(x[vs(u)]) for u in range(nS)]
            K = 1.25 * (x[iam] + x[iq1])
            for r in range(1, nS + 1):
                viol = sj[r - 1] + ss[nS - r] - K
                if smax is None or viol > smax[0]:
                    smax = (viol, t0, r, sj[r - 1], ss[nS - r], float(K))
    out['samp_max'] = smax
    return out


def main():
    t0 = time.time()
    for use_b3 in [False, True]:
        g1 = None; gs = None
        n = 0
        for m in range(6, 17):
            for cnt in [(1, m - 3, 0, 1, 0, 0), (2, m - 5, 0, 1, 1, 0)]:
                for k in range(2, m - 2):
                    o = test_config(m, cnt, k, use_b3)
                    n += 1
                    if o['r1_max'] and (g1 is None or o['r1_max'][0] > g1[0]):
                        g1 = (o['r1_max'][0], m, cnt[0], k) + o['r1_max'][1:]
                    if o['samp_max'] and (gs is None or o['samp_max'][0] > gs[0]):
                        gs = (o['samp_max'][0], m, cnt[0], k) + o['samp_max'][1:]
        print(f'B3={use_b3}: 配置 {n}')
        print(f'  ① r=1 精确最大 (s_max+j_min−K) = {g1}')
        print(f'  ② 采样全 r 最大 (j_(r)+s_(nS+1-r)−K) = {gs}')
        print(f'  判读: {"<=0 ⟹ A2 角落域成立(VALID)" if max(g1[0] if g1 else -9, gs[0] if gs else -9) <= 1e-7 else ">0 ⟹ A2 过约束(SUSPECT)"}', flush=True)
    print(f'总耗时 {time.time()-t0:.0f}s')


if __name__ == '__main__':
    main()
