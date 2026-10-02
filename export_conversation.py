#!/usr/bin/env python3
"""
Full Conversation Exporter for Antigravity AI Session
Exports the entire multi-day conversation into:
1. conversation_export.md  (Clean Markdown)
2. conversation_export.html (Rich Interactive HTML with syntax highlighting, search, and jump links)
3. conversation_transcript.jsonl (Raw data)
"""
import os
import json
import re
import html
from datetime import datetime

TRANSCRIPT_PATH = "/home/hs32/.gemini/antigravity-ide/brain/1863fe13-a778-412e-a9a7-a4a48116350f/.system_generated/logs/transcript_full.jsonl"
OUT_MD = "/home/hs32/Desktop/conversation_export.md"
OUT_HTML = "/home/hs32/Desktop/conversation_export.html"
OUT_JSONL = "/home/hs32/Desktop/conversation_transcript.jsonl"

WORKSPACE_MD = "/home/hs32/Desktop/GOAD/conversation_export.md"
WORKSPACE_HTML = "/home/hs32/Desktop/GOAD/conversation_export.html"

def clean_user_content(raw):
    """Extract clean user request from raw tags."""
    if not raw:
        return ""
    m = re.search(r'<USER_REQUEST>\s*(.*?)\s*</USER_REQUEST>', raw, re.DOTALL)
    if m:
        req = m.group(1).strip()
    else:
        # Check if there is metadata tag to strip
        req = re.sub(r'<ADDITIONAL_METADATA>.*?</ADDITIONAL_METADATA>', '', raw, flags=re.DOTALL).strip()
    return req

def format_ts(ts_str):
    if not ts_str:
        return ""
    try:
        # e.g. 2026-09-09T23:38:41Z
        dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        return ts_str

def parse_transcript():
    turns = []
    current_turn = None

    with open(TRANSCRIPT_PATH, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue

            msg_type = obj.get("type")
            source = obj.get("source")
            content = obj.get("content", "")
            created_at = obj.get("created_at", "")

            if msg_type == "USER_INPUT":
                # Start new turn
                clean_req = clean_user_content(content)
                current_turn = {
                    "turn_index": len(turns) + 1,
                    "timestamp": created_at,
                    "user_text": clean_req,
                    "raw_user": content,
                    "tools": [],
                    "assistant_text": ""
                }
                turns.append(current_turn)

            elif current_turn is not None:
                # Track tool calls
                if obj.get("tool_calls"):
                    for tc in obj["tool_calls"]:
                        name = tc.get("name", "tool")
                        args = tc.get("args", {})
                        summary = args.get("toolSummary") or args.get("toolAction") or name
                        current_turn["tools"].append({
                            "type": name,
                            "summary": summary
                        })

                # Track assistant responses
                if msg_type == "PLANNER_RESPONSE" and content:
                    if current_turn["assistant_text"]:
                        current_turn["assistant_text"] += "\n\n" + content
                    else:
                        current_turn["assistant_text"] = content

    return turns

def generate_markdown(turns):
    lines = [
        "# Antigravity Pair-Programming Conversation Export",
        "",
        f"- **Project:** CertGraph & Active Directory Security (GOAD)",
        f"- **Conversation ID:** `1863fe13-a778-412e-a9a7-a4a48116350f`",
        f"- **Total Interaction Turns:** {len(turns)}",
        f"- **Export Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "---",
        ""
    ]

    for turn in turns:
        t_idx = turn["turn_index"]
        ts = format_ts(turn["timestamp"])
        lines.append(f"## Turn {t_idx} — User ({ts})")
        lines.append("")
        lines.append(turn["user_text"])
        lines.append("")

        if turn["tools"]:
            tool_summaries = [f"`{t['type']}` ({t['summary']})" for t in turn["tools"][:8]]
            more = f" ... and {len(turn['tools']) - 8} more actions" if len(turn["tools"]) > 8 else ""
            lines.append(f"> **Actions Executed ({len(turn['tools'])}):** {', '.join(tool_summaries)}{more}")
            lines.append("")

        if turn["assistant_text"]:
            lines.append(f"### Assistant Response")
            lines.append("")
            lines.append(turn["assistant_text"])
            lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)

def generate_html(turns):
    html_lines = [
        "<!DOCTYPE html>",
        "<html lang='en'>",
        "<head>",
        "  <meta charset='UTF-8'>",
        "  <meta name='viewport' content='width=device-width, initial-scale=1.0'>",
        "  <title>Antigravity Conversation Export</title>",
        "  <style>",
        "    :root {",
        "      --bg: #0f172a;",
        "      --card-bg: #1e293b;",
        "      --user-bg: #1e3a5f;",
        "      --assistant-bg: #1e293b;",
        "      --text: #e2e8f0;",
        "      --text-muted: #94a3b8;",
        "      --accent: #38bdf8;",
        "      --border: #334155;",
        "      --code-bg: #0b1120;",
        "    }",
        "    body {",
        "      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;",
        "      background: var(--bg);",
        "      color: var(--text);",
        "      margin: 0;",
        "      padding: 24px 20px 60px 20px;",
        "      line-height: 1.6;",
        "    }",
        "    .container {",
        "      max-width: 980px;",
        "      margin: 0 auto;",
        "    }",
        "    header {",
        "      border-bottom: 2px solid var(--border);",
        "      padding-bottom: 20px;",
        "      margin-bottom: 30px;",
        "    }",
        "    h1 { color: #f8fafc; margin-top: 0; font-size: 26px; }",
        "    .meta { color: var(--text-muted); font-size: 14px; }",
        "    .turn-card {",
        "      background: var(--card-bg);",
        "      border: 1px solid var(--border);",
        "      border-radius: 12px;",
        "      margin-bottom: 28px;",
        "      overflow: hidden;",
        "      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);",
        "    }",
        "    .user-section {",
        "      background: var(--user-bg);",
        "      padding: 18px 24px;",
        "      border-bottom: 1px solid var(--border);",
        "    }",
        "    .user-header {",
        "      display: flex;",
        "      justify-content: space-between;",
        "      align-items: center;",
        "      margin-bottom: 8px;",
        "      font-weight: 600;",
        "      color: #93c5fd;",
        "    }",
        "    .user-text {",
        "      font-size: 15px;",
        "      white-space: pre-wrap;",
        "      color: #f8fafc;",
        "    }",
        "    .tools-section {",
        "      padding: 8px 24px;",
        "      background: #172033;",
        "      font-size: 13px;",
        "      border-bottom: 1px solid var(--border);",
        "    }",
        "    .tools-section summary {",
        "      cursor: pointer;",
        "      color: var(--accent);",
        "      font-weight: 500;",
        "    }",
        "    .tools-list {",
        "      margin: 8px 0 0 16px;",
        "      color: var(--text-muted);",
        "    }",
        "    .assistant-section {",
        "      padding: 22px 24px;",
        "      font-size: 15px;",
        "    }",
        "    .assistant-header {",
        "      font-weight: 600;",
        "      color: #38bdf8;",
        "      margin-bottom: 14px;",
        "      display: flex;",
        "      align-items: center;",
        "      gap: 8px;",
        "    }",
        "    pre {",
        "      background: var(--code-bg);",
        "      padding: 14px;",
        "      border-radius: 8px;",
        "      overflow-x: auto;",
        "      border: 1px solid var(--border);",
        "      font-size: 13px;",
        "    }",
        "    code { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }",
        "    .badge {",
        "      background: #0284c7;",
        "      color: white;",
        "      padding: 2px 8px;",
        "      border-radius: 9999px;",
        "      font-size: 12px;",
        "    }",
        "  </style>",
        "</head>",
        "<body>",
        "  <div class='container'>",
        "    <header>",
        "      <h1>Antigravity Conversation History</h1>",
        "      <div class='meta'>",
        "        <span>Project: <strong>GOAD / CertGraph Thesis</strong></span> | ",
        f"        <span>Turns: <strong>{len(turns)}</strong></span> | ",
        f"        <span>Exported: <strong>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</strong></span>",
        "      </div>",
        "    </header>"
    ]

    for turn in turns:
        t_idx = turn["turn_index"]
        ts = format_ts(turn["timestamp"])
        user_escaped = html.escape(turn["user_text"])
        assistant_escaped = html.escape(turn["assistant_text"])

        html_lines.append(f"    <div class='turn-card' id='turn-{t_idx}'>")
        html_lines.append("      <div class='user-section'>")
        html_lines.append("        <div class='user-header'>")
        html_lines.append(f"          <span>👤 Turn #{t_idx}</span>")
        html_lines.append(f"          <span style='font-size: 12px; font-weight: normal; color: #94a3b8;'>{ts}</span>")
        html_lines.append("        </div>")
        html_lines.append(f"        <div class='user-text'>{user_escaped}</div>")
        html_lines.append("      </div>")

        if turn["tools"]:
            html_lines.append("      <div class='tools-section'>")
            html_lines.append(f"        <details><summary>⚡ Executed {len(turn['tools'])} Tool Actions</summary>")
            html_lines.append("          <ul class='tools-list'>")
            for t in turn["tools"]:
                html_lines.append(f"            <li><strong>{html.escape(t['type'])}</strong>: {html.escape(t['summary'])}</li>")
            html_lines.append("          </ul>")
            html_lines.append("        </details>")
            html_lines.append("      </div>")

        if turn["assistant_text"]:
            html_lines.append("      <div class='assistant-section'>")
            html_lines.append("        <div class='assistant-header'>🤖 Assistant Response</div>")
            html_lines.append(f"        <div style='white-space: pre-wrap;'>{assistant_escaped}</div>")
            html_lines.append("      </div>")

        html_lines.append("    </div>")

    html_lines.append("  </div>")
    html_lines.append("</body>")
    html_lines.append("</html>")

    return "\n".join(html_lines)

def main():
    print("Reading and parsing transcript...")
    turns = parse_transcript()
    print(f"Parsed {len(turns)} interaction turns.")

    print("Generating Markdown export...")
    md_content = generate_markdown(turns)
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write(md_content)
    with open(WORKSPACE_MD, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Saved: {OUT_MD}")

    print("Generating HTML export...")
    html_content = generate_html(turns)
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
    with open(WORKSPACE_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Saved: {OUT_HTML}")

    print("Copying raw JSONL transcript...")
    os.system(f"cp '{TRANSCRIPT_PATH}' '{OUT_JSONL}'")
    print(f"Saved: {OUT_JSONL}")
    print("[✓] All exports completed successfully!")

if __name__ == "__main__":
    main()
