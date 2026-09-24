"""a3_ 审计实验：保序组消融复核 + 口袋1 q1->M0 子情形自洽性（LP_CONSTRAINTS.md 追加节的证据）。
只读他人文件（order_step.py / fast_lp.py / pocket1_bins.py），不修改。
"""
import numpy as np
from scipy.optimize import linprog
from fractions import Fraction as F
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fast_lp import rows_fixed, float_cert_rows
from pocket1_bins import build_p1b, bin_counts
from farkas_fixed import float_cert

MG = F(1, 10000)


def e_order_ablate():
    """保序组消融复核：tiered ghost 代表点 m=18 cnt=(3,11,0,1,2,0) k=17。"""
    m, cnt, k = 18, (3, 11, 0, 1, 2, 0), 17
    R, nv = rows_fixed(m, cnt, k, use_order=True)
    base = float_cert_rows(R, nv) is not None
    # 去 ord 行（保留 lowzone/hizone）
    R2 = [r for r in R if not r[3].startswith('ord')]
    noord = float_cert_rows(R2, nv) is not None
    # 去 zone 行（保留 ord）
    R3 = [r for r in R if not (r[3].startswith('lowzone') or r[3].startswith('hizone'))]
    nozone = float_cert_rows(R3, nv) is not None
    # 全去保序
    R4, nv4 = rows_fixed(m, cnt, k, use_order=False)
    noorder = float_cert_rows(R4, nv4) is not None
    print(f'm={m} cnt={cnt} k={k}（tiered ghost 代表）:')
    print(f'  完整保序: {"INF(有证书)" if base else "FEAS"}')
    print(f'  去 ord(留 zone): {"INF" if noord else "FEAS ⟹ ord 承重 ✓"}')
    print(f'  去 zone(留 ord): {"INF" if nozone else "FEAS ⟹ zone 承重 ✓"}')
    print(f'  全去保序: {"INF" if noorder else "FEAS ⟹ 保序整组承重 ✓"}')
    # ord 的 ord{jj} 边界：fast_lp 的 ord 覆盖 i<jj（low 区 0..jj）
    print('  ord 覆盖范围 i<jj（low 区含 jj，相邻对 0..jj-1）——与保序推论衔接见 LP_CONSTRAINTS.md')


def e_p1_q1onM0():
    """口袋1 角落 q1→M0 子情形：阶段 A（无 firststep）的洞 cnt 上，构造
    'q1 落 M0'（x=q1、y+q1<=K、他机全 nofit 充分条件）静态自洽性测试。
    自洽 ⟹ 阶段 B..E 的 firststep 全部不覆盖此子情形 ⟹ 闭合有洞。"""
    print('口袋1 q1->M0 子情形自洽性（阶段 A 洞 cnt 上）：')
    for m in [6, 7, 8]:
        holesA = []
        for cnt in bin_counts(m):
            A, bc, bt, names, nv = build_p1b(m, cnt, jj=None)
            if float_cert(A, bc, bt) is None:
                holesA.append(cnt)
        print(f'  m={m}: 阶段 A 洞 {holesA}')
        for cnt in holesA:
            # 加 q1->M0 约束：x=q1（x<=q1 & q1<=x）、y+q1<=K、nofit 全他机
            A, bc, bt, names, nv = build_p1b(m, cnt, jj=None)
            iam, iq1 = 2 + 2 * (m - 1), 2 + 2 * (m - 1) + 1
            ix, iy = 0, 1
            def con(row, c0, c1, nm):
                A.append([F(z) for z in row]); bc.append(F(c0)); bt.append(F(c1)); names.append(nm)
            def zero(): return [F(0)] * nv
            r = zero(); r[ix] = 1; r[iq1] = -1; con(r, 0, 0, 'x<=q1')
            r = zero(); r[ix] = -1; r[iq1] = 1; con(r, 0, 0, 'x>=q1')
            # y+q1 <= K ⟺ 4y-5am-q1 <= 0
            r = zero(); r[iy] = 4; r[iam] = -5; r[iq1] = -1; con(r, 0, 0, 'y+q1<=K')
            # am<=y（y 是初始件 >= p_m；build_p1b 缺失的合法约束，补上）
            r = zero(); r[iam] = 1; r[iy] = -1; con(r, 0, 0, 'am<=y')
            for i in range(m - 1):
                r = zero(); r[2 + i] = -4; r[iam] = 5; r[iq1] = 1; con(r, -MG, 0, f'nofitM{i}')
            cert = float_cert(A, bc, bt) is not None
            # 若无常数证书，逐 t 判可行
            feas_t = None
            if not cert:
                for t0 in np.linspace((m - 1) / (4 * (m - 2)) + 0.002, 1 / 3, 8):
                    Af = np.array([[float(z) for z in row] for row in A])
                    bf = np.array([float(bc[i]) + float(bt[i]) * t0 for i in range(len(A))])
                    res = linprog(c=np.zeros(nv), A_ub=Af, b_ub=bf, bounds=(None, None), method='highs')
                    if res.status == 0:
                        feas_t = (t0, res.x)
                        break
            if cert:
                print(f'    cnt={cnt}: q1->M0 也 INFEASIBLE（子情形被覆盖 ✓）')
            elif feas_t is not None:
                t0, x = feas_t
                print(f'    cnt={cnt}: ✗ 静态自洽! t={t0:.4f} x=q1={x[0]:.4f} y={x[1]:.4f} '
                      f'x+y+t={x[0]+x[1]+t0:.4f}')
            else:
                print(f'    cnt={cnt}: 无常数证书但窗口内无浮点可行点（INFEASIBLE/t）')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if cmd in ('all', 'order'):
        e_order_ablate()
    if cmd in ('all', 'p1m0'):
        e_p1_q1onM0()
