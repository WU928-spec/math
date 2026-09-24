import sys, os, json, time
# 运行约定：从项目根目录运行（与本目录同批自 /tmp 找回的脚本一致）
# 原为两行已失效的绝对旧路径 /Users/a123456/math/research/2026-09-19_algA_5over4/code
sys.path.insert(0, 'code')
os.chdir('code')
from a3_cert115_clean import build
from fast_lp import float_cert_rows, exact_verify_support

pts = []
for l in open('main_ablation_class.jsonl'):
    r = json.loads(l)
    if r['cls'] == 'uncond':
        pts.append((r['m'], r['cnt'], r['k']))

base = dict(use_sjrev=False, use_s1v=False, use_jjrev=False)
for vname, kw in [('noSJrev基准(B4,A2保留)', base),
                  ('noSJrev+去A2', dict(base, use_a2=False)),
                  ('noSJrev+去B4', dict(base, use_b4=False))]:
    nok = nfloat = nrat = 0
    fails = []
    for m, cnt, k in pts:
        R, nv = build(m, list(cnt), k, kw)
        yf = float_cert_rows(R, nv)
        if yf is None:
            nfloat += 1; fails.append((m, cnt[0], k)); continue
        y, sup = exact_verify_support(R, nv, yf)
        if y is None:
            nrat += 1; fails.append((m, cnt[0], k, 'RAT')); continue
        nok += 1
    print(f'{vname}: OK {nok}/115  FLOAT_NO_CERT {nfloat}  RATFAIL {nrat}', flush=True)
    if fails and nok < 115:
        print('   失败点(前12):', fails[:12], flush=True)
