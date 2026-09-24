import random
import sys
from math import sqrt, exp
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from base_case_lp import c, simulate_a3_all, brute_cstar

def ratio_of(p):
    cs, _ = brute_cstar(p)
    if cs < 1e-12:
        return None
    return max(simulate_a3_all(p)) / cs

def main():
    random.seed(12345)
    rng = random.Random(12345)
    worst = {}
    count = {}
    N = 20000
    # structured tight instance first
    tight = [1.0, c - 1, c - 1, c - 1]
    print(f"tight n=4 instance {tight}: ratio = {ratio_of(tight):.15f}")
    tight5 = [1.0, c - 1, c - 1, c - 1, 0.0]
    print(f"tight n=5 instance {tight5}: ratio = {ratio_of(tight5):.15f}")

    for n in (3, 4, 5):
        worst[n] = (0.0, None)
        count[n] = 0
        for it in range(N):
            mode = it % 4
            if mode == 0:
                raw = [rng.random() for _ in range(n)]
            elif mode == 1:
                raw = [rng.expovariate(1.0) for _ in range(n)]
            elif mode == 2:
                raw = [rng.random() for _ in range(n)]
                raw[0] += 2.0
            else:
                # clustered around the tight structure
                raw = [1.0, c - 1, c - 1, c - 1][:n]
                raw = [v * (1 + 0.3 * (rng.random() - 0.5)) for v in raw]
            p = sorted(raw, reverse=True)
            r = ratio_of(p)
            if r is None:
                continue
            count[n] += 1
            if r > worst[n][0]:
                worst[n] = (r, list(p))
        rmax, pworst = worst[n]
        print(f"n={n}: samples={count[n]}  max ratio = {rmax:.15f}  (c={c:.15f}, diff={rmax-c:+.3e})")
        if pworst is not None:
            print(f"    worst instance = {[round(v,4) for v in pworst]}")

if __name__ == "__main__":
    main()
