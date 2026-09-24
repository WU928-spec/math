"""a3_ 换元实验：把模板证书的分组相关 C/G 换成 w.l.o.g. 版 C*/G* 后，
恒等式配平（=小 LP 可行性）是否仍闭合。
配平 LP：变量=原料权（≥0），约束=每变量列系数和=0，目标=常数列和最小化（<0 即矛盾证成）。
INFEASIBLE ⟹ 该批 w.l.o.g. 原料配不出矛盾（严格障碍刻画）。
"""
import numpy as np
from scipy.optimize import linprog
from fractions import Fraction as F


def balance(ingredients, var_names, tag):
    """ingredients: [(name, {var: coeff}, const)] 表示 行 = Σ coeff·var + const >= 0。
    求权 w_i>=0 使每变量列加权和=0 且常数和 < 0。"""
    nI = len(ingredients)
    nv = len(var_names)
    Aeq = np.zeros((nv, nI))
    for j, (nm, d, c) in enumerate(ingredients):
        for v, w in d.items():
            Aeq[var_names.index(v), j] = w
    ceq = np.zeros(nv)
    # 目标：最大化 -(常数和) = -Σ c_i w_i，要求 >0
    cobj = np.array([-c for _, _, c in ingredients])
    # 先求可行性（列平衡）下常数和的最小值
    res = linprog(c=cobj, A_eq=Aeq, b_eq=ceq, bounds=(0, None), method='highs')
    if res.status == 3:
        print(f'[{tag}] 常数和无下界 ⟹ 恒等式存在（可取到 <0）✓')
        return True
    if res.status != 0:
        print(f'[{tag}] 配平 LP status={res.status}（无列平衡解）✗ 障碍')
        return False
    print(f'[{tag}] 常数和最小值 = {res.fun:.6f}（{"<0 ⟹ 恒等式存在 ✓" if res.fun < -1e-9 else ">=0 ⟹ 这批原料配不出矛盾 ✗ 障碍"}）')
    if res.fun < -1e-9:
        w = res.x
        print('   恒等式权：', {ingredients[i][0]: round(float(w[i]), 4) for i in range(nI) if w[i] > 1e-9})
        return True
    return False


def b0_wlog():
    """Template-b0 的 w.l.o.g. 换元：a>=2 自动（m>=4, b=0）。
    装箱输入 w.l.o.g. 版：极端配对 1-s0-s3>=0 与 1-s1-s2>=0（任意装箱 ⟹ 最小4台极端配对可行）；
    JJJ w.l.o.g. 版：G* = 1-t-w1-w2>=0（值序最小三件：t + 最小两 junior）。"""
    V = ['p', 't', 's0', 's1', 's2', 's3', 'w1', 'w2', 'q1']
    ING = [
        ('danger', {'p': 1, 't': 1}, -5 / 4),          # p+t-5/4>=0
        ('P0', {'s0': 1, 'j0': 1, 'p': -1}, 0),        # pair 机0（j0 = 其 junior）
        ('P1', {'s1': 1, 'j1': 1, 'p': -1}, 0),
        ('srt0', {'s1': 1, 's0': -1}, 0),
        ('srt1', {'s2': 1, 's1': -1}, 0),
        ('srt2', {'s3': 1, 's2': -1}, 0),
        ('SS*03', {'s0': -1, 's3': -1}, 1),            # 极端配对 s0+s3<=1
        ('SS*12', {'s1': -1, 's2': -1}, 1),            # 极端配对 s1+s2<=1
        ('G*', {'t': -1, 'w1': -1, 'w2': -1}, 1),      # 值序最小三件和<=1
        ('w1>=t', {'w1': 1, 't': -1}, 0),
        ('w2>=t', {'w2': 1, 't': -1}, 0),
        ('w1>=p-1', {'w1': 1, 'p': -1}, 1),            # w1=j_u>=p-s_u>=p-1
        ('w2>=p-1', {'w2': 1, 'p': -1}, 1),
        ('q1>=w1', {'q1': 1, 'w1': -1}, 0),            # q1 最大 junior
        ('q1>=w2', {'q1': 1, 'w2': -1}, 0),
        ('s0>=q1', {'s0': 1, 'q1': -1}, 0),            # a_m=s0>=q1
        ('q1>=t', {'q1': 1, 't': -1}, 0),
    ]
    # j0,j1 未入列——P0/P1 需要 j 列；简化：把 j0,j1 也列入变量
    V = ['p', 't', 's0', 's1', 's2', 's3', 'j0', 'j1', 'w1', 'w2', 'q1']
    balance(ING, V, 'b0-wlog（极端配对+G*）')


def b0_wlog_narrow():
    """加窄带 w_i<2t 的上界行（w_i<=2t 即 2t-w_i>0）与 junior 全件 >=t 的账。"""
    V = ['p', 't', 's0', 's1', 's2', 's3', 'j0', 'j1', 'w1', 'w2', 'q1']
    ING = [
        ('danger', {'p': 1, 't': 1}, -5 / 4),
        ('P0', {'s0': 1, 'j0': 1, 'p': -1}, 0),
        ('P1', {'s1': 1, 'j1': 1, 'p': -1}, 0),
        ('srt0', {'s1': 1, 's0': -1}, 0),
        ('srt1', {'s2': 1, 's1': -1}, 0),
        ('srt2', {'s3': 1, 's2': -1}, 0),
        ('SS*03', {'s0': -1, 's3': -1}, 1),
        ('SS*12', {'s1': -1, 's2': -1}, 1),
        ('G*', {'t': -1, 'w1': -1, 'w2': -1}, 1),
        ('w1>=t', {'w1': 1, 't': -1}, 0),
        ('w2>=t', {'w2': 1, 't': -1}, 0),
        ('q1>=w1', {'q1': 1, 'w1': -1}, 0),
        ('q1>=w2', {'q1': 1, 'w2': -1}, 0),
        ('s0>=q1', {'s0': 1, 'q1': -1}, 0),
        ('q1>=t', {'q1': 1, 't': -1}, 0),
        ('Pw1', {'w1': 1, 'p': -1}, 1),
        ('Pw2', {'w2': 1, 'p': -1}, 1),
        # 窄带上界：j_i<=2t（对 j0,j1）；w_i<=q1 已有
        ('j0<=2t', {'j0': -1, 't': 2}, 0),
        ('j1<=2t', {'j1': -1, 't': 2}, 0),
    ]
    balance(ING, V, 'b0-wlog+窄带上界')


def lemma2_wlog_caseA():
    """引理 2 换元（情形 A：值序最小三 junior 在低端区，机器序=值序）：
    G* = 1-t-j0-j1（w0=t, w1=j0, w2=j1），保序链 M0=j1-j0>=0，C=1-s0-s1。"""
    V = ['p', 't', 's0', 's1', 'j0', 'j1', 'q1']
    ING = [
        ('danger', {'p': 1, 't': 1}, -5 / 4),
        ('P0', {'s0': 1, 'j0': 1, 'p': -1}, 0),
        ('P1', {'s1': 1, 'j1': 1, 'p': -1}, 0),
        ('C*', {'s0': -1, 's1': -1}, 1),
        ('G*', {'t': -1, 'j0': -1, 'j1': -1}, 1),
        ('M0', {'j1': 1, 'j0': -1}, 0),
        ('j0>=t', {'j0': 1, 't': -1}, 0),
        ('j1>=t', {'j1': 1, 't': -1}, 0),
        ('q1>=j1', {'q1': 1, 'j1': -1}, 0),   # j_jj=q1 最大
        ('s0>=q1', {'s0': 1, 'q1': -1}, 0),   # a_m=s0（登记原料）
        ('q1>=t', {'q1': 1, 't': -1}, 0),
        ('srt', {'s1': 1, 's0': -1}, 0),
        # K 结构：sk+q1<=K ⟺ (5/4)s0+(5/4)q1-s_jj-q1>=0 即 (5/4)s0+(1/4)q1>=s_jj；
        # 简化 w.l.o.g. 版：s_jj>=s1（jj>=1 时）或 s_jj=s0（jj=0）；取 s_jj>=s0（恒真）
        # 太弱；暂不加 K 行看配平
    ]
    balance(ING, V, '引理2-wlog-情形A（低端区）')


if __name__ == '__main__':
    b0_wlog()
    b0_wlog_narrow()
    lemma2_wlog_caseA()
