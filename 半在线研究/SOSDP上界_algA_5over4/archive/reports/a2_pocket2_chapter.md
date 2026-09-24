# 口袋 2（单子机角落）：LP 路线的全 m 闭合

> 本章为 LP_ROUTE 终稿的口袋 2 全节草稿（agent-2 撰写，待 main 合并）。
> 记号沿用 LP_ROUTE §0/§1。所有 LP 结论基于修正 firststep 编码（SEMANTICS 行 8）。
> 验证工件：code/hole_close.py、uniform_hole_cert.py、a2_template_{b0,jt,k1,nf}.py、
> a2_forall_m.py、a2_residual_final.py、a2_lean_verify.py、fuzz_mon2.py、hole_reach.py。

## 2.0 模型、记号与计数恒等式

**口袋 2 角落**（最紧形态）：递减到达、OPT=1 归一化；fallback 任务 t 落入单子机
M₀={p}（p=最大初始任务；其余情形由 rest 体积界归纳到他处）。角落必需：
- 他机 m−1 台各恰 2 件 {s_i, j_i}（s_i 初始件 senior，j_i 首个后至件 junior）；
- 后至件递减 q₁=p_{m+1}≥…≥t（t 最闲在最后），junior 窄带 j∈[t,2t)、senior s_i>1−2t；
- danger p+t>5/4；K=(5/4)L，L=a_m+q₁≤1；**a_m=s₀**（p_m=最小初始件=最小 senior，
  递减到达 ⟹ 初始 m 件=全局最大 m 件；SEMANTICS 登记原料）；
- pair（M₀ 最闲）：s_i+j_i≥p ∀i；kcap：j_i≤q₁、q₁≤a_m、p<K。
- k 参数（firststep）：senior 升序 s₀≤…≤s_{m−2}；q₁ 落机 jj=k−1（best-fit 最满优先）：
  fit s_jj+q₁≤K；nofit s_i+q₁>K（i>jj）；j_jj=q₁。

**装箱 taxonomy 与计数**：rest（{s_i}∪{j_i}∪{t}）装入 m−1 箱（p 独占），窗口 t>1/4 排除
SJJ/SSS/SSJ/JJJJ 型 ⟹ 六型 SS/SJ/S/JJJ/JJ/J，计数 (a,b,c,d,e,f)。三守恒
（2a+b+c=m−1、b+3d+2e+f=m、箱数 m−1）⟹ **d=1+c+f≥1、a=1+c+e+2f≥1**（两箱型恒存在）。

## 2.1 保序引理（动力学的唯一入口）

**引理 2.1（保序）**：他机 2 件形态下，s_i<s_k 且 j_i>j_k ⟹ s_k+j_i>K。
证明：j_i 先到（递减）；其到达时两机各仅 senior；落 i 不落 k，best-fit 最满优先 ⟹
k 被 cap 阻断（s_k+j_i>K）或 s_i≥s_k，矛盾。∎
**推论**：低端区（s_i≤K−q₁，即 i≤jj）junior 单调不降：j₀≤…≤j_jj=q₁（同级重标号 WLOG）。
置信：双独立推导（主代理 + agent-2 的单调匹配引理）+ 1495 万实例 51516 真角落事件 0 反例
（fuzz_mon2.py）。这是全部中段论证的动力学基石。

## 2.2 全 m 手证：k=1 与 k≥m−2（无 LP）

**引理 2.2（P2K1）**：k=1 的角落不存在。
证明：a≥1 ⟹ SS 箱 {s_u,s_v}（u<v），s_u+s_v≤1。pair 与 j≤q₁ 给 s_u≥p−q₁；k=1 的 nofit
覆盖 v≥1：s_v>K−q₁=(5/4)a_m+(1/4)q₁≥(3/2)q₁。代入：1≥s_u+s_v>p+(1/2)q₁>5/4−t/2
（danger+q₁≥t）⟹ t>1/2，与 t≤2/5（Lemma B）矛盾。∎（agent-2 敌意复核通过：链极小、
原料全必要，adversarial_review.py。）

**引理 2.3（P2K-top）**：k≥m−2 的角落不存在。
证明：取 SS 箱大 mate v 分两支。
-（v 高端，v>jj）与 P2K1 同链：s_v>(5/4)a_m+(1/4)q₁，s_u≥p−q₁ ⟹ p<1−(5/4)a_m+(3/4)q₁
  ⟹（danger、a_m≥q₁）(1/2)q₁<t−1/4 ⟹ q₁<2t−1/2，与 q₁≥t 得 t>1/2 矛盾。
-（v 低端，v≤jj）：SS 配对+pair+danger ⟹ j_u+j_v>3/2−2t ⟹（低端单调）j_v>3/4−t，
  q₁≥j_v；L≤1 与 a_m=s₀ ⟹ j₀≥p−a_m>1/4−t+q₁>1−2t ⟹ 低端 junior 全>1−2t；
  JJJ 箱含低端 junior 则超载（(1−2t)+2t=1）⟹ JJJ 只能装 {t}∪{高端 junior} 共
  m−1−jj=m−k≤2 件<3 ⟹ d=0，与 d≥1 矛盾。∎（复核通过；低端支原料 a_m=s₀ 已登记。）

**引理 2.4（P2K-high，agent-2）**：任意 k，若某 SS 箱大 mate 在 nofit 区（v>jj）则矛盾
（同引理 2.2 的链）。**推论**：任何角落的全部 SS senior 都在低端区 ⟹ **2a≤k**。

**引理 2.5（P2S）**：q₁ 不入 JJJ 箱（q₁+两件≥q₁+2t，若入 JJJ 则 q₁≤1−2t；SS 箱给
p≤1/2+q₁≤3/2−2t，与 danger 得 t<1/4，与窗口矛盾）。**推论**：规范代表的池位 jj 若落入
JJJ 池段 [b, b+3d−1]（⟺ k∈[b+1, b+3d]）则该 (cnt,k) 不可能。

**引理 2.6（Class II 为空，agent-2）**：若 2a+b≤k（SS+SJ senior 全低端），则由引理 2.1
低端 junior 全>1−2t（引理 2.3 低端支链，k 无关）⟹ JJJ 只能装 {t}∪{高端} 共 m−k 件 ⟹
3d≤m−k；但 2a+b≤k ⟹ c=m−1−2a−b≥m−1−k ⟹ d=1+c+f≥m−k ⟹ 3d≥3(m−k)>m−k。矛盾。∎

## 2.3 中段模板族：∀m 统一证书

中段（2≤k≤m−3）由五个模板族覆盖，全部"不解 LP 的符号证书"：权为显式常数，
对任意 m 满足 Aᵀy=0、btᵀy=0、bcᵀy<0（y≥0）。∀m 验证 = 系数簿记（望远镜恒等式
Σ(j_i−j_{i+1})=j_u−j_{v+1}）+ 索引存在性簿记（守恒+firing ⟹ 支撑行合法），
见 midk_note.md §9（a2_forall_m.py，10 regime 全绿）。

**引理 2.7（引理 2 模板，k≥b+2 族）**：若 b≥1、b+2≤m−2、k≥b+2，则
6D+3P₀+3P₁+3C_SS+4G_JJJ+2(j_{b+1}−t)+4(j_{b+2}−t)+3M₀+6Σ_{i=1}^{b−1}M_i+2M_b = −1/2，
各项非负，矛盾（D=danger 余量、P_i=pair、C/G=箱容量余量、M_i=j_{i+1}−j_i≥0 为保序链，
存在性由 k≥b+2 保证）。**覆盖全部洞区**（m=12..30 完整洞图 154 洞逐洞精确证书，
hole_template_certs.jsonl）。

**引理 2.8（Template-b0，b=0 族）**：b=0 ⟹ m≥5 ∧ a≥2；
6D+4P₀+2P₁+4(s₁−s₀)+6(s₂−s₁)+3(s₃−s₂)+3(1−s₂−s₃)+4G_JJJ+2(j₁−t)+4(j₂−t)=−1/2。
（srt 排序链替代保序链，k-无关。）

**引理 2.9（K<1 链 / Template-K1，k≤b 族）**：k≤b ⟹ q₁ 的池位 jj 是 SJ 伙伴位，存在
SJ 箱 (s_g,q₁) 且 g=2a+k−1 恒在 nofit 区（g>jj ⟺ a≥1；g≤m−2 ⟺ m−2−g=b+c−k≥0 ⟸ k≤b）。
nofit s_g+q₁>K 与 SJ 容量 s_g+q₁≤1 ⟹ K<1 ⟹ a_m+q₁<4/5 ⟹ q₁<2/5；SS+pair ⟹ p<1/2+q₁<9/10；
danger ⟹ t>7/20>1/3；JJJ 三件各≥t ⟹ t≤1/3。矛盾。∎（RHS=−17MG，razor-thin 严格。）

**引理 2.10（Template-JT，JJJ含t 家族 (1,m−3,0,1,0,0) 在 k=m−1）**：b=m−3 时唯一 cnt，
JJJ 箱=(j_{m−3},j_{m−2},t)；引理 2.7 的同构链（链到 mon2_{m−3}，恰存在）。

**引理 2.11（Template-NF，残留首部）**：2a≤k 且 k'=k−2a∈[0,min(b−1,2a−1)] 时，
SJ 箱+nofit_k 反传 j_{k'}<1−(5/4)a_m−(1/4)q₁，SS 箱+pair 正传 s_{k'}>p−1+(5/4)a_m+(1/4)q₁，
夹出 p<1−q₁/4 ⟹ q₁<4t−1 ⟹ t>1/3 vs JJJ t≤1/3。（与 K1 独立的交叉验证件。）

**覆盖定理 2.12（全 (cnt,k) 符号闭合）**：口袋 2 角落的每个合法 (cnt,k) 至少被一条
上述引理排除：k=1（引理 2.2）；k≥m−2（引理 2.3）；2a≥k+1（引理 2.4，鸽笼：2a>k ⟹
某 SS senior 落入 nofit 区）；2a≤k ∧ 2a+b≤k（引理 2.6，含全部 b=0 情形）；其余
2≤k≤m−3 ∧ b≥1 ∧ 2a+b≥k+1：k≤b（引理 2.9）；k≥b+1：P2S 修剪（引理 2.5，junior-WLOG
条件）逼出 k≥b+3d+1≥b+2 ⟹ 引理 2.7（b≤m−4）；b=m−3 ⟹ cnt=(1,m−3,0,1,0,0)：
k≤m−3 由引理 2.9、k=m−2 由引理 2.3、k=m−1 由引理 2.10。∎（m=4..40 全 (cnt,k)
逐一举证残留 0：a2_residual_final.py；五族精确证书 m=4..40 共 150,801+4,840+9,666+9,165
例全 PASS；WLOG-free 子集覆盖 k=1、k≥m−2、2a≥k+1、2a+b≤k 四类。）

## 2.4 为何中段必须 k-适配证书（必要性定理）

**定理 2.13（fs/nofit 必要性，agent-2）**：在当前合法约束集上，k 相关约束恰为 fs 组
（j_jj=q₁、s_jj+q₁≤K）与 nofit 组（i>jj）；其余约束组全部 k-不变。对 m=12/14/16 的
全部 66 个中段残留 (cnt,k)（引理 2.7/2.9 覆盖域之外的计算闭合区），消融 fs+nofit 后
LP 全部回 feasible ⟹ **这些 (cnt,k) 的任何不可行证书必须引用 k 相关行** ⟹ 不存在
k-无关统一权向量证书（在现约束集上）。其证书实测为路径形（nofit/SJ/srt 多跳、
支撑随 |k−4a| 增长）。注：此定理不排除未来新增 k-不变合法约束改变格局；
它刻画的是"模板覆盖边界 = k 适配起点"。

## 2.5 计算证书记录（独立复核）

- m=4..30：一步 LP 全 cnt 全 k 精确常数证书（farkas_fixed 管线）+ 保序 LP
  （order_step.py），43,981 份证书独立复核 PASS/FAIL 0（verify_certs.py，纯 Fraction）。
- m=31..45：扩扫 263,575 情形零洞，证书全量独立复核 PASS（agent-4）。
- m=46..50：扩扫零洞（累计 **467,887 情形零洞**）；46..50 证书 204,312 份增量复核
  进行中（断点 .vprog，已验 275,000/467,984 全 PASS）。
- 洞图 m=12..30 全 154 洞由引理 2.7 符号证书逐洞闭合（与计算证书互证）。

## 2.6 WLOG 边界（诚实声明）

模板族（引理 2.7–2.11）与全部 LP 证书依赖**规范代表分组**（装箱按 senior 序固定指派）。
现状（agent-3 交换引理，LP_CONSTRAINTS.md §11.0）：**senior 侧已完全 w.l.o.g. 化**
（SS=最小 2a 极端配对、SJ=剩余最小 b、S=最大 c——任意装箱 ⟹ 同型此等装箱存在）；
残留缺口收窄到 **junior 侧的集合划分**（JJJ/JJ 箱的 junior 指派，指数核心）。
引理 2.7 的 JJJ 三件定位、引理 2.9 的"SJ 箱恰配 q₁"恰属此侧——故这些引理的条件
记为"规范代表框架内"。**不依赖任何分组 WLOG 的部分**：引理 2.1–2.4 与 2.6（保序、
P2K1、P2K-top、P2K-high、Class II 计数）与全部体积/计数/动力论证。引理 2.5（P2S）
本身 WLOG-free（q₁ 不入 JJJ 箱是真实装箱的命题）；但它在覆盖定理中的**修剪用法**
（规范代表的池位 jj 是否落入 JJJ 池段）依赖 junior 侧 WLOG，特此区分。
若 junior 侧 WLOG 得证，本章全线升级为无条件全 m 证明；若证伪，回落到逐 m 计算证书
（m≤50 已封顶）与 proof.md 主证明（不依赖任何 LP）。

**冗余声明（置信加强）**：Template-b0 与 Template-NF 在覆盖定理 2.12 中严格冗余——
b=0 全域已由 P2K-high（2a≥k+1）∪ Class II 计数（2a≤k）覆盖；NF 的残留首部已由
K1 链+P2S 覆盖。二者保留的价值：**不依赖保序引理**的独立交叉验证（b0 只用 srt+pair+
箱容量；NF 用 nofit/SJ/SS 直链），各自 4840+9983 / 9165+27336 例精确通过。

## 2.7 开放问题

1. **junior 侧转移引理**（唯一剩余 WLOG 缺口）：任意装箱 ⟹ 存在同型装箱使 JJJ/JJ 的
   junior 指派满足保序序——卡点已刻画（LP_CONSTRAINTS.md §11：junior 侧集合划分无
   对称可商）；候选路线：直接证明 / LP+装箱 DFS 混合。
2. **K<1 链的 WLOG-free 版**：需"q₁ 的 SJ 箱伴在 nofit 区"的独立论证（现依赖规范代表）；
   q₁∈JJ/J 箱的 case split 开放。
3. **JJJ含t 家族 k∈[4,m−4] 的 WLOG-free 处理**（现为引理 2.9 覆盖）。
4. m>50 的计算封顶已无必要（∀m 符号闭合在本章），但若 WLOG 长期未决，可偶发抽样复核。
EOF