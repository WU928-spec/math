# β 引理证明（v2，nofit 版，2026-09-23）

> **β 引理**：razor 带口袋2 角落（全部角落约束）+ sliver（J=j₁+j₂，jᵢ>1−J ∀i≥3，t+J≤1）+ 可装箱 ⟹ 矛盾。
> 证明链 = sliver 紧性引理（§1，三证齐备）+ 紧性 ⟹ mon2 不可能（§2-4，nofit 版）。
> 机器与 senior 用 0-indexed：s₀ ≤ s₁ ≤ … ≤ s_{nS−1}（nS=m−1 台非 M₀ 机）。
> v1 → v2 变化：引理 H 改为 nofit 版（agent-1 复核修复），升链杀统一为单计数（存货 ≤ k−1 < k）。

## 0. 已证输入

- sliver 紧性引理（main；agent-3 二证、agent-1 三证）：可装箱+sliver ⟹ **全紧**：JJJ={t,j₁,j₂} 且 t+j₁+j₂=1；每 SS 对和=1；每 SJ 箱=互补对 (s,1−s)。⟹ junior 多重集 **J = {j₁,j₂（和 1−t，各∈[t,2t]）} ∪ {1−s : s ∈ R}**（R=残差 senior）。
- 角落约束（全合法已审）：pair xᵢ ≥ p−sᵢ+MG（机 i 负载 >p）；mon2（低端区 [0,jj] junior 不减）；fs（x_{jj}=q₁=max J）；nofit（hi 区 sᵢ>K−q₁，K=5(a_m+q₁)/4）；窄带 t≤j≤2t；senior 非小 s≥1−2t；B3 s≤1−t；danger p+t>5/4；到达递减 **q₁≤a_m=s₀**；squeeze Σℓ≤nS−t；B1 s₀+s₁≤1。
- 实验背书：main_tight_construct 4373/4373 全紧实例角落无效（4368 mon2 死）+ 664 例存货统计（均值 1.8）。

## 1. 三个推论（C1–C3）

**(C1) 全体 junior ≤ s₀**：q₁ = max J ≤ a_m = s₀（到达递减）。
**(C2) SS={s₀,s₁} 且 s₀+s₁=1**（正法版，agent-1 复核 #11 修正）：
- s₀∈SS：若否，s₀∈R ⟹ 1−s₀∈J ⟹ q₁ ≥ 1−s₀，又 q₁≤s₀ ⟹ s₀≥1/2；SS={u,v}（u+v=1，u≤v）取 u≥s₁ ⟹ v=1−u≤1−s₁≤1−s₀≤s₀ ⟹ v=s₀，矛盾（s₀∉SS）。∴s₀∈SS。
- SS={s₀,v}，和=1 ⟹ v=1−s₀。若 v≠s₁，则 s₁∈R ⟹ 互补件 1−s₁∈J ⟹ q₁ ≥ 1−s₁；又 q₁≤s₀（C1）⟺ s₀+s₁ ≥ 1；而 B1：s₀+s₁ ≤ 1 ⟹ s₀+s₁=1 ⟹ v=1−s₀=s₁——与 v≠s₁ 矛盾。∴ **v=s₁ 且 s₀+s₁=1**。∎
- 推论（条件钉，非恒钉）：q₁ = max(j₂, 1−s₂) ≤ s₀（C1；1−s₂ ≤ 1−s₁ = s₀）；**q₁=s₀ 仅当 j₂=s₀ 或 s₂=s₁(=1−s₀)**。
**(C3) p+MG ≤ 2s₀**（机 0 pair 可行必要：x₀ ≥ p−s₀+MG 且 x₀ ≤ q₁ = s₀；否则机 0 窗口空，直接死）。

## 2. 引理 H′（高位 junior 存货，nofit 版）

**引理 H′**：令 Q = #{j ∈ J : j ≥ p−s₀+MG}（机 0 pair 下界意义的高位存货）。则
**Q ≤ (k−2) + 1 = k−1**（k=jj+1=低端区机器数）。
**证明**（按 J 的三类成员逐一计数）：
1. **j₁**：j₁ ≤ (1−t)/2（j₁+j₂=1−t、j₁≤j₂）。(1−t)/2 ≥ p−s₀ ⟺ s₀ ≥ p−(1−t)/2 > 5/4−t−(1−t)/2 = 3/4−t/2 > 1/2 ≥ s₀（s₀≤s₁=1−s₀ ⟹ s₀≤1/2；t<1/2 ⟹ 3/4−t/2>1/2）——矛盾 ⟹ **j₁ 不够格**。
2. **j₂**：j₂ ≥ p−s₀ ⟺ j₂+s₀ ≥ p。j₂ ≤ q₁ ≤ s₀（C1）⟹ **j₂ 够格 ⟺ 2s₀ ≥ p**（至多 1 件；j₂=q₁=s₀ 同值时被 fs 钉走，机 0 不可用——见 §4）。
3. **互补件 1−s（s ∈ R）**：1−s ≥ p−s₀ ⟺ s ≤ τ := 1−p+s₀−MG。
   - **hi 区成员永不够格**（nofit）：s ∈ R ∩ hi ⟹ s > K−q₁ = 5(s₀+q₁)/4−q₁ = (5s₀+q₁)/4；又 **(5s₀+q₁)/4 ≥ τ** ⟺ s₀+q₁ ≥ 4−4p——而 s₀+q₁ ≥ 1−t（s₀≥1−2t、q₁≥t）且 1−t ≥ 4−4p ⟺ p ≥ (3+t)/4 ⟸ danger p > 5/4−t ≥ (3+t)/4 ⟺ t ≤ 2/5 ✓（razor t≤1/3）⟹ s > K−q₁ ≥ τ ⟹ 1−s < p−s₀，**不够格**。
   - **low 区成员**：R ∩ low = {s₂, …, s_{jj}}（s₀,s₁ 已入 SS），共 **k−2** 台 ⟹ 互补件够格者 **≤ k−2**。
   ∴ Q ≤ (k−2) + 1 = **k−1**。∎

## 3. mon2 升链杀（k≥3）

低端区 mon2 升链 x₀ ≤ x₁ ≤ … ≤ x_{jj} = q₁：
- x₀ ≥ p−s₀+MG（机 0 pair）且链不减 ⟹ **链上 k 件全部 ≥ p−s₀+MG** ⟹ 需 Q ≥ k。
- 引理 H′：Q ≤ k−1 < k ⟹ **k ≥ 3 全部不可能**（含 open 段 k=3..nS−2）。∎

## 4. k=2（jj=1）：化归 hi 区可行性

k=2 ⟹ 低端区 = {机 0, 机 1}，机 1=jj 由 fs 取 q₁（≤s₀，C1）：
- 机 0 的 x₀：候选 = {j₂（若 2s₀≥p 且 j₂≠q₁）} ∪ {s₀ 值 junior（若 j₂=q₁=s₀，同值 distinct 件无碍，agent-1 复核④）} ∪ {1−s : s ∈ R∩low}。k=2 时 R∩low = ∅（jj=1 ⟹ 机器 2 起全 hi；R∩hi 互补件由 nofit 封死，引理 H′）⟹ **x₀ ∈ {j ≥ p−s₀+MG 的 j₂ 类}**，需存在 junior ∈ [p−s₀+MG, q₁] 供机 0——不满足 ⟹ 机 0 窗口空死 ✓。
- 满足时：机 0←x₀、机 1←q₁（fs+pair：s₀+q₁ ≥ s₀+x₀ ≥ p+MG ✓；C3：x₀ ≤ q₁ ≤ s₀ ⟹ p+MG ≤ 2s₀ ✓）。
- **剩余义务（§5）**：hi 区机器 2..nS−1 与剩余 junior（J ∖ {x₀, q₁} ⊇ {j₁} ∪ {1−s : s ∈ R}）的匹配——hi 机窗口 [max(t, p−sᵢ+MG), min(2t, K−sᵢ)] 与 nofit（sᵢ > K−q₁）。

## 5. hi 区子分析（agent-3 补全处）

预期机制：hi 区 senior sᵢ > K−s₀ = (5s₀+s₀)/4 = 3s₀/2 ⟹ 每台 hi 机 junior 窗口上界 K−sᵢ < K−3s₀/2 = (5s₀+s₀)/4−3s₀/2 = s₀/4·…（K−sᵢ 小），只能收小 junior；而剩余 junior 中最小者 j₁ 与互补件 {1−s}（s > s₁ ⟹ 1−s < s₀）——匹配结构 + 件数账（hi 机数 nS−2 vs 可用小 junior 数）预期矛盾。

## 6. 结论（条件于 §5 补全）

全紧结构 ⟹ C2/C3 + 引理 H′（Q ≤ k−1）⟹ k≥3 死；k=2 化归 hi 区可行性，其矛盾由 §5 给出 ⟹ 可装箱+sliver+razor 角落 = ∅ ⟹ **β 引理成立**。

## 复核记录

- v1（main_beta_proof_draft.md）经 agent-1 敌意复核：判 SUSPECT-可修复——引理 H 原"≤2"版被反例击穿（s₃,s₄ 同 ≤τ），其 nofit 修复（s₃ > K−q₁ ≥ τ ⟹ 互补存货 0）已并入为引理 H′；C2 VALID；紧性引理第三独立证 ✓。
- v2 待复核：重点 = 引理 H′ 第 3 类的 low/hi 分划（R∩low = {s₂..s_{jj}} 的计数 k−2）与 §4 的 j₂<q₁ 严格性。
EOF
