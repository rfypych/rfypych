#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import random
import re
from datetime import datetime, timezone

STATE_FILE = "state.json"
README_FILE = "README.md"

GRID_ROWS = 7
GRID_COLS = 50

DEFAULT_STATE = {
    "generation": 1,
    "seed_hash": "0x7a3f8c",
    "grid": [],
    "last_command": "run: status",
    "last_user": "rfypych",
    "last_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    "last_output": ""
}

def init_grid_from_seed(seed_str: str) -> list[list[int]]:
    hasher = hashlib.sha256(seed_str.encode("utf-8")).digest()
    grid = []
    bit_idx = 0
    
    for r in range(GRID_ROWS):
        row = []
        for c in range(GRID_COLS):
            byte = hasher[(bit_idx // 8) % len(hasher)]
            bit = (byte >> (bit_idx % 8)) & 1
            if 1 <= r <= 5 and 10 <= c <= 40:
                rand_val = (hasher[(bit_idx + 3) % len(hasher)] % 100) < 42
                row.append(1 if rand_val else 0)
            else:
                row.append(1 if (bit and (bit_idx % 4 == 0)) else 0)
            bit_idx += 1
        grid.append(row)
    return grid

def step_game_of_life(grid: list[list[int]]) -> list[list[int]]:
    rows = len(grid)
    cols = len(grid[0])
    new_grid = [[0 for _ in range(cols)] for _ in range(rows)]
    
    for r in range(rows):
        for c in range(cols):
            neighbors = 0
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = (r + dr) % rows, (c + dc) % cols
                    neighbors += grid[nr][nc]
            
            if grid[r][c] == 1:
                new_grid[r][c] = 1 if neighbors in [2, 3] else 0
            else:
                new_grid[r][c] = 1 if neighbors == 3 else 0
                
    alive_count = sum(sum(row) for row in new_grid)
    if alive_count < 8:
        for _ in range(12):
            rr = random.randint(1, rows - 2)
            rc = random.randint(8, cols - 8)
            new_grid[rr][rc] = 1

    return new_grid

def render_grid_ascii(grid: list[list[int]]) -> str:
    lines = []
    for row in grid:
        line = "".join("█" if cell else "░" for cell in row)
        lines.append(line)
    return "\n".join(lines)

def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    state = DEFAULT_STATE.copy()
    state["grid"] = init_grid_from_seed("genesis_seed_rfypych")
    return state

def save_state(state: dict):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def execute_command(cmd: str, user: str) -> str:
    cmd_clean = cmd.strip()
    if cmd_clean.lower().startswith("run:"):
        cmd_clean = cmd_clean[4:].strip()
    elif cmd_clean.lower().startswith("run"):
        cmd_clean = cmd_clean[3:].strip()
    
    parts = cmd_clean.split()
    action = parts[0].lower() if parts else "status"
    
    if action in ["status", "stat"]:
        return (
            "[ok] target     : rofikul huda (@rfypych)\n"
            "[ok] role       : full-stack development & security systems\n"
            "[ok] runtime    : indonesia (utc+07:00)\n"
            "[ok] stack      : typescript, node.js, python, go, linux/proxmox\n"
            "[ok] endpoints  : https://rofikul.vercel.app • https://t.me/rfyycrnge\n"
            "[ok] state      : online • systems nominal"
        )
    elif action in ["skills", "stack", "tech"]:
        return (
            "SUBSYSTEM CAPABILITIES:\n"
            "  ├── web/core      : react, next.js, node.js, fastify, rest/grpc\n"
            "  ├── security      : appsec auditing, osint tooling, threat modeling\n"
            "  ├── systems/infra : linux (ubuntu/debian), proxmox kvm/lxc, docker, ufw/iptables\n"
            "  └── databases     : postgresql, mysql, redis, sqlite"
        )
    elif action in ["neofetch", "sysinfo", "fetch"]:
        return (
            "rfypych@workspace\n"
            "-----------------\n"
            "OS       : Ubuntu 24.04 LTS (x86_64)\n"
            "Host     : Proxmox VE Hybrid Node\n"
            "Kernel   : 6.8.0-generic\n"
            "Shell    : zsh / bash\n"
            "Editor   : neovim / vscode\n"
            "Focus    : minimal, robust, secure architectures\n"
            "PGP/Key  : ssh-ed25519 (active)"
        )
    elif action in ["ping", "latency"]:
        ms = random.randint(12, 28)
        return (
            f"PING 157.15.1.184 (vps node): 56 data bytes\n"
            f"64 bytes from 157.15.1.184: icmp_seq=1 ttl=58 time={ms}.4 ms\n"
            f"64 bytes from 157.15.1.184: icmp_seq=2 ttl=58 time={ms - 1}.1 ms\n"
            f"--- 157.15.1.184 ping statistics ---\n"
            f"2 packets transmitted, 2 received, 0% packet loss, time 1002ms"
        )
    elif action in ["evolve-life", "step-life", "life"]:
        return (
            "[ok] conway cellular automata advanced by 1 generation.\n"
            "[ok] state vector recalculation complete."
        )
    elif action in ["reset-life", "reseed"]:
        return (
            "[ok] cellular automata grid reseeded with new cryptographic entropy."
        )
    elif action in ["help", "commands"]:
        return (
            "AVAILABLE COMMANDS:\n"
            "  • run: status      - print current overview & endpoints\n"
            "  • run: skills      - list technology domains & tooling\n"
            "  • run: neofetch    - display developer system specifications\n"
            "  • run: ping        - test node latency & packet heartbeat\n"
            "  • run: evolve-life - compute next generation in cellular automata\n"
            "  • run: reset-life  - reseed the automata canvas with new entropy"
        )
    else:
        text_arg = " ".join(parts[1:]) if len(parts) > 1 else action
        return (
            f"[exec] command: '{cmd}'\n"
            f"[output] echo '{text_arg}'\n"
            f"[info] available: 'run: status', 'run: skills', 'run: neofetch', 'run: ping'"
        )

def update_readme(state: dict):
    with open(README_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    automata_ascii = render_grid_ascii(state["grid"])
    
    automata_block = (
        "```text\n"
        f"[cellular automata] gen: {state['generation']} | seed: {state['seed_hash']} | rule: B3/S23\n"
        f"{automata_ascii}\n"
        "```"
    )

    terminal_block = (
        "```text\n"
        f"rfypych@terminal:~$ {state['last_command']}\n"
        f"{state['last_output']}\n\n"
        f"last interaction: @{state['last_user']} executed '{state['last_command']}' at {state['last_timestamp']}\n"
        "```"
    )

    content = re.sub(
        r"<!-- START_AUTOMATA -->.*?<!-- END_AUTOMATA -->",
        f"<!-- START_AUTOMATA -->\n{automata_block}\n<!-- END_AUTOMATA -->",
        content,
        flags=re.DOTALL
    )

    content = re.sub(
        r"<!-- START_TERMINAL -->.*?<!-- END_TERMINAL -->",
        f"<!-- START_TERMINAL -->\n{terminal_block}\n<!-- END_TERMINAL -->",
        content,
        flags=re.DOTALL
    )

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    parser = argparse.ArgumentParser(description="Autonomous Profile Terminal Engine")
    parser.add_argument("--issue-title", type=str, default="", help="Command from issue title")
    parser.add_argument("--issue-user", type=str, default="guest", help="Username of the issue creator")
    args = parser.parse_args()

    state = load_state()

    cmd = args.issue_title.strip() if args.issue_title else state.get("last_command", "run: status")
    user = args.issue_user.strip() if args.issue_user else "rfypych"

    output = execute_command(cmd, user)

    cmd_lower = cmd.lower()
    if "reset-life" in cmd_lower or not state.get("grid"):
        new_seed = f"0x{hashlib.sha256(f'{datetime.now().isoformat()}_{user}'.encode()).hexdigest()[:6]}"
        state["seed_hash"] = new_seed
        state["grid"] = init_grid_from_seed(new_seed)
        state["generation"] = 1
    else:
        state["grid"] = step_game_of_life(state.get("grid") or init_grid_from_seed("default"))
        state["generation"] = state.get("generation", 1) + 1

    state["last_command"] = cmd if cmd.lower().startswith("run:") else f"run: {cmd}"
    state["last_user"] = user
    state["last_timestamp"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    state["last_output"] = output

    save_state(state)
    update_readme(state)
    print(f"[+] Engine executed: '{state['last_command']}' by @{user}")

if __name__ == "__main__":
    main()
