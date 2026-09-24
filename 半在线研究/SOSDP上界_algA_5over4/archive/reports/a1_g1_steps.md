# G1-razor 最后定量步 (i)+(ii) — a1_

> main 全责派单。纯证成任务（39 点幻影双零，无反例压力）。目标：证成 ⟹ razor 带
> (P) 第二证明全域完成。本文 = (i) 簿记显式化 + (ii) Hall 退化分解 + 精确卡点。

## (i) 挤压簿记（SS 箱亏空与净 slack）
razor 角落：ℓ_i ≥ p > 5/4−t，Σℓ ≤ nS−t。
**亏空预算**：B := (nS−t) − nS·p < t(nS−1) − nS/4（用 p > 5/4−t）。
负载散布：max ℓ − min ℓ ≤ B（全 ℓ≥p 且总和 ≤ nS−t）。
**值散布链**：|Δs|, |Δj| ≤ B + |Δℓ| 耦合，经机器配对 ℓ=s+j 反解：
s_i = ℓ_i − j_i ⟹ |s_i − s_k| ≤ |Δℓ| + |Δj|，j 散布受 band 与 Σ 双控。
**SS 箱亏空**：真实装箱的 SS 对 (e, e′)：e + e′ ≤ 1，亏空 1−e−e′。e, e′ 均 ∈ 该 SS 箱
⟹ 箱和 = ℓ-型值（两 senior 同箱）∈ [2(1−2t), 1]。亏空下界 1−2(2t) 上界…
**净 slack 来源**：亏空预算 B 是全局的；重匹配的可行 slack = Σ(真实匹配 slack_q) ≥ 0，
需要逐 rank 分布。(i) 的可证形态：**Σ_q slack_q + (SS 箱亏空) ≥ Σ_q (μ_q + ν_q)**——
总量版（必要），逐 rank 版（充分）见 (ii)。

## (ii) Hall 退化分解（链图形式, §21.1）
真实匹配（M_old vs U）：M_old,(q) + U,(q) ≤ 1，记 slack_q = 1 − M_old,(q) − U,(q) ≥ 0。
规范匹配需：M_new,(q) + Y,(q) ≤ 1，即 **μ_q + ν_q ≤ slack_q**，其中
- μ_q = M_new,(q) − M_old,(q)（挤出换入 ≥s_{2a+1}、换出 ≤s_{2a} 的 senior 端退化）
- ν_q = Y,(q) − U,(q)（§21.3 补集反向支配：真实 JJJ/JJ 消耗 ≥ 规范 ⟹ U ≤ Y 逐分量）。
**μ_q 界**：μ_q ≤ w·δ_swap，w=交换数，δ_swap = max(e−s′) ≤ 2t−(1−2t) = 4t−1（粗）。
**ν_q 界**：ν_q ≤ Δ = Σ(T−Y0) + Σ(U_J−YJJ)（消耗超出总量）。
**razor  tightness 障碍**：slack_q 可以为 0（razor 对全紧），粗界 μ+ν = O(t) ≫ 0 ——
粗界必死，须**精确相消**。

## 二分证明骨架（关键结构）
**Case A（razor 刚性，§18.3 低端全等 + §21.5b 高端退化条件）**：值全坍缩
（s≈σ, j≈p−σ）。此时 e ≈ s′（同值）⟹ 交换值中性 ⟹ μ_q = ν_q = 0（重排同值件），
G1 成立（任何等值 senior 互换，匹配不变）。**此情形 G1 已证**（条件化于 §21.5b
的高端退化条件）。
**Case B（非刚性）**：∃ 箱 slack δ > 0（刚性 ⟺ 全箱紧；非刚性 ⟹ 有 slack）。
退化 μ_q + ν_q 被值散布控制，散布被 B 控制；需 **spread ≤ f(slack 分布)**——
精确的剩余不等式：
> ∀q：μ_q + ν_q ≤ slack_q，其中 μ_q+ν_q 由 (B, band) 定界，slack_q 由真实匹配定。
> 归约为单参数不等式：B ≤ c·min_q slack_q（c = 散布/slack 转换常数，待 agent-3
> 动力学钉 c；簿记侧 B = t(nS−1)−nS/4 已显式）。

## 精确卡点（诚实）
1. Case A 已证（条件化 §21.5b 高端退化——agent-3 域）。
2. Case B 归约为 **spread-slack 不等式**：值散布（B-界）≤ c·匹配 slack。
   逐 rank 版 μ_q+ν_q ≤ slack_q 在 slack_q = 0 的 tight 行必须由**精确等值**（Case A）
   或**动力学给出的 c**（agent-3）满足——纯计数侧已无路（粗界 O(t) vs 0）。
3. 若 agent-3 在 razor 动力学下证 min slack ≥ B/c（或其高端非刚性给出 δ 分布），
   G1-razor 即闭。簿记义务已尽：B 公式、μ/ν 分解、slack_q 定义、Case A 证明。

## 数值状态
无可装 razor 实例（39 点幻影 0/0），纯符号任务；全部判定条件化于上述卡点 2。
