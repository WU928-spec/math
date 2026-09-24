"""U(a) 对 razor+邻近全部 (c,d,e,f) 族（E-nec 损失清单键全集）的 ∀m 全 k 验证（agent-4）。"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a4_symbolic_verify import check_identity
from fractions import Fraction as F

KEYS = [(0, 1, e, 0) for e in range(6)] + [(0, 2, e, 1) for e in range(4)] + \
       [(0, 3, e, 2) for e in range(2)] + [(1, 2, e, 0) for e in range(5)] + \
       [(1, 3, e, 1) for e in range(3)] + [(1, 4, 0, 2), (2, 3, 0, 0), (2, 3, 1, 0),
       (2, 3, 2, 0), (2, 4, 0, 1)]


def U(a):
    rows = [(('j1>=t', 0), F(2)), (('danger', 0), F(6)), (('pair0', 0), F(4)),
            (('pair1', 0), F(2)), (('srt0', 0), F(1))]
    rows += [((f'srt{i}', 0), F(3)) for i in range(1, 2 * a - 1)]
    rows += [(('XSS0', 0), F(3)), (('XTRI', 0), F(4))]
    return rows


def mk_fam(a, c, d, e, f, m):
    b = m - 1 - 2 * a - c
    cnt = (a, b, c, d, e, f)
    if b < 0 or min(cnt) < 0:
        return None
    assert 2 * a + b + c == m - 1 and b + 3 * d + 2 * e + f == m
    return cnt


if __name__ == '__main__':
    import json
    t0 = time.time()
    skip = set()
    if len(sys.argv) > 1:
        skip = set(eval(sys.argv[1]))
    DONE_F = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'a4_sweep_done.json')
    done_keys = []
    if os.path.exists(DONE_F):
        done_keys = [tuple(x) for x in json.load(open(DONE_F))]
        skip |= set(done_keys)
    total_bad = total_case = 0
    for (c, d, e, f) in KEYS:
        if (c, d, e, f) in skip:
            continue
        a_num = 3 * d + 2 * e + f - 1 - c
        if a_num % 2 or a_num <= 0:
            print(f'  ({c},{d},{e},{f}): a 非正整数({a_num})，跳过'); continue
        a = a_num // 2
        bad = []
        n_case = 0
        for m in range(51):
            cnt = mk_fam(a, c, d, e, f, m)
            if cnt is None:
                continue
            for k in range(2, m):
                n_case += 1
                ok, r = check_identity(m, cnt, k, U(a))
                if not ok:
                    bad.append((m, k, r))
        total_bad += len(bad); total_case += n_case
        print(f'  ({c},{d},{e},{f}) a={a}: {n_case} 案例 '
              f'{"✓" if not bad else f"{len(bad)} 失败 例 {bad[:2]}"} ({time.time()-t0:.0f}s)',
              flush=True)
        done_keys.append((c, d, e, f))
        with open(DONE_F, 'w') as _f:
            json.dump(done_keys, _f)
    print(f'总结: {total_case} 案例, {"razor+邻近全族 U(a) 全通过 ✓" if total_bad == 0 else f"{total_bad} 处失败"}')
