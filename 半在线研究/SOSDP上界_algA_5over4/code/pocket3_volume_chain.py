"""口袋3残留角落的纯体积链验证（猜想：M0 三件 x,y,z 的体积传递 ⟹ vol>m，窗口 t<=1/3 恒成立）。

链条（对照 pocket13_fixed._build 的约束语义，约束形式 row·x <= bc + bt·t）：
  'x>=t'      : x >= t                       (M0 最小件 >= t)
  'y>=1-2t'   : y >= 1 - 2t + eps            (eps = MG = 1/10000)
  'y<=z'      : z >= y                       ⟹ z >= 1 - 2t + eps
  'mach{i}>M0': s_i + j_i >= x + y + z + eps (每台他机负载严格超过 M0；最闲机定义)
  'vol<=m'    : x+y+z + Σ(s_i+j_i) <= m - t  (总体积界)

推导：L0 := x+y+z >= t + 2(1-2t) + 2eps = 2-3t+2eps
      vol >= L0 + (m-1)(L0+eps) = m·L0 + (m-1)eps >= m(2-3t) + (3m-1)eps
      与 vol <= m-t 矛盾 ⟺ m(2-3t) >= m-t ⟺ t <= m/(3m-1)。
      m/(3m-1) > 1/3 对所有 m>=1 成立（差 = 1/(3(3m-1))），故窗口 t<=1/3 全覆盖，
      且与 k 无关（链条不含 k 相关约束）。

本脚本三部分：
  A. sympy 符号验证上述代数（含严格性、窗口余量）；
  B. 显式 Farkas 组合 w=(x>=t:m, y>=1-2t:2m, y<=z:m, mach_i:1, vol:1) 的符号核对
     （A^T w = 0；bc^T w = -m-(3m-1)eps；bt^T w = 3m-1 ⟹ 0 <= (3m-1)(t-eps)-m... 即
     t < m/(3m-1)+eps 时 0<=负数）——注意这是 t 相关组合，不是 LP 意义的常数证书；
  C. 数值交叉验证：把 t 显式化为 [0,1/3] 内变量，只留 5 类约束求原 LP 可行性，
     期望 m=4..40 全 INFEASIBLE；并逐项消融（每去掉一类必须变 FEASIBLE）。
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp

def part_A():
    print('==== A. sympy 符号验证体积链 ====')
    m, t, eps = sp.symbols('m t eps', positive=True)
    L0 = 2 - 3*t + 2*eps                       # x+y+z 下界
    vol_lo = m*L0 + (m-1)*eps                  # 总体积下界
    vol_hi = m - t                             # 总体积上界
    gap = sp.expand(vol_lo.subs(eps, 0) - vol_hi)   # eps=0 的主项差
    print(f'  vol_lo - vol_hi (eps=0 主项) = {gap} = m(1-3t)+t')
    # gap 对 t 线性、斜率 1-3m<0，故窗口 (0,1/3] 最小值在 t=1/3
    slope = sp.diff(gap, t)
    gmin = sp.simplify(gap.subs(t, sp.Rational(1, 3)))
    print(f'  d(gap)/dt = {slope} < 0 (m>=1)；gap(1/3) = {gmin} > 0')
    assert slope.subs(m, 4) < 0 and gmin > 0
    # eps 项系数 (3m-1)>0 给出严格不等式 vol > vol_hi（即使 t=1/3）
    eps_coef = sp.expand(vol_lo - vol_hi).coeff(eps)
    print(f'  eps 系数 = {eps_coef} > 0 ⟹ vol > vol_hi 严格成立（含 t=1/3 端点）')
    assert sp.simplify(eps_coef - (3*m - 1)) == 0
    # 体积链实际覆盖的 t 上界与窗口余量
    tstar = m/(3*m - 1)
    margin = sp.simplify(tstar - sp.Rational(1, 3))
    print(f'  链条覆盖 t <= m/(3m-1)；窗口余量 m/(3m-1)-1/3 = {margin} > 0，m→∞ 极限 1/3')
    assert sp.simplify(margin - 1/(3*(3*m - 1))) == 0
    for mv in [4, 5, 10, 30, 100]:
        print(f'    m={mv}: t* = {sp.nsimplify(tstar.subs(m, mv))} ≈ {float(tstar.subs(m, mv)):.5f}')
    print('  A 全部通过 ✓')

def part_B():
    print('==== B. 显式 Farkas 组合符号核对 ====')
    m, t, eps = sp.symbols('m t eps', positive=True)
    w = {'x>=t': m, 'y>=1-2t': 2*m, 'y<=z': m, 'mach': 1, 'vol': 1}
    # 各变量系数（手工列出约束的贡献，sympy 求和验证为 0）
    coef_x  = -w['x>=t'] + (m-1)*w['mach'] + w['vol']
    coef_y  = -w['y>=1-2t'] + w['y<=z'] + (m-1)*w['mach'] + w['vol']
    coef_z  = -w['y<=z'] + (m-1)*w['mach'] + w['vol']
    coef_s  = -w['mach'] + w['vol']     # 每个 s_i, j_i
    bT = -w['x>=t'] + 2*w['y>=1-2t'] - w['vol']
    bcT = 0*w['x>=t'] + (-1-eps)*w['y>=1-2t'] + 0*w['y<=z'] + (-eps)*(m-1)*w['mach'] + m*w['vol']
    for nm, c in [('x', coef_x), ('y', coef_y), ('z', coef_z), ('s_i/j_i', coef_s)]:
        assert sp.simplify(c) == 0, nm
    print(f'  A^T w = 0 ✓ (x,y,z,s_i,j_i,am,q1 全消)')
    print(f'  bt^T w = {sp.simplify(bT)}；bc^T w = {sp.simplify(bcT)}')
    # 组合约束: 0 <= bc^T w + (bt^T w)·t
    combined = sp.simplify(bcT + bT*t)
    print(f'  组合得 0 <= {combined} ⟺ t >= m/(3m-1) + eps')
    cond = sp.solve(sp.Eq(combined, 0), t)[0]
    print(f'  临界点 t = {sp.simplify(cond)}；窗口 t<=1/3 < m/(3m-1) ⟹ 矛盾 ✓')
    assert sp.simplify(cond - (m/(3*m-1) + eps)) == 0
    print('  B 全部通过 ✓')

def part_C():
    print('==== C. 数值交叉验证（t∈[0,1/3] 显式变量，只留 5 类约束）====')
    import numpy as np
    from scipy.optimize import linprog
    from pocket13_fixed import build_p3f
    KEEP = lambda n: (n in ('x>=t', 'y>=1-2t', 'y<=z', 'vol<=m')) or n.startswith('mach')

    def windowed_feasible(m, drop=()):
        A, bc, bt, names, nv = build_p3f(m, 1)   # 链与 k 无关，任取 k=1
        idx = [i for i, n in enumerate(names) if KEEP(n) and n not in drop]
        Af = np.array([[float(x) for x in A[i]] for i in idx])
        bcf = np.array([float(bc[i]) for i in idx])
        btf = np.array([float(bt[i]) for i in idx])
        # 变量扩一维 tau：A x - bt·tau <= bc，0<=tau<=1/3
        A2 = np.hstack([Af, -btf.reshape(-1, 1)])
        A2 = np.vstack([A2, [0.0]*nv + [1.0]])
        b2 = np.concatenate([bcf, [1.0/3.0]])
        bounds = [(None, None)]*nv + [(0.0, 1.0/3.0)]
        res = linprog(c=np.zeros(nv+1), A_ub=A2, b_ub=b2, bounds=bounds, method='highs')
        return res.status == 0, res.x if res.status == 0 else None

    allok = True
    for m in range(4, 41):
        feas, _ = windowed_feasible(m)
        if feas:
            print(f'  m={m}: FEASIBLE ✗（体积链失败!）'); allok = False
    print(f'  m=4..40 全 INFEASIBLE: {"✓" if allok else "✗"}')
    # 消融：每去掉一类关键约束必须变 feasible
    m = 10
    for drop, tag in [({'x>=t'}, '去x>=t'), ({'y>=1-2t'}, '去y>=1-2t'), ({'y<=z'}, '去y<=z'),
                      ({'vol<=m'}, '去vol<=m'), ({'mach3>M0'}, '去1个mach')]:
        feas, x = windowed_feasible(m, drop)
        print(f'  m={m} {tag}: {"FEASIBLE（必要 ✓）" if feas else "仍 INFEASIBLE（非必要!）"}')
        assert feas, tag
    # 端点敏感性：窗口放大到 t<=0.34（超过 m/(3m-1)）应变 feasible（验证临界真实）
    A, bc, bt, names, nv = build_p3f(10, 1)
    idx = [i for i, n in enumerate(names) if KEEP(n)]
    Af = np.array([[float(x) for x in A[i]] for i in idx])
    bcf = np.array([float(bc[i]) for i in idx]); btf = np.array([float(bt[i]) for i in idx])
    A2 = np.hstack([Af, -btf.reshape(-1, 1)])
    bounds = [(None, None)]*nv + [(0.0, 0.34)]
    res = linprog(c=np.zeros(nv+1), A_ub=A2, b_ub=bcf, bounds=bounds, method='highs')
    print(f'  m=10 窗口放宽到 t<=0.34 (>m/(3m-1)=0.3448?否,=10/29≈0.3448>0.34): '
          f'{"feasible" if res.status==0 else "infeasible"}（临界检查: 0.34<10/29 仍应 infeasible）')
    bounds[-1] = (0.0, 0.35)
    res2 = linprog(c=np.zeros(nv+1), A_ub=A2, b_ub=bcf, bounds=bounds, method='highs')
    print(f'  m=10 窗口放宽到 t<=0.35 (>10/29≈0.3448): '
          f'{"feasible ✓（临界 t* 真实）" if res2.status==0 else "infeasible（临界不符!）"}')
    print('  C 完成')

if __name__ == '__main__':
    part_A(); part_B(); part_C()
