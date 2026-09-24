"""a2_p3c_adversarial.py — 引理 P3C（SEMANTICS 行18，agent-3）敌意复核的数值证伪。

策略：随机构造满足 P3C 全部前提的角落物品多重集，用精确装箱 DFS 判定能否装入 m 箱
容量 1。P3C 预言 0 个可装。若找到可装例 → 引理有洞（报告违反的前提）。
消融（证明测试有牙）：打破前提（z<q₁ 或 t≤1/4）应出现可装例。

前提（P3C §1 角落 + 步骤1 结论）：
  t>1/4（窗口）；所有物品 ≥ t；senior s_i ≥ 2t（m−1 个）；非 senior = {x,y,z,t}+{j_i}
  共 m+3 个；mach: s_i+j_i ≥ ℓ₀=x+y+z；z ≥ q₁ ≥ j_i；x,y ≥ t。
"""
import numpy as np
from functools import lru_cache
import sys, time


def can_pack(items, m, cap=1.0):
    """精确装箱判定（子集和 + DFS）。n<=~26 可用。"""
    n = len(items)
    subsum = [0.0] * (1 << n)
    for mask in range(1, 1 << n):
        lsb = mask & (-mask)
        subsum[mask] = subsum[mask ^ lsb] + items[lsb.bit_length() - 1]

    @lru_cache(maxsize=None)
    def dfs(mask, k):
        if mask == 0:
            return True
        if k == 0:
            return False
        if subsum[mask] > k * cap + 1e-9:
            return False
        sub = mask
        while sub:
            if subsum[sub] <= cap + 1e-9 and dfs(mask ^ sub, k - 1):
                return True
            sub = (sub - 1) & mask
        return False
    return dfs((1 << n) - 1, m)


def sample_corner(rng, m, break_z=False, break_t=False):
    """采样满足前提的角落多重集。break_z: 允许 z<q1（破 z≥q₁）；break_t: t<1/4。"""
    if break_t:
        t = rng.uniform(0.20, 0.249)
    else:
        t = rng.uniform(1/4 + 0.005, 1/3)
    q1 = rng.uniform(t, min(2 * t, 0.5))
    z = rng.uniform(0.3 * q1, q1) if break_z else rng.uniform(q1, 0.6)
    x = rng.uniform(t, q1); y = rng.uniform(t, q1)
    x, y = min(x, y), max(x, y)
    l0 = x + y + z
    s = np.maximum(2 * t + rng.uniform(0, 0.05, m - 1), 0.0)
    j = rng.uniform(t, q1, m - 1)
    # mach 约束 s_i+j_i >= l0：把不满足的 senior 抬高
    s = np.maximum(s, l0 - j + 1e-6)
    if np.max(s) > 1 or np.max(s + j) > 1.6:
        return None
    items = [x, y, z, t] + list(s) + list(j)
    return items, t, q1, z, l0, s, j


def main():
    budget = float(sys.argv[1]) if len(sys.argv) > 1 else 200.0
    t0 = time.time()
    rng = np.random.default_rng(20260922)
    stats = {'tested': 0, 'packable': 0}
    abl = {'z': [0, 0], 't': [0, 0]}
    bad = []
    while time.time() - t0 < budget:
        m = int(rng.integers(4, 9))
        mode = 'main' if rng.random() < 0.6 else ('z' if rng.random() < 0.5 else 't')
        r = sample_corner(rng, m, break_z=(mode == 'z'), break_t=(mode == 't'))
        if r is None:
            continue
        items, t, q1, z, l0, s, j = r
        pk = can_pack(items, m)
        if mode == 'main':
            stats['tested'] += 1
            if pk:
                stats['packable'] += 1
                bad.append((m, t, q1, z, l0))
                print(f'  ✗✗ 可装反例! m={m} t={t:.4f} q1={q1:.4f} z={z:.4f} ℓ₀={l0:.4f}', flush=True)
        else:
            abl[mode][0] += 1
            abl[mode][1] += int(pk)
        if stats['tested'] % 2000 == 0 and stats['tested'] > 0 and stats['tested'] % 2000 < 20:
            print(f'  ... 主测试 {stats["tested"]} 例, 可装 {stats["packable"]}；'
                  f'消融z {abl["z"][1]}/{abl["z"][0]} 消融t {abl["t"][1]}/{abl["t"][0]}', flush=True)
    print(f'完成: 主测试（全前提）{stats["tested"]} 例, 可装 {stats["packable"]}（P3C 预言 0）')
    print(f'消融[破z≥q₁]: 可装 {abl["z"][1]}/{abl["z"][0]}（应>0 证明测试有牙）')
    print(f'消融[破t>1/4]: 可装 {abl["t"][1]}/{abl["t"][0]}（应>0）')
    verdict = (stats['packable'] == 0 and stats['tested'] > 100
               and abl['z'][1] > 0 and abl['t'][1] > 0)
    print('判决:', 'P3C 数值复核通过（且消融证明测试有牙）' if verdict else '见上方详情')


if __name__ == '__main__':
    main()
