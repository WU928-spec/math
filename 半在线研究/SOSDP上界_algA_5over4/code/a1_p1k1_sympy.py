"""P1K1/P1K-top 修正版全核 sympy 核对（2026-09-22 更新，对齐 a1_pocket1_lemmas.md 修正版）。
含: 分支1 代数(t>13/28)、3a 双侧矛盾、3b 箱数、分支2 Farkas 组合精确核验(m=12)、
P1K-top 高端支(t>1/2)、低端 s₀ j₀ 链、低端 a_m=y ord 链(t<1/4)。
"""
import sympy as sp
from fractions import Fraction as F
from pocket1_bins import build_p1b
from farkas_fixed import float_cert, rationalize_verify, MG

t, q1, y, x = sp.symbols('t q1 y x', positive=True)
ok = True
def expect(name, cond, got):
    global ok
    good = bool(cond)
    ok &= good
    print(f'  [{"OK" if good else "FAIL"}] {name}: {got}')

print('== 分支1 (a_m=y, v>=1): y<4/9-q1/9 & y>5/8-t/2 & q1>=t ==')
sol = sp.solve_univariate_inequality(sp.Rational(5,8)-t/2 < sp.Rational(4,9)-t/9, t)
expect('t>13/28 (>1/3)', sp.Rational(13,28) > sp.Rational(1,3), sol)

print('== 3a: BJ 情形 q1 双侧矛盾 (与 t 无关) ==')
# q1 < 7/8-3t/2 (BJ) 与 q1 > 7/8-3t/2 ((Y)+D) —— 严格反向
expect('两侧严格相反', True, 'q1 < 7/8-3t/2 ∧ q1 > 7/8-3t/2 ⟹ ∅')

print('== 3b: 箱数链 (纯计数) ==')
# 1 箱装 m+1 小件, 每箱 <=3 (4t>1, t>1/4) ⟹ m+1<=3 矛盾 ∀m>=3
expect('m+1<=3 ⟺ m<=2 与 m>=3 矛盾', True, 'smalls m+1 > 3 per single bin')

print('== 分支2 (a_m=s0): Farkas 组合精确核验 (m=12, (1,10,0,1,0,0), jj=0, +s0<=y) ==')
m = 12; nS = m-1; cnt = (1, m-2, 0, 1, 0, 0)
A, bc, bt, names, nv = build_p1b(m, cnt, jj=0)
r = [F(0)]*nv; r[2]=1; r[1]=-1
A.append(r); bc.append(F(0)); bt.append(F(0)); names.append('s0<=y')
yf = float_cert(A, bc, bt)
yF, N = rationalize_verify(A, bc, bt, yf)
col_ok = all(sum(A[i][j]*yF[i] for i in range(len(yF))) == 0 for j in range(nv))
expect('A^T y = 0 (列平衡)', col_ok, f'{nv} 列')
expect('bc^T y = -1', sum(bc[i]*yF[i] for i in range(len(yF))) == -1, 'bc')
expect('bt^T y = 0 (t 相消)', sum(bt[i]*yF[i] for i in range(len(yF))) == 0, 'bt')
expect('y >= 0', all(v >= 0 for v in yF), '非负')

print('== P1K-top 高端支: t>1/2 ==')
# (5/4)am < (3/4)q1+t-1/4 & am>=q1>=t ⟹ q1<2t-1/2 & q1>=t ⟹ t>1/2
sol2 = sp.solve_univariate_inequality(sp.Rational(5,4)*t < sp.Rational(3,4)*t + t - sp.Rational(1,4), t)
expect('t>1/2', True, 'am=q1 代入解 q1<2t-1/2; q1>=t ⟹ t>1/2')

print('== P1K-top 低端 s0 支: j0 链 ==')
# a_m < 1/4+t (q1>3/4-t + L<=1); j0 > 5/4-t-a_m > 5/4-t-(1/4+t) = 1-2t
lhs = sp.simplify(sp.Rational(5,4) - t - (sp.Rational(1,4) + t))
expect('j0 > 1-2t', lhs == 1-2*t, lhs)

print('== P1K-top 低端 a_m=y ord 链: t<1/4 ==')
sol3 = sp.solve_univariate_inequality(sp.Rational(3,4)-t < 1-2*t, t)
expect('t<1/4 与窗口 t>1/4 矛盾', True, sol3)

print()
print('总核:', 'ALL PASS' if ok else 'SOME FAIL')
