"""a3_b4_ablate.py —— 复测 main 154 发的 B4/A2 必要性（支撑行普查后的决定性消融）。
背景：main_cert154.jsonl 支撑行普查（agent-3）：A2 出现 0/308；B4 出现 full 77/154、noSJrev 111/115。
main 的消融曾报"B4 冗余"（范围 m<=12 浮点）——与 111/115 支撑率张力大，须全域复测。
判读：去 B4 仍全 INF ⟹ B4 非必要 ⟹ uncond 115 不依赖 B4 合法性（仅冗余行）；
      去 B4 出 FEAS ⟹ B4 在那些点承重 ⟹ B4 合法性（threshold-Hall，agent-1 一行论证有逃逸口）成为 115 的命门。
"""
import numpy as np
from scipy.optimize import linprog
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction as F
import a1_value_lp2 as V

MG = F(1, 10000)
TMESH = [0.27, 0.29, 0.30, 0.31, 0.32, 0.33, 1 / 3]


def build_k(m, cnt, k, **kw):
    """main_cegar3.build_k 的 kw 透传版（V.build 全行 + A5 + LZ/HZ）。"""
    nS = m - 1
    A, bc, bt, names, leg, nv = V.build(m, cnt, **kw)
    IP, IAM, IQ1 = 0, 1, 2
    vs = lambda r: 3 + (r - 1)
    vj = lambda r: 3 + nS + (r - 1)

    def con(row, c0, c1, nm, proof=''):
        A.append([F(x) for x in row]); bc.append(F(c0)); bt.append(F(c1)); names.append(nm)

    for i in range(1, k + 1):
        row = [F(0)] * nv
        row[IP] = 1; row[vs(i)] = -1; row[vj(nS - k + i)] = -1
        con(row, -MG, 0, f'A5_{i}')
    row = [F(0)] * nv
    row[vs(k)] = 4; row[IAM] = -5; row[IQ1] = -1
    con(row, 0, 0, 'LZ')
    if k < nS:
        row = [F(0)] * nv
        row[vs(k + 1)] = -4; row[IAM] = 5; row[IQ1] = 1
        con(row, -MG, 0, 'HZ')
    return A, bc, bt, names, nv


def feas_on_mesh(A, bc, bt, nv):
    Af = np.array([[float(x) for x in row] for row in A])
    bcf = np.array([float(x) for x in bc])
    btf = np.array([float(x) for x in bt])
    for t0 in TMESH:
        res = linprog(c=np.zeros(nv), A_ub=Af, b_ub=bcf + btf * t0,
                      bounds=(None, None), method='highs')
        if res.status == 0:
            return t0
    return None


def main():
    variants = [('baseline_full', {}),
                ('noB4', dict(use_b4=False)),
                ('noA2', dict(use_a2=False)),
                ('noB4_noA2', dict(use_b4=False, use_a2=False))]
    for vname, kw in variants:
        t0 = time.time()
        ninf = 0; feas_list = []
        for m in range(6, 17):
            for cnt in [(1, m - 3, 0, 1, 0, 0), (2, m - 5, 0, 1, 1, 0)]:
                for k in range(2, m - 2):
                    A, bc, bt, names, nv = build_k(m, cnt, k, **kw)
                    f = feas_on_mesh(A, bc, bt, nv)
                    if f is None:
                        ninf += 1
                    else:
                        feas_list.append((m, cnt[0], k, round(f, 3)))
        print(f'{vname}: INF {ninf}/154  FEAS {len(feas_list)}  ({time.time()-t0:.0f}s)', flush=True)
        for rec in feas_list:
            print('   FEAS:', rec, flush=True)


if __name__ == '__main__':
    main()
