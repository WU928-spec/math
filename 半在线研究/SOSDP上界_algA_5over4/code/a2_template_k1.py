"""a2_template_k1.py — "K<1 链"：k<=b 的统一符号证书（LP 规范代表框架内，同基线 WLOG）。

机制（全角落必要条件）：
  k<=b ⟹ jj=k-1<=b-1 ⟹ 池位 jj 为 SJ 伙伴位：SJ 箱 #jj = (s_{2a+jj}, j_jj)，且 fs: j_jj=q1。
  g=2a+jj=2a+k-1 > jj（a>=1 恒真）且 g<=m-2（k<=b ⟹ 2a+k<=2a+b<=m-1）⟹ nofit_g 存在。
  nofit_g: s_g+q1>K 与 SJ 箱 s_g+q1<=1 ⟹ K<1 ⟹ a_m+q1<4/5 ⟹ q1<2/5。
  SS 箱（a>=1）+pair+j<=q1 ⟹ 2(p-q1)<=1 ⟹ p<1/2+q1<9/10；danger ⟹ t>7/20>1/3；
  JJJ 箱（d>=1）三件各>=t ⟹ t<=1/3。矛盾。
实现：支撑行子集 {danger, pair0, pair1, j0<=q1, j1<=q1, nofit_g, SJ#jj, SS#0,
  q1<=am, t<=q1, q1<=j{jj}, j{jj}<=q1, JJJ#0, j>=t×(池位 b..b+2 中机器 junior)}
  上跑 float_cert + rationalize_verify（不解全 LP；权由求解器产出再精确复核）。
前台：k1_conditions。验证：m=4..30 全 k<=b (cnt,k) 精确证书。
"""
from fractions import Fraction as F
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farkas_fixed import build_fixed, float_cert, rationalize_verify
from pairing_feasible import bin_count_solutions


def k1_conditions(m, cnt, k):
    a, b, c, d, e, f = cnt
    if b < 1 or a < 1 or d < 1 or k < 2 or k > m - 3 or k > b:
        return None
    g = 2 * a + k - 1
    return g if g <= m - 2 else None


def k1_submatrix(m, cnt, k):
    g = k1_conditions(m, cnt, k)
    if g is None:
        return None
    a, b, c, d, e, f = cnt
    A, bc, bt, names, nv = build_fixed(m, cnt, k)
    jj = k - 1
    want = {'danger', 'pair0', 'pair1', 'j0<=q1', 'j1<=q1', f'nofit{g}',
            'q1<=am', 't<=q1', f'q1<=j{jj}', f'j{jj}<=q1'}
    trio = [x for x in (b, b + 1, b + 2) if x <= m - 2]
    for x in trio:
        want.add(f'j{x}>=t')
    sj = 0
    keep = []
    for i, nm in enumerate(names):
        if nm in want:
            keep.append(i)
        elif nm == 'SJ':
            if sj == jj:
                keep.append(i)
            sj += 1
        elif nm == 'SS' and not any(names[j] == 'SS' for j in keep):
            keep.append(i)   # 第一个 SS 箱
        elif nm == 'JJJ' and not any(names[j] == 'JJJ' for j in keep):
            keep.append(i)   # 第一个 JJJ 箱
    Asub = [A[i] for i in keep]
    return [A[i] for i in keep], [bc[i] for i in keep], [bt[i] for i in keep], nv, keep


if __name__ == '__main__':
    print('=== K1 链（k<=b）支撑子集精确证书：m=4..30 ===')
    allok = True
    tot = 0
    for m in range(4, 31):
        nok = ncnt = 0
        for cnt in bin_count_solutions(m):
            for k in range(2, m - 2):
                r = k1_submatrix(m, cnt, k)
                if r is None:
                    continue
                Asub, bcs, bts, nv, keep = r
                ncnt += 1
                yf = float_cert(Asub, bcs, bts)
                ok = False
                if yf is not None:
                    y, N = rationalize_verify(Asub, bcs, bts, yf)
                    ok = y is not None
                if ok:
                    nok += 1
                else:
                    allok = False
                    if ncnt - nok <= 3:
                        print(f'  ✗ m={m} cnt={cnt} k={k}', flush=True)
        tot += ncnt
        if ncnt:
            print(f'  m={m}: {nok}/{ncnt} 通过', flush=True)
    print(f'结论: {tot} 个 (cnt,k) —', 'K1链 全精确通过 ✓' if allok else '有失效!')
