"""a3_tight_stress.py —— 对 main_tight_construct 的敌意复核压测（agent-3）。
三点补测：
①e=1（cnt2：2 SS 对+JJ 对）全紧构造（main 实验疑仅 e=0）；
②(2b) 楔 t∈(5/16, 0.32] 密网格（main 网格 0.28/0.30/0.32/1/3 对楔内覆盖薄）；
③assign_juniors 窗口 K 帽敏感度：hi=min(2t,K−s)（main 版，编码"放入时 ≤K"）vs
  hi=min(2t,1−s)（放松版，允许 fallback 超 K 至 OPT 容量 1）——若判决翻转，
  main 的 "4368 mon2-death" 含窗口过紧假死（与 agent-3 的 A2/§1.3 fallback 审计同族）。
构造逻辑照抄 main_tight_construct.build_tight（e=0），e=1 为同构扩展。
"""
import numpy as np
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from main_phantom_corner import assign_juniors


def build_tight_e0(m, t, rng):
    nS = m - 1
    while True:
        s = sorted(rng.uniform(1 - 2 * t, 1 - t, nS))
        i = rng.integers(0, nS)
        u = s[i]; v = 1.0 - u
        if not (1 - 2 * t - 1e-9 <= v <= 1 - t + 1e-9):
            return None
        s = sorted(rng.uniform(1 - 2 * t, 1 - t, nS - 2).tolist() + [u, v])
        break
    s2 = list(s)
    for val in (u, v):
        for idx, x in enumerate(s2):
            if abs(x - val) < 1e-12:
                del s2[idx]; break
    comp = [1.0 - x for x in s2]
    j1 = rng.uniform(t, (1 - t) / 2)
    j2 = 1 - t - j1
    j = sorted(comp + [j1, j2])
    if j[0] + j[1] + j[2] <= 1 + 1e-12:
        return None
    p = rng.uniform(max(5 / 4 - t + 0.001, 0.9), 1.0)
    return p, s, j


def build_tight_e1(m, t, rng):
    """cnt2：2 个不交 SS 对（各和=1）+ JJ 对（和=1）+ JJJ={t,j1,j2}（和=1）。"""
    nS = m - 1
    while True:
        base = rng.uniform(1 - 2 * t, 1 - t, nS - 4).tolist()
        pairs = []
        ok = True
        for _ in range(2):
            u = rng.uniform(1 - 2 * t, 1 - t)
            v = 1.0 - u
            if not (1 - 2 * t - 1e-9 <= v <= 1 - t + 1e-9):
                ok = False; break
            pairs += [u, v]
        if not ok:
            return None
        s = sorted(base + pairs)
        if len(s) == nS:
            break
    s2 = list(s)
    for val in pairs:
        for idx, x in enumerate(s2):
            if abs(x - val) < 1e-12:
                del s2[idx]; break
    comp = [1.0 - x for x in s2]
    # JJ 对：从 comp 取一对改为 JJ 箱（其和须=1——comp 本身=1−s，JJ 对和=2−(s_a+s_b) 须=1 ⟹ s_a+s_b=1，
    # 但 SS 对已用掉全部和=1 的对；JJ 对从 junior 侧自由取两件和=1：直接构造 jJ1+jJ2=1）
    j1 = rng.uniform(t, (1 - t) / 2)
    j2 = 1 - t - j1
    jJ1 = rng.uniform(t, 0.5)
    jJ2 = 1.0 - jJ1
    j = sorted(comp + [j1, j2, jJ1, jJ2][:4])  # 池 = 残差互补 + {j1,j2}(JJJ) + {jJ1,jJ2}(JJ)
    # 池件数 = (nS-4) + 2 + 2 = nS ✓；但 juniors 变量只 nS 个（j_1..j_{nS}）+ t：池 = juniors ∪ {t}
    # cnt2 池件数 b+3d+2e = (nS-4)+3+2 = nS+1 = nS juniors + t ✓ 故 juniors 多重集 = comp+{j1,j2,jJ1,jJ2} 中 nS 件？
    # 错：comp 是残差 senior(nS-4) 的互补 junior(nS-4 件) + j1,j2 + jJ1,jJ2 = nS 件 juniors ✓ + t = nS+1 池 ✓
    if len(j) != nS:
        return None
    if j[0] + j[1] + j[2] <= 1 + 1e-12:
        return None
    p = rng.uniform(max(5 / 4 - t + 0.001, 0.9), 1.0)
    return p, s, j


def assign_relaxed(s, j, p, t, am, q1):
    """assign_juniors 的放松窗口版：hi = min(2t, 1−s)（允许负载至 OPT 容量 1，容 fallback 超 K）。"""
    nS = len(s)
    K = 5 * (am + q1) / 4
    jj = max((i for i in range(nS) if s[i] <= K - q1 + 1e-12), default=-1)
    if jj < 0:
        return False, 'nojj'
    lo = [max(t, p - s[i] + 1e-4) for i in range(nS)]
    hi = [min(2 * t, 1.0 - s[i]) for i in range(nS)]   # ← 唯一改动：K−s 换 1−s
    if any(lo[i] > hi[i] + 1e-12 for i in range(nS)):
        return False, 'window'
    jvals = list(j); q1v = jvals[-1]
    if not (lo[jj] - 1e-12 <= q1v <= hi[jj] + 1e-12):
        return False, 'fs'
    pool = jvals[:-1]
    assign = {jj: q1v}
    rest = list(pool); prev = -1
    for i in range(jj):
        cand = [v for v in rest if v >= prev - 1e-12 and lo[i] - 1e-12 <= v <= hi[i] + 1e-12]
        if not cand:
            return False, 'mon2'
        v = min(cand)
        assign[i] = v; rest.remove(v); prev = v
    hims = list(range(jj + 1, nS))
    def dfs(idx, rest):
        if idx == len(hims):
            return True
        i = hims[idx]
        for v in list(rest):
            if lo[i] - 1e-12 <= v <= hi[i] + 1e-12:
                assign[i] = v; rest.remove(v)
                if dfs(idx + 1, rest):
                    return True
                rest.append(v); del assign[i]
        return False
    if not dfs(0, rest):
        return False, 'hi'
    return True, 'ok'


def main():
    rng = np.random.default_rng(7)
    t0 = time.time()
    stats = {}
    # (2b) 楔密 t 网格 + e 两档 + 窗口两版
    for e, builder in [(0, build_tight_e0), (1, build_tight_e1)]:
        for m in range(6, 15):
            for t in [0.313, 0.315, 0.3175, 0.32, 0.325, 1 / 3]:
                n = 0; ok_main = ok_relax = 0
                for _ in range(150):
                    got = builder(m, t, rng)
                    if got is None:
                        continue
                    p, s, j = got
                    n += 1
                    am, q1 = s[0], j[-1]
                    ok1, _, _, _ = assign_juniors(s, j, p, t, am, q1)
                    ok2, _ = assign_relaxed(s, j, p, t, am, q1)
                    ok_main += bool(ok1); ok_relax += bool(ok2)
                stats[(e, m, t)] = (n, ok_main, ok_relax)
        print(f'e={e} 完成（{time.time()-t0:.0f}s）', flush=True)
    # 汇总
    flip = sum(1 for (n, a, b) in stats.values() if b > a)
    print('\ne=0 汇总（构造/main窗口/放松窗口）:')
    tot = [0, 0, 0]
    for (e, m, t), (n, a, b) in stats.items():
        if e == 0:
            tot = [tot[0] + n, tot[1] + a, tot[2] + b]
    print(' ', tot)
    print('e=1 汇总:')
    tot = [0, 0, 0]
    for (e, m, t), (n, a, b) in stats.items():
        if e == 1:
            tot = [tot[0] + n, tot[1] + a, tot[2] + b]
    print(' ', tot)
    nflip_cells = sum(1 for k, (n, a, b) in stats.items() if b != a)
    print(f'窗口判决不同的格数: {nflip_cells}/{len(stats)}（若>0：main 窗口过紧假死存在）')
    for k, (n, a, b) in stats.items():
        if b != a:
            print('  翻转格:', k, f'构造{n} main窗{a} 放松窗{b}')


if __name__ == '__main__':
    main()
