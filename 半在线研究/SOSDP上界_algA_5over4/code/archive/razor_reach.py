"""razor 带动力学不可达性诊断（razor_reach.py）——推广 hole_reach.py 到 razor 带全区。

逻辑（对应 (P) 的动力学直证）：
  角落 LP（无装箱行，仅角落约束+mon2）在 razor 带可行 ⟹ 提取值配置；
  对该值配置构造强制到达序（初始 m 件递减 → 后续 junior+t 递减），实跑 Algorithm A。
  若 razor 带的角落构型**永不产生**（t 被泄压阀收走 / 无 fallback / makespan≤K），
  则 razor 带 (P) 由动力学不可达性直接成立——**不需要装箱行/（W''）**。

对照：hole_reach.py 对洞族 20/20 得到"泄压阀收 t"。本脚本测 razor 带（非洞族+洞族）全区。
"""
import numpy as np
from scipy.optimize import linprog
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farkas_fixed import build_fixed
from hole_close import build_close
from pairing_feasible import bin_count_solutions
from toolbox import fallback_event


def corner_feasible_point(m, cnt, k, use_bins=False):
    """角落配置可行点：角落约束+mon2，无装箱行（use_bins=False）。"""
    A, bc, bt, names, nv = build_close(m, cnt, k)
    if not use_bins:
        keep = [i for i, nm in enumerate(names) if nm not in ('SS', 'SJ', 'JJJ', 'JJ')]
        A = [A[i] for i in keep]; bc = [bc[i] for i in keep]; bt = [bt[i] for i in keep]
    Af = np.array([[float(x) for x in row] for row in A])
    bcf = np.array([float(x) for x in bc]); btf = np.array([float(x) for x in bt])
    A2 = Af.copy(); A2[:, 1] -= btf   # t 在右端：A x <= bc + bt t ⟺ (A - bt·e_t) x <= bc
    res = linprog(c=np.zeros(nv), A_ub=A2, b_ub=bcf, bounds=(None, None), method='highs')
    return res.x if res.status == 0 else None


def forced_seq(x, m):
    nS = m - 1
    p, t = x[0], x[1]
    s = list(x[2:2 + nS]); j = list(x[2 + nS:2 + 2 * nS])
    return sorted([p] + s, reverse=True) + sorted(j + [t], reverse=True)


def main():
    razor_cnts = [(1, None, 0, 1, 0, 0), (2, None, 0, 1, 1, 0)]  # b 由 m 定
    print("=== razor 带动力学不可达性诊断（角落配置+mon2，无装箱行）===")
    total = reach = 0
    for m in range(6, 21):
        nS = m - 1
        for (a, _, c, d, e, f) in razor_cnts:
            b = m - 1 - 2 * a - c
            if b < 1: continue
            cnt = (a, b, c, d, e, f)
            for k in range(2, m):
                x = corner_feasible_point(m, cnt, k)
                if x is None:
                    continue  # 角落配置本身不可行（已被角落约束闭合）
                total += 1
                seq = forced_seq(x, m)
                ev = fallback_event(seq, m)
                p, t = x[0], x[1]
                if ev is None:
                    verdict = "K封顶(无fallback=无角落)"
                else:
                    # fallback 发生；检查是否构成角落（makespan > K = 失败构型）
                    verdict = f"fallback: makespan={max(ev['loads']):.4f} K={ev['K']:.4f}"
                    reach += 1
                if k in (2, m-2, m-1) or ev is not None:
                    print(f"  m={m} cnt={cnt} k={k}: p={p:.4f} t={t:.4f} -> {verdict}")
    print(f"\nrazor 带角落可行点 {total} 个，其中产生 fallback(角落)构型 {reach} 个")
    print("判决：reach=0 ⟹ razor 带角落动力学不可达 ⟹ (P)  razor 带由动力学闭合（无需装箱行/(W'')）")


if __name__ == '__main__':
    main()
