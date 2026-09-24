"""a3_ 定向搜索：装箱固定代表分组 w.l.o.g. 的反例（LP_CONSTRAINTS.md 存疑清单2）。
反例判据：无装箱角落 LP 可行点 x*，其件多重集存在某装箱（型集合 C≠∅，自由 DFS 枚举），
但对每个 cnt∈C，build_fixed 的固定分组帽在 x* 处失败 ⟹ (W') 为假 ⟹ 角落被所有 LP 漏网。
对照项：极端配对 SS（可证 w.l.o.g.）在同点的表现。
"""
import numpy as np
from scipy.optimize import linprog
from fractions import Fraction as F
import sys, os, random, itertools

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_constraints import build_p2

random.seed(20260922)
TOL = 1e-7


def all_bin_types(svals, jt_vals, nbins, cap=1.0, max_per_bin=3, type_limit=400):
    """DFS 枚举全部装箱型（senior 身份按索引）。返回 {(a,b,c,d,e,f), ...}。"""
    nS = len(svals)
    items = [(svals[i], True) for i in range(nS)] + [(v, False) for v in jt_vals]
    items.sort(key=lambda z: -z[0])
    types = set()
    bins = []  # [load, count, nsenior]

    def dfs(i):
        if len(types) >= type_limit:
            return
        if i == len(items):
            a = sum(1 for b in bins if b[2] == 2)
            b_ = sum(1 for b in bins if b[2] == 1 and b[1] == 2)
            c = sum(1 for b in bins if b[2] == 1 and b[1] == 1)
            d = sum(1 for b in bins if b[2] == 0 and b[1] == 3)
            e = sum(1 for b in bins if b[2] == 0 and b[1] == 2)
            f = sum(1 for b in bins if b[2] == 0 and b[1] == 1)
            types.add((a, b_, c, d, e, f))
            return
        w, is_s = items[i]
        seen = set()
        for b in bins:
            if b[1] < max_per_bin and b[0] + w <= cap + 1e-9 and b[0] not in seen:
                seen.add(b[0])
                b[0] += w; b[1] += 1; b[2] += is_s
                dfs(i + 1)
                b[0] -= w; b[1] -= 1; b[2] -= is_s
        if len(bins) < nbins:
            bins.append([w, 1, int(is_s)])
            dfs(i + 1)
            bins.pop()

    if sum(v for v, _ in items) > nbins * cap + 1e-9:
        return set()
    dfs(0)
    return types


def fixed_caps_ok(m, cnt, s, j, t, tol=TOL):
    """build_fixed 的固定分组帽在该点是否全满足。s 须升序（LP 有 srt）。"""
    a, b, c, d, e, f = cnt
    nS = m - 1
    js = list(j) + [t]
    for kk in range(a):
        if s[2 * kk] + s[2 * kk + 1] > 1 + tol:
            return False
    for kk in range(b):
        if s[2 * a + kk] + js[kk] > 1 + tol:
            return False
    jidx = b
    for kk in range(d):
        if js[jidx] + js[jidx + 1] + js[jidx + 2] > 1 + tol:
            return False
        jidx += 3
    for kk in range(e):
        if js[jidx] + js[jidx + 1] > 1 + tol:
            return False
        jidx += 2
    return True


def extreme_ss_ok(m, cnt, s, tol=TOL):
    """对照：SS 极端配对（最小 2a 首尾配对）。"""
    a = cnt[0]
    return all(s[kk] + s[2 * a - 1 - kk] <= 1 + tol for kk in range(a))


def run(ms=(6, 7, 8), nrand=24):
    npts = npack = nkill = 0
    for m in ms:
        nS = m - 1
        tl = (m - 1) / (4 * (m - 2))
        for k in range(1, m):
            A, bc, bt, names, nv = build_p2(m, (0, 0, nS, 0, 0, 0), k,
                                            drop=('SS', 'SJ', 'JJJ', 'JJ'))
            Af = np.array([[float(z) for z in row] for row in A])
            for t0 in np.linspace(tl + 0.002, 1 / 3, 6):
                bf = np.array([float(bc[i]) + float(bt[i]) * t0 for i in range(len(A))])
                objs = [None]
                o = np.zeros(nv); o[2 + nS - 1] = 1.0; o[2 + nS - 2] = 1.0; objs.append(o)  # 末对最大
                o = np.zeros(nv); o[2:2 + nS] = 1.0; objs.append(o)                          # Σs 最大
                o = np.zeros(nv); o[2 + nS - 1] = 1.0; o[2] = -1.0; objs.append(o)          # 跨度最大
                for _ in range(nrand):
                    objs.append(np.array([random.gauss(0, 1) for _ in range(nv)]))
                for obj in objs:
                    c = np.zeros(nv) if obj is None else -np.asarray(obj, float)
                    res = linprog(c=c, A_ub=Af, b_ub=bf, bounds=(None, None), method='highs')
                    if res.status != 0:
                        continue
                    x = res.x
                    p, tt = x[0], x[1]
                    s = sorted(x[2:2 + nS])          # srt 升序（LP 内已强制）
                    j = list(x[2 + nS:2 + 2 * nS])
                    npts += 1
                    types = all_bin_types(s, j + [tt], m - 1)
                    if not types:
                        continue
                    npack += 1
                    bad = [cnt for cnt in types if not fixed_caps_ok(m, cnt, s, j, tt)]
                    okc = [cnt for cnt in types if fixed_caps_ok(m, cnt, s, j, tt)]
                    if not okc:
                        nkill += 1
                        print(f'  ✗✗ 反例 m={m} k={k} t={t0:.4f}: 可装箱型 {sorted(types)} '
                              f'固定分组全失败!')
                        print(f'      p={p:.4f} t={tt:.4f} p+t={p+tt:.4f}')
                        print(f'      s={np.round(s,4)}')
                        print(f'      j={np.round(j,4)}')
                        for cnt in types:
                            print(f'      cnt={cnt} 固定分组ok={fixed_caps_ok(m,cnt,s,j,tt)} '
                                  f'极端SSok={extreme_ss_ok(m,cnt,s)}')
                    else:
                        # 记录部分失败（信息）
                        if bad and nkill == 0:
                            pass
    print(f'汇总：采样点 {npts}，可装箱 {npack}，其中固定分组全型失败（反例）{nkill} 个')


if __name__ == '__main__':
    run()
