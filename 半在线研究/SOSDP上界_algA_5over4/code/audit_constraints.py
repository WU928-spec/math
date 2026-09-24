"""LP 约束逐条合法性审计实验（只审不改：全部为独立变体，不动 farkas_fixed/pocket13_fixed）。

E1 装箱固定分组 w.l.o.g.：无 bins LP 找可行点 -> 精确装箱 DFS（<=3件/箱, cap 1, m-1 箱）
   -> 若可行点能装箱，则固定分组 LP 的 INFEASIBLE 结论对该点不成立（unsound 风险）。
E2 MG=0 边界：去掉 MARGIN、解除 t pin、窗口内 max(p+t) / max(ℓ0+t)，检验严格角落是否真为空。
E3 p<K：去除单条 p<K 后结论是否变化（验证其冗余性 = 被 pair+fs+sk+q1<=K 蕴含）。
E4 pocket3 y>=1-2t：去除后扫描，提取违反 y>1-2t 的见证点。
E5 j<=2t 消融（load-bearing 检验）。
E6 s>=1-2t 消融（load-bearing 检验）。
E7 pocket3 去除整个 firststep 机组（fs/nofit/sk+q1<=K/q1<=jjj）：检验 q1 放置建模是否承重
   （q1->M0 子情形覆盖缺口的实际影响）。
"""
from fractions import Fraction as F
import numpy as np
from scipy.optimize import linprog
import sys, os, itertools

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pairing_feasible import bin_count_solutions

MG = F(1, 10000)


# ---------------------------------------------------------------- 口袋2 变体构造器
def build_p2(m, cnt, k=1, drop=(), mg=MG):
    """build_fixed 的可删条变体。drop 为约束名前缀集合（按 names 前缀匹配删除）。"""
    a, b, c, d, e, f = cnt
    nS = m - 1
    nv = 2 + 2 * nS + 2
    ip, it = 0, 1
    def vs(i): return 2 + i
    def vj(i): return 2 + nS + i
    iam, iq1 = 2 + 2 * nS, 2 + 2 * nS + 1
    A, bc, bt, names = [], [], [], []

    def con(row, c0, c1, nm):
        if any(nm.startswith(pfx) for pfx in drop):
            return
        A.append([F(x) for x in row]); bc.append(F(c0)); bt.append(F(c1)); names.append(nm)

    def zero(): return [F(0)] * nv

    r = zero(); r[ip] = 1;   con(r, 1, 0, 'p<=1')
    r = zero(); r[ip] = -1;  con(r, 0, 0, 'p>=0')
    r = zero(); r[it] = 1;   con(r, 0, 1, 't<=tf')
    r = zero(); r[it] = -1;  con(r, 0, -1, 't>=tf')
    for i in range(nS):
        r = zero(); r[vs(i)] = -1; con(r, -1 - mg, 2, f's{i}>=1-2t')
        r = zero(); r[vs(i)] = 1;  con(r, 1, 0, f's{i}<=1')
        r = zero(); r[vj(i)] = 1;  con(r, -mg, 2, f'j{i}<=2t')
    for i in range(nS):
        r = zero(); r[it] = 1; r[vj(i)] = -1; con(r, 0, 0, f'j{i}>=t')
    r = zero(); r[ip] = -1; r[it] = -1; con(r, -F(5, 4) - mg, 0, 'danger')
    for i in range(nS):
        r = zero(); r[ip] = 1; r[vs(i)] = -1; r[vj(i)] = -1; con(r, -mg, 0, f'pair{i}')
    for i in range(nS):
        for kk in range(nS):
            r = zero(); r[vj(i)] = 1; r[vs(kk)] = -1; con(r, 0, 0, f'mon_j{i}_s{kk}')
    for kk in range(nS):
        r = zero(); r[it] = 1; r[vs(kk)] = -1; con(r, 0, 0, f'mon_t_s{kk}')
    for i in range(nS):
        r = zero(); r[iam] = 1; r[vs(i)] = -1; con(r, 0, 0, f'am<=s{i}')
        r = zero(); r[vj(i)] = 1; r[iq1] = -1; con(r, 0, 0, f'j{i}<=q1')
    r = zero(); r[it] = 1; r[iq1] = -1; con(r, 0, 0, 't<=q1')
    r = zero(); r[iq1] = 1; r[iam] = -1; con(r, 0, 0, 'q1<=am')
    r = zero(); r[ip] = 1; r[iam] = -F(5, 4); r[iq1] = -F(5, 4); con(r, -mg, 0, 'p<K')
    r = zero(); r[iam] = 1; r[iq1] = 1; con(r, 1, 0, 'L<=1')
    for i in range(nS - 1):
        r = zero(); r[vs(i)] = 1; r[vs(i + 1)] = -1; con(r, 0, 0, f'srt{i}')
    jj = k - 1
    for i in range(nS):
        if i != jj:
            r = zero(); r[vj(jj)] = -1; r[vj(i)] = 1; con(r, 0, 0, f'fs_j{i}')
    r = zero(); r[iq1] = 1; r[vj(jj)] = -1; con(r, 0, 0, f'q1<=j{jj}')
    r = zero(); r[vs(jj)] = 4; r[iam] = -5; r[iq1] = -1; con(r, 0, 0, 'sk+q1<=K')
    for i in range(jj + 1, nS):
        r = zero(); r[vs(i)] = -4; r[iam] = 5; r[iq1] = 1; con(r, -mg, 0, f'nofit{i}')
    jslots = [vj(i) for i in range(nS)] + [it]
    def cap(idxs, nm):
        r = zero()
        for ix in idxs: r[ix] = 1
        con(r, 1, 0, nm)
    for kk in range(a): cap([vs(2 * kk), vs(2 * kk + 1)], 'SS')
    for kk in range(b): cap([vs(2 * a + kk), jslots[kk]], 'SJ')
    jidx = b
    for kk in range(d):
        cap([jslots[jidx], jslots[jidx + 1], jslots[jidx + 2]], 'JJJ'); jidx += 3
    for kk in range(e):
        cap([jslots[jidx], jslots[jidx + 1]], 'JJ'); jidx += 2
    return A, bc, bt, names, nv


# ---------------------------------------------------------------- 口袋3 变体构造器
def build_p3(m, k=1, drop=(), mg=MG):
    nS = m - 1
    nfix = 3
    nv = nfix + 2 * nS + 2
    ix, iy, iz = 0, 1, 2
    off = nfix
    def vs(i): return off + i
    def vj(i): return off + nS + i
    iam, iq1 = off + 2 * nS, off + 2 * nS + 1
    A, bc, bt, names = [], [], [], []

    def con(row, c0, c1, nm):
        if any(nm.startswith(pfx) for pfx in drop):
            return
        A.append([F(z) for z in row]); bc.append(F(c0)); bt.append(F(c1)); names.append(nm)

    def zero(): return [F(0)] * nv

    r = zero(); r[ix] = 1; r[iy] = -1; con(r, 0, 0, 'x<=y')
    r = zero(); r[iy] = 1; r[iz] = -1; con(r, 0, 0, 'y<=z')
    r = zero(); r[ix] = -1; con(r, 0, -1, 'x>=t')
    r = zero(); r[iy] = -1; con(r, -1 - mg, 2, 'y>=1-2t')
    r = zero(); r[iy] = 1; con(r, 1, 0, 'y<=1')
    r = zero()
    for v in [ix, iy, iz]: r[v] = -1
    con(r, -F(5, 4), 1, 'danger')
    for i in range(nS):
        r = zero(); r[vs(i)] = -1; con(r, -1 - mg, 2, f's{i}>=1-2t')
        r = zero(); r[vs(i)] = 1;  con(r, 1, 0, f's{i}<=1')
        r = zero(); r[vj(i)] = 1;  con(r, -mg, 2, f'j{i}<=2t')
        r = zero(); r[vj(i)] = -1; con(r, 0, -1, f'j{i}>=t')
        r = zero()
        for v in [ix, iy, iz]: r[v] = 1
        r[vs(i)] = -1; r[vj(i)] = -1
        con(r, -mg, 0, f'mach{i}>M0')
        r = zero(); r[vj(i)] = 1; r[iam] = -1; con(r, 0, 0, f'j{i}<=am')
        r = zero(); r[iam] = 1; r[vs(i)] = -1; con(r, 0, 0, f'am<=s{i}')
        r = zero(); r[vj(i)] = 1; r[iq1] = -1; con(r, 0, 0, f'j{i}<=q1')
    r = zero(); r[iam] = -1; con(r, 0, -1, 't<=am')
    r = zero(); r[iam] = 1; r[iq1] = 1; con(r, 1, 0, 'L<=1')
    for i in range(nS - 1):
        r = zero(); r[vs(i)] = 1; r[vs(i + 1)] = -1; con(r, 0, 0, f'srt{i}')
    jj = k - 1
    for i in range(nS):
        if i != jj:
            r = zero(); r[vj(jj)] = -1; r[vj(i)] = 1; con(r, 0, 0, f'fs_j{i}')
    r = zero(); r[iq1] = 1; r[vj(jj)] = -1; con(r, 0, 0, f'q1<=j{jj}')
    r = zero(); r[vs(jj)] = 4; r[iam] = -5; r[iq1] = -1; con(r, 0, 0, 'sk+q1<=K')
    for i in range(jj + 1, nS):
        r = zero(); r[vs(i)] = -4; r[iam] = 5; r[iq1] = 1; con(r, -mg, 0, f'nofit{i}')
    r = zero()
    for v in [ix, iy, iz]: r[v] = 1
    for i in range(nS):
        r[vs(i)] = 1; r[vj(i)] = 1
    con(r, m, -1, 'vol<=m')
    return A, bc, bt, names, nv


# ---------------------------------------------------------------- 求解工具
def float_cert(A, bc, bt):
    Af = np.array([[float(x) for x in row] for row in A])
    bcf = np.array([float(x) for x in bc]); btf = np.array([float(x) for x in bt])
    Aeq = np.vstack([Af.T, btf.reshape(1, -1), bcf.reshape(1, -1)])
    beq = np.concatenate([np.zeros(Af.shape[1]), [0.0, -1.0]])
    res = linprog(c=np.zeros(Af.shape[0]), A_eq=Aeq, b_eq=beq, bounds=(0, None), method='highs')
    return res.x if res.status == 0 else None


def primal_feasible(A, bc, bt, t0, nv, drop_rows=(), obj=None):
    """原 LP 在固定 t=t0 下的可行性/最优值。drop_rows: 额外删除的行索引集合。"""
    keep = [i for i in range(len(A)) if i not in drop_rows]
    Af = np.array([[float(x) for x in A[i]] for i in keep])
    bf = np.array([float(bc[i]) + float(bt[i]) * t0 for i in keep])
    c = np.zeros(nv) if obj is None else np.array(obj, dtype=float)
    res = linprog(c=c, A_ub=Af, b_ub=bf, bounds=(None, None), method='highs')
    if res.status != 0:
        return None, None
    return res.x, (float(np.dot(c, res.x)) if obj is not None else 0.0)


def max_with_free_t(A, bc, bt, nv, idx_obj, t_lo, t_hi, it=1):
    """解除 t pin（删 t<=tf/t>=tf 行），t 作为自由变量 ∈ [t_lo, t_hi]，最大化 x[idx_obj] 之和。
    约束中 bt 列的 t 项改写为变量列。"""
    # 找到 pin 行：names 不含，这里通过结构找——bt=±1 且只有 it 列非零
    rows = []
    for i in range(len(A)):
        nz = [j for j in range(nv) if A[i][j] != 0]
        if nz == [it] and bc[i] == 0 and bt[i] in (F(1), F(-1)):
            continue  # t pin 行
        row = [float(x) for x in A[i]]
        row[it] = row[it] - float(bt[i])   # Σ a_j x_j <= bc + bt*t  ⟺  Σ a_j x_j - bt*t <= bc
        rows.append((row, float(bc[i])))
    Af = np.array([r for r, _ in rows]); bf = np.array([b for _, b in rows])
    c = np.zeros(nv); c[idx_obj] = -1.0
    bounds = [(None, None)] * nv
    bounds[it] = (t_lo, t_hi)
    res = linprog(c=c, A_ub=Af, b_ub=bf, bounds=bounds, method='highs')
    if res.status != 0:
        return None, None
    return res.x, -res.fun


# ---------------------------------------------------------------- 精确装箱 DFS
def pack_exact(items, nbins, cap=F(1), max_per_bin=3):
    """items: Fraction 列表。装进 nbins 箱，每箱和 <= cap、件数 <= max_per_bin。返回分组或 None。"""
    items = sorted(items, reverse=True)
    bins = []  # list of [sum, count, list]

    def dfs(i):
        if i == len(items):
            return True
        x = items[i]
        seen = set()
        for b in bins:
            if b[1] < max_per_bin and b[0] + x <= cap and b[0] not in seen:
                seen.add(b[0])
                b[0] += x; b[1] += 1; b[2].append(x)
                if dfs(i + 1):
                    return True
                b[0] -= x; b[1] -= 1; b[2].pop()
        if len(bins) < nbins:
            bins.append([x, 1, [x]])
            if dfs(i + 1):
                return True
            bins.pop()
        return False

    # 剪枝：总体积
    if sum(items) > nbins * cap:
        return None
    return bins if dfs(0) else None


def bin_type_of(bins, seniors):
    """由分组计算箱型计数 (a,b,c,d,e,f)。seniors: 判定集合（值）。"""
    a = b = c = d = e = f = 0
    for sm, cnt, members in bins:
        ns = sum(1 for v in members if v in seniors)
        nj = len(members) - ns
        if ns == 2: a += 1
        elif ns == 1 and nj == 1: b += 1
        elif ns == 1: c += 1
        elif ns == 0 and nj == 3: d += 1
        elif ns == 0 and nj == 2: e += 1
        elif ns == 0 and nj == 1: f += 1
        else: return None  # 不合法型（如 SSJ）
    return (a, b, c, d, e, f)


# ================================================================ E3: p<K
def e3_pk():
    print('==== E3: p<K 冗余性/必要性 ====')
    print('分析结论：p<K 被 pair{jj} + fs(q1=j_jj) + sk+q1<=K 蕴含（p <= s_jj+q1 <= K）。')
    print('数值验证：全 LP 与去 p<K 的 LP 结论一致性（m=6..8 全 cnt 全 k）：')
    bad = 0
    for m in range(6, 9):
        cnts = bin_count_solutions(m)
        for k in range(1, m):
            for cnt in cnts:
                A1, b1, t1, n1, v1 = build_p2(m, cnt, k)
                A2, b2, t2, n2, v2 = build_p2(m, cnt, k, drop=('p<K',))
                r1 = float_cert(A1, b1, t1) is not None
                r2 = float_cert(A2, b2, t2) is not None
                if r1 != r2:
                    bad += 1
                    print(f'  ✗ m={m} k={k} cnt={cnt}: 全={r1} 去p<K={r2}')
    print(f'  结论：{"全部一致（p<K 不改变可行性 ⟹ 冗余但合法）" if bad == 0 else f"{bad} 处不一致!"}')
    # 蕴含链的正面验证：无 bins、无 p<K 的可行点必须仍满足 p<K
    print('蕴含链正面验证（无 bins 无 p<K 可行点上 p - K 的值，应 <= ~0）：')
    for m in [6, 7]:
        nS = m - 1
        cnt0 = (0, 0, nS, 0, 0, 0)  # cnt 仅影响 bins，此处 bins 全删
        for k in [1, m // 2]:
            A, bc, bt, names, nv = build_p2(m, cnt0, k, drop=('p<K', 'SS', 'SJ', 'JJJ', 'JJ'))
            tl = (m - 1) / (4 * (m - 2))
            worst = -9
            for t0 in np.linspace(tl + 0.002, 1 / 3, 5):
                # max p - 5(am+q1)/4
                obj = np.zeros(nv); obj[0] = 1.0
                obj[2 + 2 * nS] = -1.25; obj[2 + 2 * nS + 1] = -1.25
                x, val = primal_feasible(A, bc, bt, t0, nv, obj=obj)
                if x is not None:
                    worst = max(worst, val)
            print(f'  m={m} k={k}: max(p-K) = {worst:.6f}  {"✓ <=0 蕴含成立" if worst <= 1e-6 else "✗ >0!"}')


# ================================================================ E4: pocket3 y>=1-2t
def e4_ybound():
    print('==== E4: pocket3 的 y>=1-2t 消融 ====')
    print('扫描 去 y>=1-2t 后 (m x k) 可行性（float 证书/原LP逐 t 判定）：')
    for m in range(4, 13):
        row = []
        for k in range(1, m):
            A, bc, bt, names, nv = build_p3(m, k, drop=('y>=1-2t',))
            y = float_cert(A, bc, bt)
            if y is not None:
                row.append('CERT')
                continue
            # 常数证书不存在：逐 t 判原 LP 可行性
            tl = m / (4 * (m - 1))
            feas = False
            for t0 in np.linspace(tl + 0.001, 1 / 3, 8):
                x, _ = primal_feasible(A, bc, bt, t0, nv)
                if x is not None:
                    feas = True
                    break
            row.append('FEAS' if feas else 'inf/t')
        print(f'  m={m}: {row}')
    print('提取 m=6 k=1 见证点（去 y>=1-2t，验证 y<1-2t 且其余约束全满足）：')
    m, k = 6, 1
    A, bc, bt, names, nv = build_p3(m, k, drop=('y>=1-2t',))
    tl = m / (4 * (m - 1))
    for t0 in np.linspace(tl + 0.001, 1 / 3, 8):
        x, _ = primal_feasible(A, bc, bt, t0, nv)
        if x is None:
            continue
        nS = m - 1
        xv, yv, zv = x[0], x[1], x[2]
        print(f'  t0={t0:.4f}: x={xv:.4f} y={yv:.4f} z={zv:.4f}  ℓ0+t={xv+yv+zv+t0:.4f}')
        print(f'    y vs 1-2t: {yv:.4f} vs {1-2*t0:.4f}  {"违反 y>1-2t ✓（约束承重）" if yv < 1-2*t0-1e-9 else "未违反"}')
        s = x[3:3+nS]; j = x[3+nS:3+2*nS]; am, q1 = x[3+2*nS], x[3+2*nS+1]
        print(f'    s={np.round(s,4)} j={np.round(j,4)} am={am:.4f} q1={q1:.4f} L={am+q1:.4f} K={1.25*(am+q1):.4f}')
        # 全约束残差
        viol = 0.0
        for i in range(len(A)):
            lhs = sum(float(A[i][j2]) * x[j2] for j2 in range(nv))
            rhs = float(bc[i]) + float(bt[i]) * t0
            viol = min(viol, rhs - lhs)
        print(f'    全约束最小松弛: {viol:.2e}')
        break


# ================================================================ E4b: pocket3 见证点装箱检验
def e4b_pack():
    print('==== E4b: pocket3 去 y>=1-2t 的可行点能否装箱（m 箱 cap1 <=3件）？====')
    print('若能装箱且 y<1-2t：该点=角落合法候选被 y>=1-2t 单独排除 ⟹ 约束过强（反例级证据）。')
    npack_y = npack_total = 0
    for m in [6, 7, 8]:
        nS = m - 1
        tl = m / (4 * (m - 1))
        for k in range(1, m):
            A, bc, bt, names, nv = build_p3(m, k, drop=('y>=1-2t',))
            for t0 in np.linspace(tl + 0.001, 1 / 3, 6):
                for obj in [None, 'maxz']:
                    o = None
                    if obj == 'maxz':
                        o = np.zeros(nv); o[2] = 1.0
                    x, _ = primal_feasible(A, bc, bt, t0, nv, obj=o)
                    if x is None:
                        continue
                    xv, yv, zv = x[0], x[1], x[2]
                    s = x[3:3 + nS]; j = x[3 + nS:3 + 2 * nS]
                    items = [F(str(v)).limit_denominator(10**6)
                             for v in [xv, yv, zv] + list(s) + list(j) + [t0]]
                    bins = pack_exact(items, m)
                    if bins is None:
                        continue
                    npack_total += 1
                    if yv < 1 - 2 * t0 - 1e-9:
                        npack_y += 1
                        if npack_y <= 3:
                            print(f'  ★ m={m} k={k} t={t0:.4f}: 可装箱且 y={yv:.4f} < 1-2t={1-2*t0:.4f}!')
                            print(f'      x={xv:.4f} y={yv:.4f} z={zv:.4f} ℓ0+t={xv+yv+zv+t0:.4f}')
                            print(f'      s={np.round(s,4)} j={np.round(j,4)}')
    print(f'  汇总：可装箱点 {npack_total} 个，其中违反 y>1-2t 的 {npack_y} 个。')


# ================================================================ E5/E6: 消融承重
def e56_ablate():
    print('==== E5/E6: j<=2t、s>=1-2t 消融承重检验（口袋2, m=6..7 全 cnt 全 k）====')
    for tag, drop in [('去j<=2t', ('j<=2t',)), ('去s>=1-2t', ('s>=1-2t',))]:
        nchange = 0
        for m in [6, 7]:
            cnts = bin_count_solutions(m)
            for k in range(1, m):
                base_ok = all(float_cert(*build_p2(m, cnt, k)[:3]) is not None for cnt in cnts)
                abl_ok = all(float_cert(*build_p2(m, cnt, k, drop=drop)[:3]) is not None for cnt in cnts)
                if base_ok != abl_ok:
                    nchange += 1
                    print(f'  {tag} m={m} k={k}: 全约束INF -> 消融后 {"仍INF" if abl_ok else "FEAS"}')
        print(f'  {tag}: {"全约束INF在所有测试点被翻转成FEAS的次数: " + str(nchange) + "（>0 ⟹ 该约束承重）" if nchange else "所有测试点结论不变（此处不承重）"}')


# ================================================================ E7: pocket3 firststep 机组
def e7_firststep():
    print('==== E7: pocket3 去整个 firststep 机组（fs/q1<=jjj/sk+q1<=K/nofit）====')
    drop = ('fs_', 'q1<=j', 'sk+q1<=K', 'nofit')
    for m in range(4, 11):
        row = []
        for k in range(1, m):
            A, bc, bt, names, nv = build_p3(m, k, drop=drop)
            y = float_cert(A, bc, bt)
            if y is not None:
                row.append('CERT')
                continue
            tl = m / (4 * (m - 1))
            feas = False
            for t0 in np.linspace(tl + 0.001, 1 / 3, 8):
                x, _ = primal_feasible(A, bc, bt, t0, nv)
                if x is not None:
                    feas = True
                    break
            row.append('FEAS' if feas else 'inf/t')
        print(f'  m={m}: {row}')


# ================================================================ E2: MG=0 边界
def e2_boundary():
    print('==== E2: MG=0 边界 max(p+t)（口袋2）/ max(ℓ0+t)（口袋3）====')
    print('-- 口袋2（去 danger 与 pin，t∈[窗,1/3]，max p+t；分别含/不含 bins）--')
    for m in [4, 5, 6, 7, 8, 10, 12]:
        nS = m - 1
        tl = (m - 1) / (4 * (m - 2))
        # 无 bins：cnt 任意
        A, bc, bt, names, nv = build_p2(m, (0, 0, nS, 0, 0, 0), 1, drop=('danger', 'SS', 'SJ', 'JJJ', 'JJ'), mg=F(0))
        x, val = max_with_free_t(A, bc, bt, nv, [0, 1], tl, 1 / 3)
        if val is None:
            print(f'  m={m} 无bins: 窗口/模型为空（m=4 窗口为空属预期）')
        else:
            print(f'  m={m} 无bins: max(p+t) = {val:.6f}  (5/4={1.25})  {"<=5/4 ✓" if val <= 1.25 + 1e-9 else "✗ 超出!"}')
        # 含 bins：对每个 cnt、k
        if tl >= 1 / 3:
            continue
        worst = -9; warg = None
        for k in range(1, m):
            for cnt in bin_count_solutions(m):
                A, bc, bt, names, nv = build_p2(m, cnt, k, drop=('danger',), mg=F(0))
                x, val = max_with_free_t(A, bc, bt, nv, [0, 1], tl, 1 / 3)
                if val is not None and val > worst:
                    worst, warg = val, (k, cnt)
        print(f'        含bins: max(p+t) = {worst:.6f} @ k,cnt={warg}  {"<=5/4 ✓" if worst <= 1.25 + 1e-9 else "✗ 超出!"}')
    print('-- 口袋3（去 danger 与 pin，t∈[窗,1/3]，max ℓ0+t）--')
    for m in [4, 5, 6, 8, 10, 12]:
        tl = m / (4 * (m - 1))
        worst = -9; warg = None
        for k in range(1, m):
            A, bc, bt, names, nv = build_p3(m, k, drop=('danger',), mg=F(0))
            # pocket3 中 t 只在 RHS：对每个 t0 网格 max(x+y+z) + t0
            for t0 in np.linspace(tl, 1 / 3, 13):
                obj = np.zeros(nv); obj[0] = obj[1] = obj[2] = 1.0
                xx, vv = primal_feasible(A, bc, bt, t0, nv, obj=obj)
                if xx is not None and vv + t0 > worst:
                    worst, warg = vv + t0, (k, round(float(t0), 4))
        print(f'  m={m}: max(ℓ0+t) = {worst:.6f} @ (k,t0)={warg}  {"<=5/4 ✓" if worst <= 1.25 + 1e-9 else "✗ 超出!"}')


# ================================================================ E1: 装箱固定分组
def e1_bins():
    print('==== E1: 装箱固定分组 w.l.o.g. 检验（口袋2 无bins LP + 精确装箱）====')
    print('对每个 (m,k)：无bins LP 在窗口 t 网格上找可行点 -> Fraction 装箱 DFS（m-1箱, cap 1, <=3件）。')
    print('若可行点可装箱：该点=松弛下合法角落候选，但被所有固定分组 LP 排除 ⟹ unsound 洞。')
    npack = 0
    for m in [6, 7, 8]:
        nS = m - 1
        tl = (m - 1) / (4 * (m - 2))
        for k in range(1, m):
            A, bc, bt, names, nv = build_p2(m, (0, 0, nS, 0, 0, 0), k,
                                            drop=('SS', 'SJ', 'JJJ', 'JJ'))
            hits = []
            for t0 in np.linspace(tl + 0.002, 1 / 3, 6):
                # 多个目标采样顶点：默认可行解 + 最大化 p
                pts = []
                x, _ = primal_feasible(A, bc, bt, t0, nv)
                if x is not None:
                    pts.append(x)
                    obj = np.zeros(nv); obj[0] = 1.0
                    x2, _ = primal_feasible(A, bc, bt, t0, nv, obj=obj)
                    if x2 is not None:
                        pts.append(x2)
                for x in pts:
                    p, tt = x[0], x[1]
                    s = x[2:2 + nS]; j = x[2 + nS:2 + 2 * nS]
                    items = [F(str(v)).limit_denominator(10**6) for v in list(s) + list(j) + [tt]]
                    seniors = set(F(str(v)).limit_denominator(10**6) for v in s)
                    bins = pack_exact(items, m - 1)
                    if bins is not None:
                        bt_ = bin_type_of(bins, seniors)
                        npack += 1
                        hits.append((t0, p, bt_, [float(v) for v in s], [float(v) for v in j]))
            for t0, p, bt_, s, j in hits[:1]:
                print(f'  ★ m={m} k={k} t={t0:.4f}: 可行点可装箱! p={p:.4f} 箱型(SS,SJ,S,JJJ,JJ,J)={bt_}')
                print(f'      s={np.round(s,4)}')
                print(f'      j={np.round(j,4)}')
            if hits:
                print(f'    m={m} k={k}: 共 {len(hits)} 个可装箱可行点')
    print(f'  汇总：可装箱可行点 {npack} 个。'
          + ('⟹ 固定分组 LP 对这些点全部 INFEASIBLE 但松弛可行 ⟹ 洞!' if npack else '⟹ 未发现可装箱可行点，固定分组在本样本内未证伪。'))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if cmd in ('all', 'e3'): e3_pk()
    if cmd in ('all', 'e4'): e4_ybound()
    if cmd in ('all', 'e4b'): e4b_pack()
    if cmd in ('all', 'e56'): e56_ablate()
    if cmd in ('all', 'e7'): e7_firststep()
    if cmd in ('all', 'e2'): e2_boundary()
    if cmd in ('all', 'e1'): e1_bins()
