"""口袋 2 角落精确峰值测量：i=1, 他机全 2 件台的形态族内做网格+随机爬山。

回答的问题: 角落(危险几何)内, 精确比值 C_A/OPT 的真实上确界距 5/4 多远?
合规: 断点续跑 + 进度打印 + 时间盒(每 chunk 内 opt_float 只对 LB 过关者)。
预估: 3 chunks × 8000 模拟 ≈ 8~12 分钟(opt_float 在 n<=12 上快)。
"""
import json, os, random, time
from toolbox import algA, opt_float

STATE = "corner2_state.json"
OUT = "corner2_hits.jsonl"


def gen(m, rng):
    t = rng.uniform(0.26, 0.34)
    p = rng.uniform(1.26 - t, 1.0)
    jobs = [p]
    for j in range(2, m + 1):
        pj = rng.uniform(t + 0.02, p)
        qj = rng.uniform(max(t, p - pj + 0.005), min(2 * t - 1e-3, 1.0))
        jobs += [pj, qj]
    jobs.append(t)
    return sorted(jobs, reverse=True)


def main(chunks=3, chunk_size=8000):
    st = {"chunk": -1, "best": 0.0}
    if os.path.exists(STATE):
        st = json.load(open(STATE))
    for c in range(st["chunk"] + 1, chunks):
        rng = random.Random(7000 + c)
        t0 = time.time()
        cnt = 0
        for it in range(chunk_size):
            m = rng.choice((5, 6, 7, 8))
            jobs = gen(m, rng)
            n = len(jobs)
            if n > 14:
                continue
            ca = algA(jobs, m)
            lb = max(sum(jobs) / m, jobs[0], jobs[m - 1] + jobs[m])
            if ca / lb < 1.10:
                continue
            o = opt_float(jobs, m)
            r = ca / o
            cnt += 1
            if r > st["best"] + 0.002:
                st["best"] = r
                with open(OUT, "a") as f:
                    f.write(json.dumps({"ratio": round(r, 6), "jobs": jobs, "m": m}) + "\n")
            if it % 2000 == 1999:
                print(f"chunk={c} it={it+1} {time.time()-t0:.0f}s evaluated={cnt} best={st['best']:.5f}", flush=True)
        st["chunk"] = c
        json.dump(st, open(STATE, "w"))
        print(f"chunk {c} done in {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
