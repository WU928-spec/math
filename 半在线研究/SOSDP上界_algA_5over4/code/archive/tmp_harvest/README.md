# tmp_harvest/ —— 自 /tmp 找回的项目脚本（2026-09-24 整理）

这些脚本原先只存在于 `/tmp`（易失：macOS 重启或清理即删）。2026-09-24 整理时自 `/tmp` 找回入库，
以保住它们所承载的核验记录——`archive/reports/` 里的复核报告已于同日按维护者决定删除，这些脚本
是同一批核验工作的**原始实跑件**。

**运行约定**：从项目根目录（`半在线研究/SOSDP上界_algA_5over4/`）运行，例如
`python code/archive/tmp_harvest/a1_iso3.py`。脚本内用相对路径 `code` 建立 `sys.path`。
（`a3_iso.py` 已改为同一约定；它原来是两行已失效的绝对旧路径。）

| 文件 | 核验目标 | 相关文档 |
|---|---|---|
| `a1_e4_check.py` | E4 审计见证复核（调 `main_cegar3.build_k`） | `完整证明_5over4.md` §3.2；`archive/collab/BOARD.md` |
| `a1_e4_true.py` | E4 见证的修正版复核（调 `main_b4eq_probe.py`） | 同上 |
| `a1_iso_check.py` | 取等格隔离检验（111+45 配置域） | §3.2 的「111/111 不可行」 |
| `a1_iso2.py` | 变体：SJrev 行单独承重（去 B4 后 SJrev 是否杀 164 配置） | §3.2 的反向对照「无 SJrev 时 82/111 可行」 |
| `a1_iso3.py` | 实质隔离**全 t 网格**（同一实验的最一般版） | §3.2 |
| `a1_final_check.py` | 终验：B4 破单独与角落矛盾（无需 r≥q） | §3.2；附录 D.2 |
| `a1_kmm2_check.py` | k=m−2 恒等式独立抽验（m=6,9，Fraction 精确） | 附录 D.1 的 `a3_endpoint_verify.py` |
| `a2_v4.py` | 值语言 LP 试点（α'/β 时代路线；**该路线的结论已随 sliver 紧性引理作废**，仅作过程记录） | `archive/superseded/` 的 α'/β 系列 |
| `a3_iso.py` | 端点证书隔离检验（遍历 `code/main_ablation_class.jsonl`） | 附录 A.2；附录 D.1 |

**已删除、未入库**：`/tmp/a2_v2.py` —— 经 `diff` 确认它是 `a2_v4.py` 的早期迭代（docstring 全同；
v4 把 JJJ 三元组由连续取件 `idx,idx+1,idx+2` 改为蛇形反射构造 `kk / 2d−1−kk / 2d+kk`，并去掉了 pair 池
循环）。v4 即该实验的最终形态，故 v2 视为无用。

**第一轮**（上表）收割的是 agent-1 复核件与 α'/β、端点件。m=3 线当时仍在迭代，故未动。

---

## 附：m=3 线的第二轮收割与 `/tmp` 的最终清空（同日，该线研究结束时）

m=3 线（`../../CKK2012_m3最优上界_A3_完整证明.md`）研究结束后补做第二轮：

**入库**
- `m3_drafts/`（5 支）—— m=3 探索脚本，**在 `code/m3_a3_verify/` 的 5 支定稿脚本中无对应内容**，故保留：
  `m3_sim.py` / `m3_sim2.py` / `m3_sim3.py`（A3 模拟的迭代版）、`probe_o8.py` / `probe_o8b.py`（观察 O8 的探针）。
  注：其余 m=3 草稿（`m3_lp.py`、`m3_base_lp.py`、`m3_base_check.py`、`m3_n9_claim.py`）已被定稿脚本取代
  （`bound_lp.py` / `base_case_lp.py` / `base_case_random.py` / `n9_claim.py`；其中 `m3_base_lp.py` 与
  `base_case_lp.py` **逐字节相同**），故未入库。
- `m3_source/ckk2012_ocr.txt` —— CKK 2012 原文的 OCR 文本（618 行）。入库原因：项目根新增了该论文的
  原文 PDF（`../../CKK2012_SOSDP_Algorithms_better_than_LPT.pdf`），但那份 PDF **无文本层**（图像扫描版、
  4 页、带水印），OCR 不易复现；留此可检索底本，便于核对 m=3 文档对原文 §3 的还原。

**一并删除**（冗余 / 被取代 / 可再生）
- 已入库的 13 支脚本与 4 支 Qcount 驱动在 `/tmp` 的同内容副本
- 6 支通用 PDF/OCR 工具（`crop.py`、`ocr.py`、`ocr2.py`、`ocr3.py`、`mkcrops.py`、`mkcrops2.py`；后两者硬编码了会话专属附件路径）
- `crops/`、`crops2/`（4.8M 页面图）与 `ckk_page-*.png`（2.2M 页面图）—— 均可由 PDF 重新渲染
- `a1_q1m0_snap.txt`、`a1_cert_snapshot.txt`（合计 7.1M）—— 经 sha256 核验，分别与
  `code/pocket1b_certificates_q1m0.txt`、`archive/data/pocket1b_certificates_13_20.txt.gz` 解压后**完全相同**
- `a3_fit_out.txt`、`ckk2012.txt`、`m3paper.txt`、`m3_ocr.txt`、`m3_ocr3.txt` 等中间输出
- `ocrvenv/`（128M、3036 个文件的 OCR 虚拟环境）

清空后 `/tmp` 内已无本项目文件。
