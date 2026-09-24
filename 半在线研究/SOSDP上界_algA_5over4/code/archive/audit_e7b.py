"""E7b: pocket3 的 q1->M0 子情形是否被 build_p3f 覆盖？
build_p3f 的 fs/q1<=j{jj} 组强制 q1 落在某台他机 jj。
若 q1（=p_{m+1}，首个后续）best-fit 落到 M0（M0 初始件 z 满足 z+q1<=K 且是最满可放机），
则角落值违反 fs 建模 ⟹ 该子情形不在 LP 覆盖范围内。
本实验：构造 q1->M0 的角落 LP（其余约束与 build_p3f 同语义），检验其静态自洽性。
  M0 = {x, y, z}: z=初始件(w), y=q1(首个后续，落 M0), x=次后续（x<=y）
  他机 {s_i, j_i}：s_i>1-2t, j_i in [t,2t)；mach s_i+j_i >= ℓ0
  q1->M0 的充分条件：z+q1<=K 且 s_i+q1>K ∀i（M0 为唯一可放机）
"""
from fractions import Fraction as F
import numpy as np
from scipy.optimize import linprog
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
MG = 1e-4


def build_q1onM0(m):
    nS = m - 1
    nv = 3 + 2 * nS + 2
    ix, iy, iz = 0, 1, 2
    off = 3
    def vs(i): return off + i
    def vj(i): return off + nS + i
    iam, iq1 = off + 2 * nS, off + 2 * nS + 1
    A, b = [], []

    def con(row, c):
        A.append(row); b.append(c)

    def z_(): return [0.0] * nv

    r = z_(); r[ix] = 1; r[iy] = -1; con(r, 0)          # x<=y
    r = z_(); r[iy] = 1; r[iz] = -1; con(r, 0)          # y<=z
    r = z_(); r[iq1] = 1; r[iy] = -1; con(r, 0)         # q1<=y
    r = z_(); r[iq1] = -1; r[iy] = 1; con(r, 0)         # y<=q1  (y=q1)
    for i in range(nS):
        r = z_(); r[vs(i)] = -1; con(r, -1 + 2 * 0)     # placeholder, t handled in solve
    return None


def build_and_solve(m, t0):
    """直接按 t0 构造浮点 LP（t 为参数）。"""
    nS = m - 1
    nv = 3 + 2 * nS + 2
    ix, iy, iz = 0, 1, 2
    off = 3
    def vs(i): return off + i
    def vj(i): return off + nS + i
    iam, iq1 = off + 2 * nS, off + 2 * nS + 1
    A, b = [], []

    def con(row, c):
        A.append(row); b.append(c)

    def z_(): return [0.0] * nv

    # M0 结构与排序
    r = z_(); r[ix] = 1; r[iy] = -1; con(r, 0)                    # x<=y
    r = z_(); r[iy] = 1; r[iz] = -1; con(r, 0)                    # y<=z
    r = z_(); r[ix] = -1; con(r, -t0)                             # x>=t
    r = z_(); r[iy] = 1; r[iq1] = -1; con(r, 0)                   # y<=q1
    r = z_(); r[iy] = -1; r[iq1] = 1; con(r, 0)                   # y>=q1  (y=q1)
    # danger: x+y+z >= 5/4 - t
    r = z_(); r[ix] = -1; r[iy] = -1; r[iz] = -1; con(r, -1.25 + t0)
    for i in range(nS):
        r = z_(); r[vs(i)] = -1; con(r, -(1 - 2 * t0) - MG)       # s_i>1-2t
        r = z_(); r[vs(i)] = 1; con(r, 1)                         # s_i<=1
        r = z_(); r[vj(i)] = 1; con(r, 2 * t0 - MG)               # j_i<2t
        r = z_(); r[vj(i)] = -1; con(r, -t0)                      # j_i>=t
        # mach: s_i+j_i >= x+y+z (+MG)
        r = z_(); r[ix] = 1; r[iy] = 1; r[iz] = 1; r[vs(i)] = -1; r[vj(i)] = -1
        con(r, -MG)
        # q1 放不进他机 i: s_i+q1 >= K+MG = 5(am+q1)/4+MG
        r = z_(); r[vs(i)] = -4; r[iam] = 5; r[iq1] = 1; con(r, -MG)
        # am <= s_i; j_i <= q1
        r = z_(); r[iam] = 1; r[vs(i)] = -1; con(r, 0)
        r = z_(); r[vj(i)] = 1; r[iq1] = -1; con(r, 0)
    # am <= z（p_m = min 全部初始 <= M0 初始 z）
    r = z_(); r[iam] = 1; r[iz] = -1; con(r, 0)
    # q1 <= am（递减 p_{m+1} <= p_m）
    r = z_(); r[iq1] = 1; r[iam] = -1; con(r, 0)
    # z+q1 <= K = 5(am+q1)/4  （q1 best-fit 落 M0）
    r = z_(); r[iz] = 4; r[iq1] = 4; r[iam] = -5; r[iq1] += -5
    # 修正上一条：4z+4q1 <= 5am+5q1 ⟺ 4z-5am-q1 <= 0
    r = z_(); r[iz] = 4; r[iam] = -5; r[iq1] = -1; con(r, 0)
    # L<=1
    r = z_(); r[iam] = 1; r[iq1] = 1; con(r, 1)
    # vol: x+y+z+Σ(s+j) <= m-t
    r = z_()
    for v in [ix, iy, iz]: r[v] = 1
    for i in range(nS):
        r[vs(i)] = 1; r[vj(i)] = 1
    con(r, m - t0)
    res = linprog(c=np.zeros(nv), A_ub=np.array(A), b_ub=np.array(b),
                  bounds=(None, None), method='highs')
    return res


if __name__ == '__main__':
    print('E7b: pocket3 q1->M0 子情形静态自洽性（feasible ⟹ build_p3f 未覆盖该子情形）')
    for m in [5, 6, 7, 8]:
        tl = m / (4 * (m - 1))
        hit = None
        for t0 in np.linspace(tl + 0.001, 1 / 3, 8):
            res = build_and_solve(m, t0)
            if res.status == 0:
                hit = (t0, res.x)
                break
        if hit:
            t0, x = hit
            nS = m - 1
            print(f'  m={m}: FEASIBLE @ t={t0:.4f}')
            print(f'    x={x[0]:.4f} y=q1={x[1]:.4f} z={x[2]:.4f} ℓ0+t={x[0]+x[1]+x[2]+t0:.4f}')
            s = x[3:3 + nS]; j = x[3 + nS:3 + 2 * nS]
            am, q1 = x[3 + 2 * nS], x[3 + 2 * nS + 1]
            print(f'    s={np.round(s, 4)}')
            print(f'    j={np.round(j, 4)} am={am:.4f} q1={q1:.4f} L={am+q1:.4f} K={1.25*(am+q1):.4f}')
            print(f'    z+q1={x[2]+q1:.4f} vs K={1.25*(am+q1):.4f}（z+q1<=K ⟹ q1 可落 M0）')
        else:
            print(f'  m={m}: 全 t 不可行（q1->M0 子情形静态上也不存在）')
