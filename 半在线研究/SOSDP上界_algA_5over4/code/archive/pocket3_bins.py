"""口袋3残留角落重建 LP：去掉不合法的 y>=1-2t（LP_CONSTRAINTS.md §2.1），装箱结构补位。
不改动 pocket13_fixed.build_p3f 基线。

角落语义（已按审计核对，LP_CONSTRAINTS.md §0/§2）：
  M0={x,y,z} 3 件最闲机，x<=y<=z；递减到达 ⟹ z=M0 初始件（后至件 ≤ q1 ≤ p_m ≤ z），
  x,y = 后至件 ∈ [t, q1] ⊂ [t, 2t)（L<4t 制度，L>=4t 由分片引理闭合：C_A<=OPT+t<=5/4）；
  t fallback 落入 M0；danger ℓ0+t>5/4（编码为非严格 >=，方向安全）；
  他机 m-1 台各 2 件 {s_i,j_i}：s_i>1-2t（非小引理，审计§1.1 已证）、j_i∈[t,2t)；
  mach: s_i+j_i >= ℓ0（M0 最闲）；OPT=1 ⟹ 2m+2 件装 m 箱，每箱 <=3 件（t>1/4）。

箱型 taxonomy（senior>1-2t 严格+MG：senior+2件>1、2senior+1件>1、3senior>1 ⟹
senior 只在 SS/SJ/S 箱；非 senior 池 = {x,y,z,t}∪{j_i} 共 m+3 件在 JJJ/JJ/J 箱）：
  a=#SS b=#SJ c=#S d=#JJJ e=#JJ f=#J
  守恒: 2a+b+c = m-1（senior）、b+3d+2e+f = m+3（非senior）、a+b+c+d+e+f = m（箱数）
  恒等式（三式相减）: d = c+f+2 >= 2（JJJ 必存在）、a = c+e+2f+1 >= 1（SS 必存在）

firststep 三分支（q1=p_{m+1} 恒 best-fit，完备覆盖其落机）：
  A1: q1→他机 jj，M0 封死（z+q1>K）
  A2: q1→他机 jj，M0 可放但不比 jj 满（z<=s_jj）
  B : q1→M0（y=q1；z+q1<=K；比 z 大的 senior 机放不下 q1：top-h 台 nofit+hizone，h 枚举）
  完备性：z+q1>K⟹A1；z+q1<=K∧z<=s_jj⟹A2；z+q1<=K∧z>s_jj⟹best-fit 必落 M0（B）。tie 组内置换 w.l.o.g.

分组纪律（LP_CONSTRAINTS.md §1.4）：SS 用【极端配对】（最小 2a 个 senior 首尾配对，
  可证 w.l.o.g.）；SJ 用反序配对（最小 SJ senior 配槽池最大件）；junior 槽固定序非 w.l.o.g.
  ——事后 no-bins+装箱 DFS 声音性核查（posthoc 命令），发现过约束即报洞。
CPU 纪律：单进程、nice -n 15、断点续跑（p3_bins_progress.jsonl）。
"""
from fractions import Fraction as F
import numpy as np
from scipy.optimize import linprog
import sys, os, json, time

MG = F(1, 10000)
PROGRESS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'p3_bins_progress.jsonl')
CERTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'p3_bins_certificates.txt')


# ---------------------------------------------------------------- 箱型计数枚举
def bin_count_solutions_p3(m):
    """枚举 cnt=(a,b,c,d,e,f)：
       senior 守恒 2a+b+c = m-1；非senior 守恒 b+3d+2e+f = m+3；箱数 = m。"""
    nS, nJ, nB = m - 1, m + 3, m
    out = []
    for a in range(nS // 2 + 1):
        for b in range(nS + 1):
            c = nS - 2 * a - b
            if c < 0:
                continue
            for d in range(nJ + 1):
                for e in range(nJ + 1):
                    f = a + 1 - d - e
                    if f < 0:
                        continue
                    if b + 3 * d + 2 * e + f != nJ:
                        continue
                    out.append((a, b, c, d, e, f))
    return out


def verify_cnt_identities(m, cnt):
    """恒等式 d = c+f+2 >= 2、a = c+e+2f+1 >= 1。"""
    a, b, c, d, e, f = cnt
    assert 2 * a + b + c == m - 1 and b + 3 * d + 2 * e + f == m + 3
    assert a + b + c + d + e + f == m
    return d == c + f + 2 >= 2 and a == c + e + 2 * f + 1 >= 1


# ---------------------------------------------------------------- LP 构造
def build_p3bins(m, cnt, case='A1', jj=1, h=0, use_bins=True, use_danger=True,
                 use_mach=True, use_fs=True, mg=MG):
    """case: 'A1'/'A2'（q1→他机 jj=k，1-indexed）/ 'B'（q1→M0，top-h nofit）。"""
    a, b, c, d, e, f = cnt
    nS = m - 1
    nv = 3 + 2 * nS + 2
    ix, iy, iz = 0, 1, 2
    def vs(i): return 3 + i
    def vj(i): return 3 + nS + i
    iam, iq1 = 3 + 2 * nS, 3 + 2 * nS + 1
    A, bc, bt, names = [], [], [], []

    def con(row, c0, c1, nm):
        A.append([F(z) for z in row]); bc.append(F(c0)); bt.append(F(c1)); names.append(nm)

    def zero(): return [F(0)] * nv

    # ---- M0 结构（递减到达 ⟹ z 初始、x,y 后至）
    r = zero(); r[ix] = 1; r[iy] = -1; con(r, 0, 0, 'x<=y')
    r = zero(); r[iy] = 1; r[iz] = -1; con(r, 0, 0, 'y<=z')
    r = zero(); r[ix] = -1; con(r, 0, -1, 'x>=t')
    r = zero(); r[iy] = 1; r[iq1] = -1; con(r, 0, 0, 'y<=q1')
    r = zero(); r[iz] = 1; con(r, 1, 0, 'z<=1')
    r = zero(); r[iam] = 1; r[iz] = -1; con(r, 0, 0, 'am<=z')
    # ---- danger（非严格，方向安全）
    if use_danger:
        r = zero(); r[ix] = -1; r[iy] = -1; r[iz] = -1; con(r, -F(5, 4), 1, 'danger')
    for i in range(nS):
        # ---- 他机 2 件：senior 非小（审计§1.1）、junior 窄带
        r = zero(); r[vs(i)] = -1; con(r, -1 - mg, 2, f's{i}>=1-2t')
        r = zero(); r[vs(i)] = 1; con(r, 1, 0, f's{i}<=1')
        r = zero(); r[vj(i)] = -1; con(r, 0, -1, f'j{i}>=t')
        r = zero(); r[vj(i)] = 1; r[iq1] = -1; con(r, 0, 0, f'j{i}<=q1')
        # ---- mach（M0 最闲）
        if use_mach:
            r = zero(); r[ix] = 1; r[iy] = 1; r[iz] = 1; r[vs(i)] = -1; r[vj(i)] = -1
            con(r, -mg, 0, f'mach{i}')
        # ---- 递减/定义
        r = zero(); r[iam] = 1; r[vs(i)] = -1; con(r, 0, 0, f'am<=s{i}')
    r = zero(); r[iq1] = 1; r[iam] = -1; con(r, 0, 0, 'q1<=am')
    r = zero(); r[iq1] = 1; con(r, -mg, 2, 'q1<=2t')       # L<4t 制度 ⟹ q1<2t
    r = zero(); r[iam] = -1; con(r, 0, -1, 't<=am')
    r = zero(); r[iq1] = -1; con(r, 0, -1, 't<=q1')
    r = zero(); r[iam] = 1; r[iq1] = 1; con(r, 1, 0, 'L<=1')
    for i in range(nS - 1):
        r = zero(); r[vs(i)] = 1; r[vs(i + 1)] = -1; con(r, 0, 0, f'srt{i}')
    # ---- vol: T = ℓ0 + Σ(s+j) + t <= m
    r = zero()
    for v in [ix, iy, iz]: r[v] = 1
    for i in range(nS):
        r[vs(i)] = 1; r[vj(i)] = 1
    con(r, m, -1, 'vol<=m')
    # ---- firststep 三分支
    jdx = jj - 1  # 0-indexed 落机
    if use_fs and case in ('A1', 'A2'):
        for i in range(nS):
            if i != jdx:
                r = zero(); r[vj(jdx)] = -1; r[vj(i)] = 1; con(r, 0, 0, f'fs_j{i}')
        r = zero(); r[iq1] = 1; r[vj(jdx)] = -1; con(r, 0, 0, f'q1<=j{jdx}')
        r = zero(); r[vs(jdx)] = 4; r[iam] = -5; r[iq1] = -1; con(r, 0, 0, 'sk+q1<=K')
        for i in range(jdx + 1, nS):
            r = zero(); r[vs(i)] = -4; r[iam] = 5; r[iq1] = 1; con(r, -mg, 0, f'nofit{i}')
        if case == 'A1':
            # M0 封死：z+q1 > K ⟺ 4z > 5am+q1 ⟺ -4z+5am+q1 <= -MG
            r = zero(); r[iz] = -4; r[iam] = 5; r[iq1] = 1; con(r, -mg, 0, 'z+q1>K')
        else:
            # M0 不满于 jj：z <= s_jj
            r = zero(); r[iz] = 1; r[vs(jdx)] = -1; con(r, 0, 0, f'z<=s{jdx}')
    elif use_fs and case == 'B':
        # y = q1（M0 首后至件）
        r = zero(); r[iq1] = 1; r[iy] = -1; con(r, 0, 0, 'q1<=y')
        # z+q1 <= K ⟺ 4z - 5am - q1 <= 0
        r = zero(); r[iz] = 4; r[iam] = -5; r[iq1] = -1; con(r, 0, 0, 'z+q1<=K')
        top = nS - h
        for i in range(top):
            r = zero(); r[vs(i)] = 1; r[iz] = -1; con(r, 0, 0, f'lz{i}')      # s_i <= z
        for i in range(top, nS):
            r = zero(); r[vs(i)] = -1; r[iz] = 1; con(r, -mg, 0, f'hz{i}')   # s_i > z
            r = zero(); r[vs(i)] = -4; r[iam] = 5; r[iq1] = 1; con(r, -mg, 0, f'nofitB{i}')
    # ---- 装箱帽（SS 极端配对 w.l.o.g.；SJ 反序配对；J 槽固定序，事后声音性核查）
    if use_bins:
        slots = [1, ix, iy] + [vj(i) for i in range(nS)] + [iz]  # [t, x, y, j_0..j_{nS-1}, z] 升序-ish
        # it=1 是变量 t 的索引
        def cap(idxs, nm):
            r = zero()
            for ii in idxs: r[ii] = 1
            con(r, 1, 0, nm)
        for kk in range(a):                                    # SS 极端配对
            cap([vs(kk), vs(2 * a - 1 - kk)], 'SS')
        for kk in range(b):                                    # SJ 反序（小 senior 配大槽）
            cap([vs(2 * a + kk), slots[b - 1 - kk]], 'SJ')
        jidx = b
        for kk in range(d):
            cap([slots[jidx], slots[jidx + 1], slots[jidx + 2]], 'JJJ'); jidx += 3
        for kk in range(e):
            cap([slots[jidx], slots[jidx + 1]], 'JJ'); jidx += 2
    return A, bc, bt, names, nv


# ---------------------------------------------------------------- 求解/验证
def float_cert(A, bc, bt):
    Af = np.array([[float(x) for x in row] for row in A])
    bcf = np.array([float(x) for x in bc]); btf = np.array([float(x) for x in bt])
    Aeq = np.vstack([Af.T, btf.reshape(1, -1), bcf.reshape(1, -1)])
    beq = np.concatenate([np.zeros(Af.shape[1]), [0.0, -1.0]])
    res = linprog(c=np.zeros(Af.shape[0]), A_eq=Aeq, b_eq=beq, bounds=(0, None), method='highs')
    return res.x if res.status == 0 else None


def exact_verify_support(A, bc, bt, names, yf):
    """OPTIMIZE 优化3：只对支撑行有理化并精确验证 Aᵀy=0、btᵀy=0、bcᵀy=-1、y>=0。"""
    sup = [i for i, v in enumerate(yf) if v > 1e-9]
    for N in [10**3, 10**4, 10**5, 10**6, 10**7]:
        y = {}
        ok = True
        for i in sup:
            y[i] = F(float(yf[i])).limit_denominator(N)
        for j in range(len(A[0])):
            if sum(A[i][j] * y[i] for i in sup) != 0:
                ok = False; break
        if not ok:
            continue
        if sum(bt[i] * y[i] for i in sup) != 0:
            continue
        if sum(bc[i] * y[i] for i in sup) != -1:
            continue
        if any(v < 0 for v in y.values()):
            continue
        return {i: y[i] for i in sup}, N
    return None, None


def primal_feasible(A, bc, bt, t0, nv):
    Af = np.array([[float(x) for x in row] for row in A])
    bf = np.array([float(bc[i]) + float(bt[i]) * t0 for i in range(len(A))])
    res = linprog(c=np.zeros(nv), A_ub=Af, b_ub=bf, bounds=(None, None), method='highs')
    return res.x if res.status == 0 else None


def case_list(m):
    nS = m - 1
    out = []
    for cs in ('A1', 'A2'):
        for jj in range(1, nS + 1):
            out.append((cs, jj, 0))
    for h in range(0, nS + 1):
        out.append(('B', 1, h))
    return out


# ---------------------------------------------------------------- sanity
def sanity():
    print('== sanity 1：E4 审计见证（m=6, t=0.3139, y<1-2t, ℓ0+t=1.2557）必须被新 LP 判死 ==')
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from audit_constraints import build_p3, primal_feasible as pf_old
    m = 6
    A0, b0, t0v, n0, v0 = build_p3(m, 1, drop=('y>=1-2t',))
    t0 = 0.3139
    obj = np.zeros(v0); obj[0] = obj[1] = obj[2] = 1.0
    from scipy.optimize import linprog as lp
    Af = np.array([[float(x) for x in row] for row in A0])
    bf = np.array([float(b0[i]) + float(t0v[i]) * t0 for i in range(len(A0))])
    res = lp(c=-obj, A_ub=Af, b_ub=bf, bounds=(None, None), method='highs')
    assert res.status == 0, '见证点重构失败'
    x = res.x
    nS = m - 1
    xv, yv, zv = x[0], x[1], x[2]
    q1v = x[3 + 2 * nS + 1]; amv = x[3 + 2 * nS]
    K = 1.25 * (amv + q1v)
    print(f'  见证: x={xv:.4f} y={yv:.4f} z={zv:.4f} q1={q1v:.4f} ℓ0+t={xv+yv+zv+t0:.4f}')
    print(f'  z+q1={zv+q1v:.4f} vs K={K:.4f}（{"M0封死=A1" if zv+q1v > K else "M0可放"}），'
          f'y{"=q1（case B 候选）" if abs(yv-q1v)<1e-6 else "<q1（case A 候选）"}')
    nS = m - 1
    s = x[3:3+nS]
    print(f'  s={np.round(s,4)}（落机 jj 应为最大 senior 侧/tie 组末尾）')
    # 全 (cnt, case) 原 LP 逐 t 判定
    cnts = bin_count_solutions_p3(m)
    print(f'  m={m} 共 {len(cnts)} 个 cnt × {len(case_list(m))} 个 case：')
    bad = []
    for cnt in cnts:
        for cs, jj, h in case_list(m):
            A, bc, bt, names, nv = build_p3bins(m, cnt, cs, jj, h)
            x2 = primal_feasible(A, bc, bt, t0, nv)
            if x2 is not None:
                bad.append((cnt, cs, jj, h))
    print(f'  见证被杀：{"✓ 全部 (cnt,case) INFEASIBLE" if not bad else f"✗ 仍可行于 {bad[:5]}"}')
    print()
    print('== sanity 2（反 sanity，按 P3C 修正期望）：结构本身即空 ⟹ 去 danger 含 bins 仍 INF；')
    print('   正确的非永假检验：去 danger+去 bins、去 danger+去 mach 必须 feasible ==')
    m = 6
    n1 = n2 = 0
    for cnt in bin_count_solutions_p3(m):
        for cs, jj, h in case_list(m):
            A, bc, bt, names, nv = build_p3bins(m, cnt, cs, jj, h, use_danger=False, use_bins=False)
            if primal_feasible(A, bc, bt, 0.31, nv) is not None:
                n1 += 1
                break
        if n1:
            break
    for cnt in bin_count_solutions_p3(m):
        for cs, jj, h in case_list(m):
            A, bc, bt, names, nv = build_p3bins(m, cnt, cs, jj, h, use_danger=False, use_mach=False)
            if primal_feasible(A, bc, bt, 0.31, nv) is not None:
                n2 += 1
                break
        if n2:
            break
    print(f'  去danger+去bins: {"✓ feasible" if n1 else "✗ 仍 INF（装箱非承重，模型可疑!）"}')
    print(f'  去danger+去mach: {"✓ feasible" if n2 else "✗ 仍 INF（mach 非承重，模型可疑!）"}')
    print()
    print('== sanity 3：消融（m=6 cnt=(1,3,0,2,0,0) case A2 jj=5）==')
    m, cnt, cs, jj, h = 6, (1, 3, 0, 2, 0, 0), 'A2', 5, 0
    base = build_p3bins(m, cnt, cs, jj, h)
    print(f'  基准: {"有证书(INF)" if float_cert(*base[:3]) is not None else "feasible"}')
    for nm, kw in [('去装箱', dict(use_bins=False)), ('去danger', dict(use_danger=False)),
                   ('去mach', dict(use_mach=False)), ('去firststep', dict(use_fs=False))]:
        A, bc, bt, names, nv = build_p3bins(m, cnt, cs, jj, h, **kw)
        print(f'   {nm:10s}: {"feasible（必要 ✓）" if float_cert(A, bc, bt) is None else "仍有证书（非必要!）"}')


# ---------------------------------------------------------------- 快速稀疏行生成器（扫描用）
def rows_p3bins(m, cnt, case='A1', jj=1, h=0, use_bins=True, use_danger=True,
                use_mach=True, use_fs=True, mg=MG):
    """与 build_p3bins 同语义，但直接产出稀疏行：(name, {var: coeff(float)}, bc(Fraction), bt(Fraction))。
    矩阵系数 ∈ {0,±1,±4,±5,±1.25} 二进制精确；bc/bt 精确 Fraction（MG=F(1,10000)）。"""
    a, b, c, d, e, f = cnt
    nS = m - 1
    nv = 3 + 2 * nS + 2
    ix, iy, iz = 0, 1, 2
    def vs(i): return 3 + i
    def vj(i): return 3 + nS + i
    iam, iq1 = 3 + 2 * nS, 3 + 2 * nS + 1
    rows = []

    def con(d, c0, c1, nm):
        rows.append((nm, d, F(c0), F(c1)))

    con({ix: 1.0, iy: -1.0}, 0, 0, 'x<=y')
    con({iy: 1.0, iz: -1.0}, 0, 0, 'y<=z')
    con({ix: -1.0}, 0, -1, 'x>=t')
    con({iy: 1.0, iq1: -1.0}, 0, 0, 'y<=q1')
    con({iz: 1.0}, 1, 0, 'z<=1')
    con({iam: 1.0, iz: -1.0}, 0, 0, 'am<=z')
    if use_danger:
        con({ix: -1.0, iy: -1.0, iz: -1.0}, F(-5, 4), 1, 'danger')
    for i in range(nS):
        con({vs(i): -1.0}, F(-1) - mg, 2, f's{i}>=1-2t')
        con({vs(i): 1.0}, 1, 0, f's{i}<=1')
        con({vj(i): -1.0}, 0, -1, f'j{i}>=t')
        con({vj(i): 1.0, iq1: -1.0}, 0, 0, f'j{i}<=q1')
        if use_mach:
            con({ix: 1.0, iy: 1.0, iz: 1.0, vs(i): -1.0, vj(i): -1.0}, -mg, 0, f'mach{i}')
        con({iam: 1.0, vs(i): -1.0}, 0, 0, f'am<=s{i}')
    con({iq1: 1.0, iam: -1.0}, 0, 0, 'q1<=am')
    con({iq1: 1.0}, -mg, 2, 'q1<=2t')
    con({iam: -1.0}, 0, -1, 't<=am')
    con({iq1: -1.0}, 0, -1, 't<=q1')
    con({iam: 1.0, iq1: 1.0}, 1, 0, 'L<=1')
    for i in range(nS - 1):
        con({vs(i): 1.0, vs(i + 1): -1.0}, 0, 0, f'srt{i}')
    dvol = {ix: 1.0, iy: 1.0, iz: 1.0}
    for i in range(nS):
        dvol[vs(i)] = 1.0; dvol[vj(i)] = 1.0
    con(dvol, m, -1, 'vol<=m')
    jdx = jj - 1
    if use_fs and case in ('A1', 'A2'):
        for i in range(nS):
            if i != jdx:
                con({vj(jdx): -1.0, vj(i): 1.0}, 0, 0, f'fs_j{i}')
        con({iq1: 1.0, vj(jdx): -1.0}, 0, 0, f'q1<=j{jdx}')
        con({vs(jdx): 4.0, iam: -5.0, iq1: -1.0}, 0, 0, 'sk+q1<=K')
        for i in range(jdx + 1, nS):
            con({vs(i): -4.0, iam: 5.0, iq1: 1.0}, -mg, 0, f'nofit{i}')
        if case == 'A1':
            con({iz: -4.0, iam: 5.0, iq1: 1.0}, -mg, 0, 'z+q1>K')
        else:
            con({iz: 1.0, vs(jdx): -1.0}, 0, 0, f'z<=s{jdx}')
    elif use_fs and case == 'B':
        con({iq1: 1.0, iy: -1.0}, 0, 0, 'q1<=y')
        con({iz: 4.0, iam: -5.0, iq1: -1.0}, 0, 0, 'z+q1<=K')
        top = nS - h
        for i in range(top):
            con({vs(i): 1.0, iz: -1.0}, 0, 0, f'lz{i}')
        for i in range(top, nS):
            con({vs(i): -1.0, iz: 1.0}, -mg, 0, f'hz{i}')
            con({vs(i): -4.0, iam: 5.0, iq1: 1.0}, -mg, 0, f'nofitB{i}')
    if use_bins:
        slots = [1, ix, iy] + [vj(i) for i in range(nS)] + [iz]
        for kk in range(a):
            con({vs(kk): 1.0, vs(2 * a - 1 - kk): 1.0}, 1, 0, 'SS')
        for kk in range(b):
            con({vs(2 * a + kk): 1.0, slots[b - 1 - kk]: 1.0}, 1, 0, 'SJ')
        jidx = b
        for kk in range(d):
            con({slots[jidx]: 1.0, slots[jidx + 1]: 1.0, slots[jidx + 2]: 1.0}, 1, 0, 'JJJ')
            jidx += 3
        for kk in range(e):
            con({slots[jidx]: 1.0, slots[jidx + 1]: 1.0}, 1, 0, 'JJ')
            jidx += 2
    return rows, nv


def fast_float_cert(rows, nv):
    """稀疏行直接装配浮点对偶 LP。"""
    nr = len(rows)
    Af = np.zeros((nr, nv))
    bcf = np.zeros(nr); btf = np.zeros(nr)
    for i, (nm, d, c0, c1) in enumerate(rows):
        for v, w in d.items():
            Af[i, v] = w
        bcf[i] = float(c0); btf[i] = float(c1)
    Aeq = np.vstack([Af.T, btf.reshape(1, -1), bcf.reshape(1, -1)])
    beq = np.concatenate([np.zeros(nv), [0.0, -1.0]])
    res = linprog(c=np.zeros(nr), A_eq=Aeq, b_eq=beq, bounds=(0, None), method='highs')
    return res.x if res.status == 0 else None


def exact_verify_sparse(rows, nv, yf):
    """支撑行精确验证：Aᵀy=0、btᵀy=0、bcᵀy=-1、y>=0。系数由 float 还原（二进制精确）。"""
    sup = [i for i, v in enumerate(yf) if v > 1e-9]
    for N in [10**3, 10**4, 10**5, 10**6, 10**7]:
        y = {i: F(float(yf[i])).limit_denominator(N) for i in sup}
        ok = True
        for j in range(nv):
            s = F(0)
            for i in sup:
                w = rows[i][1].get(j, 0.0)
                if w:
                    s += F(w) * y[i]
            if s != 0:
                ok = False; break
        if not ok:
            continue
        if sum(rows[i][3] * y[i] for i in sup) != 0:
            continue
        if sum(rows[i][2] * y[i] for i in sup) != -1:
            continue
        if any(v < 0 for v in y.values()):
            continue
        return {rows[i][0]: y[i] for i in sup}, N
    return None, None


# ---------------------------------------------------------------- 扫描（快速稀疏版）
def scan(m_lo=4, m_hi=20):
    """单进程 + 断点续跑。进度: PROGRESS (jsonl)；证书: CERTS。"""
    done = set()
    if os.path.exists(PROGRESS):
        with open(PROGRESS) as f:
            for line in f:
                try:
                    r = json.loads(line)
                    done.add((r['m'], tuple(r['cnt']), r['case'], r['jj'], r['h']))
                except Exception:
                    pass
    pf = open(PROGRESS, 'a')
    cf = open(CERTS, 'a')
    t_start = time.time()
    ncert = nfeas = 0
    for m in range(m_lo, m_hi + 1):
        cnts = bin_count_solutions_p3(m)
        cases = case_list(m)
        mok = True
        tm = time.time()
        for cnt in cnts:
            assert verify_cnt_identities(m, cnt)
            for cs, jj, h in cases:
                if (m, cnt, cs, jj, h) in done:
                    continue
                rows, nv = rows_p3bins(m, cnt, cs, jj, h)
                yf = fast_float_cert(rows, nv)
                if yf is None:
                    rec = {'m': m, 'cnt': cnt, 'case': cs, 'jj': jj, 'h': h, 'status': 'FEAS'}
                    nfeas += 1
                    mok = False
                else:
                    y, N = exact_verify_sparse(rows, nv, yf)
                    if y is None:
                        rec = {'m': m, 'cnt': cnt, 'case': cs, 'jj': jj, 'h': h, 'status': 'RATFAIL'}
                        nfeas += 1
                        mok = False
                    else:
                        rec = {'m': m, 'cnt': cnt, 'case': cs, 'jj': jj, 'h': h, 'status': 'OK', 'N': N}
                        ncert += 1
                        cf.write(json.dumps({'m': m, 'cnt': cnt, 'case': cs, 'jj': jj, 'h': h,
                                             'cert': {nm: str(v) for nm, v in y.items()}}) + '\n')
                        cf.flush()
                pf.write(json.dumps(rec) + '\n')
                pf.flush()
        el = time.time() - t_start
        print(f'  m={m}: {len(cnts)} cnt × {len(cases)} case 完成  {"全闭 ✓" if mok else "有洞 ✗"}'
              f'  （本 m 用时 {time.time()-tm:.0f}s，累计证书 {ncert}、洞 {nfeas}、总 {el:.0f}s）', flush=True)
    print(f'扫描结束：证书 {ncert}、洞/RATFAIL {nfeas}')


# ---------------------------------------------------------------- 洞提取
def holes():
    print('== 扫描洞（progress 中 FEAS/RATFAIL）+ 可行点 ==')
    if not os.path.exists(PROGRESS):
        print('  无进度文件'); return
    with open(PROGRESS) as f:
        recs = [json.loads(line) for line in f]
    hl = [r for r in recs if r['status'] != 'OK']
    print(f'  洞 {len(hl)} 个')
    from collections import defaultdict
    bym = defaultdict(list)
    for r in hl:
        bym[r['m']].append(r)
    for m in sorted(bym):
        tl = m / (4 * (m - 1))
        print(f'  m={m}: {len(bym[m])} 洞')
        for r in bym[m][:6]:
            cnt = tuple(r['cnt'])
            A, bc, bt, names, nv = build_p3bins(m, cnt, r['case'], r['jj'], r['h'])
            for t0 in np.linspace(tl + 0.002, 1 / 3, 6):
                x = primal_feasible(A, bc, bt, t0, nv)
                if x is not None:
                    nS = m - 1
                    print(f'    cnt={cnt} {r["case"]} jj={r["jj"]} h={r["h"]} t={t0:.4f}: '
                          f'x={x[0]:.3f} y={x[1]:.3f} z={x[2]:.3f} ℓ0+t={x[0]+x[1]+x[2]+t0:.4f}')
                    break


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'sanity'
    if cmd == 'sanity':
        sanity()
    elif cmd == 'scan':
        lo = int(sys.argv[2]) if len(sys.argv) > 2 else 4
        hi = int(sys.argv[3]) if len(sys.argv) > 3 else 20
        scan(lo, hi)
    elif cmd == 'holes':
        holes()
