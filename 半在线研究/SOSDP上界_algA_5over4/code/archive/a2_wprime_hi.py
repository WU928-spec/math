"""a2_wprime_hi.py — (W'')-hi 区执行块：角落值域"可装箱 ⟺ 规范可装箱"的逐点检验。

判决目标（比 (P) 弱一档、比 (P) 反例更值钱的反例）：
  x ∈ 角落值域（Π* 采样 + 松弛区采样）且存在某装箱 ⟹ 规范指派（同 cnt）也可装箱。
  反例：x 任意可装箱但规范不可装箱 ⟹ (W'') 死亡 ⟹ BREAKING。
规范指派（agent-3 交换引理 §11.0 的 senior 侧 w.l.o.g. 形式 + 机器序 junior 侧）：
  SS 箱 = 最小 2a senior 的极端配对 (s_i, s_{2a-1-i})；SJ 箱 = 次小 b 个 senior 配
  机器序池 j_0..j_{b-1}；JJJ/JJ/J 依次取池后续段；t 殿后池位。
实现：can_pack_fast 扩展为返回装箱方案；cnt 由方案计算；规范指派重建后逐箱核验。
牙齿：合成"真实可装但规范难装"实例（规范 SJ 配对超载、junior 置换后可行）必须被标出。
用法：python a2_wprime_hi.py [--m 6,8,12,16] [--relax]  (relax=去 danger 采样可装箱点)
"""
import numpy as np
from functools import lru_cache
from itertools import combinations
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a2_transfer_falsifier_v2 import feasible_at2, points_of, nv_of

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'a2_wprime_progress.jsonl')


def pack_recover(items, m, cap=1.0):
    """精确装箱并返回方案（list of frozenset 物品索引）；不可装返回 None。窗口结构版。"""
    items_sorted = sorted(range(len(items)), key=lambda i: -items[i])
    vals = [items[i] for i in items_sorted]
    n = len(vals)
    if vals[-1] <= 0.25 + 1e-12:
        return None
    feas_by_anchor = {}
    for r in (1, 2, 3):
        for comb in combinations(range(n), r):
            s = sum(vals[i] for i in comb)
            if s <= cap + 1e-9:
                mask = 0
                for i in comb:
                    mask |= 1 << i
                feas_by_anchor.setdefault(comb[0], []).append(mask)

    @lru_cache(maxsize=None)
    def dfs(mask, k):
        if mask == 0:
            return ()
        if k == 0:
            return None
        anchor = (mask & (-mask)).bit_length() - 1
        for S in feas_by_anchor.get(anchor, ()):
            if S & ~mask == 0:
                r = dfs(mask ^ S, k - 1)
                if r is not None:
                    return (S,) + r
        return None
    r = dfs((1 << n) - 1, m)
    if r is None:
        return None
    return [[items_sorted[i] for i in range(n) if S >> i & 1] for S in r]  # 原 items 的索引


def cnt_of(bins, nS):
    """bins = 物品索引列表（原值）。senior=前 nS 个 s_i（按值域顺序 idx 2..2+nS-1 传入）。
    简化：调用方传入 (bin_comp) 其中 comp=(#senior, #junior)。p 箱单列不计。"""
    a = sum(1 for s, j in bins if s == 2 and j == 0)
    b = sum(1 for s, j in bins if s == 1 and j == 1)
    c = sum(1 for s, j in bins if s == 1 and j == 0)
    d = sum(1 for s, j in bins if s == 0 and j == 3)
    e = sum(1 for s, j in bins if s == 0 and j == 2)
    f = sum(1 for s, j in bins if s == 0 and j == 1)
    return (a, b, c, d, e, f)


def canonical_bins(s_sorted, j_pool, cnt):
    """规范指派（senior 侧交换引理形式 + 机器序 junior）。
    s_sorted: senior 升序；j_pool: 机器序 junior 池（含 t 殿后）。
    返回 bins（值列表）或 None（指派超出池长）。"""
    a, b, c, d, e, f = cnt
    bins = []
    for i in range(a):
        bins.append([s_sorted[i], s_sorted[2 * a - 1 - i]])       # 极端配对
    for k in range(b):
        bins.append([s_sorted[2 * a + k], j_pool[k]])             # SJ 规范
    for i in range(c):
        bins.append([s_sorted[2 * a + b + i]])                    # S 独占
    idx = b
    for _ in range(d):
        bins.append([j_pool[idx], j_pool[idx + 1], j_pool[idx + 2]]); idx += 3
    for _ in range(e):
        bins.append([j_pool[idx], j_pool[idx + 1]]); idx += 2
    for _ in range(f):
        bins.append([j_pool[idx]]); idx += 1
    if idx != len(j_pool):
        return None
    return bins


def test_point(x, m):
    """返回 ('packable'/'unpackable'/'off-model', canonical_ok or None, detail)。"""
    nS = m - 1
    p, t = x[0], x[1]
    s = list(x[2:2 + nS]); j = list(x[2 + nS:2 + 2 * nS])
    items = [p] + s + j + [t]
    bins = pack_recover(items, m)
    if bins is None:
        return ('unpackable', None, None)
    # p 必须独占（角落模型）；按索引分类（p=0, seniors=1..nS, juniors=nS+1..2*nS, t=末位）
    pb = [bb for bb in bins if 0 in bb]
    if len(pb) != 1 or len(pb[0]) != 1:
        return ('off-model', None, None)
    rest = [bb for bb in bins if 0 not in bb]
    comp = []
    for bb in rest:
        ns = sum(1 for idx in bb if 1 <= idx <= nS)
        comp.append((ns, len(bb) - ns))
    cnt = cnt_of(comp, nS)
    s_sorted = sorted(s)
    j_pool = j + [t]
    cb = canonical_bins(s_sorted, j_pool, cnt)
    if cb is None:
        return ('packable', None, ('cnt', cnt))
    ok = all(sum(bb) <= 1 + 1e-9 for bb in cb)
    return ('packable', ok, ('cnt', cnt, None if ok else cb))


def synth_teeth():
    """合成牙齿：规范 SJ 配对超载但 junior 置换可行的实例（§12.1 形态修复版）。
    seniors 升序 [0.43,0.43,0.49,0.49,0.62,0.62]，junior 机器序 [0.52,0.52,0.46,0.46,0.33,0.33]，
    t=0.30。真实装箱存在（置换）；规范 SJ (s_2,j_0)=0.49+0.52>1 死。"""
    s = [0.43, 0.43, 0.49, 0.49, 0.62, 0.62]
    j = [0.52, 0.52, 0.46, 0.46, 0.33, 0.33]
    t = 0.30
    items = list(s) + list(j) + [t]
    m = 7  # 7 箱（senior 6 + 池 7）
    bins = pack_recover(items, m)
    if bins is None:
        return False, '合成例本身不可装（无牙）'
    comp = []
    for bb in bins:
        ns = sum(1 for idx in bb if idx < 6)   # 索引 <6 = senior（items = s+j+[t]）
        comp.append((ns, len(bb) - ns))
    cnt = cnt_of(comp, 6)
    cb = canonical_bins(sorted(s), j + [t], cnt)
    ok = cb is not None and all(sum(bb) <= 1 + 1e-9 for bb in cb)
    return (not ok), f'cnt={cnt} 规范可行={ok}（期望 False=有牙：规范死而真实活）'


def main():
    args = sys.argv[1:]
    ms = [int(x) for x in args[args.index('--m') + 1].split(',')] if '--m' in args else [6, 8, 12, 16]
    relax = '--relax' in args
    if relax:
        import a2_transfer_falsifier_v2 as _v2
        from hole_close import build_close as _bc
        def _poly_relaxed(m, k):
            if (m, k) not in _v2._POLY:
                A, bc, bt, names, nv = _bc(m, (1, m - 3, 0, 1, 0, 0), k, use_ammin=True)
                keep = [i for i, nm in enumerate(names) if nm not in ('SS', 'SJ', 'JJJ', 'JJ', 'danger')]
                _v2._POLY[(m, k)] = ([A[i] for i in keep], [bc[i] for i in keep], [bt[i] for i in keep], nv)
            return _v2._POLY[(m, k)]
        _v2._POLY.clear()
        globals()['feasible_at2'] = __import__('a2_transfer_falsifier_v2').feasible_at2
        _v2.polytope = _poly_relaxed
        import a2_transfer_falsifier_v2 as _m
        globals()['feasible_at2'] = _m.feasible_at2  # float_form 走 _v2.polytope（已替换）
    t0 = time.time()
    teeth_ok, teeth_msg = synth_teeth()
    print(f'牙齿: {teeth_msg} => {"有牙 ✓" if teeth_ok else "无牙/规范恰好可行（注明）"}', flush=True)
    if '--synth' in args:
        synth_mode(ms)
        return
    stats = {'pts': 0, 'packable': 0, 'off': 0, 'wp_ok': 0, 'wp_bad': 0}
    bad_lines = []
    for m in ms:
        nS = m - 1
        tl = (m - 1) / (4 * (m - 2))
        ks = [k for k in range(1, m) if 2 <= k <= m - 3] or list(range(1, m))
        for k in ks:
            for tt in np.linspace(tl + 0.002, 1 / 3, 3):
                feas, x = feasible_at2(m, k, [], float(tt))
                if not feas:
                    continue
                pts = [x]
                rng = np.random.default_rng(1)
                for _ in range(2):
                    f2, x2 = feasible_at2(m, k, [], float(tt), direction=rng.normal(size=nv_of(m)))
                    if f2:
                        pts.append(x2)
                for pt in pts:
                    stats['pts'] += 1
                    tag, cok, detail = test_point(pt, m)
                    if tag == 'packable':
                        stats['packable'] += 1
                        if cok is True:
                            stats['wp_ok'] += 1
                        else:
                            stats['wp_bad'] += 1
                            bad_lines.append({'m': m, 'k': k, 't': float(tt), 'detail': str(detail)})
                            print(f'  ✗✗ (W″) 反例候选 m={m} k={k} t={tt:.4f} {detail}', flush=True)
                    elif tag == 'off-model':
                        stats['off'] += 1
        print(f'  m={m}: 累计 {stats}', flush=True)
    with open(OUT, 'a') as f:
        f.write(json.dumps({'ts': time.time(), 'ms': ms, 'stats': stats, 'bad': bad_lines}) + '\n')
    print(f"=== (W'')-hi 判定：{stats}  耗时 {time.time()-t0:.0f}s ===")
    print('判决:', '(W″) 反例出现——立即 BREAKING' if stats['wp_bad'] else '采样内规范等价成立（可装箱点全规范可装箱）')



def synth_packable(rng, m):
    """公平版：先定机器对 (s_i,j_i)（角落数据：pair s_i+j_i>=p、窄带、senior>1-2t），
    junior 机器指派对抗式（大 junior 配小 senior = 鬼影形态）或随机；
    DFS 求真实装箱（找不到则弃），由装箱算 cnt，规范指派按机器序 junior。"""
    nS = m - 1
    for _ in range(80):
        t = float(rng.uniform(0.26, 0.34))
        p = float(rng.uniform(1.26 - t, 1.0))
        s = sorted(rng.uniform(1 - 2 * t + 0.005, 0.75, nS))
        j = rng.uniform(t, 2 * t - 0.005, nS)
        if rng.random() < 0.5:
            j = sorted(j, reverse=True)   # 鬼影形态：大 junior 配小 senior
        if not all(s[i] + j[i] >= p for i in range(nS)):
            continue
        items = [p] + list(s) + list(j) + [t]
        bins = pack_recover(items, m)
        if bins is None:
            continue
        pb = [bb for bb in bins if 0 in bb]
        if len(pb) != 1 or len(pb[0]) != 1:
            continue
        rest = [bb for bb in bins if 0 not in bb]
        comp = []
        for bb in rest:
            ns = sum(1 for idx in bb if 1 <= idx <= nS)
            comp.append((ns, len(bb) - ns))
        cnt = cnt_of(comp, nS)
        return list(s), list(j), t, p, cnt
    return None


def synth_mode(ms):
    """合成可装箱实例的规范等价检验 + 角落约束筛查。"""
    rng = np.random.default_rng(2026)
    st = {'gen': 0, 'canon_ok': 0, 'canon_bad': 0, 'corner_packable': 0, 'corner_canon_bad': 0}
    bad_examples = []
    for m in ms:
        for _ in range(int(__import__('os').environ.get('A2_SYNTH_N', '4000'))):
            r = synth_packable(rng, m)
            if r is None:
                continue
            s, j, t, p, cnt = r
            st['gen'] += 1
            s_sorted = sorted(s)
            j_pool = list(j) + [t]
            cb = canonical_bins(s_sorted, j_pool, cnt)
            okc = cb is not None and all(sum(bb) <= 1 + 1e-9 for bb in cb)
            # 角落约束筛查（mach/pair、窄带、danger、单调非必须——只查 pair+danger+带）
            pairs = sorted(zip(s, j), key=lambda z: -z[0])
            pair_ok = all(si + ji >= p - 1e-9 for si, ji in pairs)
            danger = p + t > 1.25
            band = all(t - 1e-9 <= ji <= 2 * t for ji in j) and all(si > 1 - 2 * t for si in s)
            is_corner = pair_ok and danger and band
            if not okc:
                st['canon_bad'] += 1
                if is_corner:
                    st['corner_canon_bad'] += 1
                    bad_examples.append({'m': m, 'cnt': cnt, 's': s, 'j': j, 't': t, 'p': p})
            elif is_corner:
                st['corner_packable'] += 1
        print(f'  m={m}: {st}', flush=True)
    print(f"=== 合成模式：{st} ===")
    if bad_examples:
        print(f'  ✗✗ 角落满足+可装箱+规范不可装箱的反例 {len(bad_examples)} 个！首例: {bad_examples[0]}')
    return st, bad_examples


if __name__ == '__main__':
    main()
