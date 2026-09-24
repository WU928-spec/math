"""口袋1子情形B：修正编码 + 装箱箱型枚举 LP + 精确常数 Farkas 证书。

修正编码（同 farkas_fixed.py，best-fit 最满优先: q1 填放得下的【最大】senior 机）:
  srt 升序 s_0<=...<=s_{nS-1}; nofit 在较大侧 i>jj: s_i+q1>K;
  fs_j: j_jj>=j_i (j_jj=q1=最大 junior); sk+q1<=K 在 jj。
角落语义: M0={x,y} (y>1-2t 初始大任务, x>=t 后至, x<=y), 他机 2 件 {s_i,j_i}
  (s_i>1-2t, j_i in [t,2t)), danger x+y+t>5/4, mach s_i+j_i>x+y, OPT=1。
装箱: 2m+1 件 (大: y + m-1 senior; 小: x + t + m-1 junior, 均 in [t,2t)) 装 m 箱。
  大+2小>1、3大>1、2大1小>1 均不可行 => 箱型 BB/BJ/B/JJJ/JJ/J。
  计数 (a,b,c,d,e,f): 2a+b+c=m; b+3d+2e+f=m+1; a+b+c+d+e+f=m
  => a=d+e+f, d=1+c+f>=1, b=m-2-3c-2e-4f>=0。参数 (c,e,f)。
t 做成钉住变量 tv (tv<=t / tv>=t, bt=±1) 进装箱行; t 只出现在右端 => 常数证书。
"""
from fractions import Fraction as F
import numpy as np
from scipy.optimize import linprog
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farkas_fixed import float_cert, rationalize_verify, MG


# ---------------- 箱型计数 (c,e,f) 参数化 ----------------
def bin_counts(m):
    """合法计数向量 [(a,b,c,d,e,f), ...]，参数 (c,e,f)>=0, b=m-2-3c-2e-4f>=0。"""
    out = []
    for c in range((m - 2) // 3 + 1):
        for e in range((m - 2 - 3 * c) // 2 + 1):
            for f in range((m - 2 - 3 * c - 2 * e) // 4 + 1):
                d = 1 + c + f
                a = d + e + f
                b = m - 2 - 3 * c - 2 * e - 4 * f
                cnt = (a, b, c, d, e, f)
                assert 2 * a + b + c == m
                assert b + 3 * d + 2 * e + f == m + 1
                assert a + b + c + d + e + f == m
                assert d >= 1
                out.append(cnt)
    return out


# ---------------- LP 构造 ----------------
def build_p1b(m, cnt=None, jj=None, use_packing=True, use_vol=False,
              use_danger=True, use_mach=True, use_narrow=True, use_kcap=True,
              use_s2=False, jj2=None, use_land2=True, use_fit=True,
              use_order=False, h=None, use_ord=True, row_names=None,
              q1m0=False, hy=None):
    """变量 [x, y, s_0..s_{nS-1}, j_0..j_{nS-1}, a_m, q_1, t_var, (q_2)]。
    row_names: 若非 None, 只构造这些名字的行（支撑行快速精确验证）。
    jj=None -> 不含 firststep；use_s2 -> 加二步动态（需 jj）；jj2 -> 加 S3 落机。
    q1m0/hy: q₁→M₀ 分支（M₀={y,q₁}）——x=q₁ 双向、y+q1≤K、am≤y、
    后缀 i≥nS−hy nofit（s_i+q₁>K）、前缀 i<nS−hy s_i≤y；需 jj=None；hy 枚举 0..nS 完备。
    返回 A, bc, bt, names, nv。"""
    nS = m - 1
    nv = 2 + 2 * nS + 3 + (1 if use_s2 else 0)
    ix, iy = 0, 1
    def vs(i): return 2 + i
    def vj(i): return 2 + nS + i
    iam, iq1, it = 2 + 2 * nS, 2 + 2 * nS + 1, 2 + 2 * nS + 2
    iq2 = 2 + 2 * nS + 3
    A, bc, bt, names = [], [], [], []

    def con(row, c0, c1, nm):
        if row_names is not None and nm not in row_names:
            return
        A.append([F(z) for z in row]); bc.append(F(c0)); bt.append(F(c1)); names.append(nm)

    def zero(): return [F(0)] * nv

    # t 变量钉到参数 t
    r = zero(); r[it] = 1;  con(r, 0, 1, 'tv<=t')
    r = zero(); r[it] = -1; con(r, 0, -1, 'tv>=t')
    # 角落约束（同 pocket13_fixed.build_p1f）
    r = zero(); r[ix] = 1; r[iy] = -1; con(r, 0, 0, 'x<=y')
    r = zero(); r[ix] = -1; con(r, 0, -1, 'x>=t')
    r = zero(); r[iy] = -1; con(r, -1 - MG, 2, 'y>=1-2t')
    r = zero(); r[iy] = 1; con(r, 1, 0, 'y<=1')
    if use_danger:
        r = zero(); r[ix] = -1; r[iy] = -1; con(r, -F(5, 4), 1, 'danger')
    for i in range(nS):
        r = zero(); r[vs(i)] = -1; con(r, -1 - MG, 2, f's{i}>=1-2t')
        r = zero(); r[vs(i)] = 1; con(r, 1, 0, f's{i}<=1')
        if use_narrow:
            r = zero(); r[vj(i)] = 1; con(r, -MG, 2, f'j{i}<=2t')
            r = zero(); r[vj(i)] = -1; con(r, 0, -1, f'j{i}>=t')
        if use_mach:
            r = zero(); r[ix] = 1; r[iy] = 1; r[vs(i)] = -1; r[vj(i)] = -1
            con(r, -MG, 0, f'mach{i}>M0')
        if use_kcap:
            r = zero(); r[vj(i)] = 1; r[iam] = -1; con(r, 0, 0, f'j{i}<=am')
            r = zero(); r[iam] = 1; r[vs(i)] = -1; con(r, 0, 0, f'am<=s{i}')
            r = zero(); r[vj(i)] = 1; r[iq1] = -1; con(r, 0, 0, f'j{i}<=q1')
    if use_kcap:
        r = zero(); r[iam] = -1; con(r, 0, -1, 't<=am')
        r = zero(); r[iam] = 1; r[iq1] = 1; con(r, 1, 0, 'L<=1')
    for i in range(nS - 1):
        r = zero(); r[vs(i)] = 1; r[vs(i + 1)] = -1; con(r, 0, 0, f'srt{i}')
    if jj is not None:
        for i in range(nS):
            if i != jj:
                r = zero(); r[vj(jj)] = -1; r[vj(i)] = 1; con(r, 0, 0, f'fs_j{i}')
        r = zero(); r[iq1] = 1; r[vj(jj)] = -1; con(r, 0, 0, f'q1<=j{jj}')
        r = zero(); r[vs(jj)] = 4; r[iam] = -5; r[iq1] = -1; con(r, 0, 0, 'sk+q1<=K')
        for i in range(jj + 1, nS):
            r = zero(); r[vs(i)] = -4; r[iam] = 5; r[iq1] = 1; con(r, -MG, 0, f'nofit{i}')
    if use_s2:
        assert jj is not None
        # (S1) q2 = max{j_i : i≠jj}（上界代理）; q2<=q1; t<=q2
        for i in range(nS):
            if i != jj:
                r = zero(); r[vj(i)] = 1; r[iq2] = -1; con(r, 0, 0, f'j{i}<=q2')
        r = zero(); r[iq2] = 1; r[iq1] = -1; con(r, 0, 0, 'q2<=q1')
        r = zero(); r[it] = 1; r[iq2] = -1; con(r, 0, 0, 't<=q2')
        # (S2) jj 机已 2 件放不下 q2: s_jj+q1+q2>K ⟺ -4s_jj+5a_m+q1-4q2<=-MG
        r = zero(); r[vs(jj)] = -4; r[iam] = 5; r[iq1] = 1; r[iq2] = -4
        con(r, -MG, 0, 'jj_nofit_q2')
        if jj2 is not None:
            assert jj2 != jj
            if use_fit:
                # fit at jj2: s_jj2+q2<=K, K=(5/4)(a_m+q1) 固定 cap（非 K2）
                #   4s_jj2+4q_2 <= 5a_m+5q_1  ⟺  4s_jj2 - 5a_m - 5q_1 + 4q_2 <= 0
                r = zero(); r[vs(jj2)] = 4; r[iam] = -5; r[iq1] = -5; r[iq2] = 4
                con(r, 0, 0, 's_jj2+q2<=K')
            if use_land2:
                # nofit2: i>jj2 且 i≠jj（load s_i）放不下 q_2
                for i in range(jj2 + 1, nS):
                    if i != jj:
                        r = zero(); r[vs(i)] = -4; r[iam] = 5; r[iq2] = 1
                        con(r, -MG, 0, f'nofit2_{i}')
                # j_jj2 = q_2：j_jj2>=j_i ∀i≠jj,jj2 且 q_2<=j_jj2
                for i in range(nS):
                    if i != jj and i != jj2:
                        r = zero(); r[vj(jj2)] = -1; r[vj(i)] = 1; con(r, 0, 0, f'fs2_j{i}')
                r = zero(); r[iq2] = 1; r[vj(jj2)] = -1; con(r, 0, 0, f'q2<=j{jj2}')
    if use_vol:
        r = zero(); r[ix] = 1; r[iy] = 1; r[it] = 1
        for i in range(nS):
            r[vs(i)] = 1; r[vj(i)] = 1
        con(r, m, 0, 'vol<=m')
    if use_packing:
        assert cnt is not None
        a, b, c, d, e, f = cnt
        bigs = [vs(i) for i in range(nS)] + [iy]      # senior 升序, y 最后
        smls = [vj(i) for i in range(nS)] + [ix, it]  # junior, x, tv
        def cap(idxs, nm):
            r = zero()
            for u in idxs: r[u] = 1
            con(r, 1, 0, nm)
        for k in range(a):
            cap([bigs[2 * k], bigs[2 * k + 1]], f'BB{k}')
        for k in range(b):
            cap([bigs[2 * a + k], smls[k]], f'BJ{k}')
        si = b
        for k in range(d):
            cap([smls[si], smls[si + 1], smls[si + 2]], f'JJJ{k}'); si += 3
        for k in range(e):
            cap([smls[si], smls[si + 1]], f'JJ{k}'); si += 2
        assert si + f == m + 1, (si, f, m, cnt)
    if use_order:
        # 保序引理 h 枚举（同 order_step.py）: top=nS−h 为低端区
        # 低端区 s_i<=K−q1 ⟺ 4s_i−5a_m−q1<=0; 高端区 s_i>K−q1 ⟺ −4s_i+5a_m+q1<=−MG
        # 低端区 junior 升序 j_i<=j_{i+1}（引理推论）; h=nS 时无任何新约束
        assert h is not None and 0 <= h <= nS
        top = nS - h
        for i in range(top):
            r = zero(); r[vs(i)] = 4; r[iam] = -5; r[iq1] = -1; con(r, 0, 0, f'lowzone{i}')
        for i in range(top, nS):
            r = zero(); r[vs(i)] = -4; r[iam] = 5; r[iq1] = 1; con(r, -MG, 0, f'hizone{i}')
        if use_ord:
            for i in range(top - 1):
                r = zero(); r[vj(i)] = 1; r[vj(i + 1)] = -1; con(r, 0, 0, f'ord{i}')
    if q1m0:
        # q₁→M₀ 分支（LP_CONSTRAINTS §7, a3 审计）：q₁ 落 M₀={y,q₁}
        assert jj is None and hy is not None and 0 <= hy <= nS
        r = zero(); r[ix] = 1; r[iq1] = -1; con(r, 0, 0, 'x<=q1')
        r = zero(); r[ix] = -1; r[iq1] = 1; con(r, 0, 0, 'x>=q1')
        # y+q1<=K ⟺ 4y-5am-q1<=0
        r = zero(); r[iy] = 4; r[iam] = -5; r[iq1] = -1; con(r, 0, 0, 'y+q1<=K')
        # am<=y（y 初始件 >= p_m）
        r = zero(); r[iam] = 1; r[iy] = -1; con(r, 0, 0, 'am<=y')
        top_y = nS - hy
        for i in range(top_y, nS):
            # 后缀（比 y 满）放不下 q₁: s_i+q1>K ⟺ -4s_i+5am+q1<=-MG
            r = zero(); r[vs(i)] = -4; r[iam] = 5; r[iq1] = 1; con(r, -MG, 0, f'nofitM{i}')
        for i in range(top_y):
            # 前缀 s_i<=y（否则比 y 满却可能放下 q₁, best-fit 不落 M₀）
            r = zero(); r[vs(i)] = 1; r[iy] = -1; con(r, 0, 0, f'le_y{i}')
    return A, bc, bt, names, nv


def lp_feas_point(m, cnt=None, jj=None, t_val=None, **kw):
    """固定参数 t 解 LP；返回 (status, x)。"""
    A, bc, bt, _, nv = build_p1b(m, cnt, jj, **kw)
    Af = np.array([[float(x) for x in row] for row in A])
    bcf = np.array([float(x) for x in bc]); btf = np.array([float(x) for x in bt])
    if t_val is None:
        res = linprog(c=np.zeros(nv), A_eq=Af, b_eq=bcf, bounds=(None, None), method='highs')
    else:
        res = linprog(c=np.zeros(nv), A_ub=Af, b_ub=bcf + btf * t_val,
                      bounds=(None, None), method='highs')
    return res.status, (res.x if res.status == 0 else None)


def packs_exact(items, m, cap=1.0):
    """精确回溯装箱测试。"""
    items = sorted(items, reverse=True)
    if items[0] > cap + 1e-9:
        return False
    loads = [0.0] * m

    def dfs(i):
        if i == len(items):
            return True
        w = items[i]
        seen = set()
        for b in range(m):
            if loads[b] in seen:
                continue
            if loads[b] + w <= cap + 1e-9:
                seen.add(loads[b])
                loads[b] += w
                if dfs(i + 1):
                    loads[b] -= w
                    return True
                loads[b] -= w
            if loads[b] < 1e-9:
                break
        return False
    return dfs(0)


def extract_hole(m, cnt, jj, jj2=None, use_order=False, h=None,
                 q1m0=False, hy=None, n_t=49, t_lo=None, t_hi=1.0 / 3 - 0.004):
    """为可行 (m,cnt[,jj[,jj2[,h[,hy]]]]) 提取可行点: 扫 t, 解 LP, 取角落点, 测精确装箱。"""
    nS = m - 1
    it_idx = 2 + 2 * nS + 2
    tl = t_lo if t_lo is not None else max(0.05, (m - 1) / (4 * (m - 2)) - 0.06)
    for t in np.linspace(tl, t_hi, n_t):
        st, x = lp_feas_point(m, cnt, jj, t_val=t, use_s2=True, jj2=jj2,
                              use_order=use_order, h=h, q1m0=q1m0, hy=hy)
        if st != 0:
            continue
        items = [x[0], x[1], x[it_idx]] + list(x[2:2 + nS]) + list(x[2 + nS:2 + 2 * nS])
        return dict(t=t, x=x[0], y=x[1], tv=x[it_idx],
                    am=x[2 + 2 * nS], q1=x[2 + 2 * nS + 1],
                    s=list(x[2:2 + nS]), j=list(x[2 + nS:2 + 2 * nS]),
                    packs=packs_exact(items, m))
    return None


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'scan'
    t0 = time.time()

    if cmd == 'scan':
        print('== 阶段A: 装箱+角落(无 firststep), m=4..12 全 cnt ==')
        holes1 = {}   # m -> [cnt]
        cert_out = []
        cert_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 'pocket1b_certificates.txt')
        total_cert = 0
        for m in range(4, 13):
            cnts = bin_counts(m)
            nc = 0; holes = []
            for cnt in cnts:
                A, bc, bt, names, _ = build_p1b(m, cnt, jj=None)
                yf = float_cert(A, bc, bt)
                if yf is None:
                    holes.append(cnt)
                    continue
                y, N = rationalize_verify(A, bc, bt, yf)
                if y is not None:
                    nc += 1
                    cert_out.append((m, cnt, None, names, y, N))
                else:
                    holes.append(cnt)
            holes1[m] = holes
            total_cert += nc
            print(f'  m={m}: {len(cnts)} cnt, 精确证书 {nc}, 洞 {len(holes)}'
                  + (f' {holes}' if holes else ''), flush=True)
        print(f'  小计 {total_cert} 证书 ({time.time()-t0:.0f}s)')

        print('\n== 阶段B: 洞 + firststep (jj=0..nS-1) ==')
        holes2 = {}   # (m,cnt) -> [jj open]
        nb_cert = 0; nb_tot = 0
        for m in range(4, 13):
            for cnt in holes1[m]:
                nS = m - 1
                open_jj = []
                for jj in range(nS):
                    nb_tot += 1
                    A, bc, bt, names, _ = build_p1b(m, cnt, jj=jj)
                    yf = float_cert(A, bc, bt)
                    if yf is None:
                        open_jj.append(jj)
                        continue
                    y, N = rationalize_verify(A, bc, bt, yf)
                    if y is None:
                        open_jj.append(jj)
                    else:
                        nb_cert += 1
                        cert_out.append((m, cnt, jj, names, y, N))
                if open_jj:
                    holes2[(m, cnt)] = open_jj
                    print(f'  洞 m={m} cnt={cnt}: 开放 jj={open_jj}', flush=True)
        if not holes2:
            print('  无洞：全部 (m,cnt,jj) 闭合 ✓')
        else:
            print(f'  共 {len(holes2)} 个 (m,cnt) 有开放 jj;  阶段B证书 {nb_cert}/{nb_tot}')
        print(f'  ({time.time()-t0:.0f}s)')

        print('\n== 阶段C/D: 二步动态 (S1+S2, 枚举 jj2) ==')
        holes3 = {}   # (m,cnt,jj,jj2) feasible
        nd_cert = 0; nd_tot = 0
        for (m, cnt), open_jj in holes2.items():
            nS = m - 1
            for jj in open_jj:
                # C: S1+S2 only
                A, bc, bt, names, _ = build_p1b(m, cnt, jj=jj, use_s2=True)
                yf = float_cert(A, bc, bt)
                if yf is not None:
                    y, N = rationalize_verify(A, bc, bt, yf)
                    if y is not None:
                        nd_cert += 1; nd_tot += 1
                        cert_out.append((m, cnt, jj, names, y, N, 'S12'))
                        print(f'  S1+S2 闭合 m={m} cnt={cnt} jj={jj}', flush=True)
                        continue
                nd_tot += 1
                for jj2 in range(nS):
                    if jj2 == jj:
                        continue
                    A, bc, bt, names, _ = build_p1b(m, cnt, jj=jj, use_s2=True, jj2=jj2)
                    yf = float_cert(A, bc, bt)
                    if yf is None:
                        holes3[(m, cnt, jj, jj2)] = True
                        print(f'  洞(二步) m={m} cnt={cnt} jj={jj} jj2={jj2}', flush=True)
                        continue
                    y, N = rationalize_verify(A, bc, bt, yf)
                    if y is None:
                        holes3[(m, cnt, jj, jj2)] = True
                        print(f'  洞(二步,证书未过) m={m} cnt={cnt} jj={jj} jj2={jj2}', flush=True)
                    else:
                        nd_cert += 1
                        cert_out.append((m, cnt, jj, names, y, N, f'jj2={jj2}'))
        if not holes3:
            print(f'  二步闭合全部洞;  阶段C/D证书 {nd_cert}  ({time.time()-t0:.0f}s)')
        else:
            print(f'  残留洞 {len(holes3)} 个;  阶段C/D证书 {nd_cert}/{nd_tot}  ({time.time()-t0:.0f}s)')

        # 证书落盘
        with open(cert_file, 'w') as fh:
            for rec in cert_out:
                m, cnt, jj, names, y, N = rec[:6]
                tag = f'jj={jj}' if jj is not None else 'nofs'
                if len(rec) > 6:
                    tag += ' ' + rec[6]
                fh.write(f'=== m={m} cnt={cnt} {tag} (den<={N}) ===\n')
                for i in range(len(y)):
                    if y[i] != 0:
                        fh.write(f'  {names[i]}: {y[i]}\n')
        print(f'  证书已写入 {cert_file}（{len(cert_out)} 份）')

        print('\n== 消融 + sanity ==')
        print('  -- 闭合代表 A: m=6 cnt=(2,2,0,1,1,0), 无 firststep --')
        m = 6
        cnt = (2, 2, 0, 1, 1, 0)
        for nm, kw in [('完整', {}),
                       ('去danger', dict(use_danger=False)),
                       ('去mach', dict(use_mach=False)),
                       ('去narrow', dict(use_narrow=False)),
                       ('去kcap', dict(use_kcap=False)),
                       ('去装箱(仅vol)', dict(use_packing=False, use_vol=True))]:
            A, bc, bt, _, _ = build_p1b(m, cnt, jj=None, **kw)
            yf = float_cert(A, bc, bt)
            print(f'   {nm:14s}: {"INFEASIBLE(有证书)" if yf is not None else "FEASIBLE(必要)"}',
                  flush=True)
        print('  -- 洞代表 B: m=6 cnt=(1,4,0,1,0,0), jj=0 (firststep 关闭它) --')
        cntB = (1, 4, 0, 1, 0, 0)
        for nm, kw in [('完整(jj=0)', {}),
                       ('去firststep(jj=None)', dict(use_fs_off=True)),
                       ('去danger', dict(use_danger=False))]:
            if kw.pop('use_fs_off', False):
                A, bc, bt, _, _ = build_p1b(m, cntB, jj=None)
            else:
                A, bc, bt, _, _ = build_p1b(m, cntB, jj=0, **kw)
            yf = float_cert(A, bc, bt)
            print(f'   {nm:22s}: {"INFEASIBLE(有证书)" if yf is not None else "FEASIBLE"}',
                  flush=True)
        st, _ = lp_feas_point(6, cnt, None, use_danger=False, t_val=0.30)
        print(f'   sanity 去danger@t=0.30 linprog: {"feasible ✓" if st == 0 else "INFEASIBLE ✗ 假阴性!"}')

        print('  -- 二步代表 C: m=12 真洞 cnt=(2,8,0,1,1,0), jj=7, jj2=0 --')
        m, cntC, jjC, jj2C = 12, (2, 8, 0, 1, 1, 0), 7, 0
        for nm, kw in [('完整(S1+S2+S3)', dict(use_s2=True, jj2=jj2C)),
                       ('去nofit2+fs2(留fit)', dict(use_s2=True, jj2=jj2C, use_land2=False)),
                       ('去S3(仅S1+S2)', dict(use_s2=True)),
                       ('去danger', dict(use_s2=True, jj2=jj2C, use_danger=False))]:
            A, bc, bt, _, _ = build_p1b(m, cntC, jj=jjC, **kw)
            yf = float_cert(A, bc, bt)
            print(f'   {nm:24s}: {"INFEASIBLE(有证书)" if yf is not None else "FEASIBLE"}',
                  flush=True)

    elif cmd == 's2':
        # m=12 真洞定向二步测试 + 证书
        m, cnt, jj = 12, (2, 8, 0, 1, 1, 0), 7
        nS = m - 1
        print('== m=12 真洞 + 二步动态 ==')
        A, bc, bt, _, _ = build_p1b(m, cnt, jj=jj, use_s2=True)
        print(f'  S1+S2 only: {"INFEASIBLE" if float_cert(A, bc, bt) is not None else "FEASIBLE（洞仍在）"}')
        certs = []
        nopen = 0
        for jj2 in range(nS):
            if jj2 == jj:
                continue
            A, bc, bt, names, _ = build_p1b(m, cnt, jj=jj, use_s2=True, jj2=jj2)
            yf = float_cert(A, bc, bt)
            if yf is None:
                nopen += 1
                print(f'  jj2={jj2}: FEASIBLE（仍洞!）')
                continue
            y, N = rationalize_verify(A, bc, bt, yf)
            tag = f'证书 den<={N} ✓' if y is not None else '证书未通过'
            if y is None:
                nopen += 1
            else:
                certs.append((m, cnt, jj, names, y, N, f'jj2={jj2}'))
            print(f'  jj2={jj2}: INFEASIBLE {tag}')
        cf = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          'pocket1b_certificates_s2.txt')
        with open(cf, 'w') as fh:
            for rec in certs:
                mm, cc, jj_, names, y, N, tag2 = rec
                fh.write(f'=== m={mm} cnt={cc} jj={jj_} {tag2} (den<={N}) ===\n')
                for i in range(len(y)):
                    if y[i] != 0:
                        fh.write(f'  {names[i]}: {y[i]}\n')
        print(f'  闭合 {len(certs)}/{nS-1} jj2, 开放 {nopen}; 证书 -> {cf}')

    elif cmd == 'extend':
        import json
        prog = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'pocket1b_progress.jsonl')
        certf = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'pocket1b_certificates_13_20.txt')
        done = {}
        if os.path.exists(prog):
            for line in open(prog):
                r = json.loads(line)
                done[(r['m'], tuple(r['cnt']), r['stage'], r['jj'], r['jj2'], r.get('h'))] = r['status']
        fh = open(prog, 'a')
        fc = open(certf, 'a')

        def record(m, cnt, stage, jj, jj2, status, N=None, h=None):
            fh.write(json.dumps({'m': m, 'cnt': list(cnt), 'stage': stage,
                                 'jj': jj, 'jj2': jj2, 'status': status, 'N': N,
                                 'h': h}) + '\n')
            fh.flush()

        def dump_cert(m, cnt, jj, names, y, N, tag):
            fc.write(f'=== m={m} cnt={cnt} jj={jj} {tag} (den<={N}) ===\n')
            for i in range(len(y)):
                if y[i] != 0:
                    fc.write(f'  {names[i]}: {y[i]}\n')
            fc.flush()

        def try_cert(m, cnt, jj, jj2, tag):
            A, bc, bt, names, _ = build_p1b(m, cnt, jj=jj, use_s2=(jj2 != 'nos2' and tag != 'B'),
                                            jj2=(jj2 if isinstance(jj2, int) else None))
            yf = float_cert(A, bc, bt)
            if yf is None:
                return None, None
            y, N = rationalize_verify(A, bc, bt, yf)
            if y is None:
                return None, None
            dump_cert(m, cnt, jj, names, y, N, tag)
            return y, N

        m_lo, m_hi = 13, 20
        if len(sys.argv) > 2:
            m_lo, m_hi = [int(v) for v in sys.argv[2].split('-')]
        for m in range(m_lo, m_hi + 1):
            t_m0 = time.time()
            cnts = bin_counts(m)
            nA = nAh = 0
            holesB = []   # (cnt, [open jj])
            for cnt in cnts:
                kA = (m, cnt, 'A', None, None, None)
                if kA in done:
                    if done[kA] == 'hole':
                        nAh += 1
                        holesB.append(cnt)   # 缓存的洞也要进 B 阶段
                    else:
                        nA += 1
                    continue
                A, bc, bt, names, _ = build_p1b(m, cnt, jj=None)
                yf = float_cert(A, bc, bt)
                if yf is not None:
                    y, N = rationalize_verify(A, bc, bt, yf)
                    if y is not None:
                        dump_cert(m, cnt, None, names, y, N, 'nofs')
                        record(m, cnt, 'A', None, None, 'cert', N)
                        nA += 1
                        continue
                record(m, cnt, 'A', None, None, 'hole')
                nAh += 1
                holesB.append(cnt)
            # stage B
            nb_cert = nb_hole = 0
            stageC = []   # (cnt, jj) 一步洞
            for cnt in holesB:
                nS = m - 1
                open_jj = []
                for jj in range(nS):
                    kB = (m, cnt, 'B', jj, None, None)
                    if kB in done:
                        if done[kB] == 'cert':
                            nb_cert += 1
                        else:   # hole 与 nocert（无常数证书）都需二步
                            open_jj.append(jj)
                        continue
                    y, N = try_cert(m, cnt, jj, 'nos2', f'jj={jj}')
                    if y is None:
                        st, _ = lp_feas_point(m, cnt, jj, t_val=0.30)
                        record(m, cnt, 'B', jj, None, 'hole' if st == 0 else 'nocert')
                        open_jj.append(jj)
                    else:
                        record(m, cnt, 'B', jj, None, 'cert', N)
                        nb_cert += 1
                nb_hole += len(open_jj)
                for jj in open_jj:
                    stageC.append((cnt, jj))
            # stage C/D
            nd_cert = 0
            holesD = []
            for cnt, jj in stageC:
                nS = m - 1
                kC = (m, cnt, 'C', jj, None, None)
                closed = False
                if kC in done:
                    if done[kC] == 'hole':
                        pass
                    else:
                        nd_cert += 1
                        closed = True
                else:
                    A, bc, bt, names, _ = build_p1b(m, cnt, jj=jj, use_s2=True)
                    yf = float_cert(A, bc, bt)
                    if yf is not None:
                        y, N = rationalize_verify(A, bc, bt, yf)
                        if y is not None:
                            dump_cert(m, cnt, jj, names, y, N, 'S12')
                            record(m, cnt, 'C', jj, None, 'cert', N)
                            nd_cert += 1
                            closed = True
                if closed:
                    continue
                if kC not in done:
                    record(m, cnt, 'C', jj, None, 'hole')
                open_jj2 = []
                for jj2 in range(nS):
                    if jj2 == jj:
                        continue
                    kD = (m, cnt, 'D', jj, jj2, None)
                    if kD in done:
                        if done[kD] == 'hole':
                            open_jj2.append(jj2)
                        else:
                            nd_cert += 1
                        continue
                    y, N = try_cert(m, cnt, jj, jj2, f'jj={jj} jj2={jj2}')
                    if y is None:
                        record(m, cnt, 'D', jj, jj2, 'hole')
                        open_jj2.append(jj2)
                    else:
                        record(m, cnt, 'D', jj, jj2, 'cert', N)
                        nd_cert += 1
                if open_jj2:
                    holesD.append((cnt, jj, open_jj2))
            # stage E: 保序 forced 单 h=nS-1-jj（nofit i>jj + fit/srt i<=jj 强制 zone 分界）
            ne_cert = 0
            holesE = []
            for cnt, jj, open_jj2 in holesD:
                nS = m - 1
                hh = nS - 1 - jj
                for jj2 in open_jj2:
                    kE = (m, cnt, 'E', jj, jj2, hh)
                    if kE in done:
                        if done[kE] == 'cert':
                            ne_cert += 1
                        else:
                            holesE.append((cnt, jj, jj2, [hh]))
                        continue
                    A, bc, bt, names, _ = build_p1b(m, cnt, jj=jj, use_s2=True,
                                                    jj2=jj2, use_order=True, h=hh)
                    yf = float_cert(A, bc, bt)
                    if yf is not None:
                        y, N = rationalize_verify(A, bc, bt, yf)
                        if y is not None:
                            dump_cert(m, cnt, jj, names, y, N, f'jj={jj} jj2={jj2} h={hh}')
                            record(m, cnt, 'E', jj, jj2, 'cert', N, h=hh)
                            ne_cert += 1
                            continue
                    record(m, cnt, 'E', jj, jj2, 'hole', h=hh)
                    holesE.append((cnt, jj, jj2, [hh]))
            print(f'  m={m}: cnt={len(cnts)} A证书{nA}/洞{nAh}'
                  f' B证书{nb_cert}/一步洞{nb_hole} 二步证书{nd_cert}'
                  f' 保序证书{ne_cert} 残留洞{len(holesE)}'
                  + (f' {[(c,j,j2) for c,j,j2,_ in holesE]}' if holesE else ''), flush=True)
            for cnt, jj, jj2, ohh in holesE:
                h = extract_hole(m, cnt, jj, jj2=jj2, use_order=True, h=ohh[0])
                if h:
                    print(f'    洞点 m={m} cnt={cnt} jj={jj} jj2={jj2} h={ohh[0]}: t={h["t"]:.4f} '
                          f'x={h["x"]:.4f} y={h["y"]:.4f} x+y+t={h["x"]+h["y"]+h["t"]:.4f} '
                          f'packs={h["packs"]}', flush=True)
            for cnt, jj, oj in holesD if not holesE else []:
                h = extract_hole(m, cnt, jj, jj2=oj[0])
                if h:
                    print(f'    洞点 m={m} cnt={cnt} jj={jj} jj2={oj[0]}: t={h["t"]:.4f} '
                          f'x={h["x"]:.4f} y={h["y"]:.4f} x+y+t={h["x"]+h["y"]+h["t"]:.4f} '
                          f'packs={h["packs"]}', flush=True)
        fh.close(); fc.close()
        print(f'进度 {prog}')
        print(f'证书 {certf}  ({time.time()-t0:.0f}s)')

    elif cmd == 'order':
        # 保序 h 枚举杀 m=17..20 二步残留（jj2 从 jsonl D-hole 重导）
        import json
        from collections import defaultdict
        prog = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'pocket1b_progress.jsonl')
        res = defaultdict(list)
        for line in open(prog):
            r = json.loads(line)
            if r['stage'] == 'D' and r['status'] == 'hole' and 17 <= r['m'] <= 20:
                res[(r['m'], tuple(r['cnt']), r['jj'])].append(r['jj2'])
        print(f'二步残留 (m,cnt,jj) -> {len(res)} 组')
        cf = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          'pocket1b_certificates_order.txt')
        total_cert = 0; nopen = 0; first_closed = None
        with open(cf, 'w') as fo:
            for (m, cnt, jj), jj2s in sorted(res.items()):
                nS = m - 1
                for jj2 in sorted(jj2s):
                    kill = []
                    for hh in range(nS + 1):
                        A, bc, bt, names, nv = build_p1b(m, cnt, jj=jj, use_s2=True,
                                                         jj2=jj2, use_order=True, h=hh)
                        yf = float_cert(A, bc, bt)
                        if yf is not None:
                            y, N = rationalize_verify(A, bc, bt, yf)
                            if y is not None:
                                total_cert += 1
                                fo.write(f'=== m={m} cnt={cnt} jj={jj} jj2={jj2} h={hh} '
                                         f'(den<={N}) ===\n')
                                for i in range(len(y)):
                                    if y[i] != 0:
                                        fo.write(f'  {names[i]}: {y[i]}\n')
                                if first_closed is None:
                                    first_closed = (m, cnt, jj, jj2, hh)
                                continue
                        kill.append(hh)
                    if kill:
                        nopen += 1
                        print(f'  m={m} cnt={cnt} jj={jj} jj2={jj2}: 保序未杀 h={kill}',
                              flush=True)
                    else:
                        print(f'  m={m} cnt={cnt} jj={jj} jj2={jj2}: 保序全杀 '
                              f'({nS+1} 个 h 全 INFEASIBLE) ✓', flush=True)
        print(f'保序证书 {total_cert} 份 -> {cf}; 未闭合 jj2 对: {nopen}')

        print('\n== 消融（可行性语义: 常数证书→INFEASIBLE; 否则扫 t）==')
        if first_closed:
            m, cnt, jj, jj2, hh = first_closed

            def feas(**kw):
                A, bc, bt, _, _ = build_p1b(m, cnt, jj=jj, **kw)
                if float_cert(A, bc, bt) is not None:
                    return 'INFEASIBLE(有证书)'
                for t in np.linspace(0.26, 0.329, 24):
                    st, _ = lp_feas_point(m, cnt, jj, t_val=t, **kw)
                    if st == 0:
                        return 'FEASIBLE'
                return 'INFEASIBLE(无常数证书)'

            for nm, kw in [('完整 h=1', dict(use_s2=True, jj2=jj2, use_order=True, h=1)),
                           ('去ord h=1(ord承重✓)', dict(use_s2=True, jj2=jj2, use_order=True, h=1, use_ord=False)),
                           ('去保序 entirely', dict(use_s2=True, jj2=jj2)),
                           ('去二步', dict()),
                           ('去danger h=1', dict(use_s2=True, jj2=jj2, use_order=True, h=1, use_danger=False)),
                           ('去mach h=1', dict(use_s2=True, jj2=jj2, use_order=True, h=1, use_mach=False)),
                           ('去装箱 h=1', dict(use_s2=True, jj2=jj2, use_order=True, h=1, use_packing=False, use_vol=True))]:
                print(f'   {nm:24s}: {feas(**kw)}', flush=True)

    elif cmd == 'holes':
        # 提取洞的可行点（先跑 scan 确定洞）
        for m in range(4, 13):
            for cnt in bin_counts(m):
                A, bc, bt, _, _ = build_p1b(m, cnt, jj=None)
                if float_cert(A, bc, bt) is not None:
                    continue
                for jj in [None] + list(range(m - 1)):
                    if jj is not None:
                        A, bc, bt, _, _ = build_p1b(m, cnt, jj=jj)
                        if float_cert(A, bc, bt) is not None:
                            continue
                    h = extract_hole(m, cnt, jj)
                    if h:
                        print(f'洞 m={m} cnt={cnt} jj={jj}:')
                        print(f'  t={h["t"]:.4f} x={h["x"]:.4f} y={h["y"]:.4f} tv={h["tv"]:.4f} '
                              f'x+y+tv={h["x"]+h["y"]+h["tv"]:.4f} 精确装箱={h["packs"]}')
                        print(f'  s={np.round(h["s"],4)}')
                        print(f'  j={np.round(h["j"],4)}')
                        break
