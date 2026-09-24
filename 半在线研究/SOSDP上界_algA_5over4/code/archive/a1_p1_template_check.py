"""口袋2 五模板族 -> 口袋1 逐字移植验证（权重映射 + 精确核验, m=4..12 对拍）。
映射: pair_i -> mach_i (p->x+y), danger -> danger, srt/SS/JJJ/j-band/kcap 同名同结构。
口袋1 无 p<K 行: 用 p<K 的家族不可逐字移植（单独标注）。
"""
from fractions import Fraction as F
from pocket1_bins import build_p1b
from farkas_fixed import MG

def verify(m, cnt, k, weights, label):
    """weights: dict 行名->Fraction。返回 (ok, detail)。"""
    nS = m - 1
    A, bc, bt, names, nv = build_p1b(m, cnt, jj=k-1)
    idx = {}
    for i, nm in enumerate(names):
        idx.setdefault(nm, []).append(i)
    y = [F(0)] * len(A)
    used = set()
    for nm, w in weights.items():
        nm_p1 = 'mach' + nm[4:] if nm.startswith('pair') else nm
        if nm_p1 not in idx:
            return False, f'缺行 {nm_p1}'
        # 重名行(装箱)取未用过的第一个
        cand = [i for i in idx[nm_p1] if i not in used]
        if not cand:
            return False, f'重名行耗尽 {nm_p1}'
        i = cand[0]
        used.add(i)
        y[i] = w
    col_ok = all(sum(A[i][j] * y[i] for i in range(len(y))) == 0 for j in range(nv))
    s_bc = sum(bc[i] * y[i] for i in range(len(y)))
    s_bt = sum(bt[i] * y[i] for i in range(len(y)))
    ok = col_ok and s_bc == -1 and s_bt == 0 and all(v >= 0 for v in y)
    return ok, f'col={col_ok} bc={s_bc} bt={s_bt}'

# Template-b0 (midk_note §3): b=0 区, 全 k。RHS -1/2-12MG(口袋2); 口袋1 mach 同结构
B0 = {'danger': F(6), 'pair0': F(4), 'pair1': F(2), 'srt0': F(4), 'srt1': F(6),
      'srt2': F(3), 'SS1': F(3), 'JJJ0': F(4), 'j1>=t': F(2), 'j2>=t': F(4)}

if __name__ == '__main__':
    import sys
    from pocket1_bins import bin_counts
    nb0 = ok0 = 0
    bad = []
    for m in range(4, 13):
        nS = m - 1
        for cnt in bin_counts(m):
            a, b, c, d, e, f = cnt
            if b != 0:
                continue
            for k in range(2, m):   # b0 全 k; 口袋1 k 即 jj=k-1
                nb0 += 1
                ok, det = verify(m, cnt, k, B0, 'b0')
                ok0 += ok
                if not ok and len(bad) < 5:
                    bad.append((m, cnt, k, det))
    print(f'Template-b0 口袋1 逐字: {ok0}/{nb0} PASS')
    for x_ in bad: print('  FAIL:', x_)
