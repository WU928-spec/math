"""口袋定向模糊测试 v2 — 合规版（预估耗时/断点续跑/进度输出）。

用法: fuzz2.py <seed> <chunks> [chunk_size]
每 chunk 独立落盘 state（json），中断后重跑自动续接。
记录口袋形状: p1=最闲机恰2件, p2=存在单子机, p3=最闲机>=3件。
只统计 m in {4,5,6}（m=3 超范围）。
吞吐基准 ~59 it/s（seed1 实测），chunk=30000 约 8.5 分钟。
"""
import json, os, random, sys, time
from toolbox import fallback_event, opt_float

STATE = "fuzz2_state.json"
OUT = "fuzz2_hits.jsonl"
MS = (4, 5, 6)


def gen(m, rng):
    n = rng.randint(m + 2, 3 * m)
    mode = rng.random()
    if mode < 0.30:
        jobs = [round(rng.uniform(0.2, 1.0), 4) for _ in range(n)]
    elif mode < 0.50:
        jobs = [rng.randint(1, 12) for _ in range(n)]
    elif mode < 0.75:
        l0 = rng.uniform(0.75, 1.0)
        x = round(l0 * rng.uniform(0.4, 0.5), 4)
        y = round(l0 - x, 4)
        t = round(rng.uniform(0.26, 0.45), 4)
        jobs = [round(rng.uniform(t, 1.0), 4) for _ in range(n - 3)] + [x, y, t]
    else:
        big = round(rng.uniform(0.6, 1.0), 4)
        t = round(rng.uniform(0.26, 0.45), 4)
        jobs = [round(rng.uniform(t, 0.9), 4) for _ in range(n - 2)] + [big, t]
    return sorted(jobs, reverse=True)


def load_state():
    if os.path.exists(STATE):
        with open(STATE) as f:
            return json.load(f)
    return {"chunk_done": -1, "best": {p: {str(m): 0.0 for m in MS} for p in ("p1", "p2", "p3")}}


def save_state(st):
    with open(STATE, "w") as f:
        json.dump(st, f)


def main(seed, chunks, chunk_size=30000):
    st = load_state()
    for c in range(st["chunk_done"] + 1, chunks):
        rng = random.Random(seed * 1000003 + c)
        t0 = time.time()
        hits = 0
        with open(OUT, "a") as fo:
            for it in range(chunk_size):
                m = rng.choice(MS)
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
                if t_n <= 0.25 or t_n > 0.45:
                    continue
                mins = ev["machine_jobs"][0]
                tags = []
                if len(mins) == 2:
                    tags.append("p1")
                if any(len(mm) == 1 for mm in ev["machine_jobs"]):
                    tags.append("p2")
                if len(mins) >= 3:
                    tags.append("p3")
                hits += 1
                for tag in tags:
                    if ratio > st["best"][tag][str(m)] + 0.002:
                        st["best"][tag][str(m)] = ratio
                        rec = {"chunk": c, "pocket": tag, "m": m,
                               "ratio": round(ratio, 6), "t": round(t_n, 4), "jobs": jobs}
                        fo.write(json.dumps(rec, ensure_ascii=False) + "\n")
                        fo.flush()
                if it % 5000 == 4999:
                    print(f"chunk={c} it={it+1} {time.time()-t0:.0f}s hits={hits} "
                          f"best={ {p: round(max(st['best'][p].values()),4) for p in ('p1','p2','p3')} }", flush=True)
        st["chunk_done"] = c
        save_state(st)
        print(f"chunk {c} done in {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]),
         int(sys.argv[3]) if len(sys.argv) > 3 else 30000)
