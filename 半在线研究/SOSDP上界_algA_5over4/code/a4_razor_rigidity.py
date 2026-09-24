"""razor 带 LP 极值点分层钉死核验（agent-4）：为刚性证明供数据。

两个点列：
  A) 鬼影洞（build_fixed 含固定分组行、无 mon2）：m=12..16 + m=18 razor 族，
     t 钉 {0.28,0.30,0.32,1/3} 网格提取可行点；
  B) razor 残留（E-nec-v2 变体 build_v2a：mon2+X行、无 caps）：
     (1,m-3,0,1,0,0) k∈{2,⌊m/2⌋,m-1}、(2,m-5,0,1,1,0) k∈{4,m-1}，m=8..16，同网格。

逐点核验（对照主代理 razor 挤压引理+值带结构推导）：
  (i) senior 分层数/层间隙（tol=2e-3 聚类）与配对帽差；
  (ii) SS 可行对图（边 s_i+s_j<=1+1e-6）：最小 2a 件是否被强制
       （a=1：s0 的唯一伴侣是否恰为 s1；一般 a：最小 2a 外点是否全孤立+内部匹配唯一）；
  (iii) 计数平衡：#(s>=2t)（值带强制 SJ 数）vs 伴侣供给 #（j∈[t,1-s] 逐 senior 存在性）；
  (iv) 挤压预算：Σℓ vs m-1-t，Σ(ℓ-p) vs (m-1)(t-1/4)-t（上界来自 razor 挤压引理）。
附：mon2 序 j_0<=...<=j_jj 满足性（鬼影点预期违反=非真角落的签名）。

输出: code/a4_razor_points.jsonl + 打印摘要。
"""
import sys, os, json, time
import numpy as np
from scipy.optimize import linprog
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farkas_fixed import build_fixed
from a4_enec2 import build_v2a

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'a4_razor_points.jsonl')
TGRID = [0.28, 0.30, 0.32, 1 / 3]


def extract(A, bc, bt, nv, t0):
    """钉 t=t0 提取可行点。返回 x 或 None。"""
    Af = np.array([[float(v) for v in row] for row in A])
    bcf = np.array([float(v) for v in bc], dtype=float)
    btf = np.array([float(v) for v in bt], dtype=float)
    A2 = Af.copy(); A2[:, 1] -= btf
    pin = np.zeros(nv); pin[1] = 1.0
    A2 = np.vstack([A2, pin, -pin])
    b2 = np.concatenate([bcf, [t0, -t0]])
    res = linprog(c=np.zeros(nv), A_ub=A2, b_ub=b2, bounds=(None, None), method='highs')
    return res.x if res.status == 0 else None


def tiers(vals, tol=2e-3):
    """聚类成层；返回 [(层值, 成员数)] 与最小层间隙。"""
    vs_ = sorted(vals)
    groups = [[vs_[0]]]
    for v in vs_[1:]:
        if v - groups[-1][-1] <= tol:
            groups[-1].append(v)
        else:
            groups.append([v])
    ts = [(float(np.mean(g)), len(g)) for g in groups]
    gap = min((ts[i + 1][0] - ts[i][0] for i in range(len(ts) - 1)), default=None)
    return ts, gap


def analyze(x, m, cnt, k, src):
    nS = m - 1
    a, b, c, d, e, f = cnt
    p, t = float(x[0]), float(x[1])
    s = np.array([float(v) for v in x[2:2 + nS]])
    j = np.array([float(v) for v in x[2 + nS:2 + 2 * nS]])
    am, q1 = float(x[2 + 2 * nS]), float(x[2 + 2 * nS + 1])
    K = 1.25 * (am + q1)
    rec = {'src': src, 'm': m, 'cnt': list(cnt), 'k': k, 't_pin': round(t, 5),
           'p': round(p, 5), 'p+t': round(p + t, 5), 'K': round(K, 5)}
    # (i) 分层
    st, sgap = tiers(s)
    jt, jgap = tiers(j)
    rec['s_tiers'] = [(round(v, 4), n) for v, n in st]
    rec['s_min_gap'] = round(sgap, 4) if sgap is not None else None
    rec['j_tiers'] = [(round(v, 4), n) for jv, n in jt for v in [jv]]
    rec['j_min_gap'] = round(jgap, 4) if jgap is not None else None
    # (ii) SS 可行对图
    ok_pair = lambda u, v: s[u] + s[v] <= 1 + 1e-6
    partner = {i: [v for v in range(nS) if v != i and ok_pair(i, v)] for i in range(nS)}
    rec['s0_partners'] = partner[0][:8]
    rec['s0_deg'] = len(partner[0])
    small = list(range(2 * a))
    rec['outside_2a_isolated'] = all(len(partner[i]) == 0 for i in range(2 * a, nS))
    # 最小 2a 内匹配（a<=2 直接判）
    if a == 1:
        rec['ss_forced_pair'] = [0, partner[0][0]] if len(partner[0]) == 1 else None
    elif a == 2:
        rec['ss_min2a_matchable'] = bool(
            (ok_pair(0, 3) and ok_pair(1, 2)) or (ok_pair(0, 2) and ok_pair(1, 3))
            or (ok_pair(0, 1) and ok_pair(2, 3)))
    # (iii) 计数平衡
    big = [i for i in range(nS) if s[i] >= 2 * t - 1e-9]
    rec['n_s_geq_2t'] = len(big)
    noband = [i for i in big if not np.any((j >= t - 1e-9) & (j <= 1 - s[i] + 1e-9))]
    rec['big_senior_no_partner'] = noband[:6]
    # (iv) 挤压预算
    ell = s + j
    rec['sum_ell'] = round(float(ell.sum()), 4)
    rec['squeeze_cap'] = round(m - 1 - t, 4)
    rec['sum_ell_minus_p'] = round(float((ell - p).sum()), 4)
    rec['budget_cap'] = round((m - 1) * (t - 0.25) - t, 4)
    # 附加签名：mon2 满足性、值带断言
    jj = k - 1
    rec['mon2_ok'] = bool(np.all(np.diff(j[:jj + 1]) >= -1e-9))
    rec['s_max_le_1-t'] = bool(s.max() <= 1 - t + 1e-6)
    return rec


def run_series(name, builder, cases, fout):
    n_ok = 0
    for m, cnt, k in cases:
        for t0 in TGRID:
            A, bc, bt, names, nv = builder(m, cnt, k)
            x = extract(A, bc, bt, nv, t0)
            if x is None:
                fout.write(json.dumps({'src': name, 'm': m, 'cnt': list(cnt), 'k': k,
                                       't_pin': round(t0, 5), 'feasible': False}) + '\n')
                continue
            rec = analyze(x, m, cnt, k, name)
            rec['feasible'] = True
            fout.write(json.dumps(rec) + '\n')
            n_ok += 1
            print(f'[{name}] m={m} cnt={cnt} k={k} t={t0:.4f}: '
                  f's层{len(rec["s_tiers"])} j层{len(rec["j_tiers"])} '
                  f's0度={rec["s0_deg"]} 2a外孤立={rec["outside_2a_isolated"]} '
                  f'#s>=2t={rec["n_s_geq_2t"]} 无伴侣={len(rec["big_senior_no_partner"])} '
                  f'Σℓ={rec["sum_ell"]}/{rec["squeeze_cap"]} Σ(ℓ-p)={rec["sum_ell_minus_p"]}/{rec["budget_cap"]} '
                  f'mon2={rec["mon2_ok"]} smax≤1-t={rec["s_max_le_1-t"]}', flush=True)
    return n_ok


if __name__ == '__main__':
    t_start = time.time()
    ghosts = [(12, (2, 7, 0, 1, 1, 0), 11), (13, (2, 8, 0, 1, 1, 0), 12),
              (14, (2, 9, 0, 1, 1, 0), 13), (15, (2, 10, 0, 1, 1, 0), 14),
              (16, (2, 11, 0, 1, 1, 0), 15),
              (18, (3, 11, 0, 1, 2, 0), 15), (18, (3, 11, 0, 1, 2, 0), 17)]
    resid = []
    for m in [8, 10, 12, 14, 16]:
        resid.append((m, (1, m - 3, 0, 1, 0, 0), 2))
        resid.append((m, (1, m - 3, 0, 1, 0, 0), m - 1))
        resid.append((m, (2, m - 5, 0, 1, 1, 0), 4))
        resid.append((m, (2, m - 5, 0, 1, 1, 0), m - 1))
    with open(OUT, 'w') as fout:
        nA = run_series('ghost', lambda m, c, k: build_fixed(m, c, k), ghosts, fout)
        nB = run_series('resid', lambda m, c, k: build_v2a(m, c, k), resid, fout)
    print(f'完成: ghost {nA}/{len(ghosts)*4} 点可行, resid {nB}/{len(resid)*4} 点可行, '
      f'{time.time()-t_start:.0f}s -> {OUT}')
