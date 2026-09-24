# 文件所有权登记制（2026-09-22 起，PROTOCOL.md 补充条款）

> 原则：**非所有者只读；要改别人的文件 → BOARD 申请或新建带自己前缀的文件。**
> 唯一的例外：BOARD.md（全员追加，不改他人行）。

## 所有者表

| 所有者 | 文件 |
|---|---|
| main（主代理） | farkas_fixed.py / pocket13_fixed.py / second_step.py / order_step.py / fast_lp.py / fast_scan*.py / LP_ROUTE.md / NOTES.md / STATUS.md / proof.md / OPTIMIZE.md / PROTOCOL.md / SEMANTICS.md / LP_CONSTRAINTS.md 以外的 *.md / pocket2_onestep_order_certs.txt / pocket2_osr_certs_v2.txt / *scan*_progress.jsonl（fast_scan 系） |
| agent-1 | pocket1_bins.py / pocket1b_certificates*.txt / pocket1b_progress.jsonl |
| agent-2 | hole_close*.py / uniform_hole_cert.py / hole_template_certs.* / fuzz_mon2.py / hole_reach.py / leftover_scan.py / cert_struct.py / hole_close_lemma.md |
| agent-3 | audit_*.py / LP_CONSTRAINTS.md / pocket3_bins.py（及后续 a3_ 前缀文件） |
| agent-4 | scan_p2*.py / verify_certs.py / gen_pocket2_certs.py / pocket2_certificates.jsonl / p2_s2_* / p2_prog/ |
| 冻结基线（全员只读，含 main） | pairing_feasible.py / toolbox.py / farkas_constant.py（废止）/ pocket1_lp.py / pocket3_lp.py / uniform_certs.py（废止） |

## 规则

1. **新文件必须带所有者前缀**（a1_/a2_/a3_/a4_，main 除外），放进本表才可被他人引用。
2. **证书/进度文件 = 所有者追加专用**。他人验证前**先快照**（cp 到 /tmp 或自带副本），
   复核快照并报告行数/哈希，禁止边写边验（agent-4 曾在此 FAIL）。
3. **BOARD.md**：全员仅追加；写自己时间戳行；禁止编辑/删除他人行。
4. **SEMANTICS.md**：自创工件自行更新；他人工件的状态变更走 BOARD，由 main 统一修改。
5. **inbox_agent{N}.md**：main 写、对应代理读；代理之间禁写。
6. 需要给别人文件提改进：BOARD 发 REQUEST，由所有者执行；紧急修复（bug）可建新文件
   并在 BOARD 声明"旧文件停用"。
7. 违反所有制的写入 = 事故，写 BOARD 事故记录并立即回滚。
