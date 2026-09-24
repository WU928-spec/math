# 敌意复核：T2 模板 + Case B 簿记（a1_review_t2_caseb.md）

## ① T2 模板（a3_template115.md / a3_template_verify.py / a3_template_fit.py）
### (a) 权重来源/过拟合风险：无统计过拟合；剩 B4 统一条件（已如实标注）
拟合=逐点精确支撑行解 A_sup^T w=0∧bc^T w=−1（Fraction 高斯消元）→最小正整数模式——
**精确有理对象，非统计拟合**；模板代数是 (m,k)-generic 指标恒等式（文档"系数核对"
∀(m,k) 机械成立）。m=17..60 的 2971/2971 是**同一代数恒等的自洽复验**而非新数据——
但这不构成过拟合，因为命题本身是 m-generic 恒等式。**独立验证**：我用**自建行**
（按 §1 表格语义独立实现，非 a3 builder）在 m=10/12/16/40 四点手工核验：列平衡
0 破坏、bc^T w = −5033/30000 = −1/6−11MG 精确、bt^T w=0 ✓ ALL PASS。第三Builder
(a3_cert115_weights) 亦对拍过。**残留统一风险 = B4 行合法性**（SUSPECT，全 m 同条件）。
### (b) 逐行角色：B4 承重已如实标注 ✓
文档明示"全部模板以 B4_{q=nS−k} 为承重行 ⟹ 与 109/115 证书同条件（B4-Hall 引理，
见 a3_b4_review.md）；其余行全 VALID"——与 SEMANTICS 的 B4 SUSPECT（逃逸 a/b）分类
一致，无隐瞒。§3 的 sjrev 边界结构解释（q 越界 ⟺ 模板死 ⟺ SJrev 承重）与我独立的
α'/sjrev 分析逐点吻合 ✓。jrt 链行=值序坐标定义行（合法）；A5_1/A5_2/HZ = main
已证的 k-结构行。**T2 判定：VALID（代数）+ 条件性（B4-Hall，如实标注）**。
建议 SEMANTICS 登记："T2 模板 = 值语言 open 段 uncond 域 ∀m 符号证书（代数独立
验证过；承重行 B4 条件于 B4-Hall 引理）"。

## ② Case B 簿记（a3_caseB_bookkeeping.md）
### 正确的部分
- §0 "B ≤ c·min slack_q 字面不可证且方向错误"——与 a1_g1_steps §4 独立同结论 ✓。
- §1 spread(ℓ) ≤ B − S_total：逐步核（max ℓ ≤ Σℓ−(nS−1)p；spread ≤ 其 −p；
  B := nS−t−nS·p 与 a1 定义一致）✓ 恒等式成立。
- Σμ = Δ_ss：senior 多重集和守恒，逐 rank 求和=总量 ✓ 严格。
- §2 deficit(u) 公式与临界窗 W=(1−e′, 1−s₂] 推导 ✓（senior 侧干净）。
### 发现 1（实质）：Σν = Δ_jjj 对 e=1 漏 Δ_jj
Σν（rank 求和）= ΣY−ΣU = [Σ(real JJJ)+Σ(real JJ)] − [Σ(can JJJ)+Σ(can JJ)] =
Δ_jjj + Δ_jj。文档取 Σν := Δ_jjj——**shape A（e=0）精确；shape B（e=1）漏 JJ 箱
slack 增益 Δ_jj ≥ 0**。"a=1 写核心情形...a 一般同理"的"同理"对 e=1 不成立。
影响：总量恒等式在 shape B 上偏 Δ_jj（JJ 箱增益被记入义务侧而非资源侧），
使 (i) 总量版在 shape B 略弱（方向安全，但非恒等）。
### 发现 2（实质，方向宿疾）：§2 "G1-razor ⟺ ∀u∈W: M(u) ≥ deficit(u)" 的 ⟺ 过claim
M(u) 用 **U（真实 SJ junior 池）**；规范匹配需对 **Y（规范池）** 满足
#{M_new>1−u} ≤ #{Y≤u}。§21.3 补集反向支配：Y ≥ U 逐分量 ⟹ #{Y≤u} ≤ #{U≤u}——
**所述条件是必要的，非充分的**（把难池 Y 换成易池 U 放宽了）。必要条件成立
**不能**推出规范匹配存在 ⟹ §3"剩余义务=窗内引理"即使证成也**不足以闭合 G1**
（G1 要存在性=充分侧）。正确形式：义务须用 #{Y≤u} = #{U≤u} − ν(u)（消耗差），
即 §2 应保留 junior 侧 ν——与发现 1 同根（JJJ/JJ 消耗差被略）。
### 发现 3（轻微）：W=∅ ⟺ 应为 e′ ≤ s₂（文档写 s₂ = e′）
e′ < s₂ 也使 W 空（真实 SS 用更小 senior 时规范交换良性）；文档的等号刻画偏窄。
Case A/B 分界本意（e′ ≤ s₂ 良性）不受影响。
### 判定
簿记 §0/§1/spread/Δ_ss/deficit/窗 推导 **成立且有用**；两处实质修正（Δ_jj 漏项、
必要-充分方向）+一处轻微（W 空界）。**修正后**临界窗归约仍是 Case B 的正确骨架
（senior 侧干净；junior 侧须以 Y 池+ν(u) 重写 ⟹ 与 a1 的 μ_q/ν_q 簿记合流）。
建议 a3 吸收两修正后 SEMANTICS 升级"Case B 簿记：骨架 VALID，Σν/⟺ 两处修正待入"。
