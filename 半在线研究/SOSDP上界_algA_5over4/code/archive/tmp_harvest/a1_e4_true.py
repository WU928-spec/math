import sys
sys.path.insert(0, 'code')
import numpy as np
from scipy.optimize import linprog
from fractions import Fraction as F
import importlib.util
spec = importlib.util.spec_from_file_location("probe", "code/main_b4eq_probe.py")
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)

m, cnt, k = 8, (1, 5, 0, 1, 0, 0), 3
A, bc, bt, nv, q = probe.build(m, cnt, k)
print('q =', q, 'nS =', m - 1)
# 名称：V.build 行 + probe 追加行（A5_1..A5_k, LZ, HZ, B4broken, req_q）
import a1_value_lp2 as V
names = list(V.build(m, cnt)[3])
names += [f'A5_{i}' for i in range(1, k + 1)] + ['LZ']
if k < m - 1:
    names += ['HZ']
names += ['B4broken', 'req_q']

Af = np.array([[float(x) for x in row] for row in A])
bcf = np.array([float(x) for x in bc]); btf = np.array([float(x) for x in bt])
Aeq = np.vstack([Af.T, btf.reshape(1, -1), bcf.reshape(1, -1)])
beq = np.concatenate([np.zeros(nv), [0.0, -1.0]])
res = linprog(c=np.zeros(len(A)), A_eq=Aeq, b_eq=beq, bounds=(0, None), method='highs')
print('status:', res.status)
if res.status == 0:
    y = res.x
    sup = [(names[i], y[i]) for i in range(len(A)) if y[i] > 1e-8]
    for nm, v in sup:
        f = F(float(v)).limit_denominator(10**6)
        print(f'{nm:12s} {f}  ({float(f):.4f})')
