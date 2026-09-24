"""main_hall_dissect.py —— 可达见证的装箱失败机理解剖（Hall 违反子提取）。
cnt=(1,m-3,0,1,0,0) 时箱型唯一：1 个 SS + (m-3) 个 SJ + 1 个 JJJ。
枚举 (SS对, JJJ三元组[from juniors∪{t}])，剩余做二部完美匹配（u+v<=1 为边）。
全部选择失败 ⟹ 不可装箱；对每个见证找"最大匹配亏缺"的 Hall 违反子并打印成分。
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from itertools import combinations
from main_open_witness import sample_witnesses
from toolbox import fallback_event


def max_match(seniors, juniors):
    """seniors x juniors 二部图(u+v<=1)，返回(匹配数, 未匹配senior下标集, 匹配映射)。"""
    n, r = len(seniors), len(juniors)
    adj = [[v for v in range(r) if seniors[u] + juniors[v] <= 1 + 1e-12] for u in range(n)]
    mt = [-1] * r

    def dfs(u, seen):
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                if mt[v] == -1 or dfs(mt[v], seen):
                    mt[v] = u
                    return True
        return False

    cnt = 0
    for u in sorted(range(n), key=lambda u: len(adj[u])):
        if dfs(u, set()):
            cnt += 1
    matched_u = set(mt)
    free_u = [u for u in range(n) if u not in matched_u]
    return cnt, free_u, mt, adj


def hall_violator(seniors, juniors, mt, adj, free_u):
    """从未匹配 senior 出发的交错可达集 S'；|N(S')|=|S'|-亏缺。返回 (S', N(S'))。"""
    reach_u = set(free_u)
    reach_v = set()
    changed = True
    while changed:
        changed = False
        for u in list(reach_u):
            for v in adj[u]:
                if v not in reach_v:
                    reach_v.add(v)
                    changed = True
                    if mt[v] != -1 and mt[v] not in reach_u:
                        reach_u.add(mt[v])
    return sorted(reach_u), sorted(reach_v)


def dissect(m=10, cnt=(1, 7, 0, 1, 0, 0), k=5, nsample=6, maxpairs=2):
    here = os.path.dirname(os.path.abspath(__file__))
    recs = [json.loads(l) for l in open(os.path.join(here, 'main_jjj_enum.jsonl'))]
    r = next(x for x in recs if x['m'] == m and tuple(x['cnt']) == cnt and x['k'] == k)
    pairs = [tuple(p) for p in r['feas_pairs']][:maxpairs]
    pts, nS = sample_witnesses(m, cnt, k, pairs, nsample, seed=m * 991 + k)
    print(f"见证点 {len(pts)} 个（m={m} cnt={cnt} k={k}）")
    npack = 0
    for idx, (pi, pj, x) in enumerate(pts):
        p, t = x[0], x[1]
        s = list(x[2:2 + nS])
        j = list(x[2 + nS:2 + 2 * nS])
        seq = sorted([p] + s, reverse=True) + sorted(j + [t], reverse=True)
        if fallback_event(seq, m) is None:
            continue
        # 箱型唯一：1 SS + (m-3) SJ + 1 JJJ。枚举 (SS对, JJJ三元组)
        best = None
        packable = False
        jpool = list(range(nS))  # junior 下标池；t 用下标 nS 表示
        for ss in combinations(range(nS), 2):
            if s[ss[0]] + s[ss[1]] > 1 + 1e-12:
                continue
            rem_s = [u for u in range(nS) if u not in ss]
            for t3 in combinations(range(nS + 1), 3):
                vals = [(j[v] if v < nS else t) for v in t3]
                if sum(vals) > 1 + 1e-12:
                    continue
                rem_j = [j[v] for v in range(nS) if v not in t3]
                cnt_, free_u, mt, adj = max_match([s[u] for u in rem_s], rem_j)
                if cnt_ == len(rem_s):
                    packable = True
                    print(f"  !! 可装箱见证 #{idx}: SS={ss} JJJ={t3}")
                    npack += 1
                    break
                if best is None or cnt_ > best[0]:
                    best = (cnt_, ss, t3, free_u, mt, adj, rem_s, rem_j)
            if packable:
                break
        if packable:
            continue
        cnt_, ss, t3, free_u, mt, adj, rem_s, rem_j = best
        Sv, Nv = hall_violator([s[u] for u in rem_s], rem_j, mt, adj, free_u)
        sv_vals = [round(rem_s and s[rem_s[u]], 3) for u in Sv]
        nv_vals = [round(rem_j[v], 3) for v in Nv]
        hi = 'hi' if all(rem_s[u] >= k for u in Sv) else ('混合' if any(rem_s[u] >= k for u in Sv) else '低')
        print(f"  见证#{idx} 不可装箱：最佳缺 {len(rem_s)-cnt_}，Hall违反子 |S'|={len(Sv)} |N'|={len(Nv)} "
              f"senior来源={hi} S'值={sv_vals} N'值={nv_vals}")
    print(f"解剖结束：可达见证中可装箱 {npack} 个")


if __name__ == '__main__':
    dissect()
