"""a3_ 敌意复核：agent-1 P1K1 §1.2-1.3 的 mini-LP 对拍。
对拍对象：分支2（a_m=s0）原料集在窗口 t∈(1/4,1/3] 是否 INFEASIBLE。
若 FEASIBLE ⟹ 文档链（t>2/5）依赖笔误 q₁>7/8−3t/4（正确为 7/8−3t/2）⟹ 分支2 未闭合。
另对拍分支1 v>=1：正确系数 y<4/9−q1/9（文档写 4/9−q1/36 笔误）结论是否仍成立。
"""
import numpy as np
from scipy.optimize import linprog
from fractions import Fraction as F

MG = 1e-4


def build_branch2(t0):
    """分支2（a_m=s0<y）原料集。变量 [x,y,s0,sv,j0,jv,q1]。
    返回 A,b（浮点，t 固定 t0）。全部原料为 P1K1 §1.1-1.3 所列合法约束。"""
    # ix,iy,is0,isv,ij0,ijv,iq1 = 0..6
    A, b = [], []
    def con(row, c):
        A.append(row); b.append(c)
    def z(): return [0.0] * 7
    # x<=y, x>=t
    r = z(); r[0] = 1; r[1] = -1; con(r, 0)
    r = z(); r[0] = -1; con(r, -t0)
    # y>=1-2t+MG（F2）
    r = z(); r[1] = -1; con(r, -(1 - 2 * t0) - MG)
    # danger: x+y >= 5/4-t+MG
    r = z(); r[0] = -1; r[1] = -1; con(r, -(5 / 4 - t0) - MG)
    # mach0: s0+j0 >= x+y
    r = z(); r[0] = 1; r[1] = 1; r[2] = -1; r[4] = -1; con(r, -MG)
    # machv: sv+jv >= x+y
    r = z(); r[0] = 1; r[1] = 1; r[3] = -1; r[5] = -1; con(r, -MG)
    # j 窄带: t<=j<=q1
    for ij in (4, 5):
        r = z(); r[ij] = -1; con(r, -t0)
        r = z(); r[ij] = 1; r[6] = -1; con(r, 0)
    # j <= 2t
    for ij in (4, 5):
        r = z(); r[ij] = 1; con(r, 2 * t0 - MG)
    # q1<=s0（分支2: a_m=s0）；s0<=y（分支定义）
    r = z(); r[6] = 1; r[2] = -1; con(r, 0)
    r = z(); r[2] = 1; r[1] = -1; con(r, 0)
    # t<=q1
    r = z(); r[6] = -1; con(r, -t0)
    # L<=1: s0+q1<=1
    r = z(); r[2] = 1; r[6] = 1; con(r, 1)
    # nofit（v>=1: sv>(5/4)s0+q1/4）
    r = z(); r[3] = -4; r[2] = 5; r[6] = 1; con(r, -MG)
    # senior 非小 sv>=1-2t+MG, s0>=1-2t+MG
    r = z(); r[3] = -1; con(r, -(1 - 2 * t0) - MG)
    r = z(); r[2] = -1; con(r, -(1 - 2 * t0) - MG)
    # BB 箱 {y, sv}: y+sv<=1
    r = z(); r[1] = 1; r[3] = 1; con(r, 1)
    # sv<=1, y<=1
    r = z(); r[3] = 1; con(r, 1)
    r = z(); r[1] = 1; con(r, 1)
    return np.array(A), np.array(b)


def check(name, builder):
    feas_ts = []
    for t0 in np.linspace(0.25 + 0.002, 1 / 3, 12):
        A, b = builder(t0)
        res = linprog(c=np.zeros(A.shape[1]), A_ub=A, b_ub=b, bounds=(None, None), method='highs')
        if res.status == 0:
            feas_ts.append(t0)
    print(f'{name}: 窗口内 {"FEASIBLE ⟹ 链未闭合 ✗✗" if feas_ts else "INFEASIBLE ✓ 链闭合"}'
          + (f'  可行 t={feas_ts[:3]}' if feas_ts else ''))
    return feas_ts


def main():
    print('== 分支2（a_m=s0）全原料对拍 ==')
    fts = check('分支2', build_branch2)
    if fts:
        # 提取一个可行点看细节
        A, b = build_branch2(fts[0])
        res = linprog(c=np.zeros(A.shape[1]), A_ub=A, b_ub=b, bounds=(None, None), method='highs')
        names = ['x', 'y', 's0', 'sv', 'j0', 'jv', 'q1']
        print('  可行点:', {nm: round(float(res.x[i]), 4) for i, nm in enumerate(names)}, f't={fts[0]:.4f}')
        # 消融：逐条去掉看哪些承重
        for kill in range(len(A)):
            A2 = np.delete(A, kill, axis=0); b2 = np.delete(b, kill)
            r2 = linprog(c=np.zeros(A.shape[1]), A_ub=A2, b_ub=b2, bounds=(None, None), method='highs')
            if r2.status != 0:
                pass
        print('  （消融在 infeasible 情形下无意义；此处 feasible 为证伪）')


if __name__ == '__main__':
    main()
