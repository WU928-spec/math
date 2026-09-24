"""二步 LP 全洞区闭合扫描：m=12..20，对每个一步洞 (cnt,k) 枚举 jj2，出精确常数证书。"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farkas_fixed import build_fixed, float_cert, rationalize_verify
from second_step import build_fixed2
from pairing_feasible import bin_count_solutions

PROG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'second_step_progress.jsonl')

if __name__ == '__main__':
    done = set()
    if os.path.exists(PROG):
        for line in open(PROG):
            r = json.loads(line)
            done.add((r['m'], tuple(r['cnt']), r['k']))
    t0 = time.time()
    fout = open(PROG, 'a')
    allclosed = True
    for m in range(12, 21):
        cnts = bin_count_solutions(m)
        nS = m - 1
        for k in range(1, m):
            for cnt in cnts:
                if (m, cnt, k) in done:
                    continue
                A, bc, bt, names, nv = build_fixed(m, cnt, k)
                if float_cert(A, bc, bt) is not None:
                    rec = {'m': m, 'cnt': cnt, 'k': k, 'one_step': 'closed'}
                    fout.write(json.dumps(rec) + '\n'); fout.flush()
                    continue
                # 一步洞 -> 二步枚举 jj2
                jj = k - 1
                bad = []
                for j2 in range(nS):
                    if j2 == jj:
                        continue
                    A2, bc2, bt2, names2, nv2 = build_fixed2(m, cnt, k, jj2=j2)
                    yf = float_cert(A2, bc2, bt2)
                    if yf is None:
                        bad.append((j2, 'feasible')); continue
                    y, N = rationalize_verify(A2, bc2, bt2, yf)
                    if y is None:
                        bad.append((j2, 'ratfail'))
                rec = {'m': m, 'cnt': cnt, 'k': k, 'one_step': 'hole',
                       'two_step': 'closed' if not bad else f'HOLE {bad}'}
                if bad:
                    allclosed = False
                fout.write(json.dumps(rec) + '\n'); fout.flush()
                print(f'm={m} k={k} cnt={cnt}: 二步 {"闭合" if not bad else "仍有洞 " + str(bad)}  ({time.time()-t0:.0f}s)')
    fout.close()
    print('总结:', 'm=12..20 全部闭合 ✓' if allclosed else '仍有洞！')
