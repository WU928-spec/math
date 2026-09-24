"""E-nec-v3：mon2 + X 必要条件行 + 挤压行 + 值带行——razor 带不经 (W'') 闭合的决战。

新增合法必要行（合法性出处：JEL.md razor 挤压引理节 / 值带结构节）：
  XSQZ 挤压行（全域合法，cnt 无关）：Σ_i(s_i+j_i) + t <= m-1。
    合法性=razor 挤压引理（p 独箱 + OPT 各箱≤1 ⟹ Σℓ≤m−1−t）。agent-4 数据：50/76 残留点违反。
  XVBI 值带行（仅 c=0 形态合法——razor 带 c=0 ✓）：s_i + t <= 1 ∀i。
    合法性=值带结构①（senior>1−t 时 SS 不可配（和>2−3t>1）且 SJ 伴侣需<t≤任意 junior ⟹ 无处可去）。
    c≥1 时 senior 可独箱，行不合法 ⟹ 本版只在 c==0 时加入（护栏：单独消融可关）。
  XPS 伴侣供给行（备用，仅 c=0 且需要时）：#{i:s_i≥2t} ≤ #{p:j_p≤1−2t} 的线性化——
    senior 侧由 srt 序给（第 idx 大 senior <2t ⟺ 计数≤nS−1−idx）；
    junior 侧无全局序 ⟹ 用最弱合法形：j_0≤...≤j_jj（mon2）低端计数代理，单独消融标记。

用法：python a4_enec3.py scan   —— razor 残留 413 处 + 洞族 20 处闭合率（V2a vs V3 对比）
      python a4_enec3.py ablate —— 闭合代表逐族消融
"""
import sys, os, json, time
from fractions import Fraction as F
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a4_enec2 import build_v2a, is_inf
from pairing_feasible import bin_count_solutions

HERE = os.path.dirname(os.path.abspath(__file__))


def build_v3(m, cnt, k, use_sqz=True, use_vb=True, **kw):
    """build_v2a + 挤压行 + 值带行（c=0 时）。返回 (A,bc,bt,names,nv)。"""
    a, b, c, d, e, f = cnt
    nS = m - 1
    A, bc, bt, names, nv = build_v2a(m, cnt, k, **kw)

    def vs(i): return 2 + i
    def vj(i): return 2 + nS + i

    def zero(): return [F(0)] * nv
    if use_sqz:
        r = zero()
        for i in range(nS):
            r[vs(i)] = 1; r[vj(i)] = 1
        A.append(r); bc.append(F(m - 1)); bt.append(F(-1)); names.append('XSQZ')
    if use_vb and c == 0:
        for i in range(nS):
            r = zero(); r[vs(i)] = 1
            A.append(r); bc.append(F(1)); bt.append(F(-1)); names.append(f'XVB{i}')
    return A, bc, bt, names, nv


def razor_resid_cases(m_hi=14):
    """E-nec-v2 razor 残留（v2a 可行处），返回 [(m,cnt,k)]。"""
    out = []
    for m in range(4, m_hi + 1):
        for k in range(1, m):
            for cnt in bin_count_solutions(m):
                if not is_inf(*build_v2a(m, cnt, k)[:3]):
                    out.append((m, cnt, k))
    return out


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'scan'
    t0 = time.time()

    if cmd == 'scan':
        print('== razor 残留（v2a 可行点）在 V3 下的命运 ==', flush=True)
        res = razor_resid_cases(14)
        print(f'残留总数（m=4..14）: {len(res)}', flush=True)
        n_close = 0
        survivors = []
        for m, cnt, k in res:
            if is_inf(*build_v3(m, cnt, k)[:3]):
                n_close += 1
            else:
                survivors.append((m, cnt, k))
        print(f'V3（+挤压+值带）重闭合: {n_close}/{len(res)}  ({time.time()-t0:.0f}s)')
        from collections import Counter
        sc = Counter((tuple(c[2:]), ) for _, c, _ in survivors)
        print(f'存活 {len(survivors)} 处，按 (c,d,e,f):', dict(sc))
        print('存活清单（前 25）:', survivors[:25])

        print('== 洞族 20 处在 V3 下的命运 ==', flush=True)
        holes = [json.loads(l) for l in open(os.path.join(HERE, 'p2_holes_big.jsonl'))
                 if json.loads(l)['m'] <= 20]
        n_surv = 0
        for h in holes:
            m, cnt, k = h['m'], tuple(h['cnt']), h['k']
            if not is_inf(*build_v3(m, cnt, k)[:3]):
                n_surv += 1
                print(f'  存活 m={m} cnt={cnt} k={k}')
        print(f'洞族存活 {n_surv}/20  ({time.time()-t0:.0f}s)')

    elif cmd == 'ablate':
        # 闭合代表消融：定位挤压/值带/ mon2 / X 的承重分配
        shown = 0
        for m in range(8, 15):
            if shown >= 5:
                break
            for cnt in bin_count_solutions(m):
                a, b, c, d, e, f = cnt
                if not (c == 0 and d == 1 and a <= 2):
                    continue
                for k in (2, m - 1):
                    if k < 1 or k >= m:
                        continue
                    A, bc, bt, names, nv = build_v3(m, cnt, k)
                    if not is_inf(A, bc, bt):
                        continue
                    print(f'm={m} cnt={cnt} k={k}（V3 闭合）消融:')
                    for fam, kw in [('去挤压XSQZ', dict(use_sqz=False)),
                                    ('去值带XVB', dict(use_vb=False)),
                                    ('去mon2', dict(use_mon2=False)),
                                    ('去XSS', dict(use_xss=False)),
                                    ('去XVOL+XBIG', dict(use_xvol=False, use_xbig=False))]:
                        A2, bc2, bt2, _, _ = build_v3(m, cnt, k, **kw)
                        print(f'   {fam:12s}: {"仍INF" if is_inf(A2, bc2, bt2) else "FEASIBLE（回弹=承重）"}')
                    shown += 1
                    if shown >= 5:
                        break
                if shown >= 5:
                    break
