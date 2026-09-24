"""a3_cert115_weights.py —— 任务③原料：uncond 115 点精确证书带权重（y 向量）落盘。
main_cert154.jsonl 只存支撑行名不存权重；本脚本重建 noSJrev 档（去SJrev/S1v/JJrev，含 B4/A2）
逐点精确 Fraction 证书 y，支撑行名+权重（分子分母）全存 a3_cert115_weights.jsonl。
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction as F
import a1_value_lp2 as V
from main_cegar3 import MG
from fast_lp import float_cert_rows, exact_verify_support

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'a3_cert115_weights.jsonl')
KW = dict(use_sjrev=False, use_s1v=False, use_jjrev=False)


def build(m, cnt, k, kw):
    nS = m - 1
    A, bc, bt, names, leg, nv = V.build(m, cnt, **kw)
    A, bc, bt, names = list(A), list(bc), list(bt), list(names)
    IP, IAM, IQ1 = 0, 1, 2
    vs = lambda r: 3 + (r - 1); vj = lambda r: 3 + nS + (r - 1)
    for i in range(1, k + 1):
        row = [F(0)] * nv; row[IP] = 1; row[vs(i)] = -1; row[vj(nS - k + i)] = -1
        A.append(row); bc.append(-MG); bt.append(F(0)); names.append(f'A5_{i}')
    row = [F(0)] * nv; row[vs(k)] = 4; row[IAM] = -5; row[IQ1] = -1
    A.append(row); bc.append(F(0)); bt.append(F(0)); names.append('LZ')
    if k < nS:
        row = [F(0)] * nv; row[vs(k + 1)] = -4; row[IAM] = 5; row[IQ1] = 1
        A.append(row); bc.append(-MG); bt.append(F(0)); names.append('HZ')
    R = [([float(x) for x in row], bc[i], bt[i], names[i]) for i, row in enumerate(A)]
    return R, nv


def main():
    pts = []
    for l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main_ablation_class.jsonl')):
        r = json.loads(l)
        if r['cls'] == 'uncond':
            pts.append((r['m'], r['cnt'], r['k']))
    done = set()
    if os.path.exists(OUT):
        for l in open(OUT):
            try:
                r = json.loads(l); done.add((r['m'], tuple(r['cnt']), r['k']))
            except Exception:
                pass
    pf = open(OUT, 'a')
    t0 = time.time(); n = 0
    for m, cnt, k in pts:
        if (m, tuple(cnt), k) in done:
            continue
        R, nv = build(m, cnt, k, KW)
        yf = float_cert_rows(R, nv)
        if yf is None:
            pf.write(json.dumps({'m': m, 'cnt': cnt, 'k': k, 'status': 'FLOAT_NO_CERT'}) + '\n'); pf.flush()
            continue
        y, sup = exact_verify_support(R, nv, yf)
        if y is None:
            pf.write(json.dumps({'m': m, 'cnt': cnt, 'k': k, 'status': 'RATFAIL'}) + '\n'); pf.flush()
            continue
        rec = {'m': m, 'cnt': cnt, 'k': k, 'status': 'OK',
               'support': [R[i][3] for i in sup],
               'weights': [[w.numerator, w.denominator] for w in y]}
        pf.write(json.dumps(rec) + '\n'); pf.flush()
        n += 1
        if n % 20 == 0:
            print(f'{n} 发完成（{time.time()-t0:.0f}s）', flush=True)
    pf.close()
    print(f'权重落盘收官：{n}/115（{time.time()-t0:.0f}s）')


if __name__ == '__main__':
    main()
