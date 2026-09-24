"""leftover 区域 LP 扫描：模板未覆盖的 (cnt,k)（b=0 / k<b+2 / JJJ含t）逐 m float 证书验证。
m<=22 已由 scanbig 全覆盖（全 k 全 cnt 闭合），此脚本推 m=23..26。
用法: python leftover_scan.py <m>  —— 单 m 扫描，打印进度。
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farkas_fixed import float_cert
from hole_close import build_close
from uniform_hole_cert import covered
from pairing_feasible import bin_count_solutions


def main():
    m = int(sys.argv[1])
    t0 = time.time()
    cnts = bin_count_solutions(m)
    todo = [(cnt, k) for cnt in cnts for k in range(1, m) if not covered(cnt, m, k)]
    bad = []
    for n, (cnt, k) in enumerate(todo):
        A, bc, bt, names, nv = build_close(m, cnt, k)
        if float_cert(A, bc, bt) is None:
            bad.append((cnt, k))
            print(f'  ✗ m={m} k={k} cnt={cnt}: feasible!', flush=True)
        if (n + 1) % 2000 == 0:
            print(f'  ... m={m} {n+1}/{len(todo)} ({time.time()-t0:.0f}s) feasible={len(bad)}', flush=True)
    print(f'm={m}: leftover {len(todo)} 个 (cnt,k), feasible {len(bad)}, '
          f'{"全闭合 ✓" if not bad else "有洞!"} ({time.time()-t0:.0f}s)', flush=True)


if __name__ == '__main__':
    main()
