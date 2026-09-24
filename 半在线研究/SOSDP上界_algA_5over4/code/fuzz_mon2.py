"""单调匹配引理（mon2）的实证验证：在真口袋2角落事件上逐例检查。

引理（hole_close.py mon2 的依据）：角落运行（n=2m，M0={p} 最大初始件且 t 前未被触碰，
他机各恰 2 件 {s_i, j_i}，s_i=初始件先到，j_i=后至件）中，q1=jobs[m]（首个后至件，最大
junior）落机 M*，则机器可按 senior 递增、同级 junior 递增重标号使
  (i)   j_i <= j_{i+1} 对所有 i < jj（jj = M* 的标号）；
  (ii)  s_jj + q1 <= K（q1 放得下 M*）；
  (iii) s_i + q1 > K 对所有 i > jj（更大 senior 机放不下 q1 ⟹ nofit）。
检查 (i) 的严格版（免标号）：s_A < s_B <= s_{M*} ⟹ j_A <= j_B。
任何反例都说明 mon2 方向写反或引理错误——历史教训：必须过这一关才可信。
"""
import numpy as np
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fuzz_mon2_state.json')


def track_run(jobs, m):
    """逐任务记录落机，返回 (loads, mach, first_fb_idx 或 None)。"""
    loads = [0.0] * m
    mach = [[] for _ in range(m)]
    L = None
    for j, p in enumerate(jobs):
        if j < m:
            loads[j] += p; mach[j].append(p)
        else:
            if L is None:
                L = jobs[m - 1] + jobs[m]
            cap = 1.25 * L
            best = -1
            for i in range(m):
                if loads[i] + p <= cap + 1e-12 and (best < 0 or loads[i] > loads[best]):
                    best = i
            if best >= 0:
                loads[best] += p; mach[best].append(p)
            else:
                mn = min(range(m), key=lambda i: loads[i])
                loads[mn] += p; mach[mn].append(p)
                return loads, mach, j, L
    return loads, mach, None, L


def check_event(jobs, m, verbose=False):
    """若是角落事件则检查 mon2 三条。返回 None(非角落) / True(通过) / (错误串)。"""
    if len(jobs) != 2 * m:
        return None
    loads, mach, fb_idx, L = track_run(jobs, m)
    if fb_idx != len(jobs) - 1:
        return None  # 角落要求 t=末件才触发首次 fallback
    K = 1.25 * L
    mi = max(range(m), key=lambda i: loads[i])
    if len(mach[mi]) != 2 or mach[mi][0] != jobs[0]:
        return None  # M0={p}+t，p 最大初始
    if any(len(mm) != 2 for mm in mach):
        return None
    p = jobs[0]
    others = [mm for i, mm in enumerate(mach) if i != mi]
    q1 = jobs[m]
    # M* = 收到 q1 的机器（首个后至件 jobs[m]）
    Mstar = None
    for mm in others:
        if mm[1] == q1:
            # 首个后至件的落机需重跑确认；同值时取 senior 最大且放得下的那台
            pass
    # 重跑到第 m 步确定 M*
    loads2 = [0.0] * m
    mach2 = [[] for _ in range(m)]
    for j, pp in enumerate(jobs[:m]):
        loads2[j] += pp; mach2[j].append(pp)
    cap = K
    best = -1
    for i in range(m):
        if loads2[i] + q1 <= cap + 1e-12 and (best < 0 or loads2[i] > loads2[best]):
            best = i
    if best < 0:
        return 'q1 放不下任何机却仍在角落?'
    # M* 在 others 中的身份：mach2[best] 的初始件
    s_star = mach2[best][0]
    # 严格版检查：s_A < s_B <= s_star ⟹ j_A <= j_B
    pairs = [(mm[0], mm[1]) for mm in others]
    for (sa, ja) in pairs:
        for (sb, jb) in pairs:
            if sa < sb - 1e-9 and sb <= s_star + 1e-9 and ja > jb + 1e-9:
                return f'严格单调违反: s_A={sa:.4f} j_A={ja:.4f} > s_B={sb:.4f} j_B={jb:.4f} (s*={s_star:.4f})'
    # 标号版检查
    order = sorted(range(len(others)), key=lambda i: (others[i][0], others[i][1]))
    srt = [others[i] for i in order]
    jj = max(i for i, mm in enumerate(srt) if mm[0] <= s_star + 1e-9)
    if abs(srt[jj][0] - s_star) > 1e-9 or abs(srt[jj][1] - q1) > 1e-9:
        # M* 应在 jj（同级块末尾，junior=q1 最大）
        return f'M* 定位异常: jj 处=({srt[jj][0]:.4f},{srt[jj][1]:.4f}) s*={s_star:.4f} q1={q1:.4f}'
    for i in range(jj):
        if srt[i][1] > srt[i + 1][1] + 1e-9:
            return f'标号单调违反: 位置{i} j={srt[i][1]:.4f} > 位置{i+1} j={srt[i+1][1]:.4f}'
    if srt[jj][0] + q1 > K + 1e-9:
        return f'(ii)违反: s_jj+q1={srt[jj][0]+q1:.4f} > K={K:.4f}'
    for i in range(jj + 1, len(srt)):
        if srt[i][0] + q1 <= K + 1e-9:
            return f'(iii)nofit违反: s_i={srt[i][0]:.4f}+q1={q1:.4f} <= K={K:.4f}'
    return True


def main():
    t0 = time.time()
    budget = float(sys.argv[1]) if len(sys.argv) > 1 else 240.0
    start_n = 0
    stats = {'tested': 0, 'corner': 0, 'ok': 0}
    if os.path.exists(STATE):
        with open(STATE) as f:
            st = json.load(f)
        start_n = st.get('tested', 0)
        stats = st.get('stats', stats)
    rng = np.random.default_rng(20260921)
    n = start_n
    bad = 0
    while time.time() - t0 < budget:
        n += 1
        m = int(rng.integers(4, 13))
        njobs = 2 * m
        # 混合分布：均匀 + 离散层（角落事件偏爱分层结构）
        if rng.random() < 0.5:
            vals = rng.uniform(0.25, 1.0, njobs)
        else:
            levels = np.array([1 / 3, 5 / 12, 1 / 2, 7 / 12, 2 / 3, 3 / 4, 11 / 12, 1.0])
            vals = rng.choice(levels, njobs) + rng.uniform(-0.01, 0.01, njobs)
            vals = np.clip(vals, 0.05, 1.0)
        jobs = sorted(vals.tolist(), reverse=True)
        stats['tested'] += 1
        r = check_event(jobs, m)
        if r is None:
            continue
        stats['corner'] += 1
        if r is True:
            stats['ok'] += 1
        else:
            bad += 1
            print(f'  ✗ 反例 m={m}: {r}\n    jobs={np.round(jobs,4).tolist()}', flush=True)
        if n % 20000 == 0:
            el = time.time() - t0
            print(f'  ... {n} 例 ({el:.0f}s) 角落 {stats["corner"]} 通过 {stats["ok"]} 反例 {bad}', flush=True)
            with open(STATE, 'w') as f:
                json.dump({'tested': n, 'stats': stats}, f)
    with open(STATE, 'w') as f:
        json.dump({'tested': n, 'stats': stats}, f)
    print(f'完成: 总测 {stats["tested"]} 角落事件 {stats["corner"]} 全部通过 {stats["ok"]} 反例 {bad}')
    print('结论:', '单调匹配引理实证通过 ✓' if bad == 0 and stats['corner'] > 0 else
          ('未采到角落事件（需加样）' if stats['corner'] == 0 else '引理有错!'))


if __name__ == '__main__':
    main()
