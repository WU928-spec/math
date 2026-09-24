# B4 单行合法性：取等格精确证书记录（main，2026-09-23）

判决：B4_q（s_{nS+1−q}+j_{q+2}≤1, q∈[2a+1,nS−2]）为合法必要条件（razor 角落+可装箱 ⟹ 成立）。

## 证明链
1. **e=0（cnt=(1,m−3,0,1,0,0)）**：corner LP+B4_q 破+(r≥q) 全域 INFEASIBLE——**111/111 精确 t-uniform Farkas 证书**（m=6..16，Fraction，A^Ty=0/bt^Ty=0/bc^Ty=−1，零 RATFAIL；管线 main_b4eq_probe.py + fast_lp.exact_verify_support）⟹ B4 破 ⟹ r<q；r<q ⟹ C 可用 r−2<q−2≤q−g（g≤2）⟹ Hall 亏缺 ⟹ 不可装箱（main_b4_supply.md Case 2）。
2. **e=1（cnt=(2,m−5,0,1,1,0)）**：corner LP+B4 破+(r≥q−2) 全域 INFEASIBLE——**45/45 精确证书**（m=6..16，同标准）⟹ r<q−2 ⟹ 可用<q−4≤q−g（g≤4）⟹ 亏缺 ⟹ 不可装箱。
3. ∴ B4 破 ⟹ 不可装箱 ⟹ **B4_q 合法**。
4. 行集合法性：V.build 默认行（agent-1 审）、A5+LZ/HZ（agent-3 复核 VALID）、B1（SS01，a≥1 直证）、B2（min-triple，agent-1 引理）、B3（c=0 ⟹ s≤1−t）；取等/破例两行=case 假设（分情形法合法）。
5. 推论：**uncond 115 点与 T2 模板（m=6..60, 2971/2971, agent-1 复核 VALID）的唯一条件行解除 ⟹ uncond 层转无条件**。
