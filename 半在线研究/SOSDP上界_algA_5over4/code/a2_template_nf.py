"""a2_template_nf.py — Template-NF：残留域（nofit 区 SJ senior + SS 伙伴 junior）统一符号证书。

机制（全合法角落必要条件）：
  SJ 箱 (s_g + j_k' <= 1) + nofit_g (s_g > (5/4)am + (1/4)q1) ⟹ j_k' < 1 - (5/4)am - (1/4)q1；
  pair_k' ⟹ s_k' > p - 1 + (5/4)am + (1/4)q1；pair_mate + j_mate<=q1 ⟹ s_mate >= p - q1；
  SS 箱 (s_k' + s_mate <= 1) ⟹ 2p < 2 - (5/4)am + (3/4)q1 <= 2 - (1/2)q1 (q1<=am)
  ⟹ p < 1 - (1/4)q1；danger p > 5/4 - t ⟹ q1 < 4t - 1；t<=q1 ⟹ t > 1/3；
  JJJ 箱三件各 >= t ⟹ 3t <= 1。矛盾。
Farkas 权（RHS = -17MG < 0，恰好 razor-thin 严格）：
  danger:8, pair_k':4, pair_mate:4, j{mate}<=q1:4, nofit_g:1, SJ#k':4, SS#(k'//2):4,
  q1<=am:5, t<=q1:2, JJJ#0:2, j>=t（JJJ 三件中的机器 junior）:2 each
前台条件（残留域 2a<=k 内）：k' = k-2a ∈ [0, min(b-1, 2a-1)]，g = 2a+k' = k ∈ nofit 区
（g <= nS-1 ⟺ k <= m-2 ✓ mid-k）；JJJ#0 若含 t 则其 j>=t 行免用（t 自身权重并入）。
"""
from fractions import Fraction as F
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farkas_fixed import build_fixed
from pairing_feasible import bin_count_solutions
from uniform_hole_cert import covered


def nf_conditions(m, cnt, k):
    """返回 (k', g, mate) 或 None。"""
    a, b, c, d, e, f = cnt
    if b < 1 or a < 1 or d < 1 or k < 2 or k > m - 2:
        return None
    if 2 * a > k:            # 残留域外（P2K-high 杀）
        return None
    kp = k - 2 * a
    if kp < 0 or kp > min(b - 1, 2 * a - 1):
        return None
    g = 2 * a + kp           # = k，nofit 区首台
    if g > m - 2:
        return None
    mate = kp ^ 1            # SS 箱 (s_{2i},s_{2i+1}) 内的伙伴
    return kp, g, mate


def template_nf(m, cnt, k):
    r = nf_conditions(m, cnt, k)
    if r is None:
        return None
    kp, g, mate = r
    a, b, c, d, e, f = cnt
    A, bc, bt, names, nv = build_fixed(m, cnt, k)
    idx = {}
    sj = 0
    ss = 0
    for i, nm in enumerate(names):
        if nm == 'danger': idx['danger'] = i
        elif nm == f'pair{kp}': idx['pk'] = i
        elif nm == f'pair{mate}': idx['pm'] = i
        elif nm == f'j{mate}<=q1': idx['jmq'] = i
        elif nm == f'nofit{g}': idx['nf'] = i
        elif nm == 'SJ':
            if sj == kp: idx['SJ'] = i
            sj += 1
        elif nm == 'SS':
            if ss == kp // 2: idx['SS'] = i
            ss += 1
        elif nm == 'q1<=am': idx['qa'] = i
        elif nm == 't<=q1': idx['tq'] = i
        elif nm == 'JJJ' and 'JJJ' not in idx: idx['JJJ'] = i
    # JJJ#0 的三件（池位 b..b+2 = 机器 junior j_b,j_{b+1},j_{b+2}；若 b+2>m-2 则含 t）
    trio = [x for x in (b, b + 1, b + 2) if x <= m - 2]
    jt = []
    for i, nm in enumerate(names):
        for x in trio:
            if nm == f'j{x}>=t':
                jt.append(i)
    if len(jt) != len(trio) or len(trio) < 2:
        return None
    w = {idx['danger']: 8, idx['pk']: 4, idx['pm']: 4, idx['jmq']: 4, idx['nf']: 1,
         idx['SJ']: 4, idx['SS']: 4, idx['qa']: 5, idx['tq']: 2, idx['JJJ']: 2}
    for i in jt:
        w[i] = 2
    # t 平衡：danger -8，t<=q1 +2，j>=t 行各 +2，JJJ 含 t 时再 +2
    if -8 + 2 + 2 * len(jt) + (2 if len(trio) < 3 else 0) != 0:
        return None
    return A, bc, bt, nv, {i: F(v) for i, v in w.items()}


if __name__ == '__main__':
    from template_b0 import verify_sparse
    print('=== Template-NF 精确验证：m=4..30 全部满足前台条件的 (cnt,k) ===')
    allok = True
    tot = 0
    for m in range(4, 31):
        nok = ncnt = 0
        for cnt in bin_count_solutions(m):
            for k in range(2, m - 1):
                r = template_nf(m, cnt, k)
                if r is None:
                    continue
                ncnt += 1
                ok, rhs = verify_sparse(*r)
                if ok:
                    nok += 1
                else:
                    allok = False
                    print(f'  ✗ m={m} cnt={cnt} k={k} rhs={rhs}')
        tot += ncnt
        if ncnt:
            print(f'  m={m}: {nok}/{ncnt} 通过', flush=True)
    print(f'结论: {tot} 个 (cnt,k) —', 'Template-NF 全精确通过 ✓' if allok else '有失效!')

    print()
    print('=== 全覆盖扫描：P2K1/P2K-top/Lemma2/b0/JT/P2K-high/NF 后还剩什么 ===')
    for m in [12, 18, 20, 25, 30, 40]:
        left = []
        for cnt in bin_count_solutions(m):
            a, b, c, d, e, f = cnt
            for k in range(1, m):
                if k == 1 or k >= m - 2:                       # P2K1 / P2K-top
                    continue
                if cnt == (1, m - 3, 0, 1, 0, 0) and k == m - 1:  # Template-JT
                    continue
                if b == 0:                                      # Template-b0
                    continue
                if covered(cnt, m, k):                          # Lemma 2 模板
                    continue
                if 2 * a >= k + 1:                              # P2K-high
                    continue
                if nf_conditions(m, cnt, k) is not None:        # Template-NF
                    continue
                left.append((cnt, k))
        fams = sorted(set(c for c, _ in left))
        print(f'  m={m}: 未覆盖 {len(left)} 个 (cnt,k)，cnt 族 {fams[:6]}')
        if left:
            ks = sorted(set(k for _, k in left))
            print(f'       k 范围 {ks[:10]}{"..." if len(ks) > 10 else ""}')
