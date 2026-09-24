# 半在线（Semi-Online）调度研究 · 总目录

> 主题：SOSDP（decreasing processing times 半在线调度）及其近亲模型。
> 核心问题轴：**上界 5/4（CKK Algorithm A）↔ 下界 (1+√37)/6 ≈ 1.18046（SSW）之间的 gap**。

## 目录结构与三条线

### SOSDP上界_algA_5over4/（上界线·当前主项目）
CKK 2012 Algorithm A 竞争比 ≤ 5/4 的证明（m ≥ 4 半在线递减到达）。
- **完整证明_5over4.md** —— ★ **本线现行定稿**。第 I 部分＝第一证明（极小反例，引理 T''）+ 第 II 部分＝razor 带 LP 第二证明（∀m 零证书：端点三段 + uncond 层 T2+B4 + 薄层 Qcount 闭式）+ 附录 A–E；
- CKK2012_SOSDP_Algorithms_better_than_LPT.md —— 原论文（md 版，背景资料）；⚠️ 该摘要件**只收录了 §2（5/4）**，未收录 §3；
- **CKK2012_m3最优上界_A3_完整证明.md** —— ★ 补齐上述缺口：原文 §3（m=3 专用算法 A3，竞争比恰为 c=(1+√37)/6，与 SSW 下界相等故 m=3 完全闭合）的逐条严谨还原。含 A3 定义、定理 2、O1–O9 全部观察、Case 1/2 全套子情形，并把原文 "elementary calculations"／"hence" 带过的步骤逐一补出（基例 n≤5、p4+p9≤2/3、L0/L 是 C* 下界等）；
- **code/m3_a3_verify/** —— 该文档的验证脚本：`bound_lp.py`（逐条数值界的精确 LP）、`base_case_lp.py`（基例 n≤5 逐分支 LP，得 R=c）、`base_case_random.py` / `a3_crosscheck.py` / `n9_claim.py`（随机对拍与中间界的适用性检验）；
- LP_CONSTRAINTS.md —— 22 条 LP 角落约束逐条合法性审计（定稿附录 E / B.1 引用）；
- hole_close_lemma.md —— mon2 / 保序引理出处（定稿附录 B.5 引用）；
- 作废引理_sliver紧性.md —— sliver 紧性引理作废记录 + 反例（定稿修订记录引用）；
- pocket3_counting.md —— 引理 P3C（口袋 3 纯计数闭合；有效，尚未并入定稿 §6'）；
- **archive/** —— 过程文献与历史版本：`reports/`（多代理时代工作报告）、`drafts/`（废稿）、`data/`（大证书 gzip，gunzip 即恢复）、`superseded/`（已被定稿取代的证明旧版）、`collab/`（BOARD/PROTOCOL/OWNERS 等协作基建）；
- **artifact/** —— 口袋 2 计算闭合证据包（证书 + 独立复核器 + manifest.sha256）；
- **code/** —— 复用模块与验证器在顶层；`code/archive/`＝一次性探测脚本，`code/data/`＝可再生中间产物。

> 历史版本说明：`proof.md` 已删（与定稿第 I 部分逐字节相同）；`second_proof.md`、`razor_closure.md`、`LP_ROUTE.md`、`main_alpha_tight.md`、`main_beta_proof_v2.md`、`a3_beta_hi.md` 等已移入 `archive/superseded/`——**它们含已作废的 sliver 紧性引理，勿作依据**。

### SOSDP下界_SSW系列/（下界线）
Seiden–Sgall–Woeginger 2000 系列下界与探索：
- SSW_m3下界_c等于1加根号37除6_完整证明.md —— m=3 下界 (1+√37)/6 完整证明（对抗序列+配平分析）；
- m2证明_紧界7除6.md —— m=2 最优 LPT 7/6 完整证明；
- m4下界试点扫描报告.md —— m=4 显式对抗构造（9 任务序列 1,1,1,r,r,r,s,s,s，博弈值恰 (1+√37)/6）+ 25000+ 实例扫描记录；
- m4_search/ —— 上述扫描的计算件（脚本 + r3/f2/scan2/fine334 结果）；archive/ssw_m4_dim01_construction.md —— 同一构造的早期草稿（推理步骤有误，已被正式报告取代）；
- SSW_m3_配平图.png —— m=3 配平图。

### 序数调度_n4/（近亲模型线，独立问题）
Liu–Sidney–van Vliet 1996 开启的 ordinal scheduling 模型（与 SOSDP 不同）：
- lsv1996.pdf / lsv1996.txt —— 原始论文；
- 序数调度_模型识别与n4真实开放区间.md —— 模型识别、猜想证否、n=4 真实开放区间 [23/16, 101/70]（30 年开放情形）；
- 统一构造_人工证明.md、填充提升引理_详细证明.md —— 构造与引理证明；
- n4_compute/ —— 计算件（scan_n3/n4.jsonl、cover_1e11_matrix.npy.gz、compute.py、results.md）。

### 方法库/（跨线沉淀）
- 复盘_可复用证明技巧_2026-09.md —— 可复用技巧（LP 证书/组合计数/动力学/证明工程纪律）；
- 可复用引理库_2026-09.md —— 32 条可复用引理（精确陈述+证明状态+复用场景）。

> ⚠️ **2026-09-24 校订**：两份文档原把 sliver 紧性引理（引理库 L5 / 技巧 B3）列为"最推荐、最可移植"的一条，
> 该引理已于同日被证伪（见 `SOSDP上界_algA_5over4/作废引理_sliver紧性.md`）。现已改标【已作废】并把错因析出成教训；
> 依赖它的 L25/L26 降级为"待复核·未被采用"。**引用这两份文档前请先确认条目标注。**

## 线间关系
上界线证明的 razor 带（5/4 证明最硬段）正是上界与下界 gap 的硬点；下界线的 m=4 探索（把 (1+√37)/6 往上抬）与上界线的 razor 带在数值结构上同域。序数调度线独立（不同模型），仅方法论共享（对抗构造、配平图、计算封底）。
