"""形 B (2,m-5,0,1,1,0) 可装箱角落构造搜索 m=6..14（证伪 junior 预算矛盾主张）。
参数化族: t, p, SS 对(两种模态), 大 senior(数量 nS-4), 绑机 junior 分配, typed_feasible 验证。
"""
import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a2_g1_flow import typed_feasible

def try_construct(m, t0, rng, trials=400):
    nS = m - 1
    for _ in range(trials):
        p = 5 / 4 - t0 + 0.003 + rng.random() * 0.02
        if p > 1: continue
        mode = rng.integers(0, 2)  # 0: 全小 SS (t<0.3 型); 1: 混合对 (t>=0.3 型)
        if mode == 0:
            s4 = 0.45 + rng.random(4) * (min(0.5, 2 * t0) - 0.45)
        else:
            hi = min(2 * t0, 0.62)
            s4 = np.concatenate([0.37 + rng.random(2) * 0.05, hi - 0.04 + rng.random(2) * 0.04])
            if np.any(s4 > 2 * t0): continue
        sbig = 2 * t0 + 0.01 + rng.random(nS - 4) * (1 - t0 - 2 * t0 - 0.02)  # (2t, 1-t]
        if np.any(sbig > 1 - t0) or np.any(sbig <= 2 * t0): continue
        s = np.concatenate([s4, sbig])
        # 绑机 junior: 每台 s 需要 j>=p-s (band [t,2t)); 之后 OPT 由 typed_feasible 判
        # 随机可行绑机: 从 band 采样 j 直到全部满足 (或按需构造)
        for _ in range(50):
            j = t0 + rng.random(nS) * (min(2 * t0, 0.66) - t0)
            if np.all(s + j >= p - 1e-9):
                pool = list(j) + [t0]
                if typed_feasible(list(s), pool, (2, m - 5, 0, 1, 1, 0)):
                    return s, j, p
    return None

if __name__ == '__main__':
    for m in [6, 8, 10, 12, 14]:
        found = None
        for t0 in [0.26, 0.28, 0.30, 0.32, 1/3 - 0.005]:
            rng = np.random.default_rng(hash((m, round(t0, 3))) % 2**31)
            r = try_construct(m, t0, rng)
            if r is not None:
                found = (t0, r); break
        if found:
            t0, (s, j, p) = found
            print(f'm={m}: ** 可装箱构造成功 ** t={t0:.3f} p={p:.3f}', flush=True)
            print(f'   s={np.round(s,3)}'); print(f'   j={np.round(j,3)}')
        else:
            print(f'm={m}: 构造失败（{5} 个 t × 400 试）', flush=True)
