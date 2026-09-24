"""scan.py - scan profiles for given n, m range; append results to JSONL."""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compute import (minmax_profile, partition_str, machine_str, packing_str,
                     KillMILP)


def all_profiles(m):
    out = []
    def rec(rem, cur):
        if rem == 0:
            out.append(tuple(cur))
            return
        for x in range(1, rem + 1):
            rec(rem - x, cur + [x])
    rec(m, [])
    return out


def summarize(res):
    best_info = res["best_info"]
    wit = None
    if best_info is not None:
        M, r = best_info
        wit = {
            "machine": machine_str(M),
            "ratio": float(r["ratio"]),
            "v_weak": [round(float(x), 8) for x in r["v"]],
            "packing_weak": packing_str(r["assign"], KillMILP(res["profile"], res["n"]).ranks),
        }
    return {
        "profile": list(res["profile"]),
        "n": res["n"], "k": res["k"], "m": res["m"],
        "minmax": float(res["minmax"]),
        "best_partition": partition_str(res["best_partition"]) if res["best_partition"] else None,
        "witness": wit,
        "num_partitions": res["num_partitions"],
        "fully_evaluated": res["partitions_fully_evaluated"],
        "kill_milp_calls": res["kill_milp_calls"],
        "time": round(res["time"], 2),
    }


def done_profiles(path):
    done = set()
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                try:
                    d = json.loads(line)
                    done.add((tuple(d["profile"]), d["n"]))
                except Exception:
                    pass
    return done


def main():
    n = int(sys.argv[1])
    m_lo = int(sys.argv[2])
    m_hi = int(sys.argv[3])
    outfile = sys.argv[4]
    only = None
    if len(sys.argv) > 5:
        only = set()
        for spec in sys.argv[5:]:
            only.add(tuple(int(x) for x in spec.split(",")))
    done = done_profiles(outfile)
    for m in range(m_lo, m_hi + 1):
        profs = all_profiles(m)
        if only is not None:
            profs = [p for p in profs if p in only]
        for c in profs:
            if (c, n) in done:
                continue
            t0 = time.time()
            try:
                res = minmax_profile(c, n, verbose=False)
                s = summarize(res)
            except Exception as e:
                s = {"profile": list(c), "n": n, "error": repr(e)}
            with open(outfile, "a") as f:
                f.write(json.dumps(s) + "\n")
            print(f"[n={n}] {c} -> {s.get('minmax')}  "
                  f"({s.get('num_partitions')} parts, {time.time()-t0:.1f}s)", flush=True)


if __name__ == "__main__":
    main()
