"""XTRI 索引合法性证伪器（agent-4）：t+j₀+j₁≤1 的 j₀,j₁ 是否恒为全局最小两 junior？

检查对象=真口袋2角落事件（检测协议同 fuzz_mon2.py）：
  标号（senior,junior 字典序）后 j₀=srt[0][1], j₁=srt[1][1]，hi 区=位置>jj。
  XTRI 合法 ⟺ min{j_i : i>jj} >= j₁（hi 区 junior 不小于低端第 2 小）。
任何反例（hi 区 junior < j₁）⟹ XTRI 过强、E-nec-v4 闭合为假阳性风险 ⟹ 立即上板。
附带统计余量分布（min_hi − j₁）供供给引理（主代理卡点）校准。
用法: python a4_fuzz_tri.py [budget_sec]
"""
import numpy as np
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fuzz_mon2 import track_run

STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fuzz_tri_state.json')


def check_tri(jobs, m):
    """角落事件内检查 hi 区 junior 下界。返回 None/'violation:...'/余量值。"""
    if len(jobs) != 2 * m:
        return None
    loads, mach, fb_idx, L = track_run(jobs, m)
    if fb_idx != len(jobs) - 1:
        return None
    K = 1.25 * L
    mi = max(range(m), key=lambda i: loads[i])
    if len(mach[mi]) != 2 or mach[mi][0] != jobs[0]:
        return None
    if any(len(mm) != 2 for mm in mach):
        return None
    others = [mm for i, mm in enumerate(mach) if i != mi]
    q1 = jobs[m]
    # M*（重跑到第 m 步）
    loads2 = [0.0] * m
    mach2 = [[] for _ in range(m)]
    for j, pp in enumerate(jobs[:m]):
        loads2[j] += pp; mach2[j].append(pp)
    best = -1
    for i in range(m):
        if loads2[i] + q1 <= K + 1e-12 and (best < 0 or loads2[i] > loads2[best]):
            best = i
    if best < 0:
        return None
    s_star = mach2[best][0]
    srt = sorted(others, key=lambda mm: (mm[0], mm[1]))
    jj = max(i for i, mm in enumerate(srt) if mm[0] <= s_star + 1e-9)
    if abs(srt[jj][0] - s_star) > 1e-9 or abs(srt[jj][1] - q1) > 1e-9:
        return None
    j0, j1 = srt[0][1], srt[1][1]
    hi = [mm[1] for mm in srt[jj + 1:]]
    t = jobs[-1]
    if not hi:
        return None
    margin = min(hi) - j1
    if margin < -1e-9:
        return ('VIOL', f'hi 区 junior={min(hi):.4f} < j1={j1:.4f}（m={m}, jj={jj}, '
                        f'j0={j0:.4f}, t+j0+j1={t+j0+j1:.4f}）')
    return margin


def main():
    t0 = time.time()
    budget = float(sys.argv[1]) if len(sys.argv) > 1 else 240.0
    start_n = 0
    stats = {'tested': 0, 'corner': 0, 'viol': 0, 'margins': []}
    if os.path.exists(STATE):
        with open(STATE) as f:
            st = json.load(f)
        start_n = st.get('tested', 0)
        stats = st.get('stats', stats)
    rng = np.random.default_rng(20260923)
    n = start_n
    viol = stats['viol']
    margins = []
    while time.time() - t0 < budget:
        n += 1
        m = int(rng.integers(4, 13))
        njobs = 2 * m
        if rng.random() < 0.5:
            vals = rng.uniform(0.25, 1.0, njobs)
        else:
            levels = np.array([1 / 3, 5 / 12, 1 / 2, 7 / 12, 2 / 3, 3 / 4, 11 / 12, 1.0])
            vals = rng.choice(levels, njobs) + rng.uniform(-0.01, 0.01, njobs)
            vals = np.clip(vals, 0.05, 1.0)
        jobs = sorted(vals.tolist(), reverse=True)
        stats['tested'] += 1
        r = check_tri(jobs, m)
        if r is None:
            continue
        stats['corner'] += 1
        if isinstance(r, tuple) and r[0] == 'VIOL':
            viol += 1
            print(f'  ✗ 反例: {r[1]}\n    jobs={np.round(jobs, 4).tolist()}', flush=True)
        else:
            margins.append(float(r))
        if n % 20000 == 0:
            mm = np.array(margins) if margins else np.array([0.0])
            print(f'  ... {n} 例 ({time.time()-t0:.0f}s) 角落 {stats["corner"]} 反例 {viol} '
                  f'余量 min/med = {mm.min():.4f}/{np.median(mm):.4f}', flush=True)
            with open(STATE, 'w') as f:
                json.dump({'tested': n, 'stats': stats}, f)
    mm = np.array(margins) if margins else np.array([0.0])
    with open(STATE, 'w') as f:
        json.dump({'tested': n, 'stats': stats}, f)
    print(f'完成: 总测 {stats["tested"]} 角落事件 {stats["corner"]} 反例 {viol}')
    print(f'余量分布: min={mm.min():.4f} p5={np.percentile(mm,5):.4f} med={np.median(mm):.4f}')
    print('结论:', 'XTRI 索引形式实证支持 ✓（hi 区 junior 恒 >= j₁）' if viol == 0 and stats['corner'] > 0
          else ('未采到角落' if stats['corner'] == 0 else '发现反例——XTRI 索引过强，须重定性!'))


if __name__ == '__main__':
    main()
