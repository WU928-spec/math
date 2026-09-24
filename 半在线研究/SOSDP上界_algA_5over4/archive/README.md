# archive/ 归档说明

> 本目录存放**过程文献与历史版本**，都不是最终证明文本。**现行定稿见 `../完整证明_5over4.md`。**

- **reports/**：多代理协作时代（已停用）的工作报告（a1_/a2_/a3_ 系列 md）与 inbox 通信记录。部分结论已被后续路线取代（尤其涉及 sliver 紧性者），**勿作依据**。内含若干旧路径 `/Users/a123456/math/research/2026-09-19_algA_5over4/` 的历史命令记录，未逐条改写。
- **drafts/**：被取代的草稿——main_beta_proof_draft.md（v1）、midk_note.md、lemma_T_draft.md、a1_tight_real.py（code/ 版的旧版）。
- **superseded/**：曾被当作正文的证明旧版，归档时**未改动内容**——
  - `second_proof.md`（第二证明符号化前的完整版）、`LP_ROUTE.md`（LP 路线旧终稿 v1.0）、`razor_closure.md`（闭合总结）；
  - `main_alpha_tight.md` / `main_beta_proof_v2.md` / `a3_beta_hi.md`（薄层 α'/β，**均建立在已作废的 sliver 紧性引理上**）；
  - `a1_b4_symbolic.md`、`main_b4_supply.md`、`a3_endpoint_symbolic.md`、`a2_tightness_machine.md`、`a1_second_proof_review.md`；
  - `pocket1.md` / `pocket2.md` / `pocket3_volume.md`（口袋攻击笔记；pocket3_volume 依赖已判 INVALID 的约束）。
- **collab/**：协作基建与账本——BOARD.md、NOTES.md、STATUS.md、JEL.md、SEMANTICS.md、PROTOCOL.md、OWNERS.md、OPTIMIZE.md、opt_db.json、agents_registry.json、board_watch.py、main_a4_watchdog.sh。其中部分文件含改名前路径，属历史记录，未逐条改写（NOTES.md / STATUS.md 已加路径说明）。
- **data/**：大型验证证书的 gzip 压缩版（原始 .txt/.jsonl 已删，内容无损——gunzip 即恢复）：
  - `pocket2_onestep_order_certs_31_45.txt.gz`（177M → 8.6M）：**实为 m=31..50 的合并整文件**（467984 行），同时包含 m=31..45（263575 行）与 m=46..50（204409 行）两个原 txt 的全部内容；
  - `pocket2_onestep_order_certs.txt.gz`（m=4..30）、`pocket2_osr_certs_v2.txt.gz`、`p3_bins_certificates.txt.gz`、`pocket1b_certificates_13_20.txt.gz`、`fast_scan_progress_31_45.jsonl.gz`（扫描断点边车，扫描已完成、无续跑价值）；
  - 以上 gzip 的 sha256 见 `data/SHA256SUMS`（`../artifact/manifest.sha256` 只覆盖 artifact/ 自身文件）。
- **顶层两个文件**：`完整证明_5over4_备份_before_rewrite.md`（定稿改写前的备份，保留作追溯）、`证书样张_附录E.md`（已从正文移出的证书样张，正文不再引用）。

相关：计算证据包在 `../artifact/`（含 manifest.sha256 校验）。

已清除：__pycache__、.DS_Store、watch_daemon.err。
