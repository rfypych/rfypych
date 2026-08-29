#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import random
import re
from datetime import datetime, timezone

STATE_FILE = "state.json"
SVG_FILE = "card.svg"

GRID_ROWS = 6
GRID_COLS = 50

DEFAULT_STATE = {
    "generation": 1,
    "seed_hash": "0x7a3f8c",
    "grid": [],
    "last_command": "run: sysinfo",
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
    cmd_name = parts[0] if parts else "sysinfo"

    t1_col, t2_col, t3_col, t4_col = "#484f58", "#484f58", "#484f58", "#484f58"
    body_elements = []

    if cmd_name in ["sysinfo", "status", "whoami"]:
        t1_col = "#58a6ff"
        body_elements = [
            '<text x="0" y="0" class="code-text"><tspan class="prompt">❯</tspan> <tspan class="cmd">sysinfo --identity</tspan></text>',
            '<text x="0" y="28" class="code-text"><tspan class="key">subject     :</tspan> <tspan class="val">Rofikul Huda</tspan> <tspan class="dim">(@rfypych)</tspan></text>',
            '<text x="0" y="52" class="code-text"><tspan class="key">location    :</tspan> <tspan class="str">Indonesia (WIB • UTC+07:00)</tspan></text>',
            '<text x="0" y="76" class="code-text"><tspan class="key">focus       :</tspan> <tspan class="str">Full-Stack Architecture, Application Security, Distributed Tooling</tspan></text>',
            '<text x="0" y="100" class="code-text"><tspan class="key">core_stack  :</tspan> <tspan class="tag">TypeScript</tspan><tspan class="dim">, </tspan><tspan class="tag">Node.js</tspan><tspan class="dim">, </tspan><tspan class="tag">Python</tspan><tspan class="dim">, </tspan><tspan class="tag">Go</tspan><tspan class="dim">, </tspan><tspan class="tag">Linux/Proxmox</tspan></text>',
            '<text x="0" y="124" class="code-text"><tspan class="key">philosophy  :</tspan> <tspan class="str">"Less abstraction, zero bloat, high resilience"</tspan></text>',
            '<line x1="0" y1="146" x2="752" y2="146" stroke="#21262d" stroke-width="1" />',
            '<text x="0" y="172" class="code-text"><tspan class="key">status      :</tspan> <tspan class="success pulse">●</tspan> <tspan class="str">Online • Systems nominal • Ed25519 identity verified</tspan></text>'
        ]
    elif cmd_name in ["skills", "stack", "tree"]:
        t2_col = "#58a6ff"
        body_elements = [
            '<text x="0" y="0" class="code-text"><tspan class="prompt">❯</tspan> <tspan class="cmd">tree --subsystems</tspan></text>',
            '<text x="0" y="28" class="code-text"><tspan class="dim">├── [0x01]</tspan> <tspan class="val">web_foundations</tspan> <tspan class="dim">:</tspan> <tspan class="str">React, Next.js, Fastify, High-Throughput REST/gRPC</tspan></text>',
            '<text x="0" y="52" class="code-text"><tspan class="dim">├── [0x02]</tspan> <tspan class="val">app_security</tspan>    <tspan class="dim">:</tspan> <tspan class="str">Vulnerability Assessment, OSINT Tooling, Surface Hardening</tspan></text>',
            '<text x="0" y="76" class="code-text"><tspan class="dim">├── [0x03]</tspan> <tspan class="val">infra_systems</tspan>   <tspan class="dim">:</tspan> <tspan class="str">Proxmox KVM / LXC, Docker, UFW/iptables, Debian/Ubuntu</tspan></text>',
            '<text x="0" y="100" class="code-text"><tspan class="dim">└── [0x04]</tspan> <tspan class="val">persistence</tspan>     <tspan class="dim">:</tspan> <tspan class="str">PostgreSQL, Redis, SQLite, Vector stores</tspan></text>',
            '<line x1="0" y1="146" x2="752" y2="146" stroke="#21262d" stroke-width="1" />',
            '<text x="0" y="172" class="code-text"><tspan class="key">dispatch    :</tspan> <tspan class="dim">[web] </tspan><tspan class="val">rofikul.vercel.app</tspan> <tspan class="dim">• [wire] </tspan><tspan class="val">t.me/rfyycrnge</tspan></text>'
        ]
    elif cmd_name in ["ping", "telemetry", "nodes"]:
        t3_col = "#58a6ff"
        ms1 = random.randint(14, 22)
        ms2 = random.randint(15, 24)
        body_elements = [
            '<text x="0" y="0" class="code-text"><tspan class="prompt">❯</tspan> <tspan class="cmd">ping --cluster --all-nodes</tspan></text>',
            f'<text x="0" y="28" class="code-text"><tspan class="dim">[node-01]</tspan> <tspan class="val">vps-master</tspan>  <tspan class="dim">[157.15.1.184:51515]</tspan> <tspan class="key">RTT:</tspan> <tspan class="str">{ms1}.4ms</tspan> <tspan class="success">● ACK</tspan></text>',
            f'<text x="0" y="52" class="code-text"><tspan class="dim">[node-02]</tspan> <tspan class="val">vps-worker</tspan>  <tspan class="dim">[157.15.1.184:55551]</tspan> <tspan class="key">RTT:</tspan> <tspan class="str">{ms2}.1ms</tspan> <tspan class="success">● ACK</tspan></text>',
            '<text x="0" y="76" class="code-text"><tspan class="dim">[node-03]</tspan> <tspan class="val">edge-gateway</tspan><tspan class="dim">[rofikul.vercel.app]</tspan> <tspan class="key">RTT:</tspan> <tspan class="str">12.8ms</tspan> <tspan class="success">● ACK</tspan></text>',
            '<text x="0" y="100" class="code-text"><tspan class="key">cluster_load:</tspan> <tspan class="str">0.11, 0.08, 0.05</tspan> <tspan class="dim">| </tspan><tspan class="key">mem_usage:</tspan> <tspan class="str">18.4%</tspan> <tspan class="dim">| </tspan><tspan class="key">packet_loss:</tspan> <tspan class="success">0.0%</tspan></text>',
            '<line x1="0" y1="146" x2="752" y2="146" stroke="#21262d" stroke-width="1" />',
            '<text x="0" y="172" class="code-text"><tspan class="key">diagnostics :</tspan> <tspan class="str">All virtual machines responding on Proxmox NAT matrix</tspan></text>'
        ]
    elif cmd_name in ["automata", "life", "evolve-life", "evolve"]:
        t4_col = "#58a6ff"
        gen = state.get("generation", 1)
        seed = state.get("seed_hash", "0x7a3f8c")
        grid = state.get("grid", [])
        grid_lines = []
        for idx, row in enumerate(grid[:6]):
            row_str = "".join("█" if cell else "░" for cell in row)
            grid_lines.append(f'<text x="0" y="{28 + idx*20}" class="code-text" fill="#7ee787">{row_str}</text>')
        body_elements = [
            f'<text x="0" y="0" class="code-text"><tspan class="prompt">❯</tspan> <tspan class="cmd">automata --seed {seed} --gen {gen}</tspan></text>',
            *grid_lines,
            '<line x1="0" y1="146" x2="752" y2="146" stroke="#21262d" stroke-width="1" />',
            f'<text x="0" y="172" class="code-text"><tspan class="key">conway_state:</tspan> <tspan class="str">Generation #{gen} • Triggered by @{user}</tspan></text>'
        ]
    elif cmd_name in ["neofetch", "fetch"]:
        body_elements = [
            '<text x="0" y="0" class="code-text"><tspan class="prompt">❯</tspan> <tspan class="cmd">neofetch</tspan></text>',
            '<text x="0" y="28" class="code-text"><tspan class="val">OS      :</tspan> <tspan class="str">Ubuntu 24.04 LTS (x86_64) on Proxmox VE</tspan></text>',
            '<text x="0" y="52" class="code-text"><tspan class="val">Kernel  :</tspan> <tspan class="str">6.8.0-generic • Uptime: 99.98%</tspan></text>',
            '<text x="0" y="76" class="code-text"><tspan class="val">Shell   :</tspan> <tspan class="str">zsh 5.9 (x86_64-debian-linux-gnu)</tspan></text>',
            '<text x="0" y="100" class="code-text"><tspan class="val">Identity:</tspan> <tspan class="str">Rofikul Huda • full-stack &amp; security engineer</tspan></text>',
            '<line x1="0" y1="146" x2="752" y2="146" stroke="#21262d" stroke-width="1" />',
            '<text x="0" y="172" class="code-text"><tspan class="key">endpoints:</tspan> <tspan class="val">rofikul.vercel.app</tspan> <tspan class="dim">•</tspan> <tspan class="val">t.me/rfyycrnge</tspan></text>'
        ]
    else:
        body_elements = [
            f'<text x="0" y="0" class="code-text"><tspan class="prompt">❯</tspan> <tspan class="cmd">{cmd}</tspan></text>',
            f'<text x="0" y="28" class="code-text"><tspan class="key">[output] :</tspan> <tspan class="str">Executed custom command</tspan></text>',
            '<line x1="0" y1="146" x2="752" y2="146" stroke="#21262d" stroke-width="1" />',
            '<text x="0" y="172" class="code-text"><tspan class="key">available:</tspan> <tspan class="str">sysinfo, skills, ping, automata, neofetch</tspan></text>'
        ]

    body_xml = "\n    ".join(body_elements)

    svg_content = f"""<svg width="800" height="350" viewBox="0 0 800 350" fill="none" xmlns="http://www.w3.org/2000/svg">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&amp;display=swap');

    .bg {{ fill: #0d1117; stroke: #30363d; stroke-width: 1; rx: 8px; }}
    .header-bar {{ fill: #161b22; stroke: #30363d; stroke-width: 1; }}
    .dot {{ fill: #383e47; }}
    .title-text {{ fill: #7d8590; font-family: 'JetBrains Mono', ui-monospace, monospace; font-size: 11px; font-weight: 500; }}
    
    .tab-btn {{ font-family: 'JetBrains Mono', ui-monospace, monospace; font-size: 11px; font-weight: 600; }}
    .code-text {{ font-family: 'JetBrains Mono', ui-monospace, monospace; font-size: 12.5px; }}

    .prompt {{ fill: #7ee787; font-weight: 700; }}
    .cmd {{ fill: #e6edf3; font-weight: 600; }}
    .key {{ fill: #7d8590; font-weight: 500; }}
    .val {{ fill: #58a6ff; font-weight: 500; }}
    .str {{ fill: #a5d6ff; }}
    .dim {{ fill: #484f58; }}
    .success {{ fill: #3fb950; font-weight: 600; }}
    .tag {{ fill: #d2a8ff; }}

    @keyframes blink {{
      0%, 49% {{ opacity: 1; }}
      50%, 100% {{ opacity: 0; }}
    }}
    .cursor {{
      animation: blink 1s infinite;
      fill: #58a6ff;
    }}

    @keyframes statusPulse {{
      0%, 100% {{ opacity: 0.4; }}
      50% {{ opacity: 1; }}
    }}
    .pulse {{ animation: statusPulse 2s infinite ease-in-out; }}
  </style>

  <rect x="1" y="1" width="798" height="348" rx="8" class="bg" />
  <path d="M 1 9 Q 1 1 9 1 L 791 1 Q 799 1 799 9 L 799 36 L 1 36 Z" class="header-bar" />
  
  <circle cx="18" cy="18" r="4.5" class="dot" />
  <circle cx="32" cy="18" r="4.5" class="dot" />
  <circle cx="46" cy="18" r="4.5" class="dot" />

  <text x="400" y="22" text-anchor="middle" class="title-text">rfypych@workspace ~ zsh (interactive terminal)</text>

  <g transform="translate(24, 52)">
    <text x="0" y="0" class="tab-btn" fill="{t1_col}">[01: SYSINFO]</text>
    <text x="140" y="0" class="tab-btn" fill="{t2_col}">[02: SKILLS]</text>
    <text x="280" y="0" class="tab-btn" fill="{t3_col}">[03: PING_NODES]</text>
    <text x="440" y="0" class="tab-btn" fill="{t4_col}">[04: AUTOMATA]</text>
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
    parser.add_argument("--issue-title", type=str, default="run: sysinfo")
    parser.add_argument("--issue-user", type=str, default="rfypych")
    args = parser.parse_args()

    state = load_state()
    user = args.issue_user.strip() or "rfypych"
    cmd = args.issue_title.strip() or "run: sysinfo"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    if any(k in cmd.lower() for k in ["automata", "life", "evolve"]):
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

    print(f"[+] Rendered dynamic card.svg for command '{cmd}' by @{user}")

if __name__ == "__main__":
    main()
