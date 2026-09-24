"""洞区可达性诊断：对 m=12..20 全部洞 (cnt,k) 提取 LP 可行点，
检查"单调匹配"违反情况，并构造强制到达序实跑 Algorithm A 看动态是否偏离角落。

强制到达序（角落 n=2m 形状下唯一）：
  初始 m 件递减（p 最大，然后 senior 递减）→ 每台一件；
  后续 m 件 = m-1 个 junior + t，递减到达（t 最小在最后）。
LP 角落声称终态 = M0={p,t}、他机 {s_i, j_i}；动态若偏离（j_i 落点不同/泄压阀/t 不落 M0），
则该可行点序动态不可达。
"""
import numpy as np
from scipy.optimize import linprog
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farkas_fixed import build_fixed, float_cert
from pairing_feasible import bin_count_solutions
from toolbox import algA, fallback_event


def holes_of(m):
    out = []
    for k in range(1, m):
        for cnt in bin_count_solutions(m):
            A, bc, bt, names, nv = build_fixed(m, cnt, k)
            if float_cert(A, bc, bt) is None:
                out.append((cnt, k))
    return out


def primal_point(m, cnt, k):
    A, bc, bt, names, nv = build_fixed(m, cnt, k)
    Af = np.array([[float(x) for x in row] for row in A])
    bcf = np.array([float(x) for x in bc])
    btf = np.array([float(x) for x in bt])
    A2 = Af.copy(); A2[:, 1] -= btf
    res = linprog(c=np.zeros(nv), A_ub=A2, b_ub=bcf, bounds=(None, None), method='highs')
    return res.x if res.status == 0 else None


def simulate_corner(x, m):
    """由 LP 可行点构造强制到达序并实跑。返回 (seq, ev, ratio_to_K, loads)。"""
    nS = m - 1
    p, t = x[0], x[1]
    s = list(x[2:2 + nS]); j = list(x[2 + nS:2 + 2 * nS])
    seq = sorted([p] + s, reverse=True) + sorted(j + [t], reverse=True)
    ev = fallback_event(seq, m)
    return seq, ev


def main():
    for m in range(12, 21):
        hs = holes_of(m)
        print(f'=== m={m}: {len(hs)} 个洞 ===')
        for cnt, k in hs:
            x = primal_point(m, cnt, k)
            if x is None:
                print(f'  k={k} cnt={cnt}: 原LP无可行点??')
                continue
            nS = m - 1
            p, t = x[0], x[1]
            s = x[2:2 + nS]; j = x[2 + nS:2 + 2 * nS]
            am, q1 = x[2 + 2 * nS], x[2 + 2 * nS + 1]
            K = 1.25 * (am + q1)
            jj = k - 1
            # 单调性检查（部分单调：j_0<=...<=j_jj；全单调 k=m-1 时 jj=nS-1）
            viol_partial = sum(1 for i in range(jj) if j[i] > j[i + 1] + 1e-6)
            viol_full = sum(1 for i in range(nS - 1) if j[i] > j[i + 1] + 1e-6)
            seq, ev = simulate_corner(x, m)
            if ev is None:
                reach = 'K封顶(无fallback)'
            else:
                fb_jobs = ev['machine_jobs'][-1]
                reach = (f"真fallback: t={ev['t']:.4f} fb机件={np.round(fb_jobs,4)} "
                         f"loads_max={max(ev['loads']):.4f} K={ev['K']:.4f}")
            print(f'  k={k} cnt={cnt}: p={p:.4f} t={t:.4f} K={K:.4f} '
                  f'单调违反[0..jj]={viol_partial} 全序违反={viol_full}')
            print(f'      seniors={np.round(s,3)}')
            print(f'      juniors={np.round(j,3)}')
            print(f'      动态: {reach}')


if __name__ == '__main__':
    main()
