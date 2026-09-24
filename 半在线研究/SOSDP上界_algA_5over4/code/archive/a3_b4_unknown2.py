"""a3_b4_unknown2.py —— B4 攻击二过：DFS 超预算（未知）见证的 cnt 形式装箱判定。
razor 带计数守恒强制装箱必属两 cnt 形式之一 ⟹ cnt 形式装箱 ⟺ 自由装箱。
cnt 形式判定=匹配问题（多项式）：枚举 SS 对（族1: C(nS,2)；族2: 无序对的对）
× JJJ 三元组（池 nS+1 件含 t，C(nS+1,3)），残差链图 SJ 匹配（贪心可判）。
输入 a3_b4_attack2.jsonl 的 unk>0 记录 → 重新取点（同 LP）→ cnt 形式判定。
"""
import numpy as np
from scipy.optimize import linprog
from itertools import combinations
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a3_b4_attack2 import build_rows


def cnt_packable(s, j, t, cnt, eps=1e-9):
    """池 = seniors s + juniors j + {t}；razor 两族 cnt 形式装箱判定（预筛候选+反向匹配判定）。
    链图 SJ 可行性=反向配对全 <=1（minimax 最优）。"""
    a, b, c, d, e, f = cnt
    nS = len(s)
    pool = list(j) + [t]
    np_ = len(pool)
    # 预筛：合格 SS senior 对、JJJ 三元组、JJ 对
    ss_pairs = [(u, v) for u, v in combinations(range(nS), 2) if s[u] + s[v] <= 1 + eps]
    triples = [tr for tr in combinations(range(np_), 3) if sum(pool[x] for x in tr) <= 1 + eps]
    jj_pairs = set()
    for u, v in combinations(range(np_), 2):
        if pool[u] + pool[v] <= 1 + eps:
            jj_pairs.add((u, v))

    def sj_ok(free_s, free_j):
        if len(free_s) != len(free_j):
            return False
        ps = sorted(free_s, key=lambda i: -s[i])       # senior 降序（最受限优先）
        pj = sorted(free_j, key=lambda x: pool[x])      # junior 升序（大 senior 配小 junior）
        return all(s[ps[r]] + pool[pj[r]] <= 1 + eps for r in range(len(ps)))

    def sj_ok_e1(free_s, free_j):
        """e=1 精确判定：|free_j| = |free_s|+2，须删恰 2 件（JJ 对和<=1）使反向配对可行。
        最优删除=最大两件（阶统计量逐位最小 ⟹ 任何删除可行性不超此）；
        规范化可行 ⟹ 剩 2 大；其和<=1 即成。和>1 时枚举含/不含两大件的合格 JJ 对（罕见）。"""
        ns_, nj_ = len(free_s), len(free_j)
        if nj_ != ns_ + 2:
            return False
        pj = sorted(free_j, key=lambda x: pool[x])
        keep = pj[:ns_]
        if not sj_ok(free_s, keep):
            return False                       # 最优删除都失败 ⟹ 一切删除失败
        z1, z2 = pj[-2], pj[-1]                # 规范化剩余 = 最大两件
        if pool[z1] + pool[z2] <= 1 + eps:
            return True
        # 罕见支：须把 z1/z2 压入匹配，删别处合格对
        for u, v in jj_pairs:
            if u not in free_j or v not in free_j or (u == z1 and v == z2):
                continue
            rem = [x for x in free_j if x != u and x != v]
            if sj_ok(free_s, rem):
                return True
        return False

    def ss_sets(indices, a):
        if a == 0:
            yield ()
            return
        cand = [(u, v) for u, v in ss_pairs if u in indices and v in indices]
        for u, v in cand:
            rest = [w for w in indices if w != u and w != v]
            for tail in ss_sets(rest, a - 1):
                yield ((u, v),) + tail

    for ss in ss_sets(list(range(nS)), a):
        used_s = {w for pr in ss for w in pr}
        free_s = [i for i in range(nS) if i not in used_s]
        for tr in triples:
            free_j = [x for x in range(np_) if x not in tr]
            if e == 0:
                if sj_ok(free_s, free_j):
                    return True
            else:
                if sj_ok_e1(free_s, free_j):
                    return True
    return False


def main():
    t0 = time.time()
    base = os.path.dirname(os.path.abspath(__file__))
    recs = [json.loads(l) for l in open(os.path.join(base, 'a3_b4_attack2.jsonl'))]
    unk = [r for r in recs if r.get('unk', 0) > 0]
    opath = os.path.join(base, 'a3_b4_unknown2.jsonl')
    done = set()
    if os.path.exists(opath):
        for l in open(opath):
            try:
                r = json.loads(l); done.add((r['m'], tuple(r['cnt']), r['k'], r['q'], r['mode']))
            except Exception:
                pass
        print(f'断点：已判 {len(done)} 条，续跑', flush=True)
    print(f'未知记录 {len(unk)} 条，二过开始')
    out = open(opath, 'a')
    npack = nclosed = 0
    for r in unk:
        m, cnt, k, q, mode = r['m'], r['cnt'], r['k'], r['q'], r['mode']
        if (m, tuple(cnt), k, q, mode) in done:
            continue
        nS = m - 1
        Af, bcf, nv = build_rows(m, cnt, k, q, mode)
        tlo = (m - 1) / (4 * (m - 2))
        bounds = [(None, None)] * nv + [(tlo, 1 / 3)]
        vs = lambda rr: 3 + (rr - 1); vj = lambda rr: 3 + nS + (rr - 1)
        verdict = 'closed'
        for csign in [1.0, -1.0, 0.0]:
            c = np.zeros(nv + 1); c[nv] = csign
            res = linprog(c=c, A_ub=Af, b_ub=bcf, bounds=bounds, method='highs')
            if res.status != 0:
                continue
            x = res.x
            s = [x[vs(rr)] for rr in range(1, nS + 1)]
            j = [x[vj(rr)] for rr in range(1, nS + 1)]
            if cnt_packable(s, j, x[nv], cnt):
                verdict = 'PACKABLE'
                npack += 1
                print(f'  ★ cnt 形式可装箱! m={m} cnt={cnt} k={k} q={q} {mode} t={x[nv]:.4f}',
                      flush=True)
                break
        if verdict == 'closed':
            nclosed += 1
        out.write(json.dumps(dict(m=m, cnt=cnt, k=k, q=q, mode=mode, verdict=verdict)) + '\n')
        out.flush()
    out.close()
    print(f'\n二过收官：闭合 {nclosed}，可装箱 {npack}（{time.time()-t0:.0f}s）')


if __name__ == '__main__':
    main()
