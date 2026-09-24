"""Template-b0：b=0（无 SJ 箱）角落的统一符号证书，全 m>=4、全 k（k-无关）。

证书（权；RHS = -1/2-12MG < 0）：
  danger:6, pair0:4, pair1:2, srt0:4, srt1:6, srt2:3, SS#1(s_2+s_3<=1):3,
  JJJ#0(j_0+j_1+j_2<=1):4, j1>=t:2, j2>=t:4
恒等式（括号均非负）：
  6(p+t-5/4)+4(s_0+j_0-p)+2(s_1+j_1-p)+4(s_1-s_0)+6(s_2-s_1)+3(s_3-s_2)
  +3(1-s_2-s_3)+4(1-j_0-j_1-j_2)+2(j_1-t)+4(j_2-t) = -1/2
  [p:6-4-2=0; t:6-2-4=0; s0:-4+4=0; s1:-2-4+6=0; s2:-6+3+3=0; s3:-3+3=0;
   j0:-4+4=0; j1:-2-2+4=0; j2:-4+4=0; 常数:-7.5+3+4=-0.5]
适用：b=0（JJJ#0 恰为 junior 池前三件 j_0,j_1,j_2）、a>=2（m>=4 且 b=0 时自动：
  a=1 ⟹ d=1,e=f=0 ⟹ m=3）、m>=4（s_3 存在）。
"""
from fractions import Fraction as F
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farkas_fixed import build_fixed
from pairing_feasible import bin_count_solutions


def template_b0(m, cnt, k):
    a, b, c, d, e, f = cnt
    if b != 0 or a < 2 or m < 4:
        return None
    A, bc, bt, names, nv = build_fixed(m, cnt, k)
    idx = {}
    ss_count = 0
    for i, nm in enumerate(names):
        if nm == 'danger': idx['danger'] = i
        elif nm == 'pair0': idx['pair0'] = i
        elif nm == 'pair1': idx['pair1'] = i
        elif nm == 'srt0': idx['srt0'] = i
        elif nm == 'srt1': idx['srt1'] = i
        elif nm == 'srt2': idx['srt2'] = i
        elif nm == 'SS':
            ss_count += 1
            if ss_count == 2: idx['SS1'] = i   # 第二个 SS 箱 = (s_2,s_3)
        elif nm == 'JJJ' and 'JJJ0' not in idx: idx['JJJ0'] = i
        elif nm == 'j1>=t': idx['j1'] = i
        elif nm == 'j2>=t': idx['j2'] = i
    w = {idx['danger']: 6, idx['pair0']: 4, idx['pair1']: 2, idx['srt0']: 4,
         idx['srt1']: 6, idx['srt2']: 3, idx['SS1']: 3, idx['JJJ0']: 4,
         idx['j1']: 2, idx['j2']: 4}
    return A, bc, bt, nv, {i: F(v) for i, v in w.items()}


def verify_sparse(A, bc, bt, nv, w):
    sup = list(w.items())
    for j in range(nv):
        s = F(0)
        for i, wi in sup:
            s += A[i][j] * wi
        if s != 0:
            return False, None
    s = F(0)
    for i, wi in sup:
        s += bt[i] * wi
    if s != 0:
        return False, None
    rhs = F(0)
    for i, wi in sup:
        rhs += bc[i] * wi
    return rhs < 0, rhs


if __name__ == '__main__':
    print('=== Template-b0 精确验证：m=4..30 全部 b=0 cnt × 全 k ===')
    allok = True
    tot = 0
    for m in range(4, 31):
        nok = ncnt = 0
        for cnt in bin_count_solutions(m):
            if cnt[1] != 0:
                continue
            for k in range(1, m):
                ncnt += 1
                r = template_b0(m, cnt, k)
                if r is None:
                    print(f'  ✗ 模板不适用 m={m} cnt={cnt} k={k}')
                    allok = False
                    continue
                ok, rhs = verify_sparse(*r)
                if ok:
                    nok += 1
                else:
                    allok = False
                    print(f'  ✗ m={m} cnt={cnt} k={k} rhs={rhs}')
        tot += ncnt
        print(f'  m={m}: {nok}/{ncnt} 通过', flush=True)
    print(f'结论: {tot} 个 (cnt,k) —', 'Template-b0 全精确通过 ✓ b=0 区符号闭合' if allok else '有失效!')
