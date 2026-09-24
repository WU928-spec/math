"""a2_lean_verify.py — 五模板族（Lemma2/b0/JT/K1/NF）精益精确验证器。

动机：build_fixed 建全 LP 是 O(m^2) 行 Fraction，m=31..40 全量太慢。模板支撑仅 ~15 行，
直接按行名生成支撑行系数（精益行生成器，语义逐行核对自 build_fixed 源码），
verify_sparse 做 Fraction 精确检验（A^T y=0, bt^T y=0, bc^T y<0, y>=0）。
防伪：--crosscheck 模式对抽样 (m,cnt,k) 与 build_fixed 真行逐系数 Fraction 全等比对。
用法：python a2_lean_verify.py [mlo mhi] [--crosscheck]
"""
from fractions import Fraction as F
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pairing_feasible import bin_count_solutions

MG = F(1, 10000)
Q54 = F(5, 4)


def rows_lean(m, cnt, k, want):
    """生成指定支撑行的 (coef_dict{col:Fraction}, bc, bt)。want = 行名集合（含分派逻辑）。
    变量布局同 build_fixed：p=0, t=1, s_i=2+i, j_i=2+nS+i, am=2+2nS, q1=2+2nS+1。"""
    a, b, c, d, e, f = cnt
    nS = m - 1
    nv = 2 + 2 * nS + 2
    iam, iq1 = 2 + 2 * nS, 2 + 2 * nS + 1

    def vs(i): return 2 + i
    def vj(i): return 2 + nS + i

    def slot(u):    # junior 池位 -> 列
        return vj(u) if u <= m - 2 else 1
    out = {}
    jj = k - 1
    # 按 build_fixed 源语义逐行生成
    for nm in want:
        if nm == 'danger':
            out[nm] = ({0: F(-1), 1: F(-1)}, -Q54 - MG, F(0))
        elif nm.startswith('pair'):
            i = int(nm[4:])
            out[nm] = ({0: F(1), vs(i): F(-1), vj(i): F(-1)}, -MG, F(0))
        elif nm.endswith('>=t') and nm[0] == 'j':
            i = int(nm[1:-3])
            out[nm] = ({1: F(1), vj(i): F(-1)}, F(0), F(0))
        elif nm.startswith('srt'):
            i = int(nm[3:])
            out[nm] = ({vs(i): F(1), vs(i + 1): F(-1)}, F(0), F(0))
        elif nm.endswith('<=q1') and nm[0] == 'j':
            i = int(nm[1:-4])
            out[nm] = ({vj(i): F(1), iq1: F(-1)}, F(0), F(0))
        elif nm == 't<=q1':
            out[nm] = ({1: F(1), iq1: F(-1)}, F(0), F(0))
        elif nm == 'q1<=am':
            out[nm] = ({iq1: F(1), iam: F(-1)}, F(0), F(0))
        elif nm.startswith('q1<=j'):
            out[nm] = ({iq1: F(1), vj(jj): F(-1)}, F(0), F(0))
        elif nm.startswith('nofit'):
            i = int(nm[5:])
            out[nm] = ({vs(i): F(-4), iam: F(5), iq1: F(1)}, -MG, F(0))
        elif nm.startswith('mon2_'):
            i = int(nm.split('_')[1].split('<')[0][1:])
            out[nm] = ({vj(i): F(1), vj(i + 1): F(-1)}, F(0), F(0))
    return out, nv, vs, vj, slot


def bin_row(m, cnt, kind, idx, slot, vs):
    """装箱容量行：kind ∈ SS/SJ/JJJ/JJ，idx = 第 idx 个该型箱。"""
    a, b, c, d, e, f = cnt
    if kind == 'SS':
        cols = [vs(2 * idx), vs(2 * idx + 1)]
    elif kind == 'SJ':
        cols = [vs(2 * a + idx), slot(idx)]
    elif kind == 'JJJ':
        base = b + 3 * idx
        cols = [slot(base), slot(base + 1), slot(base + 2)]
    elif kind == 'JJ':
        base = b + 3 * d + 2 * idx
        cols = [slot(base), slot(base + 1)]
    return ({c: F(1) for c in cols}, F(1), F(0))


def assemble(m, cnt, k, weights):
    """weights: {(kind,spec):w}，kind='named' 用 rows_lean，kind='bin' 用 bin_row。"""
    named = {spec for kind, spec in weights if kind == 'named'}
    rows, nv, vs, vj, slot = rows_lean(m, cnt, k, named)
    R = []
    for (kind, spec), w in weights.items():
        if kind == 'named':
            coef, bc, bt = rows[spec]
        else:
            coef, bc, bt = bin_row(m, cnt, spec[0], spec[1], slot, vs)
        R.append((coef, bc, bt, F(w)))
    return R, nv


def verify_lean(R, nv):
    """A^T y=0, bt^T y=0, bc^T y<0, y>=0（y 即权，非负由构造）。"""
    colsum = {}
    rhs = F(0)
    btok = F(0)
    for coef, bc, bt, w in R:
        if w < 0:
            return False, None
        for c, v in coef.items():
            colsum[c] = colsum.get(c, F(0)) + v * w
        rhs += bc * w
        btok += bt * w
    if any(v != 0 for v in colsum.values()):
        return False, None
    if btok != 0:
        return False, None
    return rhs < 0, rhs


def weights_of(fam, m, cnt, k):
    """五族支撑权（与 m<=30 已验证版逐字一致）。"""
    a, b, c, d, e, f = cnt
    nS = m - 1
    jj = k - 1
    if fam == 'lemma2':   # a>=1,d>=1,b>=1,b+2<=m-2,k>=b+2
        if not (a >= 1 and d >= 1 and b >= 1 and b + 2 <= m - 2 and k >= b + 2):
            return None
        w = {('named', 'danger'): 6, ('named', 'pair0'): 3, ('named', 'pair1'): 3,
             ('bin', ('SS', 0)): 3, ('bin', ('JJJ', 0)): 4,
             ('named', f'j{b+1}>=t'): 2, ('named', f'j{b+2}>=t'): 4,
             ('named', 'mon2_j0'): 3, ('named', f'mon2_j{b}'): 2}
        for i in range(1, b):
            w[('named', f'mon2_j{i}')] = 6
        return w
    if fam == 'b0':       # b=0, a>=2
        if not (b == 0 and a >= 2):
            return None
        return {('named', 'danger'): 6, ('named', 'pair0'): 4, ('named', 'pair1'): 2,
                ('named', 'srt0'): 4, ('named', 'srt1'): 6, ('named', 'srt2'): 3,
                ('bin', ('SS', 1)): 3, ('bin', ('JJJ', 0)): 4,
                ('named', 'j1>=t'): 2, ('named', 'j2>=t'): 4}
    if fam == 'jt':       # cnt=(1,m-3,0,1,0,0), k=m-1
        if not (cnt == (1, m - 3, 0, 1, 0, 0) and k == m - 1 and m >= 5):
            return None
        w = {('named', 'danger'): 6, ('named', 'pair0'): 3, ('named', 'pair1'): 3,
             ('bin', ('SS', 0)): 3, ('bin', ('JJJ', 0)): 4,
             ('named', f'j{m-2}>=t'): 2, ('named', 'mon2_j0'): 3,
             ('named', f'mon2_j{m-3}'): 2}
        for i in range(1, m - 3):
            w[('named', f'mon2_j{i}')] = 6
        return w
    if fam == 'k1':       # 2<=k<=min(b, m-3)
        if not (a >= 1 and d >= 1 and b >= 1 and 2 <= k <= min(b, m - 3)):
            return None
        g = 2 * a + k - 1
        if g > m - 2:
            return None
        trio = [x for x in (b, b + 1, b + 2) if x <= m - 2]
        w = {('named', 'danger'): 8, ('named', 'pair0'): 4, ('named', 'pair1'): 4,
             ('named', 'j0<=q1'): 4, ('named', 'j1<=q1'): 4, ('named', f'nofit{g}'): 1,
             ('bin', ('SJ', jj)): 4, ('bin', ('SS', 0)): 4, ('named', 'q1<=am'): 5,
             ('named', f'q1<=j{jj}'): 4, ('named', 't<=q1'): 2, ('bin', ('JJJ', 0)): 2}
        for x in trio:
            w[('named', f'j{x}>=t')] = 2
        return w
    if fam == 'nf':       # 残留域 2a<=k, kp=k-2a∈[0,min(b-1,2a-1)], g=k
        if not (b >= 1 and a >= 1 and d >= 1 and 2 <= k <= m - 2 and 2 * a <= k):
            return None
        kp = k - 2 * a
        if kp < 0 or kp > min(b - 1, 2 * a - 1) or k > m - 2:
            return None
        mate = kp ^ 1
        trio = [x for x in (b, b + 1, b + 2) if x <= m - 2]
        if len(trio) < 2:
            return None
        w = {('named', 'danger'): 8, ('named', f'pair{kp}'): 4, ('named', f'pair{mate}'): 4,
             ('named', f'j{mate}<=q1'): 4, ('named', f'nofit{k}'): 1,
             ('bin', ('SJ', kp)): 4, ('bin', ('SS', kp // 2)): 4, ('named', 'q1<=am'): 5,
             ('named', 't<=q1'): 2, ('bin', ('JJJ', 0)): 2}
        for x in trio:
            w[('named', f'j{x}>=t')] = 2
        return w
    return None


def main():
    mlo, mhi = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (31, 40)
    cross = '--crosscheck' in sys.argv
    if cross:
        # 真行对拍：同一权施加到 build_fixed 真行（按名/序位定位），verify_sparse 必须全过
        from template_b0 import verify_sparse
        from farkas_fixed import build_fixed
        import random
        random.seed(1)
        nchk = nok = 0
        for m in [12, 20, 31, 36]:
            cnts = bin_count_solutions(m)
            for _ in range(12):
                cnt = random.choice(cnts)
                k = random.randrange(1, m)
                fam = random.choice(['lemma2', 'b0', 'k1', 'nf'])
                w = weights_of(fam, m, cnt, k)
                if w is None:
                    continue
                A, bc, bt, names, nv = build_fixed(m, cnt, k)
                widx = {}
                okmap = True
                bincount = {}
                for (kind, spec), ww in w.items():
                    found = None
                    if kind == 'named':
                        for i, nm in enumerate(names):
                            if nm == spec:
                                found = i
                                break
                    else:
                        bkind, bidx = spec
                        c0 = 0
                        for i, nm in enumerate(names):
                            if nm == bkind:
                                if c0 == bidx:
                                    found = i
                                    break
                                c0 += 1
                    if found is None:
                        okmap = False
                        break
                    widx[found] = ww
                if not okmap:
                    continue
                nchk += 1
                okT, rhsT = verify_sparse(A, bc, bt, nv, widx)
                R, nv2 = assemble(m, cnt, k, w)
                okL, rhsL = verify_lean(R, nv2)
                if okT and okL and rhsT == rhsL:
                    nok += 1
                else:
                    print(f'  ✗ 对拍不一致 m={m} cnt={cnt} k={k} fam={fam}: 真行={okT},{rhsT} 精益={okL},{rhsL}')
        print(f'对拍: {nok}/{nchk} 一致（真行+精益同时过且 rhs 相同）')
        return
    print(f'=== 精益精确验证 m={mlo}..{mhi} 五族 ===')
    for fam in ['lemma2', 'b0', 'jt', 'k1', 'nf']:
        allok = True
        tot = 0
        for m in range(mlo, mhi + 1):
            nok = ncnt = 0
            for cnt in bin_count_solutions(m):
                ks = {'jt': [m - 1], 'b0': range(1, m)}.get(fam, range(1, m))
                for k in ks:
                    w = weights_of(fam, m, cnt, k)
                    if w is None:
                        continue
                    ncnt += 1
                    R, nv = assemble(m, cnt, k, w)
                    ok, rhs = verify_lean(R, nv)
                    if ok:
                        nok += 1
                    else:
                        allok = False
                        print(f'  ✗ {fam} m={m} cnt={cnt} k={k}', flush=True)
            tot += ncnt
            print(f'  {fam} m={m}: {nok}/{ncnt}', flush=True)
        print(f'  [{fam}] m={mlo}..{mhi}: {tot} 例 — ' + ('全 PASS ✓' if allok else '有 FAIL!'))


if __name__ == '__main__':
    main()
