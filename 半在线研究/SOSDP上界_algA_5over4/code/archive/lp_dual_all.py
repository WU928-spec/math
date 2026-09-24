"""提取全部 12 张卡片的对偶证书，找统一模式。"""
import numpy as np
from scipy.optimize import linprog
import lp_dual
from lp_dual import build, NAMES, L0, T_

for m in (4, 5, 6):
    for a in range(0, (m - 1) // 2 + 1):
        for ci in (True, False):
            lp_dual.DESC.clear()          # 关键修复：清空名称列表再 build
            A, b, c, names = build(m, a, ci)
            res = linprog(c, A_ub=A, b_ub=b, bounds=[(0.0, None)] * 13, method="highs")
            ca = res.x[L0] + res.x[T_]
            bind = [(names[i], round(-mg, 4)) for i, mg in enumerate(res.ineqlin.marginals) if abs(mg) > 1e-9]
            print(f"m={m} a={a} {'i' if ci else 'ii'}: max={ca:.6f} t*={res.x[T_]:.4f} l0*={res.x[L0]:.4f}")
            for nm, w in bind:
                print(f"    {w:8.4f}  {nm}")

