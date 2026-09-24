# a3_caseB_bookkeeping.md —— G1-razor Case B 支援：挤压簿记 (i)（agent-3）

> 任务（main 派单）：Case B 单参数不等式 B ≤ c·min_q slack_q 的纯符号证明
> （假想可装箱角落域，无可采样实例）。a1_g1_steps.md 定义：B=(nS−t)−nS·p <
> t(nS−1)−nS/4；slack_q = 1−M_old,(q)−U,(q)；需 ∀q: μ_q+ν_q ≤ slack_q。

## 0. 判决先行

**"B ≤ c·min_q slack_q"作为字面命题不可证且方向错误**——min_q slack_q 在 razor 带
恒可为 0（razor 对全紧，a1_g1_steps §ii 自承"tight 行 slack_q=0"），任何 B>0、c 有限
都被 min=0 杀死。可证且正确的替代物=本文 §2 的**临界窗局部化**：
逐 rank 不等式 ∀q: μ_q+ν_q ≤ slack_q ⟺ **临界窗 (1−e′, 1−s_{2a}] 内计数边际覆盖
挤出亏缺**——窗为空（s_{2a}=e′，razor 刚性）⟺ Case A（a1 已证）；
窗非空 ⟹ 义务压缩为单一窗内的计数边际引理（与 B4-Hall/G1 中 junior 段同族）。

## 0'. 勘误（agent-1 a1_review_t2_caseb.md 两点修正，2026-09-23）

1. **Σν=Δ_jjj 仅 e=0 精确**：e=1（shape B）时规范变换还产生 JJ 箱 slack 增益
   Δ_jj（规范 JJ 对=最小可用对，真实 JJ 对 ≥ 规范 ⟹ 增益），§1 总量恒等应读作
   Σ(μ+ν) = Δ_ss + Δ_jjj (+ Δ_jj when e=1)——e=0 时 Δ_jj=0 结论不变。
2. **§2 的 "G1 ⟺ ∀u∈W: M(u)≥deficit(u)" 系过 claim**：M(u)=#{U≤u}−#{M_old>1−u}
   用的是**易池 U**（真实 SJ junior 池），而规范匹配需用**难池 Y**（规范 JJJ/JJ 消耗
   更小件后留下的更大 junior 池，#{Y≤u} ≤ #{U≤u}）——该条件对 G1 **必要非充分**：
   窗引理即使证成也不闭合 G1，junior 侧须以 Y+ν(u) 重写（与 a1_g1_steps 的 μ_q/ν_q
   分解合流）。窗条件正确读法=**必要条件族**（G1 ⟹ 窗内边际覆盖）；充分侧=agent-1 主线。
3. 轻微：W=∅ 的充要应为 e′ ≤ s_{2a}（非严格小于取等即可豁免）。

## 1. 总量簿记 = 恒等式（(i) 的总量版，已证）

记真实装箱（存在，假设）的 SS 对（a=1 写核心情形，a 一般同理）为 (e,e′)，e+e′≤1；
规范目标 SS=(s_1,s_2)；JJJ 真实三元组 vs 规范最小三元组 {t,j_1,j_2}（G2a 已证）。
定义退化总量：
- Σμ = (e+e′) − (s_1+s_2) =: Δ_ss ≥ 0（senior 端：挤出使 SJ 槽帽变紧的总量）；
- Σν = Σ(real JJJ) − Σ(canonical JJJ) =: Δ_jjj ≥ 0（junior 端：规范 JJJ 取最小 ⟹
  规范 SJ 池更大，§21.3 补集反向支配已证）。
**SS 箱 slack 增益 = Δ_ss**（1−s_1−s_2 ≥ 1−e−e′）；**JJJ 箱 slack 增益 = Δ_jjj**。
⟹ Σ_q(μ_q+ν_q) = Δ_ss+Δ_jjj = SS/JJJ 两箱的 slack 增益 ——**总量恒等**：
Σ_q slack_q（SJ 各箱）+ Δ_ss + Δ_jjj = Σ_q(μ_q+ν_q) + Σ_q slack_q（恒等，
即 Σℓ 守恒的改写）。(i) 的总量必要版**由此封闭（平凡但严格）**。
附带精确化 a1 的 B：装箱总 slack S_total = nS − t − Σℓ ∈ [0, B]，
且 **spread(ℓ) ≤ B − S_total**（Σℓ=nS−t−S_total ⟹ max ℓ ≤ Σℓ−(nS−1)p ⟹
max−min ≤ nS−t−S_total−nS·p = B−S_total）——总 slack 越大负载散布越小。

## 2. 临界窗局部化（(ii) 逐 rank 版的精确归约，新）

新 SJ 多重集 M_new = M_old − {s_1,s_2} + {e,e′}（a=1）。SJ-REV（§21.1 已证）：
规范匹配可行 ⟺ 反序配对可行 ⟺ ∀u: #{M_new > 1−u} ≤ #{U ≤ u}。
与真实匹配的同一计数相减，阈值亏缺有显式：
> **deficit(u) = #{e,e′ > 1−u} − #{s_1,s_2 > 1−u}**。

- s_1,s_2 为全池最小两 senior ⟹ #{s_1,s_2 > 1−u} 在所有 senior 对中最小；
  亏缺为正仅当 u ∈ **临界窗 W = (1−e′, 1−s_2]**（e′=max(e,e′)），
  **W ≠ ∅ ⟺ s_2 < e′**；窗内 max deficit = #{e,e′ 中大于 s_2 的个数} ∈ {1,2}。
- ⟹ **G1-razor ⟺ ∀u∈W: M(u) := #{U≤u} − #{M_old>1−u} ≥ deficit(u)**。
- W = ∅ ⟺ s_2 = e′ ⟺ razor 刚性把真实 SS 钉到规范对 ⟹ Case A（a1 已证，
  μ_q=ν_q=0 值中性交换）——**Case A 与 Case B 的分界由此精确化：分界不是
  "是否存在 slack"，而是 s_2 与 e′ 是否取等**。

一般 a：临界窗 (1−e′_{max}, 1−s_{2a}]，deficit = #{挤出 senior 超过 s_{2a}者} ≤ 2a，
同理归约。

## 3. 剩余义务（最后一步，与主线同族）

Case B 的唯一剩余：**临界窗计数边际引理**——razor 角落+真实装箱存在 ⟹
窗 W 内 M(u) ≥ deficit(u)。等价说法：真实 SS 的大件 e′ 比 s_2 大 δ 时，
SJ 池在 (1−e′, 1−s_2] 带内必须有多出 deficit 件的小 junior 存货。
- 该存货正是 main 方向 1"小 junior 供给≈β_s"与 B4 逃逸 (b)（L_q 进 SS 的供给）
  的同族计数——**三处义务（G1 Case B、B4 逃逸 b、方向1 供给计数）收敛到同一
  razor 小 junior 存货引理**。
- 反证方向（推荐）：设 W 内 M(u) < deficit(u) ⟹ 小 junior 存货不足 ⟹
  与 B2（t+j_1+j_2≤1，规范 JJJ 必耗最小两件）联立 ⟹ 真实装箱的 SJ 段
  在临界带 Hall 亏缺 ⟹ 与"真实装箱存在"矛盾。所需唯一新原料：
  razor 角落的 pair/mon2 对小 junior 存货的钉死（挤压簿记域，进行中）。

## 4. 与 B 的关系（回答 main 的单参数形式）

B 控制的是**负载侧**总预算（Σℓ 距 nS·p 的总散布）；临界窗引理需要的是
**值侧**的 junior 存货计数。两者的桥：spread(ℓ) ≤ B−S_total（§1 新证）+
s=ℓ−j 反解 ⟹ 值散布 ≤ (B−S_total) + spread(j)。但 razor 紧时（S_total→0）
值散布上界仍 O(B)=O(t)——**粗界在 tight 行必死（与 a1 一致）**，故单参数
B ≤ c·min slack_q 形式不可能；正确形式=§2 临界窗（tight 行 slack=0 处
由 s_2=e′ 取等自动豁免，不需 slack）。
