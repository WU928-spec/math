"""离散度引理 ∀m 链的数值护栏: 联合咬条件 (m-1)p > Σs + a 在可装箱实例上的检验。
主张: 可装箱 ⟹ Σℓ - a <= Σs (juniors 体积入 a 箱); 角落 ⟹ Σℓ >= (m-1)p;
离散度 ⟹ Σs 上界。核验: 合法实例(角落+可装箱)是否全满足 (m-1)p <= Σs + a - (即无咬)。
razor 带: 全序 k=m-1, 挤压行 Σℓ<=m-1-t。
"""
import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a2_g1_flow import typed_feasible
from pairing_feasible import bin_count_solutions

def guard(m, trials=2000, seed=0):
    rng = np.random.default_rng(seed)
    nS = m - 1
    bites = 0; feas = 0
    for _ in range(trials):
        t0 = 0.25 + rng.random() * (1/3 - 0.25)
        p = 5/4 - t0 + 0.003 + rng.random() * 0.02
        if p > 1: continue
        s = 1 - 2*t0 + rng.random(nS) * (0.75 - (1 - 2*t0))
        j = t0 + rng.random(nS) * t0 * 0.95
        if np.any(s + j < p - 1e-9): continue          # pair 下界
        if np.sum(s + j) > m - 1 - t0 + 0.05: continue  # 挤压行(容差)
        # 可装箱性(任一 cnt, p 独箱): 试 razor 带两形态 + 邻近
        ok_pack = False
        for cnt in [(1, m-3, 0, 1, 0, 0), (2, m-5, 0, 1, 1, 0)]:
            if cnt[1] < 0 or 2*cnt[0]+cnt[1]+cnt[2] != nS: continue
            if typed_feasible(list(s), list(j)+[t0], cnt):
                a = cnt[0]
                ok_pack = True
                break
        if not ok_pack: continue
        feas += 1
        # 咬条件: juniors 体积 V=Σj 需 <= a 箱(体积) 且池 m 件 <= 3a(计数)
        V = float(np.sum(j))
        if V > a + 1e-9 or m > 3 * a:
            bites += 1
    return feas, bites

if __name__ == '__main__':
    for m in [6, 8, 10, 12]:
        f, b = guard(m, seed=m)
        print(f'm={m}: 合法可装箱实例 {f}, 触发体积/计数咬 {b}', flush=True)
