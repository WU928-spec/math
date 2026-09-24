"""a1_tight_test.py — sliver 紧性引理证伪狩猎（σ=挤压零松弛检验）。

紧性引理（second_proof.md 引理1.7 / JEL.md）声称：razor 角落+sliver+可装箱 ⟹ 装箱全紧。
而 装箱全紧（nS 箱每箱=1）⟹ 总体积=nS ⟹ Σℓ=nS−t（挤压取等）。
记 σ = (nS−t) − Σℓ ≥ 0（挤压松弛）。紧性引理 ⟺ "无可装箱角落+sliver 点有 σ>0"。
本文体积账（main/agent-1 第三证）只证出 四项和 ≥ 2−σ（e=0）/ ≥4−σ（e=1)，
达不到 ≥2/≥4 —— σ=0 未证。本实验直接搜 σ>0 的可装箱见证：
  ① 值语言角落 LP（最小合法行集: 去 A2/B4/sjrev）+ sliver 行，min Σℓ → σ_max；
  ② σ_max>tol 时，加 σ≥σ_max/2 行 + 随机目标采样 → typed_feasible 精确装箱判定；
  ③ 任何 (σ>tol ∧ 可装箱) 点 = 紧性引理反例（BREAKING）；全灭 = 引理经验支持、
     但书面证明缺 σ=0 一步（两族同病，F1 升级为 F1′）。
输出 a1_tight_test.jsonl + stdout 摘要。
"""
import numpy as np, sys, os, json, time, random
from fractions import Fraction as F
from scipy.optimize import linprog
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a1_value_lp2 as V
from a2_g1_flow import typed_feasible
from farkas_fixed import MG

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'a1_tight_test.jsonl')
random.seed(20260923)


def build_lp(m, cnt, t0, sigma_lb=None):
    """值语言全行(去A2/B4/sjrev) + sliver 行 [+ σ≥sigma_lb 行]。返回 LP 数据与索引器。"""
    A, bc, bt, names, leg, nv = V.build(m, cnt, use_a2=False, use_b4=False, use_sjrev=False)
    nS = m - 1
    IP = 0
    vs = lambda r: 3 + (r - 1)
    vj = lambda r: 3 + nS + (r - 1)

    def con(row, c0, c1, nm):
        A.append([F(x) for x in row]); bc.append(F(c0)); bt.append(F(c1)); names.append(nm)

    z = [F(0)] * nv
    # sliver: j1+j2+j3 >= 1+MG ；t+j1+j2 <= 1（B2 已含则重复无害）
    r_ = list(z); r_[vj(1)] = -1; r_[vj(2)] = -1; r_[vj(3)] = -1
    con(r_, -1 - MG, 0, 'sliver_j1j2j3')
    # 严格化（机器角落语义）：A1 行加 +MG（j_r + s_{nS+1-r} >= p+MG）、danger 加 +MG
    for rr in range(1, nS + 1):
        r_ = list(z); r_[IP] = 1; r_[vs(nS + 1 - rr)] = -1; r_[vj(rr)] = -1
        con(r_, -MG, 0, f'A1M_{rr}')
    r_ = list(z); r_[IP] = -1
    con(r_, -F(5, 4) - MG, 1, 'dangerM')
    if sigma_lb is not None:
        # σ = nS−t−Σℓ ≥ sigma_lb  ⟺ Σℓ ≤ nS−t−sigma_lb
        r_ = list(z)
        for rr in range(1, nS + 1):
            r_[vs(rr)] = 1; r_[vj(rr)] = 1
        con(r_, nS - float(sigma_lb), -1, 'sigma_lb')
    Af = np.array([[float(x) for x in row] for row in A])
    b = np.array([float(x) for x in bc]) + np.array([float(x) for x in bt]) * t0
    return Af, b, nv, vs, vj, nS


def main():
    tmesh = [0.27, 0.30, 0.31, 0.32, 0.3333, 1 / 3]
    t0_start = time.time()
    n_packable = n_tested = n_configs = 0
    witnesses = []
    for m in range(6, 10):
        nS = m - 1
        for cnt in [(1, m - 3, 0, 1, 0, 0), (2, m - 5, 0, 1, 1, 0)]:
            for t0 in tmesh:
                if t0 <= float(F(m - 1, 4 * (m - 2))):
                    continue  # 窗口下界之外（squeeze∧pair 不可行）
                n_configs += 1
                Af, b, nv, vs, vj, nS_ = build_lp(m, cnt, t0)
                cmin = np.zeros(nv)
                for rr in range(1, nS + 1):
                    cmin[vs(rr)] = 1; cmin[vj(rr)] = 1
                res = linprog(c=cmin, A_ub=Af, b_ub=b, bounds=(None, None), method='highs')
                if not res.success:
                    continue
                sig_max = (nS - t0) - res.fun
                rec = {'m': m, 'cnt': cnt[0], 't': round(t0, 6), 'sigma_max': round(sig_max, 6)}
                if sig_max > 1e-6:
                    # 采样：σ≥σ_max/2 约束 + 随机目标
                    Af2, b2, nv, vs, vj, nS_ = build_lp(m, cnt, t0, sigma_lb=sig_max / 2)
                    pack_any = False
                    for it in range(60):
                        rng = np.random.default_rng(1000 * m + 100 * cnt[0] + it)
                        cobj = rng.normal(size=nv)
                        rs = linprog(c=cobj, A_ub=Af2, b_ub=b2, bounds=(None, None), method='highs')
                        if not rs.success:
                            continue
                        x = rs.x
                        s = [x[vs(r)] for r in range(1, nS + 1)]
                        j = [x[vj(r)] for r in range(1, nS + 1)]
                        sig = (nS - t0) - (sum(s) + sum(j))
                        if sig <= 1e-6:
                            continue
                        n_tested += 1
                        if typed_feasible(list(s), list(j) + [t0], cnt):
                            # 鬼影过滤：真机配对核验（reversed=maximin 指派）
                            # 须 ∃ 指派 s_i+j_{π(i)} >= p+MG 且负载 <= K=5(am+q1)/4
                            nS2 = len(s)
                            p_v = x[0]
                            am_v, q1_v = x[1], x[2]
                            K_v = 1.25 * (am_v + q1_v)
                            sr = sorted(s); jr = sorted(j, reverse=True)
                            pair_ok = all(sr[i] + jr[i] >= p_v + 1e-4 - 1e-9 for i in range(nS2))
                            cap_ok = all(sr[i] + jr[i] <= K_v + 1e-9 for i in range(nS2))
                            real = pair_ok and cap_ok
                            n_packable += 1
                            pack_any = True
                            witnesses.append({'m': m, 'cnt': cnt[0], 't': t0, 'sigma': sig,
                                              'p': round(p_v, 6), 'K': round(K_v, 6),
                                              'machine_realizable': bool(real),
                                              's': [round(v, 6) for v in s],
                                              'j': [round(v, 6) for v in j]})
                            break
                    rec['packable_sigma_pos'] = pack_any
                    rec['tested'] = n_tested
                with open(OUT, 'a') as f:
                    f.write(json.dumps(rec) + '\n')
                if n_configs % 10 == 0:
                    print(f'[progress] m={m} cnt={cnt[0]} t={t0:.4f} σ_max={sig_max:.4f} '
                          f'tested={n_tested} packable={n_packable} elapsed={time.time()-t0_start:.0f}s',
                          flush=True)
                if time.time() - t0_start > 420:
                    print('[timeout] 7min 盒到点，断点续跑可用（jsonl 追加）', flush=True)
                    return
    print(f'[done] configs={n_configs} tested={n_tested} packable_sigma_pos={n_packable}')
    if witnesses:
        print('[BREAKING] 紧性引理反例见证：')
        for w in witnesses[:5]:
            print(json.dumps(w))
    else:
        print('[ok] 无 σ>0 可装箱见证——紧性引理经验支持，但书面证明缺 σ=0 一步（F1′）')


if __name__ == '__main__':
    main()
