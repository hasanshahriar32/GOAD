#!/usr/bin/env python3
import os
import re
import sys

def verify_latex():
    tex_files = []
    for root, dirs, files in os.walk('thesis_paper'):
        for f in files:
            if f.endswith('.tex'):
                tex_files.append(os.path.join(root, f))

    print(f"Checking {len(tex_files)} .tex files in thesis_paper/ ...")

    total_errors = 0
    for fpath in sorted(tex_files):
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')
        stack = []
        
        # We need to ignore lines inside lstlisting or verbatim when counting braces or commands
        in_code_block = False
        code_env = ""
        brace_depth = 0

        for line_idx, line in enumerate(lines, 1):
            line_stripped = line.strip()

            # Check code environment start/end
            if not in_code_block:
                m_start = re.search(r'\\begin\{(lstlisting|verbatim|minted)\}', line)
                if m_start:
                    in_code_block = True
                    code_env = m_start.group(1)
                    stack.append((code_env, line_idx))
                    continue
            else:
                m_end = re.search(r'\\end\{' + code_env + r'\}', line)
                if m_end:
                    in_code_block = False
                    last_env, last_line = stack.pop()
                    continue
                else:
                    # Inside code block, do not parse LaTeX commands or braces
                    continue

            # Outside code blocks, strip LaTeX comments
            line_clean = re.sub(r'(?<!\\)%.*$', '', line)

            # Check \begin and \end environments
            for m in re.finditer(r'\\(begin|end)\{([a-zA-Z0-9*]+)\}', line_clean):
                cmd, env = m.group(1), m.group(2)
                if cmd == 'begin':
                    stack.append((env, line_idx))
                else:
                    if not stack:
                        print(f"ERROR: Unmatched \\end{{{env}}} at {fpath}:{line_idx}")
                        total_errors += 1
                    else:
                        last_env, last_line = stack.pop()
                        if last_env != env:
                            print(f"ERROR: Mismatched env at {fpath}:{line_idx}: expected \\end{{{last_env}}} (from line {last_line}), got \\end{{{env}}}")
                            total_errors += 1

            # Check brace depth outside code blocks
            # remove escaped braces \{ and \}
            line_no_escaped = line_clean.replace(r'\{', '').replace(r'\}', '')
            # remove \verb|...|
            line_no_escaped = re.sub(r'\\verb(.)(.*?)\1', '', line_no_escaped)
            for char in line_no_escaped:
                if char == '{':
                    brace_depth += 1
                elif char == '}':
                    brace_depth -= 1
                    if brace_depth < 0:
                        print(f"ERROR: Extra closing brace at {fpath}:{line_idx}")
                        total_errors += 1
                        brace_depth = 0

        if brace_depth != 0:
            print(f"ERROR: Unclosed opening brace ({brace_depth} remaining) in {fpath}")
            total_errors += 1

        if stack:
            for env, l in stack:
                print(f"ERROR: Unclosed \\begin{{{env}}} at {fpath}:{l}")
                total_errors += 1

    if total_errors == 0:
        print("SUCCESS: All 21 LaTeX files passed environment pairing and syntax verification cleanly!")
        return 0
    else:
        print(f"FAILED: {total_errors} syntax/environment errors found.")
        return 1

if __name__ == '__main__':
    sys.exit(verify_latex())
