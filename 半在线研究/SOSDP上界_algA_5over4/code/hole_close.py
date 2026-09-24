"""强化 LP 闭合 m>=12 洞区：在 farkas_fixed.build_fixed 基础上加两条序动态约束。

新约束（均有必要性证明，见 hole_close_lemma.md / 本文件 docstring）：

(mon2) 单调匹配：j_0 <= j_1 <= ... <= j_jj（jj=k-1，q1 落机）。
  必要性：s_jj+q1<=K（fs）且 s_i<=s_jj、任意 junior q<=q1 ⟹ [0,jj] 机对任意 junior
  恒放得下。角落形状（每台恰 1 junior）下，已填机若再收一 junior 则必有他机 0 junior
  （n=2m 计数），破角落形状；故角落产生运行中，每个 junior 落到"当前最满的放得下
  的单 senior 机"。归纳：q1→jj；之后落到 [0,jj] 的 junior 必落在该区间当前最满单机
  = 剩余最大 senior，且 junior 递减到达 ⟹ [0,jj] 上 junior 随 senior 单调不减。
  senior 相等时机器可重标号（LP 机器标号对称），故约束 WLOG。∎

(ammin) am >= s_0（p_m = 最小 senior）：
  递减到达 ⟹ 初始 m 件 = 全局最大 m 件 = {p}∪{senior}（mon 组已给 junior<=s_i），
  故 p_m = min 初始件 = min senior = s_0。LP 原有 am<=s_i，补 am>=s_0 使 am=s_0 精确。∎

验证协议（任务要求）：闭合扫描（m=12..20 洞区逐 cnt,k INFEASIBLE）+ 消融（去 mon2 /
ammin / 各旧组应变 feasible）+ sanity（去 danger 应 feasible）+ 精确有理证书 +
m=4..11 回归（加约束后仍全闭合）。
"""
from fractions import Fraction as F
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farkas_fixed import build_fixed, float_cert, rationalize_verify, MG
from pairing_feasible import bin_count_solutions


def build_close(m, cnt, k, use_mon2=True, use_ammin=False, **kw):
    """build_fixed + mon2 (+可选 ammin)。开关用于消融。
    默认仅 mon2：消融显示 mon2 单独闭合全部洞，ammin 非必要（仅作额外强度保留）。"""
    A, bc, bt, names, nv = build_fixed(m, cnt, k, **kw)
    nS = m - 1
    jj = k - 1

    def vs(i): return 2 + i
    def vj(i): return 2 + nS + i
    iam = 2 + 2 * nS

    def con(row, c0, c1, nm):
        A.append([F(x) for x in row]); bc.append(F(c0)); bt.append(F(c1)); names.append(nm)

    if use_mon2:
        for i in range(jj):
            r = [F(0)] * nv; r[vj(i)] = 1; r[vj(i + 1)] = -1
            con(r, 0, 0, f'mon2_j{i}<=j{i+1}')
    if use_ammin:
        r = [F(0)] * nv; r[iam] = -1; r[vs(0)] = 1
        con(r, 0, 0, 'am>=s0')
    return A, bc, bt, names, nv


def holes_of(m):
    out = []
    for k in range(1, m):
        for cnt in bin_count_solutions(m):
            A, bc, bt, names, nv = build_fixed(m, cnt, k)
            if float_cert(A, bc, bt) is None:
                out.append((cnt, k))
    return out


def cert(A, bc, bt, exact=False):
    yf = float_cert(A, bc, bt)
    if yf is None:
        return None
    if not exact:
        return yf
    y, N = rationalize_verify(A, bc, bt, yf)
    return (yf, y, N) if y is not None else None


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'close'
    if cmd == 'close':
        print('=== 洞区闭合扫描：base=feasible 的洞，加 mon2 / ammin / 两者 ===')
        allclosed = True
        for m in range(12, 21):
            hs = holes_of(m)
            for cnt, k in hs:
                r0 = cert(*build_close(m, cnt, k, use_mon2=False, use_ammin=False)[:3]) is not None
                r1 = cert(*build_close(m, cnt, k, use_mon2=True, use_ammin=False)[:3]) is not None
                r2 = cert(*build_close(m, cnt, k, use_mon2=False, use_ammin=True)[:3]) is not None
                r3 = cert(*build_close(m, cnt, k, use_mon2=True, use_ammin=True)[:3]) is not None
                tag = lambda b: 'INF' if b else 'fea'
                print(f'  m={m} k={k} cnt={cnt}: base={tag(r0)} +mon2={tag(r1)} '
                      f'+ammin={tag(r2)} +both={tag(r3)}')
                if not r3:
                    allclosed = False
        print('结论:', '洞区全闭合(+both)' if allclosed else '仍有洞!')
    elif cmd == 'ablate':
        m, cnt, k = 12, (2, 7, 0, 1, 1, 0), 11
        print(f'=== 消融（m={m} k={k} cnt={cnt}，基准=+both 闭合）===')
        base = build_close(m, cnt, k)
        print(f'  基准(+mon2+ammin): {"INFEASIBLE(闭合)" if cert(*base[:3]) is not None else "feasible"}')
        for nm, kw in [('去mon2', dict(use_mon2=False)), ('去ammin', dict(use_ammin=False)),
                       ('去danger', dict(use_danger=False)), ('去pair', dict(use_pair=False)),
                       ('去kcap', dict(use_kcap=False)), ('去fs', dict(use_fs=False)),
                       ('去nofit', dict(use_nofit=False)), ('去装箱', dict(use_bins=False)),
                       ('去mon递减', dict(use_mon=False))]:
            A, bc, bt, names, nv = build_close(m, cnt, k, **kw)
            print(f'  {nm:8s}: {"feasible（必要 ✓）" if cert(A, bc, bt) is None else "INFEASIBLE（非必要）"}')
    elif cmd == 'sanity':
        print('=== sanity：去 danger 后应 feasible（防假阴性/方向写反）===')
        ok = True
        for m in range(12, 21):
            for cnt, k in holes_of(m):
                A, bc, bt, names, nv = build_close(m, cnt, k, use_danger=False)
                fea = cert(A, bc, bt) is None
                if not fea:
                    ok = False
                    print(f'  m={m} k={k} cnt={cnt}: 去danger仍INFEASIBLE ✗ 假阴性风险!')
            print(f'  m={m}: 去danger全feasible ✓' )
        print('sanity:', '通过' if ok else '失败')
    elif cmd == 'exact':
        print('=== 精确有理证书（洞区全 cnt,k，+both）===')
        allok = True
        for m in range(12, 21):
            for cnt, k in holes_of(m):
                A, bc, bt, names, nv = build_close(m, cnt, k)
                r = cert(A, bc, bt, exact=True)
                if r is None:
                    allok = False
                    print(f'  m={m} k={k} cnt={cnt}: 无有理证书!')
                else:
                    print(f'  m={m} k={k} cnt={cnt}: 精确证书 ✓ (分母界 N={r[2]})')
        print('结论:', '全部有精确有理证书' if allok else '有缺!')
    elif cmd == 'regress':
        print('=== 回归：m=4..11 全 cnt 全 k（+both）应仍全闭合 ===')
        allok = True
        for m in range(4, 12):
            bad = []
            for k in range(1, m):
                for cnt in bin_count_solutions(m):
                    A, bc, bt, names, nv = build_close(m, cnt, k)
                    if cert(A, bc, bt) is None:
                        bad.append((cnt, k))
            print(f'  m={m}: {"全闭合 ✓" if not bad else f"新洞 {bad}"}')
            if bad:
                allok = False
        print('结论:', 'm=4..11 回归通过' if allok else '回归失败!')
    elif cmd == 'scanbig':
        print('=== 大 m 扫描（+both，float）：m=12..26 全 k 全 cnt ===')
        for m in range(12, 27):
            bad = []
            for k in range(1, m):
                for cnt in bin_count_solutions(m):
                    A, bc, bt, names, nv = build_close(m, cnt, k)
                    if cert(A, bc, bt) is None:
                        bad.append((cnt, k))
            print(f'  m={m}: {"全闭合 ✓" if not bad else f"洞 {bad}"}', flush=True)
