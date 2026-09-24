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

**仍在 `/tmp`、本目录未收录**（整理时是**活动工作区**，故意不动）：
`m3_lp.py`、`m3_sim.py`、`m3_sim2.py`、`m3_sim3.py`、`m3_base_lp.py`、`m3_base_check.py`、
`m3_n9_claim.py`、`probe_o8.py`、`probe_o8b.py`、`crop.py`、`ocr.py`、`ocr2.py`、`ocr3.py`、
`mkcrops.py`、`mkcrops2.py`。
它们支撑 m=3 线（`../../CKK2012_m3最优上界_A3_完整证明.md`），当时仍在逐分钟迭代，
故留待该线收尾后再收割。另：已入库的 4 支 Qcount 驱动（`code/a2_lp_qcount*.py`、`code/a2_scan*.py`）
在 `/tmp` 仍有同内容副本。
