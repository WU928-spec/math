"""a2_value_lp.py — 值语言 LP 试点：洞区在值语言重构下是否仍闭合。

值语言变量：p, t, am, q1, seniors s_0<=...<=s_{nS-1}（排序），juniors w_0<=...<=w_{nS-1}
（排序；t 另列）。约束（全为角落必要条件或已证 w.l.o.g. 形式）：
- 反序 pair（杠杆1/Hall）：s_i + w_{nS-1-i} >= p ∀i   [机器指派 ⟹ Hall ⟹ 反序成立]
- nofit/fit（值形）：s_{k-1}+q1<=K 且 i>=k: s_i+q1>K   [q1 落机按 senior 值阈]
- q1 = w_{nS-1}（值最大 junior）；am = s_0（a_m=s_0 登记原料）；q1<=am；t<=w_i；w_i<=2t；
  s_i>=1-2t；L=am+q1<=1；p<K=5/4(am+q1)；danger p+t>5/4。
- 装箱（值语言规范形）：SS 相邻配对 (s_{2i},s_{2i+1})<=1；SJ 反序配对
  s_{2a+i}+w_{b-1-i}<=1（存在可行 SJ 匹配 ⟺ 反序可行——重排不等式 w.l.o.g. 方向已正）；
  JJJ/JJ 取排序池连续段（w_{b..} + t 殿后）。
目的：洞区 (cnt,k) 若在此值语言 LP 下仍 INFEASIBLE，则值语言重构保住杀力 ⟹ 高端 junior
的"机器索引桥"可拆除（JJJ 身份变纯值聚合）。否则记录失效点 = 机器语言的必需位置清单。
"""
import numpy as np
from scipy.optimize import linprog
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pairing_feasible import bin_count_solutions
from hole_close import holes_of  # 基线洞清单（只读）

MG = 1e-4


def build_value_lp(m, cnt, k):
    """返回值语言 LP 的 (A_ub, b_ub, bounds)；feasible ⟺ 洞未闭合。"""
    a, b, c, d, e, f = cnt
    nS = m - 1
    nv = 2 + 2 * nS + 2  # p, t, s_0.., w_0.., am, q1
    ip, it = 0, 1
    def vs(i): return 2 + i
    def vw(i): return 2 + nS + i
    iam, iq1 = 2 + 2 * nS, 2 + 2 * nS + 1
    A, bb = [], []
    bounds = [(0, 1)] * nv
    def con(row, rhs):
        A.append(row); bb.append(rhs)
    # danger: -p-t <= -5/4-MG
    r = [0.0] * nv; r[ip] = r[it] = -1; con(r, -1.25 - MG)
    # 反序 pair: s_i + w_{nS-1-i} >= p ⟺ p - s_i - w_{nS-1-i} <= -MG
    for i in range(nS):
        r = [0.0] * nv; r[ip] = 1; r[vs(i)] = -1; r[vw(nS - 1 - i)] = -1; con(r, -MG)
    # bands
    for i in range(nS):
        r = [0.0] * nv; r[vs(i)] = -1; con(r, -(1 - 2 / 3) - MG)     # s_i >= 1-2t 松界(保守 t<=1/3)
        r = [0.0] * nv; r[it] = 1; r[vw(i)] = -1; con(r, 0)          # w_i >= t
        r = [0.0] * nv; r[vw(i)] = 1; r[it] = -2; con(r, -MG)        # w_i <= 2t-MG
    # 排序
    for i in range(nS - 1):
        r = [0.0] * nv; r[vs(i)] = 1; r[vs(i + 1)] = -1; con(r, 0)
        r = [0.0] * nv; r[vw(i)] = 1; r[vw(i + 1)] = -1; con(r, 0)
    # kcap：am=s_0（两向）、w_i<=q1、q1=w_{nS-1}（两向）、t<=q1、q1<=am、p<K、L<=1
    r = [0.0] * nv; r[iam] = 1; r[vs(0)] = -1; con(r, 0)
    r = [0.0] * nv; r[iam] = -1; r[vs(0)] = 1; con(r, 0)
    for i in range(nS):
        r = [0.0] * nv; r[vw(i)] = 1; r[iq1] = -1; con(r, 0)
    r = [0.0] * nv; r[iq1] = 1; r[vw(nS - 1)] = -1; con(r, 0)
    r = [0.0] * nv; r[iq1] = -1; r[vw(nS - 1)] = 1; con(r, 0)
    r = [0.0] * nv; r[it] = 1; r[iq1] = -1; con(r, 0)
    r = [0.0] * nv; r[iq1] = 1; r[iam] = -1; con(r, 0)
    r = [0.0] * nv; r[ip] = 1; r[iam] = -1.25; r[iq1] = -1.25; con(r, -MG)   # p<K
    r = [0.0] * nv; r[iam] = 1; r[iq1] = 1; con(r, 1)                         # L<=1
    # fit/nofit（值形）：s_{k-1}+q1<=K；i>=k: s_i+q1>K
    r = [0.0] * nv; r[vs(k - 1)] = 4; r[iam] = -5; r[iq1] = -1; con(r, 0)
    for i in range(k, nS):
        r = [0.0] * nv; r[vs(i)] = -4; r[iam] = 5; r[iq1] = 1; con(r, -MG)
    # 装箱（值语言规范形）
    for kk in range(a):     # SS 极端配对（§11.0 交换引理 w.l.o.g. 形式）
        r = [0.0] * nv; r[vs(kk)] = 1; r[vs(2 * a - 1 - kk)] = 1; con(r, 1)
    for kk in range(b):     # SJ 反序：s_{2a+kk} + w_{b-1-kk} <= 1
        r = [0.0] * nv; r[vs(2 * a + kk)] = 1; r[vw(b - 1 - kk)] = 1; con(r, 1)
    # JJJ 蛇形三件（排序池：第 i 组 = y_i + y_{2d+1-i} + y_{2d+i}，1-based）
    pool = [vw(i) for i in range(nS)] + [it]
    for kk in range(d):
        u1 = kk            # y_{kk+1}（小）
        u2 = 2 * d - 1 - kk  # y_{2d-kk}（中段反射）
        u3 = 2 * d + kk    # y_{2d+kk+1}（大）
        r = [0.0] * nv
        for u in (u1, u2, u3):
            r[pool[u]] = 1
        con(r, 1)
    idx = b  # 注意：此变体池段从 0 起（纯值语言试验，不按 SJ 池段对齐）
    for kk in range(e):
        pass
    res = linprog(c=np.zeros(nv), A_ub=np.array(A), b_ub=np.array(bb), bounds=bounds, method='highs')
    return res.status == 0


if __name__ == '__main__':
    print('=== 值语言 LP 洞区测试（m=12..20 全洞）===')
    nfeas = ninf = 0
    for m in range(12, 21):
        for cnt, k in holes_of(m):
            fea = build_value_lp(m, cnt, k)
            if fea:
                nfeas += 1
                print(f'  m={m} k={k} cnt={cnt}: FEASIBLE（值语言未杀）')
            else:
                ninf += 1
        print(f'  m={m}: 累计 值语言杀 {ninf} / 漏 {nfeas}', flush=True)
    print('结论:', '洞区在值语言 LP 下仍全闭合 ✓' if nfeas == 0 else f'{nfeas} 洞漏杀（机器语言必需位待标）')
