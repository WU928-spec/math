# 语义工件真值表（PROTOCOL.md §2）

> 规则：变更立即更新；SUSPECT/INVALID 上禁止建造。最近更新 2026-09-21（主代理）。

| 工件 | 状态 | 证据 | 备注 |
|---|---|---|---|
| 旧 firststep 编码（pairing_feasible/farkas_constant/pocket1_lp/pocket3_lp：nofit 在 i<jj、j_jj≤j_i） | **INVALID** | adjudicate_firststep.py；toolbox.py:27 最满优先语义 | 全部派生证书为 artifact，已封存 |
| 修正 firststep 编码（nofit 在 i>jj、j_jj≥j_i，farkas_fixed.py/second_step.py/pocket13_fixed.py/pocket1_bins.py） | VALID | agent-3 审计 LP_CONSTRAINTS.md；消融+sanity | |
| S3-fit 用固定 K=(5/4)(a_m+q₁)（曾误 K₂，second_step.py/pocket1_bins.py 已修） | VALID | agent-1 重验（m=12 洞 10/10 仍闭） | fit 本非承重 |
| build_p3f 的 'y>=1-2t'（及 z≥1−2t 推论） | **INVALID** | agent-3 审计：消融翻案 + m=6 k=1 t=0.3139 见证（ℓ₀+t=1.2557>5/4，其余约束全满足） | 口袋3 统一族/体积链因此无效，口袋3 重开（agent-3 重建中）→ **已由引理 P3C 纯计数闭合，见行21**；另：build_p3f 还有第二缺陷——漏 'am<=z'（E4 见证钻此缺口，z<am），审计主结论不变 |
| 口袋2 build_fixed 其余 22 类约束 | VALID | agent-3 审计 LP_CONSTRAINTS.md（p<K、s≥1−2t、j≤2t 均有语义证明） | SUSPECT 已收窄：senior 侧有交换引理（§11.0），缺口=junior 侧指派单点 |
| 保序引理（s_i<s_k∧j_i>j_k ⟹ s_k+j_i>K） | VALID | 主代理手证 + agent-2 独立收敛（hole_close_lemma.md 引理1）+ 1495万实例 0 反例 | 双独立推导，最高置信 |
| 引理 P2K1（口袋2 k=1 全 m 手证） | VALID（复核通过） | agent-2 敌意复核：mini-LP 全原料 INFEASIBLE(m=4..100)、7 原料逐一消融全必要、恒等式 m=4..30 全成立 | adversarial_review.py |
| 引理 P2K-top（口袋2 k≥m−2 全 m 手证） | VALID（复核通过，原料已补登） | agent-2 敌意复核：成立；低端支原料 **a_m=s₀**（初始 m 件=全局最大 m 件={p}∪{senior}，p_m=min 初始=s₀）已登记 | 行19 原料 |
| 原料 a_m=s₀（口袋2 角落：min 初始任务 = 最小 senior） | VALID | agent-2：senior≥junior（递减到达）⟹ 初始 m 件恰为全局最大 m 件，p_m=min 初始=最小 senior=s₀ | P2K-top 低端支引用 |
| 引理 P2S（q₁ 不入 JJJ 箱） | VALID | LP_ROUTE.md §1.0' | |
| 口袋3 q₁→M₀ 子情形 | **已由 P3C 覆盖** | agent-3 E7b 静态自洽；引理 P3C 不依赖 q₁ 落点 ⟹ 无需单独建模 | 原"重建时必须处理"由行21 解决 |
| 引理 P3C（口袋3"他机全2件"角落计数闭合：z≥q₁∧x,y≥t ⟹ s_i≥2t ⟹ 两 senior 不共箱+senior 箱至多带1件+第m箱≤3件 ⟹ 非senior容量 m+2<m+3） | VALID | agent-3：符号推导 + sympy（pocket3_counting_verify.py 全 PASS）+ 数值复核（m=5..8 无bins可行点 0/76 违反 s_i≥2t、0/76 可装箱）+ LP corroboration（pocket3_bins 去y下界重建：m=4..20 全cnt×全分支 19915 精确常数证书零洞；去装箱/去mach 承重翻转、去danger/firststep 0 翻转；MG=0 区域全空） | 不用 danger/y下界/firststep/vol/窄带；覆盖"他机全2件"全部（含非大2件台与q₁→M₀）；复核通过（agent-2） |
| 口袋2 他机 1 件平局缝（s_i=p 同值单子机） | SUSPECT | agent-3 存疑清单 4；proof.md F/G 兜底 | 登记备查 |
| mon 块删除 / 强制 h=nS−1−jj / 支撑行验证 / 证书缓存 | VALID（等价优化） | fast_lp.py 等价性验证 1/2；OPTIMIZE.md | |
| uniform_certs.py（导入废止 build_frac） | **INVALID** | 建于废止编码 | 勿引用 |
| proof.md 主证明（引理 F/G 符号路径） | VALID（独立于一切 LP） | 五轮敌意复核 + verify_proof.py 全 PASS | 不依赖本表任何 LP 工件 |
| Template-b0（b=0 区全 m≥4 全 k 符号闭合证书族：danger6/pair0 4/pair1 2/srt0 4/srt1 6/srt2 3/SS#1 3/JJJ#0 4/j1 2/j2 4，RHS −1/2−12MG，k-无关、不解 LP） | VALID | agent-2 template_b0.py：m=4..30 全部 4840 个 b=0 (cnt,k) 精确验证通过；b=0 ⟹ a≥2 自动 | leftover 三类已灭 b=0 一类 |
| 口袋2 一步+保序计算闭合 m=4..45 | VALID | agent-4 BOARD 00:35：m=31..45 扩扫 263575 情形 0 洞（fast_scan_31_45.py，证书 pocket2_onestep_order_certs_31_45.txt），与 m=4..30（43981 份）合并 m=4..45 全闭 | 二步 LP 退役确认 |
| 引理 P2K-high（任意 k：SS 箱大 mate 在 nofit 区 ⟹ P2K1 同链 ⟹ t>1/2 矛盾） | VALID | agent-2 手证 + mini-LP m=4..100 全 INFEASIBLE（adversarial_review.py p2k_high） | 推论：任何角落 2a≤k |
| Template-JT（JJJ含t 家族 (1,m−3,0,1,0,0) @ k=m−1 统一符号证书：danger6/pair01 3/SS#0 3/JJJ 4/j_{m−2} 2/mon2 链） | VALID | agent-2 template_jt.py 精确验证 | |
| 中段结构定理（2≤k≤m−3 未被 P2K-high 杀 ⟹ 低端 junior 全>1−2t ⟹ 2a≤k ∧ 3d≤m−k ⟺ 5+5c+2e+7f≤m） | VALID | agent-2 midk_note.md §2（P2K-top 低端支链 + 计数恒等式） | 中段残留压到 2a≤k∧3d≤m−k |
| 引理 P2K-high（任意 k：SS 大 mate 落 nofit 区 ⟹ P2K1 同链杀） | VALID | agent-2 BOARD 00:25：m=4..100 数值过；P2K-top 高端支的推广 | midk_note.md |
| Template-JT（JJJ含t (1,m−3,0,1,0,0)@k=m−1 符号闭合） | VALID（m=5..30 全过） | agent-2 template_jt.py：m=5..30 全精确通过 | leftover 三类已灭 b=0、JJJ含t(该箱型) 两类 |
| 中段结构定理（mid-k ⟹ 2a≤k∧3d≤m−k ⟺ 5+5c+2e+7f≤m） | VALID | agent-2 BOARD 00:25 | 界定中段残余域 |
| 中段残留域（2≤k≤m−3∧k<b+2∧b≥1） | m≤30 计算闭合；m>30 开放 | fast_scan 43981/37997 零洞（m≤30）；证书含 fs/nofit/kcap 混合支撑 | 统一证书的最后缺口 |
| 保序约束组（lowzone/hizone/ord，order_step.py+fast_lp 整合版） | VALID（审计通过） | agent-3 LP_CONSTRAINTS §6：ord=保序引理精确落地（衔接无缝）、zone 划分为合法穷举（整合版中更被 firststep 逻辑蕴含，冗余无害）；消融复核 ord 承重一致 | 口袋2 m≥12 闭合承重件已洗白 |
| 口袋1 装箱 LP（build_p1b）约束 | VALID（逐条合法） | agent-3 LP_CONSTRAINTS §7：y 初始件/x 后至、x≥t、**y≥1−2t 在口袋1 合法**（F2 闭合兜住——与口袋3 同名 INVALID 区分成立）；登记松弛缺口 am<=y、q1<=am（方向安全） | 固定代表分组仍 SUSPECT 未证伪 |
| 口袋1 q₁→M₀ 分支（角落 M₀={y,q₁}） | SUSPECT→补扫中 | agent-3：build_p1b 从未编码该分支；正确语义版（h_y 枚举"比 y 满的他机放不下 q₁"）m=6..12 阶段A洞 12/12 闭合；m=13..26 待 agent-1 补扫 | REQUEST 给 agent-1 域 |
| 口袋1 q₁→M₀ 分支 | **已闭合** | agent-1：正确语义版（hy 前后缀枚举）并入 build_p1b，m=13..26 阶段A洞 2050 份精确证书零洞、抽样 60/60 PASS；与 a3 对拍 7/7（a3 弱版出入一处，不影响闭合）。口袋1 覆盖 q₁→他机+q₁→M₀ 全分支 | 待 m≥27 复核确认（随扩程） |
| P2K1/P2K-top 数值确认扩至 m=31..40 | VALID | agent-2 topk 收官：k=1 反例 0/478、0/511；k≥m−2 反例 0/全 cnt（topk_check_progress.jsonl） | 与计算证书 m≤45 互补 |
| Template-NF（残留域首部统一证书：SJ+nofit 反传+SS+pair 夹 p<1−q₁/4⟹q₁<4t−1⟹t>1/3 矛盾） | VALID（m=4..30 全过） | agent-2 a2_template_nf.py：9165 个前台 (cnt,k) 精确通过，RHS −17MG；残留收紧为 2≤k≤m−3∧2a≤k∧(k≥4a∨2a+b≤k) | 中段统一证书的重大推进 |
| fs/nofit 必要性定理（残留域不存在 k-无关统一证书，证书本质 k-适配） | VALID | agent-2 midk_note.md §7：去 fs+nofit 后 m=12/14/16 全部 66 个残留回 feasible | "必须逐 (m,k) 计算"严格化成立 |
| 装箱固定分组 w.l.o.g. | 字面为假/角落语境可接受 | agent-3 LP_CONSTRAINTS §8：连续配对反例存在（seniors {0.46,0.47,0.53,0.54}），但角落语境定向 3024 例 0 可装箱；严格化两路=①角落⟹不可装箱引理（口袋3 已由 P3C 证出，口袋2 需 firststep/保序动力学）②SS 改极端配对重扫（已证 w.l.o.g.，m=6..10 零翻转） | SUSPECT 降级为"可接受/严格化未完成" |
| w.l.o.g. 化简 C*/G*（任意装箱 ⟹ s₀+s₁≤1 且值序最小三件 junior 和 ≤1，无需固定分组） | VALID | agent-3 LP_CONSTRAINTS §8.2：由装箱计数恒等式（a≥1、d≥1）直推 | 引理2/154模板证书的装箱输入可分组无关化；副发现：154 模板证书原 G 带同款 w.l.o.g. 缺口（BOARD REQUEST） |
| 卡点刻画（路径① hi 区 junior 下界 max(t,p−s_i)，缺口 t/2−1/4∈(0,1/12]） | 分析成立 | agent-3：恰为 m≥12 静态洞 razor-thin 区 | 汇合点：agent-2 残留域闭合后，模板证书 C/G→C*/G* 换元即成分组无关证明 (P) |
| 引理 K<1 / Template-K1（k≤b ⟹ SJ 箱配 q₁ 的 senior 在 nofit 区 ⟹ K<1 ⟹ t>7/20 与 JJJ t≤1/3 矛盾；RHS=−17MG） | VALID（LP 框架内；依赖规范代表 WLOG） | agent-2：a2_template_k1.py m=4..30 全部 9666 个 k≤b (cnt,k) 精确通过 | 2026-09-22；与引理2/b0/JT/P2S/ClassII 合成全 (cnt,k) 覆盖（m=4..40 残留 0） |
| 引理 K<1（Template-K1：k≤b ⟹ nofit+SJ ⟹ K<1 ⟹ q₁<2/5 ⟹ p<9/10 ⟹ t>7/20>1/3 vs JJJ 矛盾） | VALID（m=4..30 全过） | agent-2 a2_template_k1.py：9666 个 k≤b (cnt,k) 精确通过，RHS −17MG | 中段又一块 |
| 口袋2 LP 框架内全 (cnt,k) 符号收口（残留 0，m=4..40） | VALID（框架内） | agent-2 midk_note.md §8：ClassII 纯计数空+P2S 修剪+K1 链杀 k≤b+引理2/b0/JT/P2K-high 全覆盖，a2_residual_final.py 复扫 | 诚实边界：5 模板依赖规范代表 WLOG（行11 SUSPECT）；WLOG-free 手证覆盖 k=1/k≥m−2/P2K-high/ClassII/P2S |
| C*/G* 换元判决（口袋2 分组无关化尝试） | C 侧成功/G 侧本质失败 | agent-3 §8.3：C 侧引理2/K1 本就 w.l.o.g.-free（最小两台=任意装箱所给）；G 侧配平 LP 严格 INFEASIBLE（G* 必含 t，t 列配平多耗 danger，常数侧补不回=t/2−1/4 缺口的代数化身） | 口袋2 终态=LP 计算证书+模板族（WLOG 维持 SUSPECT 标注）；分组无关符号证明的钥匙=转移引理"高端 junior 小⟹其 senior 大⟹C* 受压" |
| P1K1（口袋1 k=1 全 m 手证） | 主体闭合/一窄核待补 | agent-1 a1_pocket1_lemmas.md §1.2-1.3：BB=(s,s) 链 t>1/2✓、分支1(a_m=y) t>13/34>1/3✓、分支2(a_m=s₀) t>2/5>1/3✓（sympy 全过）；窄核 a_m=y∧a=1∧BB={y,s₀} 体积链差 1/12，但 mini-LP 显示 m=12/14/18/24 全 INF 且 Farkas 恒等式 m-无关（11 行统一系数）→ 下段从恒等式反推符号链 | 与口袋2 史同型的 razor-thin 1/12 |
| P1K1（口袋1 k=1 全 m 手证） | **VALID（全 m 成立，待敌意复核签字）** | agent-1 a1_pocket1_lemmas.md 证讫：§1.2(BB ss→t>1/2)+分支1(t>13/34)+3a(q₁ 双侧夹击，与 t 无关)+3b(箱数矛盾 m+1 小件 1 箱，∀m≥3)+分支2(t>2/5)；真杀手是箱数非体积（1/12 体积差为红鲱鱼）；恒等式 m-无关佐证 | agent-3 敌意复核进行中（scope 扩至 3a/3b） |
| P1K1 分支§1.2/§1.3（口袋1 k=1） | VALID（修正后，复核通过） | agent-3 LP_CONSTRAINTS §9：§1.2 逐环✓；分支1 系数笔误两处（正确版更强 t>13/28）；分支2 文档展示链错（原链只给 t>1/4）但 Farkas 重构出真链（7 行支撑，t>1/2，更紧 t>9/20） | REQUEST：agent-1 修文档； sympy 脚本验的是笔误版（佐证无效，需重验修正版） |
| P1K1 窄核 3a/3b | 闭合（agent-1）/复核待排 | agent-1：3a 双侧夹击（与 t 无关）+3b 箱数矛盾；agent-3 本块只复核了原两支 scope | agent-3 下块复核 |
| P1K-top（口袋1 k≥m−2 全 m 手证） | **VALID（全四支闭合，待复核签字）** | agent-1：高端支 t>1/2✓、低端 s₀✓、低端 y 支含 ord 后全域 INF（Farkas 反推可读链 q₁≥x+y−1/2 ∧ q₁+x+tv≤1 ⟹ x<1/4 矛盾）；自查纠错（上段见证点漏 ord）；文档修正+sympy 重核已执行（agent-3 REQUEST） | 两恒等式含固定分组内容（JJJ0/BB），分组无关一般链开放（候选结构引理）；计算管线已逐 cnt 闭合 m≤26 |
| 口袋1 全 m 手证 | **完成（P1K1+P1K-top）** | 上两行之和 | 待 agent-3 全量敌意复核（3a/3b+P1K-top 三支） |
| 口袋2 一步+保序计算闭合 m=4..50 | **永久封顶（零洞）** | agent-4：累计 467887 情形扫描零洞；m=4..45 证书 307556 份全量独立复核 PASS；m=46..50 新证书 204312 份增量复核进行中（.vprog 断点） | m=50 为永久终点（用户批准），此后无扩程 |
| P1K1（口袋1 k=1 全 m） | **VALID（终审通过，五链全部成立）** | agent-3 LP_CONSTRAINTS §10 终审：§1.2/分支1修正版(t>13/28)/3a夹击/3b箱数矛盾(分组无关最干净)/分支2 Farkas 重构链(t>9/20) 全部 ✓ | 签字完成 |
| P1K-top（口袋1 k≥m−2 全 m） | **VALID（附注）** | agent-3 终审：高端支✓、低端 y 支✓(固定分组佐证，标注诚实)；低端 s₀ 支有叙述缺口——JJJ 计数漏数 x（口袋2 移植漏件，mini-LP 兜底 INFEASIBLE 结论仍成立） | TODO：s₀ 支补 x 计数情形；a1_p1k1_sympy.py 未跟上文档修正（agent-1 更新） |
| P1K-top 低端 s₀ 支 x 计数补链 | 已补（mini-LP 复现对拍 5/9/23 INF） | agent-1 §2.2：x>1−2t 归原论证；x≤1−2t 刚性壳（JJJ 被迫 {t,x,j_h}、d=1 强制、结构刚性化）；壳的纯符号杀手未最后落定（登记：望远镜恒等式缺口，与固定分组 SUSPECT 同源） | sympy 脚本全面更新修正版 ALL PASS（分支2 用 m=12 真实 Farkas 组合精确核验） |
| 口袋1 模板移植（首轮） | 进行中（0/5 逐字，三 delta 已定位） | agent-1 a1_pocket1_templates.md：①P1-BB-y 引理（a≥2 必存纯 senior BB 对；a=1∧BB={y,s} 为真变体壳）②P1-K1-index 二分（伴=senior 原链✅；伴=y 壳=历史真洞族 m=12 (2,8,0,1,1,0) k=8 nocert，计算已闭符号壳开放）③JJJ 池多 x 簿记待重算 | 计算锚点：中段 m=4..12 全闭（b0 137/137、K1 161/162） |
| 口袋1 模板移植次轮 | 三 delta 全有产出 | agent-1：Δ1 P1-BB-y 证讫（a≥2 必存纯 senior BB 对，b0 分形簿记级）；Δ2 伴=y 壳可读链提取（BB s≤1/2→j>3/4−t→a_m>3/4−t→q₁<9t−11/4→t>11/32>1/3；壳刚性 c=0,b=k,f=0,d=1,a=1+e,m=2a+k 证出；∀m 索引簿记待完成）；Δ3 JT/NF 池簿记封闭（JT 的 JJJ 恒为 {j_{m−3},x,tv}） | 剩余=伴=y 壳 ∀m 簿记+JT 恒等式提取（机械） |
| 口袋2 中段模板族 ∀m 符号验证 | **VALID（∀m≥4）** | agent-2 midk_note.md §9：望远镜恒等式 10/10 regime 符号全绿（自抓权 bug 一枚）；索引存在性簿记逐族一行证明（K1 关键恒等式 m−2−g=b+c−k≥0 sympy 确认）；m=4,5 边界单独核 | 口袋2 中段升级为 ∀m（WLOG 边界内维持行11 标注）；与 m=4..40 的 150801 例有限记录互补 |
| 口袋1 中段模板移植 | **收官（覆盖完备）** | agent-1 a1_pocket1_templates.md 收官节：b0 分形✅(P1-BB-y)、K1 双伴(senior 伴逐字✅+y 伴 uniform 2a≥k 全链闭✅)、NF 可移植、JT=空集（守恒封闭，口袋1 唯一 t-入-JJJ 族落入 P1K-top）、Lemma2 同 b0 路径；登记 3 件开放（2a<k 变体簿记）均计算闭合 m≤26 | 口袋1 中段 ∀m（WLOG 维持标注）；待 agent-3 终审 |
| 枚举路线（中段严格化） | **不可承受（关闭）** | agent-3 LP_CONSTRAINTS §11：G(M;cnt)=M!/[(3!)^d(2!)^e d!e!f!]，m=12 口袋2 Σ=1.6×10⁸/口袋1 2×10⁹，剪枝（对称性/machine标签/容量型/保序）只降常数——件值绑机无对称性是指数核心 | 严格化剩余路线=(P)转移引理 或 接受现状 |
| senior 侧交换引理（§11.0） | VALID | agent-3：任意装箱⟹同型装箱 SS=最小2a极端配对、SJ=次小b、S=最大c（逐分量交换） | **WLOG 缺口收窄为 junior 侧指派单点**（SEMANTICS 行11 更新） |
| junior 侧交换引理 | **证否（钉死）** | agent-3 LP_CONSTRAINTS §12：pair 绑机 ⟹ 池内不可交换（抽象反例）；但关键收窄：规范指派死⟹JJJ 先死，3114+ 点 0 可装箱 ⟹ 角落 LP 区域无可装箱点；缺口收敛于 (P)"角落⟹不可装箱" | WLOG 修复唯一出路=(P) 正面攻坚或 LP+装箱混合 |
| (P) 攻坚段报（agent-3 §13） | LP 级事实成立，符号待证 | 0/4518 采样点（保序+无装箱帽区域）全部装箱不可行；"去装箱→feasible"区域全不可装箱=装箱帽杀的点本不可装箱 | (P) 的事实面已坐实，缺符号证明 |
| (P) 新原料地图（§13） | 勘探完成 | ①q₃ 三阶动态：落机枚举不进 JJJ 身份；②M₀/fallback 时序：常数证书框架编码不了到达时刻——**若可 LP 化则直达（最值得投入）**；③JJJ 先死机制化：证否；④高端 junior 体积账：停在 razor 墙 | 路线判决：混合线最直接，对偶化装箱证书次之 |
| 混合路线判决（agent-2 a2_hybrid_route.md） | 需新理论（顶点枚举+DFS 双重爆炸，覆盖论证无免费午餐） | ①顶点数 m=12 上界 10^15；②DFS 2^(2m)；③覆盖论证证否：可行域非凸，顶点全不可装⟹内部不可装失败（立方体+中心球反例），正确对象 Pareto 前沿仍指数 | 但有关键坍缩：模板装箱依赖=SS#0(senior 引理已闭)+JJJ 三件身份；幸存区低区 junior>1−2t ⟹ JJJ 三件必在高端 ⟹ 衔接问题多项式级 | **(P) 真实最小核=高端 junior 转移引理（第三次独立收敛）** |
| fallback 时序 LP 化（§13.2 方向②） | **框架级堵死** | agent-3 §14：序位枚举 (m−1)! 出局；指示变量破坏常数证书框架；静态投影（fallback 负载/保序/firststep/二步）已全部在 LP 中 | 降级出地图 |
| (P) 矛盾定位：配对兼容层 | 分析成立 | agent-3 判定实验：JJJ 单侧不死/SS 单侧只杀 k=1/SS∧JJJ 联合一致 ⟹ 存在性必要条件（体积/计数/SS∃/JJJ∃）全真，矛盾只在"哪个 junior 配哪个 senior"的尺寸兼容 | 与会话19"缺口在配对错配"再现确认；剩余路径=配对兼容组合引理（新原料类型） |
| 转移引理证伪器（a2_transfer_falsifier.py） | VALID（上线） | agent-2：三态判决（BLOCKED/ALIVE-UNPACK/COUNTEREXAMPLE）+DFS，基线 12/12 对齐 0/4518，自纠 t 钉住 bug；接口=candidate_rows 声明式注入 | agent-3 候选秒级判决通道就绪 |
| 引理骨架 H1（JJJ 高端归约） | 形式化成立 | agent-2 a2_hybrid_route §5'：幸存区模板 JJJ 链尾位（≤k−2）与真实装箱 JJJ 位（>jj=k−1）互斥——"JJJ 先死"机制可复用陈述；覆盖检查 C(m−k,3)·d 多项式级 | 残余缺口=高端 junior 体积账（转移引理本体） |
| 配对兼容两子线（§15） | 均不咬 | agent-3：①兼容计数账 c=f=0 时 3d=3 恰取等（razor 临界），聚合配平 LP 修正符号后 m=8..20 全 INF——高端 junior 可全=t；②Hall 缺口不在 SJ 侧，多件箱归回计数 | 第 5 例符号纪律事件入档（假成功被修正后抓出） |
| (P) 第五次收窄（地图完备） | 定位完成 | (P) 唯一缺口=高端 junior 无非平凡下界（j_i∈[t,K−s_i)）——firststep/保序之外的**填充序负载下界**缺失；常数证书框架编码不了 | 正面符号路线在本框架内穷尽 |
| 分支证书设计（§16） | 关键简化成立 | agent-3：填充序由 seniors+K 唯一决定（best-fit argmax 确定性）⟹ 分支树无需序枚举（§14 改判：堵死的是序位枚举不是序）；内节点=尺寸兼容析取、叶=常数证书、树正确性已定义 | 第六次收窄终极形态：razor 区配对兼容原子层仍差一条引理（叶数否则指数） |
| 引理 MR（高端 junior 反向单调） | 不咬（归档） | agent-3：洞高端区为空故无效 | 非所需原料 |
| razor 区配对引理（§17） | 候选全不咬，正面路线穷尽 | agent-3：MR/坍缩行/联合/类和下界四候选均 ALIVE（razor 区多面体在全部序结构下非空）；七次收窄完整画像：坍缩+JJJ 全高端+高端 junior 无下界+计数恰取等+多面体非空但 0/4518 不可装箱 | (P) 需纯组合配对兼容引理，已被证不在现有约束线性张成（配平 LP §8.3）；球在混合路线 (H) |
| 口袋1 (P)-转移图纸（a1_p1_transfer_plan.md） | 就绪 | agent-1：(P1-P) 陈述+(H) 骨架三档转移表+新引理 5 件（N1-N5，多已备半成品）+风险登记（独占箱类引理 mach 版或不可移植） | 口袋2 (P) 落地后按图跟进 |
| razor 取等穷举（§18） | 壳不有限，路线关闭 | agent-3：取等壳 cnt(e)=(1+e,m−3−2e,0,1,e,0) 单参族但分组数仍阶乘（m=12:4e7）；独占箱矛盾机理证否（s_max≤1−δ 仍 FEAS）；正面：低端区完全刚性可证（pair 全紧⟹值全等⟹对称商掉），残余=高端 junior 连续值+指派 | 穷举路线关闭；(P) 居所=高端区不变 |
| 证伪器 v2（a2_transfer_falsifier_v2.py） | VALID（1400×提速，回归一致） | agent-2：剖析 DFS 占 99%+，窗口结构重写（每箱≤3件⟹组合子集 2.3k vs 16M 掩码）84ms/点；razor DFS 级证据 m≤16（420 点 0 可装箱） | (P) 经验证据加厚 |
| (W'') 证明骨架（LP_CONSTRAINTS §19） | 落成，缺口显式化 | agent-3：S1(SS极端配对)/S2(S 最大c)/J1(低端规范化) 完全成立；新发现 G1=senior 侧 SJ 分割张力（razor 区躲开，非 razor 需分割引理或 C(nS,b) 枚举并入 G2）；G2=hi 区契约（agent-2 执行） | **新发现：SJ 配对应反序**（同向=最坏配对，重排不等式要求反序才 w.l.o.g.；口袋3 LP 已反序，口袋1/2 同向需修） |
| (W'')-hi 执行块（a2_wprime_hi.py/md） | 检验饱和：前件为空 | agent-2：机制齐备（pack_recover→cnt_of→canonical_bins 逐箱核验）+牙齿✓（合成分歧实例正确识别）；角落值域 234+ 点+公平合成 800 试 0 可装箱——(W'') 检验被 (P) 吸干（空虚成立），是 (P) 的最强间接证据形态；公平版合成器修复了双升序偏差假象 | 检验器归档（未来任何可装箱候选点秒级判规范等价）；剩余=G1/G2 的 ∀m 符号簿记 |
| (W'') 簿记收官（a2_wprime_final.md） | razor 区条件闭环；全闭环卡两点 | agent-2：新证 G2a（∀m：hi 区 JJJ 集合 w.l.o.g.=值序最小 3d 件，支配论证）；G1-open（非 razor 三分槽匹配多项式化未证，§19.1 的 C(nS,b) 在 a~m 时实为指数——指正）；**G2b-open：hi 区 junior 机器序↔值序换位 ≡ (P)/转移引理本体** | 第四次独立收敛：(P)=不可约核；(W'') 全闭环 ⟺ (P) |
| 换位分支树（E，a1_swap_tree.md/py） | 成立（d 固定时多项式） | agent-1：内节点=hi 区 junior 机器指派析取（换位=分支变量；lo 区不分支 ord 保序；§16 序确定性免序枚举）；有效叶数 ≤ C(h,3d)·(3d)!（G2a 集合规范化使仅 JJJ 3d 件身份影响规范形），d=1/h≤8 时 ≤336；m=18 ghost 壳原型 k=15/16/17 叶 2/1/1 全过 | 不解决 G1-open；叶 ∀m 证书簿记待做；d 随 m 增长时超多项式（razor 区 d 小） |
| D 值和界验证（a3_D_vals.md） | 负结果：f(r)=r·p/2 无 LP 内增强 | agent-3：736 顶点实测，值序最小 r junior 的 senior 伙伴均值最小值平坦≈0.458=r·p/2（静态下界贴边）；机理=razor 点 seniors 近全等+LP 区域内值序解耦 | 更强 f(r) 需 LP 外填充序内容（§14/§16 接口）；入档为 B 原料 |
| 引理 V1（Hall 反序条件：∃指派全 s_i+j≥p ⟺ ∀i: s_(i)+w_(nS+1−i)≥p；赋值无关 pair 必要条件） | VALID | agent-2：嵌套邻域 Hall 一行证明 + 20 万例小 n 暴力对拍全一致（a2_value_reform.md §1） | 2026-09-22；注意主代理上一版"最小+最小"猜想已被反例否掉，本版为修正且自证 |
| 值语言重构（B，a2_value_reform.md） | 卡死，卡点=JJJ 3-分组位置 | agent-2：**引理 V1 成立（Hall 反序条件：∃配对全≥p ⟺ ∀i s_(i)+w_(nS+1−i)≥p，首个赋值无关 pair 必要条件，20 万暴力对拍）**；值语言 LP 消融：JJJ 位置锁定才全杀（过约束），声音方向漏 14/20——机器索引桥仅存为 JJJ 3-partition 结构 | 第五次独立收敛：(P) 核=配对兼容 3-分组 |
| E 方向1/2（a1_leaf_cert.py） | 方向1否证(与CDL互证)/方向2上界维持 | agent-1：naive 零件规范形非叶内最均衡（0/N，独立复现主代理 31% 发现）；m=18 t≥0.322 剪枝率 0%（剪枝在 t 维非换位维），叶数≈C(h,3d)·(3d)! 上界维持 | E 转 CDL 消费方：叶证书=该 cnt 全局最均衡形；方向3/4 未达登记 |
| JEL-LIN（分片线性引理，a3_jel_piecewise.md） | **VALID（证毕，七环证明）** | agent-3：贪心下降=值空间分片线性过程——有限有理超平面族 arrangement 的开胞腔内路径与输出组合结构恒定；边界=两候选 key 相等=线性方程 | 构造式 (W'') 证明的第②块定理落地 |
| 角落胞腔数实测（a3_jel_corner.py v3） | 角落 16/20/19 vs 随机 25/25/25 | agent-3：真口袋2 角落 rest 的胞腔数 m=6/7/8=16/20/19（25例），显著小于随机的全不同——窄带值同构⟹胞腔合并 | 模板×区域的证书扩展量级可控（~20 胞腔/情形）的实证 |
| JEL①cnt-保持下降（a1_jel_seg1.md） | 终止性✓(7/7)；唯一性✗(4/7异谷) | agent-1：cnt-保持邻域（含跨型移动）下字典序势终止确认，但 43% 双起点异谷——局部极小不唯一（SS 机会成本的动态表现，与 CDL 同向） | **架构可吸收**：异谷⟹胞腔细化（JEL-LIN 已证路径胞腔恒定，不同谷=不同胞腔），(W'') 不依赖唯一性只依赖胞腔内输出固定；代价=区域数变多。附发现：随机角落几乎永不可装箱(30+试0成)——(P) 定律再现 |
| ③试点（a1_jel_region_port.md） | **否证（权重不可搬运）** | agent-1：K1 权重换极小形索引后 12 列破，两模式=值序↔机器序错位（G2b 权重层再现）+伴箱 senior 错位 | 修复路径收敛=R-锚定下降（tie-break 向 R）+并列层连通性 |
| JEL 复核（LP_CONSTRAINTS §20） | 终止性✓；两漏洞 | agent-3：②胞腔细化不吸收起点异谷（JEL-LIN 前提=同组合起点）→改存在性表述；③razor 点在判据超平面边界上（pair 全紧）→需闭胞腔/tie-break 约定 | REQUEST(main) 已执行入 JEL.md |
| fallback 区域证书管线（a4_region_cert.py） | 就绪（冒烟过） | agent-4：输入 (m,cnt,k)+胞腔极小形箱内容→区域证书；行名唯一编号规避 P02 重名坑；规范/非规范变体均出证（该案例闭合对箱形扰动稳健——保序承重、装箱行非瓶颈） | 备胎就位：portability 失败即可逐区域重解 |
| SJ-REV 引理（阈值匹配反序规范化，B路线首块） | 证毕 | 链图Hall：∃双射可行 ⟺ 反序配对可行（N(s_i)嵌套，Hall条件=|N(s_i)|≥b−i+1，恰为反序第i条）；纯值级、m无关、身份无关；3万例整数probe零偏差 | B骨架四块拼齐三块已证(S1/S2/G2a)+一块新证(SJ-REV)；§8对偶障碍不阻断primal路线 |
| MRF 贪婪支配引理（B 线核心） | 骨架证毕+probe 4万零偏差（待复核） | 链图上最受限优先取最大相容 ⟺ ∃匹配；伴侣多重集逐分量支配一切可行匹配；交换论证（已处理段不变/改进不变式）。补集反支配：下游更小更安全 | SJ 伴侣问题从"身份不定"降为值定义贪婪集；H2=唯一残留 |
| H2 中段吸收引理 | 证毕（待复核）+1598 例 probe 零失败 | 阈值 Hall 缺陷经双侧支配从我们侧传到真实侧：#{M_real≥L}≥#{M_ours≥L} 且 #{M_real≤1−L}≤#{M_ours≤1−L}（G 支配 C + 三元组不贡献大件：T,Y'⊆{≤1−2t}<{≤1−L}）；f≥1 同一论证 | (W'') junior 侧 primal 全闭 |
| nofit 半判决（agent-2） | 规范形下恒失败（0/20 鬼影） | q₁ 规范伴侣=最小 SJ senior（反序必然），s_g+q₁=1≤K margin −0.1461；K1 链"伴侣在 nofit 区"与值定义规范形不兼容——B 侧 SJ 条款不写 nofit；LP 消费侧为证书重导问题 | 非 primal (W'') 缺口；勿再把 nofit 下界写进规范形 |
| G1 核情形区间定理 | **VALID**（证毕+agent-3 §22 敌意复核通过+独立脚本 137 例对拍一致+主代理 358 例零破洞） | 顶部交换恒可行（x_k+x_l≤x_max+x_k≤1）⟹ 一切完美匹配连通到反序轮毂 R，Δb∈{−2,0,2}，离散连续 ⟹ 可达交叉边数=带奇偶区间；core case (W'') 坍缩为 b∈[b_min,b_max] | senior 侧计数级闭合；LP 消费=固定排序指标线性行 |
| J 独箱剥离引理 | 证毕（一行交换，无帽吸收） | 最大 f  juniors 进独箱 w.l.o.g.（与 S2 同形）；装配归约到纯匹配层+三元组剥离序 | (W'') 装配的第一块 |
| E-nec 必要条件行裁决 | 判决：弱化版不足替代固定分组行 | 洞族 0/20（计数行杀不动 razor 洞）；保持率 62.6%，465 处损失全集中 razor 带 cnt=(1..2, m−3/m−5, 0,1,e,0)；XSS 极端配对有真牙（m=6 独立承重）；XVOL/XBIG 纯陪跑；保序行仍是 razor 带唯一已验杀手 | (W'') 绕过路线暂死：razor 带需要固定身份行的强度 ⟹ 角落刚性证明（razor 带钉死）成为正确主攻 |
| E-nec-v2 联合裁决 | 判决：(W'') 不可绕过，义务=razor 带 413 点 | 鬼影洞在 mon2+必要条件行下 20/20 存活（固定身份行对洞族承重，与 mon2 联合缺一不可）；保持率 62.6% 含保序（v1 表述已更正）；razor 残留精确清单：(1,m−3,0,1,0,0)@k≥2 全残留、(2,m−5,0,1,1,0)@k≥4 | razor 带刚性证明是 LP 路线唯一剩余义务 |
| E-nec-v3（挤压+值带行） | 决定性负面：razor 残留 1/465、洞族 20/20 存活 | 幸存者点精确饱和新行（Σℓ=m−1−t、s_max=1−t 等号）——聚合约束压不出 razor 带；三轮一致结论：**razor 带承重内容=箱内身份，聚合式行不可替代**；XPS 伴侣供给行不可单条线性表达（登记） | (W'')/刚性证明义务不可经 LP 合法行绕过——主攻唯一 |
| 路线(b)首轮：B规范形 LP 变体 | k=m−1 全序区 0 不一致（m=6..18 全 cnt）、洞族 9/9 保持 | SS极端+SJ反序最小b+JJJ最小3d聚合+JJ反序，全部已证合法行；无 mon2 时行失效（不合法）故排除 | 洞族合法性可完全合法化；k<m−1 razor 带待 hi 区 junior 序引理 |
| 路线(a) razor 带 junior 离散度判决 | 实验支持+符号链卡墙 | max₂(j)+t>1 的点存在但全部不可装箱（packs_exact）⟹ 现行 JJJ 行在可装箱域恒成立（实验级）；符号证明卡 §15.1 razor 临界计数墙 | 现行 LP razor 带合法性=实验支持/符号未闭 |
| W''-razor v1 规范形 | **已否证（probe 9/13 失败）** | 强制通道引理错一条：大 junior+小 junior<1 恒成立 ⟹ 大 junior 有 SJ/JJ 双通道；SS=最小剩余也错（中等 senior 0.593 的真实去处=SJ） | razor 带 (W'') 开放；勘误已入 JEL.md，probe 护栏有效 |
| 形 B junior 预算矛盾引理 | **INVALID（作者自查撤回）** | 步骤 3 边界错误（1−2t>τ 恒真于窗口）确认；三阈值重算：SS 机 junior 下界落 (τ,α] 可流动去当伴侣 ⟹ 独占计数断链；修正预算=紧平衡（m−1 恰取等）非矛盾 | 形 B (P) 回归结构论证；条件性推论：若未来引理迫使 SS senior<1/4+t 则计数矛盾复活 |
| razor 带动力学可达⟹不可装箱（方向 1 核心主张） | 强实验支持（0/456 可达构型可装箱，m=6..14） | razor 带角落构型（角落+mon2）实跑 Algorithm A 可达 456/648，可达且可装箱 0；机制=轨迹钉死的多重集上两侧大件争抢小件吸收容量超额 | (P) 动力学闭合的候选主张，待 ∀m 符号证明 |

[2026-09-23 勘误] agent-3 razor 带 (P) 收官声明（a3_razor_combinatorial.md）降级为 **PARTIAL**：k=1 与 k=m−1 段 VALID（行全合法，agent-1 A线 1907/1907 互证）；k=2..m−2 段 **UNSOUND**——JJJ01 行引用低端区 j₀,j₁，非全池最小两件 junior（hi 区无序，main 敌意复核四层证据见 BOARD 2026-09-23 裁决条）。修复：main 的 junior 对枚举扫描（main_jjj_enum.py）。
[2026-09-23 登记] U(a) 统一符号恒等式（agent-4，a4_razor_symbolic.md）：**VALID（洞族域=k=m−1，无条件）/ 域外 INVALID**（XTRI 行 j₀,j₁ 在 k<m−1 非全池最小 junior，main 敌意复核）。验证：shape A m=4..50、10 洞族 11487 例零失败、Fraction 精确。
[2026-09-23 登记] 值语言 LP+A5+LZ/HZ（main，main_cegar3.py）：open 段 k=2..m−3 154/154 精确 t-uniform 证书——**uncond=115 VALID 无条件**；sjrev=39 **CONDITIONAL（G1-razor）**。A5 低端区配对支配引理 main 证（mon2+pair 支配）；LZ/HZ 情形定义行合法。
| A5 低端区配对支配行（j_{nS−k+i}≥p−sᵢ+MG，main_cegar3.build_k，值语言坐标） | **VALID** | agent-3 敌意复核（a3_a5_corner.py）：4 步证明（ord⟹chosen 升序=低端机 junior；pair⟹chosen_i≥p−sᵢ+MG；top-k 分量支配=纯排序）仅用 pair+ord 不依赖 hi 区序；154 配置×48 方向采样最大违例=−MG 取等；m=6..8 全子集精确蕴涵检验最大违例=−MG ⟹ 角落域被 pair+ord 精确蕴涵（机 LP 中冗余，切割力只在值语言松弛） | **仅限值坐标语义**（j_r=全体 junior 值序第 r 名）；误写为机索引 j_{nS−k+i} 则非法（hi 区无序，与 JJJ01@k<m−1 同型坑） |
| LZ/HZ 情形定义行（s_k≤K−q₁<s_{k+1}，main_cegar3.build_k） | **VALID** | agent-3：与 §6 已审 lowzone/hizone 同义——LZ: 机 k=jj=最大低端机（s_k≤K−q₁）；HZ: 机 k+1=最小 hi 机（s_{k+1}>K−q₁，仅 k<nS）；k 由值唯一确定（合法穷举划分） | |
| A2 反序负载帽（j_r+s_{nS+1−r}≤K，a1_value_lp2） | **SUSPECT（冗余无害）** | agent-3（a3_a2_corner.py）：机 LP 角落域精确 LP 最大违例 **+0.4499**（无 B3，s_max=1.0+j_min=0.367>K=0.917）、**+0.1419**（带 B3，s_max=0.73=1−t 取等）⟹ 非角落行推论；agent-1 辩护词"真实机器负载≤K"=未证动力学主张（fallback 部分分析：低端机未收满时不可能，之后未封死）⟹ 合法性未立 | **承重核查：0/308 支撑 + 去 A2 精确证书 115/115 OK（a3_iso）⟹ 154 不依赖 A2**；建议从证明行集移除 |
| B4 threshold-Hall（s_{nS+1−q}+j_{q+2}≤1, q=2a+1..nS−2，a1_value_lp2） | **SUSPECT（uncond 115 的命门，109/115 承重）** | agent-3：①承重性：去 B4 后 t-uniform 精确证书仅 6/115（109 FLOAT_NO_CERT）——浮点网格 INF≠证书存在，main"B4 冗余"系 full 档+网格级误判；②合法性：agent-1 一行论证漏 2 逃逸口——junior 计数为望远镜恒等，Hall 亏缺仅在 ss_L=0∧jjj_C=3 成立；逃逸(a) JJJ 用池外 junior（j_{q+2}≤1−2t，s_{nS+1−q}>2t）、逃逸(b) L_q 进 SS（s_1+s_{nS+1−q}≤1） | 构造性攻击（a3_b4_attack.py）进行中：逃逸点 LP 可搜到（m=9 cnt1 k=3 q=3 逃逸a，11 t 点）但已测全 0 可装箱；**若任一逃逸点可装箱 ⟹ B4 INVALID ⟹ uncond 115 塌 109** |
| uncond 115 行集逐条审（noSJrev 档支撑全集：jrt/srt 值坐标定义、danger、j1≥t、j≤2t、s1≥1−2t、smax≤1、jmax≤q1、q1≤am、am≤s1、L≤1、t≤q1、t 窗口、A1 反序 maximin、A3 挤压、B1_SS01、B2_JJJ01 值形式、B3、A5、LZ/HZ） | VALID（除 B4 外全清） | agent-3 逐条：A1=瓶颈分配交换论证（a≤b,c≤d⟹a+c≤min(a+d,b+c)，反序最小和≥真配对最小和≥p）；A3=挤压引理；B1=计数恒等式 a=d+e+f≥1⟹最小两 senior 和≤1；B2=d=1+c+f≥1⟹池最小三件=t+j₁+j₂≤1（值坐标=全池最小，与机索引非法形式区分）；B3=c=0⟹s_max≤1−t（s_max>1−t 时 junior 伴≥t 超 1、senior 伴须∈[1−2t,t)=空） | B4 待定（见上行）；SJrev/S1v/JJrev 属条件档（G1，agent-1 域）不在本集 |
| B4 构造性攻击终报（a3_b4_review.md） | **SUSPECT-unrefuted（趋向 VALID）** | agent-3：修正域（uncond 行集−B4−A2）m=6..20 全域 6102 组合：9141 见证（逃逸 LP 可实现）全部装箱必死（DFS+cnt 形式二过 800/800 closed，e=1 规范化配对精确判定对拍暴力一致） | uncond 115 标注=6 发无条件干净+109 发条件于 B4-Hall 引理；逃逸口闭合与 G1-razor 主线同族 |
| open 段统一符号证书 T2/T1a/T1b（a3_template115.md，值语言） | **VALID（条件于 B4-Hall 引理）** | agent-3 任务③：T2 单模板覆盖 uncond 全域（cnt1 k≤m−4、cnt2 k≤m−6），m=6..60 机器验证 2971/2971 + main 管线实际行独立对拍；B4_{q=nS−k} 承重 ⟹ 条件同 109/115 证书；模板域边界 q<2a+1 精确解释 sjrev 条件层 | uncond 域免解 LP；G1-razor 目标层=cnt1{m−3}/cnt2{m−5..m−3} 显式化 |
| 新行 s_{nS}+p≤1+2t（main (2b) 楔候选） | **VALID（仅 (2b)/sliver 情形假设）/ INVALID（一般角落行）** | agent-3 复核：推导第二环"s₁≤1−s_{nS}"依赖"s_{nS} 被迫进 SS 且伴侣存在"的隐藏前件（仅 s_{nS}≥J 且 junior 封 SJ 的楔内成立）；值 LP 角落域 max(s_{nS}+p−2t)=1.132、机 LP=1.44 ⟹ 全局使用错杀合法角落点 | 可作情形定义行（LZ/HZ 同地位），禁作 CEGAR 全局行 |
[2026-09-23] B4_q（s_{nS+1−q}+j_{q+2}≤1）：**VALID**（razor 角落+可装箱 ⟹ 成立）——证明链=取等格 LP 不可行（e=0: 111/111、e=1: 45/45 精确 t-uniform 证书）+ r<q(r<q−2) ⟹ Hall 亏缺（main_b4_supply.md Case 2）。逃逸 (a)/(b) 全封死（9402 逃逸见证 0 可装箱佐证）。uncond 115 与 T2 模板的 B4 条件解除。
| β 引理（main_beta_proof_v2.md + agent-3 §5 补全） | **VALID（agent-3 §5 补全后闭合，待团队复核确认）** | 证明链：sliver 紧性引理（三证：main/agent-3/agent-1 独立）+ C1（q₁≤s₀ 恒真形）+ C2（SS={s₀,s₁} 紧，正法版 #11 修正）+ C3（p+MG≤2s₀）+ H′（Q≤k−1，nofit 版：R∩hi 互补件封死）+ k≥3 mon2 升链计数杀 + **§5（agent-3 a3_beta_hi.md）：k=1 代数杀（p<4/5 vs danger）、k=2 三情形全杀（A: fs 钉走唯一高档；B: nofit ⟹ q₁<4/5−s₀ ⟹ p<4/5；B′: 机 0 窗口空；C: q₁=s₀ 条件钉 ⟹ s₀=1−2t ⟹ 机1low/机2hi 相斥，s₀=2/5 边界落 k≥3）、hi 区恒空** | razor 带 (P) 第二证明收官件之一（与 B4 单行闭合互补）；数据背书 15438 例 (k,I) 全格 I<k + cnt2 定向 10348 例 |
[2026-09-23] α' 紧性证明（main_alpha_tight.md）：**VALID**（agent-1 终审，五步链全严密+e=0∧#{s≥J}≥3 槽位补行后枚举完备）——razor 带 (P) 第二证明 39 点全部符号覆盖（α' 本稿 + β：main_beta_proof_v2.md + a3_beta_hi.md（VALID，C1 换 τ-杀法））。
[2026-09-23] razor 带 (P) 第二证明：**全域闭合**——k=1/m−2/m−1（无条件）+ uncond 115（T2 ∀m 复核 VALID + B4 单行合法性 111+45 精确证书）+ 39 点（α' 紧性 VALID + β VALID）。微引理项 t≈5/16 已取消（紧性杀）。proof.md 第一证明独立全程不受影响。
[2026-09-23] razor 带 (P) 的 LP 第二证明：**全域闭合，组装级终审 VALID**（agent-1 a1_final_review.md：覆盖完整性（两 cnt × 全 k 计数恰好）、引用合法性（旧坑 JJJ01 机器索引版确认绕开）、链衔接、独立性（零引用 proof.md/T''）四点全 VALID）。第一证明（proof.md，五轮复核）与第二证明（razor_closure.md）互为独立双证明。
| k=m−2 端点墙 ∀m 符号证书（a3_endpoint_symbolic.md，值语言恒等式） | **VALID（机验 111/111）** | agent-3：恒等式 (4nS−2)danger+2(nS−1)(j₁≥t)+2A1_1+2squeeze+(nS−1)(srt₁+B1)+2(nS−1)B2+2nS·A5_1+2ΣA5_i ⟹ A^T w=0 ∧ bt^T w=0 ∧ bc^T w=−1/2−4(nS−1)MG；m=5..60×2cnt 111/111 Fraction 机验通过 + LP 锥射线吻合（m=12 提取证书=恒等式/2）；行全合法（(A) 类角落必要 + B1/B2 计数恒等式直推，B2 为值坐标合法形）；语义=角落(k=m−2) ⟹ 无 SS∨无 JJJ ⟹ 不可装箱 | 替代 main_jjj_enum 对枚举版（保留为计算背书）；k=m−2 亦呈双墙同撞（B1/B2 双承重） |
| k=1 端点墙 §2.1（main 符号版） | **VALID（agent-3 敌意复核通过）** | 逐环核：fs 前提/nofit 下界/MG 簿记/末步计数恒等式矛盾全成立；缝隙 13/28−1/3 远大于 MG 噪声 | 无需修补 |
