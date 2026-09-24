"""A 线: razor 带 k=m-1 全合法行 LP 扫描（build_bcanon = mon2 + B 规范形全合法行）。
每 (m,cnt): 常数证书精确验证 + 逐族消融(去行族应回弹 feasible) + 合法性标注。
断点: a1_razor_closure_progress.jsonl；内部 7.5min 自退, 重跑续。
"""
import json, os, sys, time
from fractions import Fraction as F
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_bcanon import build_bcanon
from farkas_fixed import float_cert, rationalize_verify, MG
from pairing_feasible import bin_count_solutions

PROG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'a1_razor_closure_progress.jsonl')
FAMILIES = ['mon2', 'SS', 'SJ', 'JJJ', 'JJ']

def family(nm):
    if nm.startswith('mon2_j'): return 'mon2'
    if nm == 'SS': return 'SS'
    if nm.startswith('SJ'): return 'SJ'
    if nm in ('JJJ', 'JJJagg'): return 'JJJ'
    if nm == 'JJ': return 'JJ'
    return None

def check(m, cnt):
    k = m - 1
    A, bc, bt, names, nv = build_bcanon(m, cnt, k)
    yf = float_cert(A, bc, bt)
    rec = {'m': m, 'cnt': list(cnt), 'k': k}
    if yf is None:
        rec['status'] = 'FEASIBLE(洞!)'
        return rec
    y, N = rationalize_verify(A, bc, bt, yf)
    if y is None:
        rec['status'] = 'nocert'
        return rec
    rec['status'] = 'cert'; rec['N'] = N
    rec['support'] = sorted({names[i] for i in range(len(y)) if y[i] != 0})
    # 消融: 去每族行应回弹(无常数证书)
    abl = {}
    for fam in FAMILIES:
        idx = [i for i, nm in enumerate(names) if family(nm) != fam]
        A2 = [A[i] for i in idx]; bc2 = [bc[i] for i in idx]; bt2 = [bt[i] for i in idx]
        abl[fam] = float_cert(A2, bc2, bt2) is None   # True=回弹(必要), False=仍闭(非必要)
    rec['ablation'] = abl
    return rec

def main():
    t0 = time.time()
    done = set()
    if os.path.exists(PROG):
        for line in open(PROG):
            r = json.loads(line)
            done.add((r['m'], tuple(r['cnt'])))
    fh = open(PROG, 'a')
    n_cert = n_feas = n_all = 0
    abl_necessary = {f: [0, 0] for f in FAMILIES}   # [必要数, 总 cert 数]
    for m in range(4, 31):
        for cnt in bin_count_solutions(m):
            key = (m, cnt)
            if key in done: continue
            if time.time() - t0 > 430:      # 7.2min 自退
                fh.close(); print('TIME SLICE END, resume by rerun'); return
            rec = check(m, cnt)
            fh.write(json.dumps(rec) + '\n'); fh.flush()
            n_all += 1
            if rec['status'] == 'cert':
                n_cert += 1
                for fam in FAMILIES:
                    abl_necessary[fam][1] += 1
                    if rec['ablation'].get(fam): abl_necessary[fam][0] += 1
            elif rec['status'].startswith('FEASIBLE'):
                n_feas += 1
                print(f'!! 洞 m={m} cnt={cnt}', flush=True)
        print(f'  m={m} done (累计 cert={n_cert} feas={n_feas}, {time.time()-t0:.0f}s)', flush=True)
    fh.close()
    print(f'扫描完成: {n_all} (cnt,k=m-1), 证书 {n_cert}, 洞 {n_feas}')
    for fam in FAMILIES:
        a, t = abl_necessary[fam]
        print(f'  消融[{fam}]: 必要 {a}/{t}')

if __name__ == '__main__':
    main()
