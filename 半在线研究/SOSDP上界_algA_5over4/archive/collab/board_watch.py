"""BOARD.md 监视器 v3：侦测 + 扇出到各代理 inbox + 通知主代理 + 孤儿猎手。
职责：
1. 每 20s 查 BOARD.md：有非 main/auto 新条目 →
   a) 扇出：追加到 AGENTS 注册表所列每个 inbox_agent{N}.md（代理工具间隙自查，~1min 送达）；
   b) 打印并退出 → 通知主代理（随后主代理重启本脚本）。
2. 每周期查孤儿 python 扫描进程（PPID=1）→ kill -9 并记 BOARD（auto 标签自过滤）。
CPU：sleep 轮询，可忽略。2 小时自毁。
"""
import os, sys, time, subprocess, json

ROOT = '/Users/a123456/math/research/2026-09-19_algA_5over4'
BOARD = os.path.join(ROOT, 'BOARD.md')
REGISTRY = os.path.join(ROOT, 'agents_registry.json')
DEADLINE = time.time() + 2 * 3600
PATTERNS = ['pocket', 'scan', 'verify_certs', 'fuzz', 'order_step', 'uniform', 'second_step',
            'fast_lp', 'hole_close', 'audit_', 'topk', 'template_', 'adversarial']
SKIP = ['board_watch']


def readlines():
    return open(BOARD).readlines() if os.path.exists(BOARD) else []


def poll_once(agent_id):
    """一次性拉取：读 agent 的已读位置，打印新条目并更新位置。供代理在工具间隙调用。"""
    seen_file = os.path.join(ROOT, f'.board_seen_{agent_id}')
    try:
        seen = int(open(seen_file).read().strip())
    except Exception:
        seen = 0
    cur = readlines()
    fresh = cur[seen:]
    with open(seen_file, 'w') as f:
        f.write(str(len(cur)))
    if fresh:
        sys.stdout.write('BOARD 新条目:\n' + ''.join(fresh))
    # 无新条目则静默（不打扰代理回合）


def live_inboxes():
    """读 agents_registry.json（{"live": [2,3,4,...]}），返回 inbox 路径列表。"""
    try:
        reg = json.load(open(REGISTRY))
        return [os.path.join(ROOT, f'inbox_agent{n}.md') for n in reg.get('live', [])]
    except Exception:
        return []


def fanout(fresh):
    ts = time.strftime('%Y-%m-%d %H:%M')
    for ib in live_inboxes():
        try:
            with open(ib, 'a') as f:
                f.write(f'\n[{ts}] BOARD-fanout | ' + ''.join(fresh))
        except Exception:
            pass


def kill_orphans():
    try:
        out = subprocess.run(['ps', '-eo', 'pid,ppid,command'], capture_output=True, text=True,
                             timeout=10).stdout
    except Exception:
        return []
    killed = []
    for line in out.splitlines()[1:]:
        parts = line.split(None, 2)
        if len(parts) < 3:
            continue
        pid, ppid, cmd = parts
        if ppid != '1' or 'python' not in cmd or any(s in cmd for s in SKIP):
            continue
        if any(p in cmd for p in PATTERNS):
            try:
                os.kill(int(pid), 9)
                killed.append((pid, cmd.strip()[-60:]))
            except Exception:
                pass
    return killed


def log_auto(msg):
    with open(BOARD, 'a') as f:
        f.write(f'[{time.strftime("%Y-%m-%d %H:%M")}] auto CPU | {msg} | board_watch\n')


def main():
    seen = len(readlines())
    while time.time() < DEADLINE:
        time.sleep(20)
        cur = readlines()
        fresh = [l for l in cur[seen:] if '] main ' not in l and '] auto ' not in l]
        seen = len(cur)
        killed = kill_orphans()
        if killed:
            log_auto(f'杀孤儿进程 {len(killed)} 个: ' + '; '.join(f'{p}({c})' for p, c in killed[:6]))
            cur = readlines(); seen = len(cur)
        if fresh:
            fanout(fresh)
            sys.stdout.write('BOARD 新条目（已扇出至各 inbox）:\n' + ''.join(fresh))
            sys.exit(0)


LOGDIR = '/Users/a123456/math/research/2026-09-19_algA_5over4/logs'


def daemon():
    """launchd 守护模式：常驻循环，扇出+猎杀，不退出（无通知需求）。日志落 logs/watch_daemon.log。"""
    os.makedirs(LOGDIR, exist_ok=True)
    logf = open(os.path.join(LOGDIR, 'watch_daemon.log'), 'a')
    seen = len(readlines())
    while True:
        time.sleep(20)
        try:
            cur = readlines()
            fresh = [l for l in cur[seen:] if '] main ' not in l and '] auto ' not in l and '] daemon ' not in l]
            seen = len(cur)
            if fresh:
                fanout(fresh)
                logf.write(f'[{time.strftime("%H:%M:%S")}] fanout {len(fresh)} 条\n'); logf.flush()
            killed = kill_orphans()
            if killed:
                logf.write(f'[{time.strftime("%H:%M:%S")}] kill {len(killed)}: ' +
                           '; '.join(f'{p}({c})' for p, c in killed[:6]) + '\n'); logf.flush()
        except Exception as e:
            logf.write(f'[{time.strftime("%H:%M:%S")}] ERR {e!r}\n'); logf.flush()


if __name__ == '__main__':
    if len(sys.argv) >= 3 and sys.argv[1] == '--once':
        poll_once(sys.argv[2])
    elif len(sys.argv) >= 2 and sys.argv[1] == '--daemon':
        daemon()
    else:
        try:
            main()
        except Exception as e:
            import traceback
            sys.stdout.write('watcher 异常退出: ' + repr(e) + '\n' + traceback.format_exc())
            sys.stdout.flush()
            raise
