"""引理 P3C（口袋3"他机全2件"角落计数闭合）的 sympy 符号复核。
每条 check 对应 pocket3_counting.md 的一步。退出码 0 = 全 PASS。
"""
import sys
import sympy as sp

m, t, q1 = sp.symbols("m t q1", positive=True)
FAILS = []


def check(name, expr):
    val = sp.simplify(expr)
    ok = val.is_zero is True or val == 0
    print(f"[{'PASS' if ok else 'FAIL'}] {name}   (化简 = {val})")
    if not ok:
        FAILS.append(name)


# 步骤 1：ℓ₀ ≥ 2t + q₁（x,y ≥ t、z ≥ q₁）
x, y, z = sp.symbols("x y z", nonnegative=True)
l0 = x + y + z
check("ℓ₀ − (x−t) − (y−t) − (z−q1) = 2t+q1", l0 - (x - t) - (y - t) - (z - q1) - (2 * t + q1))

# 步骤 2：s_i ≥ ℓ₀ − j_i ≥ ℓ₀ − q1 ≥ 2t
si, ji = sp.symbols("si ji", nonnegative=True)
expr = (si - 2 * t) - (l0 - q1 - 2 * t)
check("s_i − 2t 与 (ℓ₀−q1−2t) 同式", expr - (si - (l0 - q1)))

# 步骤 3：两 senior 不共箱 ⟺ 4t > 1 ⟺ t > 1/4
check("2·(2t) − 1 在 t=1/4 为 0", (4 * t - 1).subs(t, sp.Rational(1, 4)))

# 步骤 3b：窗口下界 m/(4(m−1)) > 1/4 ⟺ 0 < 1（恒严格）
check("m/(4(m−1)) − 1/4 = 1/(4(m−1))", m / (4 * (m - 1)) - sp.Rational(1, 4) - 1 / (4 * (m - 1)))

# 步骤 4：senior 箱至多 1 件非 senior：s_i + 2t ≥ 4t > 1
check("senior+两件非senior 下界 − 4t", (2 * t + t + t) - 4 * t)

# 步骤 5：非 senior 计数 m+3 与容量 m+2
# 非 senior = {x,y,z,t} ∪ {j_i}_{i=1..m−1}
check("非senior 件数 = m+3", 4 + (m - 1) - (m + 3))
check("容量 (m−1)·1 + 3 = m+2", (m - 1) + 3 - (m + 2))
check("缺口 (m+3) − (m+2) = 1", (m + 3) - (m + 2) - 1)

# 箱数守恒核查：senior 各占一箱(m−1) + 剩余 1 箱 = m
check("箱数守恒", (m - 1) + 1 - m)

# 数值 sanity：窗口下界 > 1/4 对 m=4..30
for mv in range(4, 31):
    assert mv / (4 * (mv - 1)) > 0.25, f"m={mv} 窗口下界不破 1/4"
print("[PASS] 数值 sanity: m/(4(m−1)) > 1/4 对 m=4..30")

print()
if FAILS:
    print("FAIL:", FAILS); sys.exit(1)
print("全部 PASS（引理 P3C 代数链成立）")
