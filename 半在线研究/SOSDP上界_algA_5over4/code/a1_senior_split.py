"""B 线: razor 带 senior 分割 w.l.o.g. 数值检验。
洞点(build_fixed 基 LP, k=m-1)上检验: 'SS=最小 2a 可行' ⟸ '某 SS 集可行'（w.l.o.g. 方向）。
对每个洞点: 遍历 SS 集 Λ(|Λ|=2a), 检查 (SS 极端配对 + 剩余 senior 入 SJ/S + 池入 JJJ/JJ/J) 可行性。
 feasibility: SS 对极端配对后; SJ 匹配(bipartite senior-junior s+j<=1, b 槽) + S 槽 c;
 池余件 JJJ(3d 件和<=d) + JJ(2e 反序) + J 单 — 小规模 brute force/贪心+回溯。
"""
import numpy as np, sys, os, itertools
from scipy.optimize import linprog
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farkas_fixed import build_fixed

def ss_set_feasible(s, pool, cnt, lam):
    """Λ=ss 集(索引)。返回该 SS 集下全装箱可行性。"""
    a, b, c, d, e, f = cnt
    nS = len(s)
    rest = [i for i in range(nS) if i not in lam]
    ss = sorted(lam, key=lambda i: s[i])
    pairs = [(ss[k], ss[2 * a - 1 - k]) for k in range(a)]
    if any(s[i] + s[j] > 1 + 1e-9 for i, j in pairs):
        return False
    rest_s = sorted(rest, key=lambda i: -s[i])      # 大 senior 先配小 junior
    # 回溯: SJ 槽 b 个 + S 槽 c 个; 剩余 senior 必入 S(独箱<=1 恒真)
    juniors = sorted(range(len(pool)), key=lambda i: pool[i])
    def match(idx, js):
        if idx == len(rest_s):
            return True
        si = rest_s[idx]
        for slot in range(b):
            pass
        # 简化: 贪心最大 senior 配最小可行 junior; 配不完入 S 槽
        return None
    # brute: b 个 SJ 槽, 从 juniors 选 b 个分配(Hall 贪心: senior 降序配最小可行 junior)
    used = [False] * len(pool)
    s_rest = rest_s
    ok = True
    n_sj = 0
    for si in s_rest:
        best = None
        for ji in range(len(pool)):
            if not used[ji] and s[si] + pool[ji] <= 1 + 1e-9:
                if best is None or pool[ji] < pool[best]:
                    best = ji
        if best is not None and n_sj < b:
            used[best] = True; n_sj += 1
        else:
            if c <= 0:
                # 无 S 槽: senior 必须 SJ — 贪心失败则回溯
                return 'backtrack'
    rem = [pool[ji] for ji in range(len(pool)) if not used[ji]]
    rem.sort()
    # JJJ: 3d 件和<=d(分组); JJ: 2e 反序; J: f
    if d > 0:
        if len(rem) < 3 * d or sum(rem[:3 * d]) > d + 1e-9:
            return False
        rem = rem[3 * d:]
    if e > 0:
        if len(rem) < 2 * e: return False
        jj = rem[:2 * e]
        if any(jj[k] + jj[2 * e - 1 - k] > 1 + 1e-9 for k in range(e)):
            return False
        rem = rem[2 * e:]
    if len(rem) != f: return False
    return True

def hole_point(m, cnt, k, t0):
    A, bc, bt, names, nv = build_fixed(m, cnt, k)
    Af = np.array([[float(z) for z in row] for row in A])
    bf = np.array([float(bc[i]) + float(bt[i]) * t0 for i in range(len(A))])
    res = linprog(c=np.zeros(nv), A_ub=Af, b_ub=bf, bounds=(None, None), method='highs')
    if res.status != 0: return None
    nS = m - 1
    return list(res.x[:2 + 2 * nS])

if __name__ == '__main__':
    for m in [12, 14, 16]:
        cnt = (2, m - 5, 0, 1, 1, 0)
        k = m - 1
        pt = None
        for t0 in [0.30, 0.31, 0.32, 0.328]:
            pt = hole_point(m, cnt, k, t0)
            if pt is not None: break
        if pt is None:
            print(f'm={m}: 无洞点'); continue
        nS = m - 1
        s = pt[2:2 + nS]; pool = list(pt[2 + nS:2 + 2 * nS]) + [pt[1]]
        a = 2
        lams = list(itertools.combinations(range(nS), 2 * a))
        feas_any = feas_min = False
        min_lam = tuple(sorted(range(2 * a)))
        backtrack_needed = 0
        for lam in lams:
            r = ss_set_feasible(s, pool, cnt, set(lam))
            if r == 'backtrack':
                backtrack_needed += 1
                continue
            if r:
                feas_any = True
                if lam == min_lam: feas_min = True
        print(f'm={m}: SS 集 {len(lams)} 个, 可行(any)={feas_any}, 最小 2a 集可行={feas_min}, '
              f'需回溯={backtrack_needed}', flush=True)
