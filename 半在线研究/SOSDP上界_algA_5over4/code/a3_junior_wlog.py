"""a3_ junior 侧规范指派 w.l.o.g. 定向裁决。
目标结构：JJJ 可行（三小件和<=1）+ 规范 SJ 失败（s_{2a}+j_0>1 类）——即"junior 前大后小、
senior 前小后大"的 pair 绑机角点。若在角落非装箱 LP 区域找到"可装箱但规范指派失败"的点
⟹ (W'') 反例（BREAKING）；若找不到 ⟹ 障碍证据：可装箱性先死（(P) 方向）。
"""
import numpy as np
from scipy.optimize import linprog
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_constraints import build_p2
from a3_grouping_wlog import all_bin_types, fixed_caps_ok


def run(ms=(6, 7, 8)):
    npts = npack = nkill = 0
    for m in ms:
        nS = m - 1
        tl = (m - 1) / (4 * (m - 2))
        for k in range(1, m):
            A, bc, bt, names, nv = build_p2(m, (0, 0, nS, 0, 0, 0), k,
                                            drop=('SS', 'SJ', 'JJJ', 'JJ'))
            Af = np.array([[float(z) for z in row] for row in A])
            for t0 in np.linspace(tl + 0.002, 1 / 3, 5):
                bf = np.array([float(bc[i]) + float(bt[i]) * t0 for i in range(len(A))])
                # 定向目标：juniors 前大后小 + seniors 前小后大（pair 绑机的 JJJ 活/SJ 规范死结构）
                obj = np.zeros(nv)
                obj[2 + nS + 0] = 1.0; obj[2 + nS + 1] = 1.0      # j_0, j_1 大
                obj[2 + 2 * nS - 1] = -1.0; obj[2 + 2 * nS - 2] = -1.0  # j 末小
                obj[2 + nS - 1] = 1.0; obj[2] = -1.0              # s 末大 s_0 小
                res = linprog(c=-obj, A_ub=Af, b_ub=bf, bounds=(None, None), method='highs')
                if res.status != 0:
                    continue
                x = res.x
                p, tt = x[0], x[1]
                s = sorted(x[2:2 + nS])
                j = list(x[2 + nS:2 + 2 * nS])
                npts += 1
                types = all_bin_types(s, j + [tt], m - 1)
                if not types:
                    continue
                npack += 1
                okc = [cnt for cnt in types if fixed_caps_ok(m, cnt, s, j, tt)]
                print(f'  可装箱点 m={m} k={k} t={t0:.4f}: 型 {sorted(types)} 规范ok={[fixed_caps_ok(m,c,s,j,tt) for c in types]}')
                if not okc:
                    nkill += 1
                    print(f'  ✗✗ (W\'\') 反例！p={p:.4f} s={np.round(s,3)} j={np.round(j,3)}')
    print(f'汇总：定向角点 {npts}，可装箱 {npack}，规范全失败（反例）{nkill}')


if __name__ == '__main__':
    run()
