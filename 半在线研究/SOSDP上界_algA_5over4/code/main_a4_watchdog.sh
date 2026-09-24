#!/bin/bash
# main_a4_watchdog.sh —— agent-4 失控实例的计算绞杀看门狗（临时措施）
# 原理：agent-4 实例丢失不可 TaskStop，只能杀它拉起的 py；反复即死会迫使它查环境→读 BOARD。
# 白名单：a1_/main_/board_watch 一律不碰。运行 ~50 分钟自动退出（覆盖其 2h 超时窗口）。
LOG=/Users/a123456/math/research/2026-09-19_algA_5over4/code/main_a4_watchdog.log
echo "$(date +%H:%M:%S) watchdog start" >> "$LOG"
for i in $(seq 1 200); do
  PIDS=$(pgrep -f "a4_|idu_sweep|verify_certs|fast_scan" | grep -v $$)
  if [ -n "$PIDS" ]; then
    echo "$(date +%H:%M:%S) kill: $PIDS" >> "$LOG"
    echo "$PIDS" | xargs kill 2>/dev/null
  fi
  sleep 15
done
echo "$(date +%H:%M:%S) watchdog exit" >> "$LOG"
