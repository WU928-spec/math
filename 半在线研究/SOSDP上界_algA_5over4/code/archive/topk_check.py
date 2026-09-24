"""P2K1/P2K-top 结论性数值检查（新鲜 m=31..40，nice 后台）：
- k=1：base build_fixed 全 cnt 应全 INFEASIBLE（P2K1 结论）；
- k>=m-2：build_close(mon2+ammin) 全 cnt 应全 INFEASIBLE（P2K-top 结论）。
逐 m 落盘 progress。"""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farkas_fixed import build_fixed, float_cert
from hole_close import build_close
from pairing_feasible import bin_count_solutions

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'topk_check_progress.jsonl')


def main():
    t0 = time.time()
    with open(OUT, 'w') as f:
        for m in range(31, 41):
            cnts = bin_count_solutions(m)
            bad1 = badtop = 0
            for cnt in cnts:
                A, bc, bt, names, nv = build_fixed(m, cnt, 1)
                if float_cert(A, bc, bt) is None:
                    bad1 += 1
                    print(f'  ✗ P2K1 反例? m={m} cnt={cnt}', flush=True)
                for k in (m - 2, m - 1):
                    A, bc, bt, names, nv = build_close(m, cnt, k, use_ammin=True)
                    if float_cert(A, bc, bt) is None:
                        badtop += 1
                        print(f'  ✗ P2K-top 反例? m={m} k={k} cnt={cnt}', flush=True)
            rec = {'m': m, 'k1_bad': bad1, 'ktop_bad': badtop, 'sec': round(time.time() - t0)}
            f.write(json.dumps(rec) + '\n'); f.flush()
            print(f'  m={m}: k=1 反例 {bad1}/{len(cnts)}, k>=m-2 反例 {badtop} ({rec["sec"]}s)', flush=True)


if __name__ == '__main__':
    main()
