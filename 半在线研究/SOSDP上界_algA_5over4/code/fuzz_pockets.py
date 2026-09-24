"""定向模糊测试：冲两个口袋的构造空间，找出逼近 5/4 的绑定子形。

归一化 OPT=1（opt_float），记录 fallback 事件中：
- 口袋1: 最闲机恰 2 件 (x<=y) —— 记录 (t, x, y, C_A)
- 口袋2: 存在单子机（初始任务独占未再动）—— 记录 (t, p_i, C_A)
输出 JSONL + 汇总裁决哪个子形最危险。
"""
import json, random, sys, heapq
from toolbox import fallback_event, opt_float


def gen(m, rng):
    n = rng.randint(m + 2, 3 * m)
    mode = rng.random()
    if mode < 0.30:
        jobs = [round(rng.uniform(0.2, 1.0), 4) for _ in range(n)]
    elif mode < 0.50:
        jobs = [rng.randint(1, 12) for _ in range(n)]
    elif mode < 0.75:
        # 口袋1 定向: 一台两件 ~ (l0/2, l0/2)，t 在硬窗口 (0.25, 0.45]
        l0 = rng.uniform(0.75, 1.0)
        x = round(l0 * rng.uniform(0.4, 0.5), 4)
        y = round(l0 - x, 4)
        t = round(rng.uniform(0.26, 0.45), 4)
        rest = [round(rng.uniform(t, 1.0), 4) for _ in range(n - 3)]
        jobs = rest + [x, y, t]
    else:
        # 口袋2 定向: 一个超大初始任务独占
        big = round(rng.uniform(0.6, 1.0), 4)
        t = round(rng.uniform(0.26, 0.45), 4)
        rest = [round(rng.uniform(t, 0.9), 4) for _ in range(n - 2)]
        jobs = rest + [big, t]
    return sorted(jobs, reverse=True)


def main(seed=1, N=200000):
    rng = random.Random(seed)
    # 每个 m 维护最大堆 (ratio, record)
    top1 = {m: [] for m in (3, 4, 5, 6, 7, 8)}   # 口袋1
    top2 = {m: [] for m in (3, 4, 5, 6, 7, 8)}   # 口袋2
    n1 = {m: 0 for m in top1}
    n2 = {m: 0 for m in top2}
    import time
    t_start = time.time()
    for it in range(N):
        if it and it % 5000 == 0:
            b1 = {m: (round(max([k for k, _ in top1[m]], default=0), 4)) for m in top1}
            b2 = {m: (round(max([k for k, _ in top2[m]], default=0), 4)) for m in top2}
            print(f"it={it} elapsed={time.time()-t_start:.0f}s p1max={b1} p2max={b2}", flush=True)
        m = rng.choice((3, 4, 5, 6))
        jobs = gen(m, rng)
        if len(jobs) > 13:
            continue
        ev = fallback_event(jobs, m)
        if not ev:
            continue
        try:
            o = opt_float(jobs, m)
        except Exception:
            continue
        if o <= 0:
            continue
        ca = ev["loads"][-1]
        ratio = ca / o
        t_n = ev["t"] / o
        if t_n <= 0.25 or t_n > 0.45:   # 硬窗口外已由 Lemma A/B 处理
            continue
        rec = {"ratio": round(ratio, 6), "t": round(t_n, 4), "jobs": jobs, "m": m}
        mins = ev["machine_jobs"][0]
        s1 = sum(mins)
        if len(mins) == 2:                       # 口袋1
            n1[m] += 1
            rec["x"], rec["y"] = min(mins) / o, max(mins) / o
            rec["l0"] = s1 / o
            h = top1[m]
            key = ratio
            if len(h) < 40: heapq.heappush(h, (key, json.dumps(rec)))
            elif key > h[0][0]: heapq.heapreplace(h, (key, json.dumps(rec)))
        singletons = [mm for mm in ev["machine_jobs"] if len(mm) == 1]
        if singletons:                            # 口袋2
            n2[m] += 1
            rec["singleton"] = max(sum(s) for s in singletons) / o
            h = top2[m]
            if len(h) < 40: heapq.heappush(h, (ratio, json.dumps(rec)))
            elif ratio > h[0][0]: heapq.heapreplace(h, (ratio, json.dumps(rec)))

    out = open(f"pockets_seed{seed}.json", "w")
    import io
    for m in top1:
        best1 = sorted(top1[m], key=lambda z: -z[0])[:5]
        best2 = sorted(top2[m], key=lambda z: -z[0])[:5]
        out.write(f"== m={m} pocket1 events={n1[m]} top5 ==\n")
        for k, s in best1: out.write(f"  r={k:.5f} {s}\n")
        out.write(f"== m={m} pocket2 events={n2[m]} top5 ==\n")
        for k, s in best2: out.write(f"  r={k:.5f} {s}\n")
    out.close()
    print("done", seed)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 1,
         int(sys.argv[2]) if len(sys.argv) > 2 else 200000)
