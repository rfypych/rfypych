#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import random
from datetime import datetime, timezone

STATE_FILE = "state.json"
SVG_FILE = "card.svg"

GRID_ROWS = 6
GRID_COLS = 50

DEFAULT_STATE = {
    "generation": 1,
    "seed_hash": "0x7a3f8c",
    "grid": [],
    "last_command": "run: whoami",
    "last_user": "rfypych",
    "last_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
}

def init_grid(seed_str: str) -> list[list[int]]:
    hasher = hashlib.sha256(seed_str.encode("utf-8")).digest()
    grid = []
    bit_idx = 0
    for r in range(GRID_ROWS):
        row = []
        for c in range(GRID_COLS):
            byte = hasher[(bit_idx // 8) % len(hasher)]
            bit = (byte >> (bit_idx % 8)) & 1
            if 1 <= r <= 4 and 10 <= c <= 40:
                rand_val = (hasher[(bit_idx + 3) % len(hasher)] % 100) < 42
                row.append(1 if rand_val else 0)
            else:
                row.append(1 if (bit and (bit_idx % 4 == 0)) else 0)
            bit_idx += 1
        grid.append(row)
    return grid

def step_grid(grid: list[list[int]]) -> list[list[int]]:
    rows = len(grid)
    cols = len(grid[0])
    new_grid = [[0 for _ in range(cols)] for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            neighbors = 0
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0: continue
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

def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    state = DEFAULT_STATE.copy()
    state["grid"] = init_grid("rfypych_genesis")
    return state

def save_state(state: dict):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def generate_svg(cmd: str, user: str, timestamp: str, state: dict) -> str:
    cmd_clean = cmd.strip()
    if cmd_clean.lower().startswith("run:"):
        action = cmd_clean[4:].strip().lower()
    elif cmd_clean.lower().startswith("run"):
        action = cmd_clean[3:].strip().lower()
    else:
        action = cmd_clean.lower()
    
    parts = action.split()
    cmd_name = parts[0] if parts else "whoami"

    t1_col, t2_col, t3_col, t4_col = "#484f58", "#484f58", "#484f58", "#484f58"
    body_elements = []

    if cmd_name in ["whoami", "sysinfo", "status", "bio"]:
        t1_col = "#58a6ff"
        body_elements = [
            '<text x="0" y="0" class="code-text"><tspan class="prompt">❯</tspan> <tspan class="cmd">whoami</tspan></text>',
            '<text x="0" y="28" class="code-text"><tspan class="key">user        :</tspan> <tspan class="val">Rofikul Huda</tspan> <tspan class="dim">(@rfypych)</tspan></text>',
            '<text x="0" y="52" class="code-text"><tspan class="key">role        :</tspan> <tspan class="str">Full-Stack Developer &amp; Security Analyst</tspan></text>',
            '<text x="0" y="76" class="code-text"><tspan class="key">location    :</tspan> <tspan class="str">Indonesia (UTC+07:00)</tspan></text>',
            '<text x="0" y="100" class="code-text"><tspan class="key">languages   :</tspan> <tspan class="tag">TypeScript</tspan><tspan class="dim">, </tspan><tspan class="tag">Node.js</tspan><tspan class="dim">, </tspan><tspan class="tag">Python</tspan><tspan class="dim">, </tspan><tspan class="tag">Go</tspan><tspan class="dim">, </tspan><tspan class="tag">SQL</tspan></text>',
            '<text x="0" y="124" class="code-text"><tspan class="key">links       :</tspan> <tspan class="str">rofikul.vercel.app / t.me/rfyycrnge</tspan></text>',
            '<line x1="0" y1="146" x2="752" y2="146" stroke="#21262d" stroke-width="1" />',
            '<text x="0" y="172" class="code-text"><tspan class="key">status      :</tspan> <tspan class="str">active</tspan></text>'
        ]
    elif cmd_name in ["stack", "skills", "cat"]:
        t2_col = "#58a6ff"
        body_elements = [
            '<text x="0" y="0" class="code-text"><tspan class="prompt">❯</tspan> <tspan class="cmd">cat stack.txt</tspan></text>',
            '<text x="0" y="28" class="code-text"><tspan class="key">frontend    :</tspan> <tspan class="str">React, Next.js, Tailwind CSS</tspan></text>',
            '<text x="0" y="52" class="code-text"><tspan class="key">backend     :</tspan> <tspan class="str">Node.js, Fastify, Express, Python</tspan></text>',
            '<text x="0" y="76" class="code-text"><tspan class="key">security    :</tspan> <tspan class="str">Application Security, OSINT, Threat Modeling</tspan></text>',
            '<text x="0" y="100" class="code-text"><tspan class="key">infra       :</tspan> <tspan class="str">Linux (Debian/Ubuntu), Docker, Nginx, PostgreSQL</tspan></text>',
            '<line x1="0" y1="146" x2="752" y2="146" stroke="#21262d" stroke-width="1" />',
            '<text x="0" y="172" class="code-text"><tspan class="key">tools       :</tspan> <tspan class="str">Git, Bash, Neovim, VS Code</tspan></text>'
        ]
    elif cmd_name in ["ping"]:
        t3_col = "#58a6ff"
        ms1 = random.randint(12, 18)
        ms2 = random.randint(12, 18)
        ms3 = random.randint(12, 18)
        body_elements = [
            '<text x="0" y="0" class="code-text"><tspan class="prompt">❯</tspan> <tspan class="cmd">ping -c 3 1.1.1.1</tspan></text>',
            '<text x="0" y="28" class="code-text"><tspan class="dim">PING 1.1.1.1 (1.1.1.1) 56(84) bytes of data.</tspan></text>',
            f'<text x="0" y="52" class="code-text"><tspan class="dim">64 bytes from 1.1.1.1: icmp_seq=1 ttl=57 time={ms1}.2 ms</tspan></text>',
            f'<text x="0" y="76" class="code-text"><tspan class="dim">64 bytes from 1.1.1.1: icmp_seq=2 ttl=57 time={ms2}.8 ms</tspan></text>',
            f'<text x="0" y="100" class="code-text"><tspan class="dim">64 bytes from 1.1.1.1: icmp_seq=3 ttl=57 time={ms3}.4 ms</tspan></text>',
            '<line x1="0" y1="146" x2="752" y2="146" stroke="#21262d" stroke-width="1" />',
            '<text x="0" y="172" class="code-text"><tspan class="key">summary     :</tspan> <tspan class="str">3 packets transmitted, 3 received, 0% packet loss</tspan></text>'
        ]
    elif cmd_name in ["automata", "life", "conway"]:
        t4_col = "#58a6ff"
        gen = state.get("generation", 1)
        seed = state.get("seed_hash", "0x7a3f8c")
        grid = state.get("grid", [])
        grid_lines = []
        for idx, row in enumerate(grid[:6]):
            row_str = "".join("█" if cell else "░" for cell in row)
            grid_lines.append(f'<text x="0" y="{28 + idx*20}" class="code-text" fill="#c9d1d9">{row_str}</text>')
        body_elements = [
            f'<text x="0" y="0" class="code-text"><tspan class="prompt">❯</tspan> <tspan class="cmd">conway --gen {gen} --seed {seed}</tspan></text>',
            *grid_lines,
            '<line x1="0" y1="146" x2="752" y2="146" stroke="#21262d" stroke-width="1" />',
            f'<text x="0" y="172" class="code-text"><tspan class="key">state       :</tspan> <tspan class="str">generation {gen} (B3/S23)</tspan></text>'
        ]
    elif cmd_name in ["uname", "neofetch"]:
        body_elements = [
            '<text x="0" y="0" class="code-text"><tspan class="prompt">❯</tspan> <tspan class="cmd">uname -srmo</tspan></text>',
            '<text x="0" y="28" class="code-text"><tspan class="str">Linux 6.8.0-generic x86_64 GNU/Linux</tspan></text>',
            '<text x="0" y="60" class="code-text"><tspan class="prompt">❯</tspan> <tspan class="cmd">uptime</tspan></text>',
            '<text x="0" y="88" class="code-text"><tspan class="str">up 42 days, 12:30, 1 user, load average: 0.12, 0.08, 0.05</tspan></text>',
            '<line x1="0" y1="146" x2="752" y2="146" stroke="#21262d" stroke-width="1" />',
            '<text x="0" y="172" class="code-text"><tspan class="key">shell       :</tspan> <tspan class="str">zsh 5.9</tspan></text>'
        ]
    else:
        body_elements = [
            f'<text x="0" y="0" class="code-text"><tspan class="prompt">❯</tspan> <tspan class="cmd">{cmd}</tspan></text>',
            f'<text x="0" y="28" class="code-text"><tspan class="str">Command executed</tspan></text>',
            '<line x1="0" y1="146" x2="752" y2="146" stroke="#21262d" stroke-width="1" />',
            '<text x="0" y="172" class="code-text"><tspan class="key">commands    :</tspan> <tspan class="str">whoami, stack, ping, automata, uname</tspan></text>'
        ]

    body_xml = "\n    ".join(body_elements)

    svg_content = f"""<svg width="800" height="350" viewBox="0 0 800 350" fill="none" xmlns="http://www.w3.org/2000/svg">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&amp;display=swap');

    .bg {{ fill: #0d1117; stroke: #30363d; stroke-width: 1; rx: 8px; }}
    .header-bar {{ fill: #161b22; stroke: #30363d; stroke-width: 1; }}
    .title-text {{ fill: #7d8590; font-family: 'JetBrains Mono', ui-monospace, monospace; font-size: 11px; font-weight: 500; }}
    
    .tab-btn {{ font-family: 'JetBrains Mono', ui-monospace, monospace; font-size: 11px; font-weight: 600; }}
    .code-text {{ font-family: 'JetBrains Mono', ui-monospace, monospace; font-size: 12.5px; }}

    .prompt {{ fill: #58a6ff; font-weight: 700; }}
    .cmd {{ fill: #e6edf3; font-weight: 600; }}
    .key {{ fill: #7d8590; font-weight: 500; }}
    .val {{ fill: #58a6ff; font-weight: 500; }}
    .str {{ fill: #c9d1d9; }}
    .dim {{ fill: #484f58; }}
    .tag {{ fill: #d2a8ff; }}

    @keyframes blink {{
      0%, 49% {{ opacity: 1; }}
      50%, 100% {{ opacity: 0; }}
    }}
    .cursor {{
      animation: blink 1s infinite;
      fill: #58a6ff;
    }}
  </style>

  <rect x="1" y="1" width="798" height="348" rx="8" class="bg" />
  <path d="M 1 9 Q 1 1 9 1 L 791 1 Q 799 1 799 9 L 799 36 L 1 36 Z" class="header-bar" />

  <text x="24" y="22" class="title-text">rfypych@workspace ~ zsh</text>

  <g transform="translate(24, 52)">
    <text x="0" y="0" class="tab-btn" fill="{t1_col}">[01: WHOAMI]</text>
    <text x="130" y="0" class="tab-btn" fill="{t2_col}">[02: STACK]</text>
    <text x="250" y="0" class="tab-btn" fill="{t3_col}">[03: PING]</text>
    <text x="360" y="0" class="tab-btn" fill="{t4_col}">[04: AUTOMATA]</text>
    <line x1="0" y1="12" x2="752" y2="12" stroke="#21262d" stroke-width="1" />
  </g>

  <g transform="translate(24, 90)">
    {body_xml}
    <text x="0" y="202" class="code-text"><tspan class="dim">last_execution: @{user} ran '{cmd}' at {timestamp}</tspan></text>
    <text x="0" y="232" class="code-text"><tspan class="prompt">❯</tspan> <rect x="14" y="221" width="7" height="13" class="cursor" /></text>
  </g>
</svg>"""

    return svg_content

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue-title", type=str, default="run: whoami")
    parser.add_argument("--issue-user", type=str, default="rfypych")
    args = parser.parse_args()

    state = load_state()
    user = args.issue_user.strip() or "rfypych"
    cmd = args.issue_title.strip() or "run: whoami"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    if any(k in cmd.lower() for k in ["automata", "life", "conway"]):
        state["grid"] = step_grid(state.get("grid") or init_grid("default"))
        state["generation"] = state.get("generation", 1) + 1
    elif not state.get("grid"):
        state["grid"] = init_grid("genesis")

    state["last_command"] = cmd
    state["last_user"] = user
    state["last_timestamp"] = timestamp

    save_state(state)

    svg_content = generate_svg(cmd, user, timestamp, state)
    with open(SVG_FILE, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"[+] Rendered card.svg for '{cmd}' by @{user}")

if __name__ == "__main__":
    main()
