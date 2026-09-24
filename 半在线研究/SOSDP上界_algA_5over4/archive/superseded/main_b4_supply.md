# B4 单行合法性证明（main，2026-09-23）

> **目标**：razor 角落+可装箱 ⟹ **B4_q**：s_{nS+1−q} + j_{q+2} ≤ 1 对 q ∈ [2a+1, nS−2] 成立（T2 模板与 uncond 115 的唯一条件行）。
> 策略：设 B4_q 破（j_{q+2} > 1−s_{nS+1−q}），导出不可装箱。

## 0. 记号与预备

- L_q = {s_{nS+1−q}, …, s_{nS}}（q 个最大 senior）；其 SJ 伴侣 ⊆ C = {t} ∪ {j ≤ 1−s_{nS+1−q}}（senior ≥ s_{nS+1−q} 配 j > 1−s_{nS+1−q} 则和 >1）。
- **B4_q 破 ⟹ r := #{j ≤ 1−s_{nS+1−q}} ≤ q+1**（第 q+2 小 junior 超阈 ⟹ 至多 q+1 件在阈下）。
- **B4_q 破 ⟹ s_{nS+1−q} > 1−2t**（否则 j_{q+2} ≤ 2t ≤ 1−s_{nS+1−q} 自动成立）。
- razor cnt：(1+e, m−3−2e, 0, 1, e, 0)（c=f=0，a=1+e SS 箱=2+2e 槽，d=1 JJJ，e JJ 箱）。
- **min-triple w.l.o.g.**（G2a/Y′，LP_CONSTRAINTS §21.3 复核 VALID）：可装箱 ⟹ ∃装箱使 **JJJ={t, j₁, j₂}**（合法支配）。
- **JJ 自由性**：任意两 junior 和 ≤ 2q₁ ≤ 1（q₁≤1/2）⟹ JJ 箱可吃任意 junior（不占 C）。
- 预备恒真：t ≤ 1/3、q₁ ≤ 1/2、senior ∈ [1−2t, 1−t]（B3）、j ∈ [t, 2t]（窄带）。

## 1. 案例树（按 SS 槽中 L_q 成员数 g 分）

设 g = L_q 中进 SS 的 senior 数（0 ≤ g ≤ min(q, 2a)）。SS 伴侣来自 D = {s ≤ 1−s_{nS+1−q}}。

### Case 1：g = 0（L_q 全 SJ）

- JJJ={t,j₁,j₂}（w.l.o.g.）消耗 C 中 3 件（t,j₁,j₂ ∈ C ⟸ j₁,j₂ 为最小 junior、r≥2 时 j₂ ≤ j_r ≤ 阈 ✓；**r≤1 时见 Case 1b**）。
- C 可用 = r+1−3 = r−2 ≤ q−1 < q = SJ 需求 ⟹ **Hall 亏缺 ⟹ 不可装箱** ✓。

### Case 1b：g = 0 且 r ≤ 1（C = {t}∪{j₁} 或 {t}）

- C 可用 = r+1−|{t,j₁,j₂}∩C| ≥ r+1−(r+1) = 0 当 j₂∉C ⟹ JJJ 的 j₂ 不在 C 但 L_q 的 SJ 可用 = r+1−|C∩{t,j₁,j₂}|。
- r = 1：C={t,j₁}，JJJ 消耗 {t,j₁}（j₂∉C）⟹ 可用 0 < q（q ≥ 2a+1 ≥ 3）⟹ 亏缺 ✓。
- r = 0：C={t}，JJJ 消耗 t ⟹ 可用 0 < q ⟹ 亏缺 ✓。

### Case 2：g ≥ 1（逃逸 b：部分 L_q 进 SS）

- SJ 侧：L_q 中 q−g 个 SJ，需 C 可用 ≥ q−g。同 Case 1 计数：C 可用 ≤ r−2（r≥2）⟹ **需 r ≥ q+2−g**。
- **r < q 直接死**（e=0/1 通用）：可用 = r−2 < q−2 ≤ q−g（g ≤ 2a）⟹ 无论 g 取何值 Hall 亏缺 ✓。
- e=0（a=1，SS 槽=2）：g ≤ 2 ⟹ 需 r ≥ q ⟹ **幸存仅 (r, g) ∈ {(q,2), (q+1,1), (q+1,2)} 三格**（razor 薄）：
  - **(r=q, g=2)**：两 SS 槽全被 L_q 占 ⟹ SS={s_a,s_b}（L_q 内互配，s_a+s_b≤1），C 可用 r−2 = q−2 = SJ 需求恰取等；
  - **(r=q+1, g=1)**：一个 L_q 成员+D 伴侣（≤1−s_{nS+1−q}），C 可用 q−1 = 需求取等；
  - **(r=q+1, g=2)**：同 (r=q,g=2) 或两件各配 D。
- e=1（a=2，SS 槽=4）：g ≤ 4 ⟹ 需 r ≥ q−2 ⟹ **r ∈ {q−2, q−1, q, q+1}**，g ∈ {1..4}——格子更多但同型（L_q 互配对 + D 伴侣分配）。
- **立即死引理**：若 **s₁+s_{nS+1−q} > 1**（最小 senior 都配不了 L_q 最小成员）⟹ g=0，回 Case 1 杀 ✓——逃逸 b 仅在 s₁+s_{nS+1−q} ≤ 1 时存活。
- SS 侧可行性（**引理 SS-B4**，逃逸 b 封死，待证）：(r,g) 三格（e=0）逐格 + e=1 格子——候选杀法：①L_q 互配对的 razor 值带冲突（两大 senior 和 ≤1 ⟹ 两者 ∈ [1−2t, 1/2]，与其机器 junior ≥ p−s > p−1/2 的高位性冲突）；②D 伴侣的机器 junior ≥ p−d ≥ p−(1−s_{nS+1−q})=τ_q 高位 ⟹ 与 C 的小 junior（L_q 的 SJ 所需）构成 razor 两侧争夺；③取等格子（r−2 = q−g）下每个可用 junior 分配唯一 ⟹ razor pinning 后由 nofit/A5 杀（β v2 机制）。

## 2. 关键中间引理（待证）

**引理 SS-B4**（逃逸 b 封死）：razor 角落+可装箱+B4_q 破 ⟹ L_q 成员进 SS 不可行（g=0）。
- 思路 1（伴侣带）：L_q 成员 s（>1−2t）的 SS 伴侣须 ≤ 1−s < 2t，而 senior ≥ 1−2t（senior 非小引理）⟹ 伴侣 ∈ [1−2t, 1−s]。s > 1−2t ⟹ 伴侣带宽 = (1−s)−(1−2t) = 2t−s < 4t−1（razor 薄）。
- 思路 2（机器 junior 冲突）：伴侣 d ∈ D（小 senior）的机器 junior ≥ p−d ≥ p−(1−s_{nS+1−q}) ——此 junior 高位，与 C 的小 junior（L_q 所需）构成 razor 带两侧争夺（同 sliver 存货机制）。
- 思路 3（q 大情形）：q ≥ 2a+1 且 g ≤ 2a ⟹ L_q 的 SJ 成员 ≥ q−2a ≥ 1，SJ 侧取等 r−2 = q−g ⟹ C 可用全耗尽 ⟹ 每个可用 junior 分配唯一—— razor 值带 pinning 后由 nofit/A5 杀（β v2 机制）。

## 3. 与 v2（β）机制的关系

v2 的 nofit 存货引理（H′）是 corner 全约约束：hi 区 senior（s > K−q₁）的互补 junior 不可作高位件。B4 的 C-junior 供给同法：C 的 junior（≤1−s_{nS+1−q}）须住 senior ≥ p−1+s_{nS+1−q} =: τ_q 的机器 ⟹ **r ≤ #{s ≥ τ_q}**（供给上界）。τ_q = s_{nS+1−q}−(1−p)：与 L_q（≥ s_{nS+1−q}）的关系 = razor 带计数核。

## 4. 待办

1. 引理 SS-B4 三思路择优证成（逃逸 b 封死）；
2. Case 2 的 r 边界格（r ∈ {q, q+1}）逐格封闭；
3. 复核（agent-1）+ 实验（B4_q 破 + SS 可行构型的 LP 采样→装箱判定，补 agent-3 的 9402 逃逸扫描）。
EOF
