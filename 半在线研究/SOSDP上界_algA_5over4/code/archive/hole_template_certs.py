"""对 p2_holes_big.jsonl 全部 154 个洞（m=12..30）逐一构造统一模板符号证书并
Fraction 精确验证（A^T y=0, bt^T y=0, bc^T y<0, y>=0）——不解 LP。
输出 hole_template_certs.jsonl（每洞：m,k,cnt,证书支撑,rhs）。
"""
import json, sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from uniform_hole_cert import template_weights, verify_y, covered

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hole_template_certs.jsonl')


def main():
    t0 = time.time()
    holes = [json.loads(l) for l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'p2_holes_big.jsonl'))]
    nok = 0
    with open(OUT, 'w') as f:
        for h in holes:
            m, k, cnt = h['m'], h['k'], tuple(h['cnt'])
            assert covered(cnt, m, k), f'未覆盖: {m},{k},{cnt}'
            A, bc, bt, nv, w = template_weights(m, cnt, k)
            ok, rhs = verify_y(A, bc, bt, nv, w)
            rec = {'m': m, 'k': k, 'cnt': list(cnt), 'ok': ok, 'rhs': str(rhs),
                   'support': {str(i): str(v) for i, v in w.items()}}
            f.write(json.dumps(rec) + '\n')
            if ok:
                nok += 1
            else:
                print(f'  ✗ m={m} k={k} cnt={cnt} rhs={rhs}', flush=True)
    print(f'154 洞模板符号证书: {nok}/154 精确通过 ({time.time()-t0:.0f}s), 输出 {OUT}')


if __name__ == '__main__':
    main()
