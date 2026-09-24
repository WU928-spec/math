"""U(a) 快速验证的分块执行器：python a4_idu_chunk.py C D E F（单族全 m 全 k）。"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a4_idu_fast import check, U, mk_fam

if __name__ == '__main__':
    c, d, e, f = (int(x) for x in sys.argv[1:5])
    a_num = 3 * d + 2 * e + f - 1 - c
    a = a_num // 2
    t0 = time.time()
    bad = []
    n = 0
    for m in range(51):
        cnt = mk_fam(a, c, d, e, f, m)
        if cnt is None:
            continue
        for k in range(2, m):
            n += 1
            ok, r = check(m, cnt, k, U(a))
            if not ok:
                bad.append((m, k, r))
    print(f'({c},{d},{e},{f}) a={a}: {n} 案例 {"✓" if not bad else f"{len(bad)} 失败 例 {bad[:3]}"} '
          f'({time.time()-t0:.0f}s)')
