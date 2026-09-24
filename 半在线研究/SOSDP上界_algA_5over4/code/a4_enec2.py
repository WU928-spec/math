"""E-nec-v2：mon2（build_close 骨架）+ 必要条件行族替换固定分组装箱行——决定性组合裁决。

与 a4_enec.py retain 的差异：retain 用 rows_fixed(use_order=True)（ord≡mon2 + lowzone/hizone）；
本版严格按 brief：build_close 骨架（build_fixed 全约束 + mon2，无 lowzone/hizone）去 caps + X 行。
两版对拍以定位 lowzone/hizone 的边际强度。

用法：
  python a4_enec2.py retain [m_hi]   # m=4..m_hi 全 cnt 全 k 保持率（V2a），razor 残留单独列
  python a4_enec2.py ghost           # m=12..20 洞点命运（预期 mon2 保持 INFEASIBLE）
  python a4_enec2.py ablate          # razor 闭合代表消融（去 mon2 / 去 X 行）
  python a4_enec2.py resid           # razor 残留点提取（t 窗口位置）——(W'') 最小区域清单
"""
import sys, os, json, time
from fractions import Fraction as F
import numpy as np
from scipy.optimize import linprog
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hole_close import build_close
from farkas_fixed import float_cert
from pairing_feasible import bin_count_solutions

CAPNAMES = {'SS', 'SJ', 'JJJ', 'JJ'}


def build_v2a(m, cnt, k, use_mon2=True, use_xss=True, use_xvol=True, use_xbig=True):
    """build_close 骨架去 caps + X 必要条件行。返回 (A, bc, bt, names, nv)。"""
    a, b, c, d, e, f = cnt
    nS = m - 1
    A, bc, bt, names, nv = build_close(m, cnt, k, use_mon2=use_mon2)
    idx = [i for i, n in enumerate(names) if n not in CAPNAMES]
    A = [A[i] for i in idx]; bc = [bc[i] for i in idx]; bt = [bt[i] for i in idx]
    names = [names[i] for i in idx]

    def vs(i): return 2 + i
    def vj(i): return 2 + nS + i
    it = 1

    def zero(): return [F(0)] * nv
    if use_xss:
        for i in range(a):
            r = zero(); r[vs(i)] = 1; r[vs(2 * a - 1 - i)] = 1
            A.append(r); bc.append(F(1)); bt.append(F(0)); names.append(f'XSS{i}')
    if use_xvol:
        r = zero()
        for p in range(nS):
            r[vj(p)] = 1
        r[it] = 1
        for i in range(b):
            r[vs(i)] = 1
        A.append(r); bc.append(F(b + d + e + f)); bt.append(F(0)); names.append('XVOL')
    if use_xbig:
        ix = nS - 1 - (c + a + b)
        if 0 <= ix < nS:
            r = zero(); r[vs(ix)] = 1
            A.append(r); bc.append(F(1, 2)); bt.append(F(0)); names.append('XBIG')
    return A, bc, bt, names, nv


def is_inf(A, bc, bt):
    return float_cert(A, bc, bt) is not None


def resid_point(A, bc, bt, nv):
    """提取残留可行点（bt 并入 t 列），返回 (t, x) 或 None。"""
    Af = np.array([[float(v) for v in row] for row in A])
    bcf = np.array([float(v) for v in bc]); btf = np.array([float(v) for v in bt])
    A2 = Af.copy(); A2[:, 1] -= btf
    res = linprog(c=np.zeros(nv), A_ub=A2, b_ub=bcf, bounds=(None, None), method='highs')
    return (float(res.x[1]), res.x) if res.status == 0 else (None, None)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'retain'
    t0 = time.time()

    if cmd == 'retain':
        m_hi = int(sys.argv[2]) if len(sys.argv) > 2 else 14
        n_tot = n_keep = 0
        losses = []
        razor_loss = []
        for m in range(4, m_hi + 1):
            for k in range(1, m):
                for cnt in bin_count_solutions(m):
                    n_tot += 1
                    A, bc, bt, names, nv = build_v2a(m, cnt, k)
                    if is_inf(A, bc, bt):
                        n_keep += 1
                    else:
                        losses.append((m, cnt, k))
                        a, b, c, d, e, f = cnt
                        if c == 0 and d == 1 and a <= 2:
                            razor_loss.append((m, cnt, k))
            print(f'  m={m}: 累计保持 {n_keep}/{n_tot} ({time.time()-t0:.0f}s)', flush=True)
        print(f'V2a（mon2+X行）保持率: {n_keep}/{n_tot} = {n_keep/n_tot:.4f}')
        print(f'总损失 {len(losses)}；其中 razor 带 (c=0,d=1,a<=2) 损失 {len(razor_loss)}')
        print('razor 残留清单:', razor_loss)

    elif cmd == 'ghost':
        holes = [json.loads(l) for l in open(os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'p2_holes_big.jsonl')) if json.loads(l)['m'] <= 20]
        print(f'洞族命运（V2a=mon2+X行，{len(holes)} 个 m=12..20 洞）:')
        n_surv = 0
        for h in holes:
            m, cnt, k = h['m'], tuple(h['cnt']), h['k']
            if not is_inf(*build_v2a(m, cnt, k)[:3]):
                n_surv += 1
                print(f'  *** 存活 m={m} cnt={cnt} k={k}')
        print(f'结果: {n_surv}/{len(holes)} 存活（0=mon2 保持全杀 ✓ 预期）  ({time.time()-t0:.0f}s)')

    elif cmd == 'ablate':
        # 找 razor 带闭合代表（V2a INF 的），消融定位承重
        shown = 0
        for m in range(6, 15):
            if shown >= 4:
                break
            for cnt in bin_count_solutions(m):
                a, b, c, d, e, f = cnt
                if not (c == 0 and d == 1 and a <= 2):
                    continue
                for k in range(2, m):
                    A, bc, bt, names, nv = build_v2a(m, cnt, k)
                    if not is_inf(A, bc, bt):
                        continue
                    print(f'm={m} cnt={cnt} k={k}（razor 带，V2a 闭合）消融:')
                    for fam, kw in [('去mon2', dict(use_mon2=False)),
                                    ('去XSS', dict(use_xss=False)),
                                    ('去XVOL', dict(use_xvol=False)),
                                    ('去XBIG', dict(use_xbig=False)),
                                    ('去全部X', dict(use_xss=False, use_xvol=False, use_xbig=False))]:
                        A2, bc2, bt2, _, _ = build_v2a(m, cnt, k, **kw)
                        print(f'   {fam:6s}: {"仍INF" if is_inf(A2, bc2, bt2) else "FEASIBLE（回弹）"}')
                    shown += 1
                    break
                if shown >= 4:
                    break

    elif cmd == 'resid':
        # razor 残留点的 t 位置（m=4..14）
        print('razor 残留点 t 窗口位置（V2a FEASIBLE 处）:')
        n = 0
        for m in range(4, 15):
            for k in range(1, m):
                for cnt in bin_count_solutions(m):
                    a, b, c, d, e, f = cnt
                    if not (c == 0 and d == 1 and a <= 2):
                        continue
                    A, bc, bt, names, nv = build_v2a(m, cnt, k)
                    if is_inf(A, bc, bt):
                        continue
                    t, x = resid_point(A, bc, bt, nv)
                    n += 1
                    if n <= 12 or t > 1 / 3 + 1e-9:
                        print(f'  m={m} cnt={cnt} k={k}: t={t:.4f} {"（窗口外!）" if t > 1/3 + 1e-9 else ""}')
        print(f'共 {n} 个 razor 残留点')
