import re, sys, os, glob

def replace_macro_balanced(text, macro_name, wrapper_prefix, wrapper_suffix):
    cmd = '\\' + macro_name
    while cmd in text:
        idx = text.find(cmd)
        if idx == -1: break
        start = text.find('{', idx)
        if start == -1 or start > idx + len(cmd) + 2: break
        depth = 0
        end = -1
        for i in range(start, len(text)):
            if text[i] == '{' and (i == 0 or text[i-1] != '\\'):
                depth += 1
            elif text[i] == '}' and (i == 0 or text[i-1] != '\\'):
                depth -= 1
                if depth == 0:
                    end = i
                    break
        if end == -1: break
        inner = text[start+1:end]
        text = text[:idx] + wrapper_prefix + inner + wrapper_suffix + text[end+1:]
    return text

def extract_braced_arg(line, cmd):
    m = re.search(re.escape(cmd) + r'\s*\{', line)
    if not m:
        return None
    start = m.end() - 1
    depth = 0
    for i in range(start, len(line)):
        if line[i] == '{' and (i == 0 or line[i-1] != '\\'):
            depth += 1
        elif line[i] == '}' and (i == 0 or line[i-1] != '\\'):
            depth -= 1
            if depth == 0:
                return line[start+1:i]
    return line[start+1:]

def replace_frac(s):
    while r'\frac' in s:
        idx = s.find(r'\frac')
        if idx == -1: break
        num_start = s.find('{', idx)
        if num_start == -1: break
        depth = 0
        num_end = -1
        for i in range(num_start, len(s)):
            if s[i] == '{' and (i == 0 or s[i-1] != '\\'):
                depth += 1
            elif s[i] == '}' and (i == 0 or s[i-1] != '\\'):
                depth -= 1
                if depth == 0:
                    num_end = i
                    break
        if num_end == -1: break
        
        den_start = s.find('{', num_end)
        if den_start == -1 or den_start > num_end + 2: break
        depth = 0
        den_end = -1
        for i in range(den_start, len(s)):
            if s[i] == '{' and (i == 0 or s[i-1] != '\\'):
                depth += 1
            elif s[i] == '}' and (i == 0 or s[i-1] != '\\'):
                depth -= 1
                if depth == 0:
                    den_end = i
                    break
        if den_end == -1: break
        
        num = s[num_start+1:num_end]
        den = s[den_start+1:den_end]
        s = s[:idx] + f"({num})/({den})" + s[den_end+1:]
    return s

def replace_sqrt(s):
    while r'\sqrt' in s:
        idx = s.find(r'\sqrt')
        if idx == -1: break
        start = s.find('{', idx)
        if start == -1 or start > idx + 6: break
        depth = 0
        end = -1
        for i in range(start, len(s)):
            if s[i] == '{' and (i == 0 or s[i-1] != '\\'):
                depth += 1
            elif s[i] == '}' and (i == 0 or s[i-1] != '\\'):
                depth -= 1
                if depth == 0:
                    end = i
                    break
        if end == -1: break
        inner = s[start+1:end]
        s = s[:idx] + f"sqrt({inner})" + s[end+1:]
    return s

def convert_latex_math_to_typst(math_str):
    s = math_str
    s = re.sub(r'\\left\b', '', s)
    s = re.sub(r'\\right\b', '', s)

    # Labeled arrows \xrightarrow{label}
    s = re.sub(r'\\xrightarrow(?:\[([^\]]*)\])?\{([^}]+)\}', r'limits(arrow.r)^(\2)', s)

    # Fractions: \frac{a}{b} -> (a)/(b)
    s = replace_frac(s)

    # \sqrt{x} -> sqrt(x)
    s = replace_sqrt(s)

    # Text in math
    s = re.sub(r'\\text\{([^}]+)\}', r'"\1"', s)
    s = re.sub(r'\\operatorname\*?\{([^}]+)\}', r'op("\1")', s)
    s = re.sub(r'\\mathrm\{([^}]+)\}', r'"\1"', s)

    # Fonts
    s = re.sub(r'\\mathbb\{([A-Za-z])\}', r'bb(\1)', s)
    
    # Bold in math: commas inside bold() must be escaped as \, to avoid Typst argument split
    def rep_bold(m):
        inner = m.group(1).replace(',', r'\,')
        return f'bold({inner})'
    s = re.sub(r'\\(?:mathbf|bm)\{([^}]+)\}', rep_bold, s)
    s = re.sub(r'\\mathcal\{([A-Za-z])\}', r'cal(\1)', s)

    # Operators & relations
    replacements = [
        (r'\le', '<='),
        (r'\leq', '<='),
        (r'\ge', '>='),
        (r'\geq', '>='),
        (r'\neq', '!='),
        (r'\times', 'times'),
        (r'\cdot', 'dot'),
        (r'\dots', 'dots'),
        (r'\cdots', 'dots'),
        (r'\in', 'in'),
        (r'\notin', 'not in'),
        (r'\subset', 'subset'),
        (r'\subseteq', 'subset.eq'),
        (r'\forall', 'forall'),
        (r'\exists', 'exists'),
        (r'\infty', 'infinity'),
        (r'\rightarrow', 'arrow.r'),
        (r'\to', 'arrow.r'),
        (r'\leftarrow', 'arrow.l'),
        (r'\gets', 'arrow.l'),
        (r'\implies', '=>'),
        (r'\Rightarrow', '=>'),
        (r'\iff', '<=>'),
        (r'\sim', 'tilde'),
        (r'\approx', 'approx'),
        (r'\pm', 'plus.minus'),
        (r'\emptyset', 'emptyset'),
        (r'\mid', '|'),
        (r'\sum', 'sum'),
        (r'\prod', 'product'),
        (r'\partial', 'diff'),
        (r'\nabla', 'nabla'),
        (r'\cup', 'union'),
        (r'\cap', 'sect'),
        (r'\bigcup', 'union.big'),
        (r'\bigvee', 'or.big'),
        (r'\bigoplus', 'plus.circle.big'),
        (r'\wedge', 'and'),
        (r'\neg', 'not'),
        (r'\Delta', 'Delta'),
        (r'\Theta', 'Theta'),
        (r'\Pi', 'Pi'),
        (r'\alpha', 'alpha'),
        (r'\beta', 'beta'),
        (r'\gamma', 'gamma'),
        (r'\delta', 'delta'),
        (r'\epsilon', 'epsilon'),
        (r'\eta', 'eta'),
        (r'\theta', 'theta'),
        (r'\lambda', 'lambda'),
        (r'\mu', 'mu'),
        (r'\nu', 'nu'),
        (r'\pi', 'pi'),
        (r'\rho', 'rho'),
        (r'\sigma', 'sigma'),
        (r'\tau', 'tau'),
        (r'\phi', 'phi'),
        (r'\chi', 'chi'),
        (r'\psi', 'psi'),
        (r'\omega', 'omega'),
        (r'\rightsquigarrow', 'arrow.squiggly'),
        (r'\Leftarrow', 'arrow.l.double'),
        (r'\langle', 'angle.l'),
        (r'\rangle', 'angle.r'),
        (r'\setminus', '\\'),
        (r'\log', 'log'),
        (r'\min', 'min'),
        (r'\max', 'max'),
        (r'\exp', 'exp'),
        (r'\gg', '>>'),
        (r'\ll', '<<'),
        (r'\{', '{'),
        (r'\}', '}'),
        (r'\_', '_'),
        (r'\|', '||'),
        (r'\quad', ' '),
        (r'\qquad', '  '),
        (r'\,', ' '),
        (r'\;', ' '),
        (r'\:', ' '),
        (r'\!', ''),
    ]
    for old, new in replacements:
        s = re.sub(re.escape(old) + r'(?![a-zA-Z])', lambda m, n=new: n, s)

    # Subscripts and superscripts with braces (loop innermost-to-outermost to support nested subscripts)
    while True:
        new_s = re.sub(r'_\{([^{}]+)\}', r'_(\1)', s)
        new_s = re.sub(r'\^\{([^{}]+)\}', r'^(\1)', new_s)
        if new_s == s:
            break
        s = new_s

    # Fix variables like vu, vw in subscripts
    s = re.sub(r'_\(vu\)', '_(v u)', s)
    s = re.sub(r'_\(vw\)', '_(v w)', s)
    s = re.sub(r'_\(uv\)', '_(u v)', s)
    s = re.sub(r'\\dot\{([^}]+)\}', r'dot(\1)', s)
    s = re.sub(r'\\bar\{([^}]+)\}', r'macron(\1)', s)
    s = re.sub(r'\\hat\{([^}]+)\}', r'hat(\1)', s)
    s = re.sub(r'\\tilde\{([^}]+)\}', r'tilde(\1)', s)

    return s

def extract_balanced_braces(s, start_idx):
    depth = 0
    begin = -1
    for i in range(start_idx, len(s)):
        if s[i] == '{' and (i == 0 or s[i-1] != '\\'):
            if depth == 0:
                begin = i
            depth += 1
        elif s[i] == '}' and (i == 0 or s[i-1] != '\\'):
            depth -= 1
            if depth == 0:
                return s[begin+1:i], i + 1
    return "", len(s)

def convert_latex_table_to_typst(tab_tex):
    cap_m = re.search(r'\\caption\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}', tab_tex)
    caption = cap_m.group(1) if cap_m else "Table"
    lab_m = re.search(r'\\label\{([^}]+)\}', tab_tex)
    label = lab_m.group(1) if lab_m else None

    caption = replace_macro_balanced(caption, 'textbf', '*', '*')
    caption = replace_macro_balanced(caption, 'textit', '_', '_')
    caption = replace_macro_balanced(caption, 'texttt', '`', '`')
    caption = caption.replace(r'\%', '%').replace(r'\_', '_').replace(r'\&', '&')

    # Find \begin{tabularx} or \begin{tabular}
    m_start = re.search(r'\\begin\{(tabularx|tabular)\}', tab_tex)
    if not m_start:
        return f"/* Table: {caption} */\n"
    
    is_tabularx = m_start.group(1) == 'tabularx'
    idx = m_start.end()
    
    if is_tabularx:
        # First braced arg is width (e.g. \textwidth)
        _, idx = extract_balanced_braces(tab_tex, idx)
    
    # Skip optional [pos]
    m_opt = re.match(r'\s*\[[^\]]*\]', tab_tex[idx:])
    if m_opt:
        idx += m_opt.end()
        
    col_spec, body_start_idx = extract_balanced_braces(tab_tex, idx)
    end_tag = r'\end{' + m_start.group(1) + '}'
    end_idx = tab_tex.find(end_tag, body_start_idx)
    if end_idx == -1:
        body = tab_tex[body_start_idx:]
    else:
        body = tab_tex[body_start_idx:end_idx]

    clean_col_spec = re.sub(r'[><@]\{.*?\}', '', col_spec)
    cols = re.findall(r'[lcrX]|p\{[^}]+\}', clean_col_spec)
    num_cols = len(cols) if cols else 1
    if num_cols == 4 and 'p{' in clean_col_spec:
        typst_cols = "auto, 1.3fr, 2fr, 2fr"
    elif num_cols == 5:
        typst_cols = "1.5fr, 1fr, 1fr, 1fr, 2fr"
    else:
        typst_cols = ", ".join(["1fr"] * num_cols)

    raw_rows = body.strip().split(r'\\')
    parsed_rows = []
    for r in raw_rows:
        r = r.strip()
        r = re.sub(r'\\(hline|toprule|midrule|bottomrule)', '', r).strip()
        if not r:
            continue
        cells = [c.strip() for c in r.split('&')]
        if len(cells) == 1 and not cells[0]:
            continue
        cleaned_cells = []
        for c in cells:
            # Convert math first so math symbols don't interfere with macro replacements
            c = re.sub(r'\$(.*?)\$', lambda m: '$' + convert_latex_math_to_typst(m.group(1)) + '$', c)
            c = replace_macro_balanced(c, 'textbf', '*', '*')
            c = replace_macro_balanced(c, 'textit', '_', '_')
            c = replace_macro_balanced(c, 'texttt', '`', '`')
            c = replace_macro_balanced(c, 'nolinkurl', '`', '`')
            c = re.sub(r'\\cite\{([^}]+)\}', r'@\1', c)
            c = replace_macro_balanced(c, 'mathbf', 'bold(', ')')
            c = c.replace(r'\allowbreak', '')
            c = re.sub(r'`\s*`', '', c)
            c = c.replace(r'\%', '%').replace(r'\&', '&').replace(r'\_', '_')
            cleaned_cells.append(f'[{c}]')
        parsed_rows.append(cleaned_cells)

    if not parsed_rows:
        return ""

    # Use compact font for large taxonomy tables
    table_size = "8pt" if len(parsed_rows) > 10 else "9.5pt"
    stroke_rule = f"(x, y) => if y == 0 {{ (top: 1.2pt + luma(0), bottom: 0.8pt + luma(0)) }} else if y == 1 {{ (bottom: 0.8pt + luma(0)) }} else if y == {len(parsed_rows)} {{ (bottom: 1.2pt + luma(0)) }} else {{ none }}"

    out = f"#figure(\n  text(size: {table_size})[\n  #table(\n    columns: ({typst_cols}),\n    stroke: {stroke_rule},\n    inset: (x: 4pt, y: 3.8pt),\n"
    header_cells = ", ".join(parsed_rows[0])
    out += f"    table.header({header_cells}),\n"
    for row in parsed_rows[1:]:
        row_str = ", ".join(row)
        out += f"    {row_str},\n"
    out += f"  )\n],\n  caption: [{caption}],\n)"
    if label:
        out += f" <{label}>\n"
    else:
        out += "\n"
    return out

def format_condition(cond):
    parts = cond.split("$")
    new_parts = []
    for i, p in enumerate(parts):
        if i % 2 == 1:
            new_parts.append("$" + convert_latex_math_to_typst(p) + "$")
        else:
            p = replace_macro_balanced(p, "textbf", "*", "*")
            new_parts.append(p)
    return "".join(new_parts)

def convert_latex_to_typst(tex):
    tex = re.sub(r'(?<!\\)%.*$', '', tex, flags=re.MULTILINE)

    # Protect code listings
    listings = []
    def save_listing(m):
        opt = m.group(1) or ""
        body = m.group(2).strip()
        lang_m = re.search(r'language=([A-Za-z0-9_-]+)', opt)
        lang = lang_m.group(1).lower() if lang_m else ""
        cap_m = re.search(r'caption=\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}', opt)
        caption = cap_m.group(1) if cap_m else ""
        lab_m = re.search(r'label=([A-Za-z0-9_:-]+)', opt)
        label = lab_m.group(1) if lab_m else ""

        lbl_str = f" <{label}>" if label else ""
        if caption:
            rep = f'\n#figure(\n```{lang}\n{body}\n```,\n  caption: [{caption}],\n){lbl_str}\n'
        else:
            rep = f'\n```{lang}\n{body}\n```\n'
        idx = len(listings)
        listings.append(rep)
        return f"%%LISTING_PLACEHOLDER_{idx}%%"

    tex = re.sub(r'\\begin\{lstlisting\}(?:\[([^\]]*)\])?(.*?)\\end\{lstlisting\}', save_listing, tex, flags=re.DOTALL)

    # Tables
    def rep_tab(m):
        return convert_latex_table_to_typst(m.group(0))
    tex = re.sub(r'\\begin\{table\*?\}.*?\\end\{table\*?\}', rep_tab, tex, flags=re.DOTALL)

    # Figures
    def rep_fig(m):
        fig_body = m.group(0)
        img_m = re.search(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', fig_body)
        cap_m = re.search(r'\\caption\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}', fig_body)
        lab_m = re.search(r'\\label\{([^}]+)\}', fig_body)
        img_path = img_m.group(1) if img_m else ""
        caption = cap_m.group(1) if cap_m else ""
        label = lab_m.group(1) if lab_m else ""

        caption = replace_macro_balanced(caption, 'textbf', '*', '*')
        caption = replace_macro_balanced(caption, 'textit', '_', '_')
        caption = replace_macro_balanced(caption, 'texttt', '`', '`')
        caption = caption.replace(r'\%', '%').replace(r'\_', '_').replace(r'\&', '&')
        caption = re.sub(r'\$(.*?)\$', lambda mm: '$' + convert_latex_math_to_typst(mm.group(1)) + '$', caption)

        res = f'#figure(\n  image("{img_path}", width: 90%),\n  caption: [{caption}],\n)'
        if label:
            res += f' <{label}>\n'
        else:
            res += '\n'
        return res

    tex = re.sub(r'\\begin\{figure\*?\}.*?\\end\{figure\*?\}', rep_fig, tex, flags=re.DOTALL)

    # Headings with optional immediate label
    def rep_heading(level_prefix):
        def handler(m):
            title = m.group(1).strip()
            lab = m.group(2)
            if lab:
                return f"{level_prefix} {title} <{lab}>\n"
            return f"{level_prefix} {title}\n"
        return handler

    tex = re.sub(r'\\chapter\*?\{([^}]+)\}(?:\s*\\label\{([^}]+)\})?', rep_heading("="), tex)
    tex = re.sub(r'\\section\*?(?:\[[^\]]*\])?\{([^}]+)\}(?:\s*\\label\{([^}]+)\})?', rep_heading("=="), tex)
    tex = re.sub(r'\\subsection\*?(?:\[[^\]]*\])?\{([^}]+)\}(?:\s*\\label\{([^}]+)\})?', rep_heading("==="), tex)
    tex = re.sub(r'\\subsubsection\*?(?:\[[^\]]*\])?\{([^}]+)\}(?:\s*\\label\{([^}]+)\})?', rep_heading("===="), tex)
    tex = re.sub(r'\\paragraph\*?\{([^}]+)\}', r'*\1*', tex)

    # Theorems, Corollaries, Lemmas, Propositions (process BEFORE converting general \label)
    def rep_thm(m):
        env = m.group(1)
        opt = m.group(2) or ""
        body = m.group(3).strip()
        labs = re.findall(r'\\label\{([^}]+)\}', body)
        label = labs[0] if labs else ""
        body = re.sub(r'\\label\{[^}]+\}', '', body).strip()
        title = f"{env.capitalize()} {opt}".strip()
        body = convert_latex_math_to_typst(body)
        lbl_str = f" <{label}>" if label else ""
        supp = env.capitalize()
        return f'\n#figure(\n  block(fill: rgb("#f8fafc"), inset: 1.2em, radius: 4pt, stroke: (left: 3pt + rgb("#1e3a8a")), width: 100%)[\n#align(left)[\n    *{title}.* \\\n    {body}\n  ]\n  ],\n  caption: none,\n  kind: "{env}",\n  supplement: [{supp}],\n){lbl_str}\n'
    tex = re.sub(r'\\begin\{(theorem|corollary|lemma|definition|proposition)\}(?:\[([^\]]*)\])?(.*?)\\end\{\1\}', rep_thm, tex, flags=re.DOTALL)

    def rep_prf(m):
        body = m.group(1).strip()
        body = convert_latex_math_to_typst(body)
        return f'\n_Proof._ {body} #h(1fr) $square$\n'
    tex = re.sub(r'\\begin\{proof\}(.*?)\\end\{proof\}', rep_prf, tex, flags=re.DOTALL)

    # Labels and refs
    tex = re.sub(r'(?:Figure|Table|Section|Chapter|Equation|Theorem|Corollary|Lemma|Algorithm)[\s~]+\\ref\{([^}]+)\}', r'@\1', tex)
    tex = re.sub(r'\\autoref\{([^}]+)\}', r'@\1', tex)
    tex = re.sub(r'\\ref\{([^}]+)\}', r'@\1', tex)
    tex = re.sub(r'\\label\{([^}]+)\}', r'<\1>', tex)

    # Citations: \cite{k1, k2} -> @k1 @k2
    def replace_cite(m):
        keys = [k.strip() for k in m.group(1).split(',')]
        return ' '.join(f'@{k}' for k in keys if k)
    tex = re.sub(r'\\cite\{([^}]+)\}', replace_cite, tex)
    tex = re.sub(r'~@', ' @', tex)
    tex = re.sub(r'(@[a-zA-Z0-9_:]+)---', r'\1 --- ', tex)
    tex = re.sub(r'(@[a-zA-Z0-9_:]+)--', r'\1 -- ', tex)

    # Algorithms
    def rep_alg(m):
        alg_body = m.group(0)
        cap_m = re.search(r'\\caption\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}', alg_body)
        caption = cap_m.group(1) if cap_m else "Algorithm"
        lab_m = re.search(r'(?:\\label\{([^}]+)\}|<([a-zA-Z0-9_:-]+)>)', alg_body)
        label = (lab_m.group(1) or lab_m.group(2)) if lab_m else ""
        if lab_m:
            alg_body = alg_body[:lab_m.start()] + alg_body[lab_m.end():]
        
        alg_lines_m = re.search(r'\\begin\{algorithmic\}(?:\[\d+\])?(.*?)\\end\{algorithmic\}', alg_body, re.DOTALL)
        if alg_lines_m:
            raw_lines = alg_lines_m.group(1).strip().split('\n')
            clean_lines = []
            indent_level = 0
            for line in raw_lines:
                l = line.strip()
                if not l: continue

                # Structural keywords
                if re.search(r'^\s*\\For\b', l):
                    cond = extract_braced_arg(l, r'\For') or ""
                    cond_str = format_condition(cond)
                    clean_lines.append(f"#h({indent_level * 1.5}em) *for* {cond_str}: \\")
                    indent_level += 1
                    continue
                elif re.search(r'^\s*\\If\b', l):
                    cond = extract_braced_arg(l, r'\If') or ""
                    cond_str = format_condition(cond)
                    clean_lines.append(f"#h({indent_level * 1.5}em) *if* {cond_str}: \\")
                    indent_level += 1
                    continue
                elif re.search(r'^\s*\\While\b', l):
                    cond = extract_braced_arg(l, r'\While') or ""
                    cond_str = format_condition(cond)
                    clean_lines.append(f"#h({indent_level * 1.5}em) *while* {cond_str}: \\")
                    indent_level += 1
                    continue
                elif re.search(r'^\s*\\Else\b', l):
                    indent_level = max(0, indent_level - 1)
                    clean_lines.append(f"#h({indent_level * 1.5}em) *else:* \\")
                    indent_level += 1
                    continue
                elif re.search(r'^\s*\\(EndFor|EndIf|EndWhile)\b', l):
                    indent_level = max(0, indent_level - 1)
                    continue

                # Strip prefixes
                l = re.sub(r'^\s*\\Require\s*', '*Require:* ', l)
                l = re.sub(r'^\s*\\Ensure\s*', '*Ensure:* ', l)
                l = re.sub(r'^\s*\\State\s*', '', l)
                l = re.sub(r'^\s*\\Return\s*', '*return* ', l)
                l = re.sub(r'\\quad\s*', '  ', l)
                l = replace_macro_balanced(l, 'textbf', '*', '*')

                # Handle bare math and sets outside $...$
                parts = l.split('$')
                reconstructed = []
                for i, p in enumerate(parts):
                    if i % 2 == 1:
                        reconstructed.append('$' + convert_latex_math_to_typst(p) + '$')
                    else:
                        p = re.sub(r'\\\{.*?(?<!\\)\\\}(?:_\{[^}]+\}|_[a-zA-Z0-9]+)?', lambda mm: '$' + convert_latex_math_to_typst(mm.group(0)) + '$', p)
                        p = p.replace('<-', 'arrow.l')
                        reconstructed.append(p)
                l = ''.join(reconstructed)
                clean_lines.append(f"#h({indent_level * 1.5}em) {l} \\")
            if clean_lines and clean_lines[-1].endswith(" \\"):
                clean_lines[-1] = clean_lines[-1][:-2]
            alg_text = "\n".join(clean_lines)
        else:
            alg_text = alg_body

        lbl_str = f" <{label}>" if label else ""
        return f'\n#figure(\n  block(fill: rgb("#f8fafc"), inset: 1.2em, radius: 4pt, stroke: 1pt + rgb("#cbd5e1"), width: 100%)[\n#align(left)[\n{alg_text}\n]\n  ],\n  caption: [{caption}],\n  kind: "algorithm",\n  supplement: [Algorithm],\n){lbl_str}\n'

    tex = re.sub(r'\\begin\{algorithm\*?\}.*?\\end\{algorithm\*?\}', rep_alg, tex, flags=re.DOTALL)

    # First handle nested equations: \begin{equation} ... \begin{aligned} ... \end{aligned} ... \end{equation}
    def rep_eq_aligned(m):
        body = m.group(1).strip()
        lab = ""
        lab_m = re.search(r'\\label\{([^}]+)\}', body)
        if lab_m:
            lab = f' <{lab_m.group(1)}>'
            body = body[:lab_m.start()] + body[lab_m.end():]
        body = convert_latex_math_to_typst(body.strip())
        body = body.replace(r'\\', '\n')
        return f'$ {body} ${lab}\n'
    tex = re.sub(r'\\begin\{equation\*?\}\s*\\begin\{aligned\*?\}(.*?)\\end\{aligned\*?\}\s*\\end\{equation\*?\}', rep_eq_aligned, tex, flags=re.DOTALL)
    tex = re.sub(r'\\\[\s*\\begin\{aligned\}(.*?)\\end\{aligned\}\s*\\\]', rep_eq_aligned, tex, flags=re.DOTALL)

    # Standalone aligned or align
    def rep_disp_align(m):
        body = m.group(1).strip()
        body = convert_latex_math_to_typst(body)
        body = body.replace(r'\\', '\n')
        return f'$ {body} $\n'
    tex = re.sub(r'\\begin\{(?:align|aligned)\*?\}(.*?)\\end\{(?:align|aligned)\*?\}', rep_disp_align, tex, flags=re.DOTALL)

    # Display equations \begin{equation} ... \end{equation}
    def rep_eq(m):
        body = m.group(1).strip()
        lab = ""
        lab_m = re.search(r'\\label\{([^}]+)\}', body)
        if lab_m:
            lab = f' <{lab_m.group(1)}>'
            body = body[:lab_m.start()] + body[lab_m.end():]
        body = body.strip()
        if body.startswith('$') and body.endswith('$'):
            body = body[1:-1].strip()
        body = convert_latex_math_to_typst(body.strip())
        return f'$ {body} ${lab}\n'
    tex = re.sub(r'\\begin\{equation\*?\}(.*?)\\end\{equation\*?\}', rep_eq, tex, flags=re.DOTALL)
    tex = re.sub(r'\\\[(.*?)\\\]', lambda m: '$ ' + convert_latex_math_to_typst(m.group(1).strip()) + ' $\n', tex, flags=re.DOTALL)

    # Inline math $ ... $
    tex = re.sub(r'\$(.*?)\$', lambda m: '$' + convert_latex_math_to_typst(m.group(1)) + '$', tex)

    # Markdown **bold** to *bold*
    tex = re.sub(r'\*\*([^*]+)\*\*', r'*\1*', tex)

    # Text formatting
    tex = replace_macro_balanced(tex, 'textbf', '*', '*')
    tex = replace_macro_balanced(tex, 'textit', '_', '_')
    tex = replace_macro_balanced(tex, 'emph', '_', '_')
    tex = replace_macro_balanced(tex, 'texttt', '`', '`')
    tex = replace_macro_balanced(tex, 'nolinkurl', '`', '`')
    tex = replace_macro_balanced(tex, 'url', '`', '`')

    # Ordered lists strictly (handle nested lists from innermost to outermost)
    def rep_enum(m):
        items = re.findall(r'\\item\s*(.*?)(?=\\item|\Z)', m.group(1), re.DOTALL)
        out = "\n"
        for it in items:
            it = it.strip()
            if it:
                if '\n+' in it or '\n-' in it:
                    sub_lines = [l.strip() for l in it.split('\n') if l.strip()]
                    out += f"+ {sub_lines[0]}\n"
                    for sl in sub_lines[1:]:
                        if sl.startswith('+') or sl.startswith('-'):
                            out += f"  {sl}\n"
                        else:
                            out += f"  {sl}\n"
                else:
                    it_clean = re.sub(r'\s+', ' ', it)
                    out += f"+ {it_clean}\n"
        return out + "\n"

    while r'\begin{enumerate}' in tex:
        new_tex = re.sub(r'\\begin\{enumerate\}((?:(?!\\begin\{enumerate\}).)*?)\\end\{enumerate\}', rep_enum, tex, count=1, flags=re.DOTALL)
        if new_tex == tex:
            break
        tex = new_tex

    while r'\begin{itemize}' in tex:
        new_tex = re.sub(r'\\begin\{itemize\}((?:(?!\\begin\{itemize\}).)*?)\\end\{itemize\}', rep_enum, tex, count=1, flags=re.DOTALL)
        if new_tex == tex:
            break
        tex = new_tex

    # Cleanups
    tex = tex.replace(r'\allowbreak', '')
    tex = re.sub(r'`\s*`', '', tex)
    tex = tex.replace(r'\%', '%')
    tex = tex.replace(r'\_', '_')
    tex = tex.replace(r'\&', '&')
    tex = tex.replace(r'\#', '#')
    tex = tex.replace(r'---', '---')
    tex = tex.replace(r'--', '--')
    tex = tex.replace('``', '"').replace("''", '"')
    tex = re.sub(r'\\noindent\s*', '', tex)
    for idx, rep in enumerate(listings):
        tex = tex.replace(f"%%LISTING_PLACEHOLDER_{idx}%%", rep)

    return tex

if __name__ == "__main__":
    os.makedirs("typst_chapters", exist_ok=True)

    chapters = [
        ("chapters/ch01_introduction.tex", "typst_chapters/ch01_introduction.typ"),
        ("chapters/ch02_background_threat.tex", "typst_chapters/ch02_background_threat.typ"),
        ("chapters/ch03_formal_methodology.tex", "typst_chapters/ch03_formal_methodology.typ"),
        ("chapters/ch04_forensic_audit.tex", "typst_chapters/ch04_forensic_audit.typ"),
        ("chapters/ch05_empirical_benchmarks.tex", "typst_chapters/ch05_empirical_benchmarks.typ"),
        ("chapters/ch06_real_world_case_study.tex", "typst_chapters/ch06_real_world_case_study.typ"),
        ("chapters/ch07_robustness_scalability.tex", "typst_chapters/ch07_robustness_scalability.typ"),
        ("chapters/ch08_neuro_symbolic_hybrid.tex", "typst_chapters/ch08_neuro_symbolic_hybrid.typ"),
        ("chapters/ch09_game_theoretic_defense.tex", "typst_chapters/ch09_game_theoretic_defense.typ"),
        ("chapters/ch10_conclusion.tex", "typst_chapters/ch10_conclusion.typ"),
    ]

    for src, dst in chapters:
        print(f"Converting {src} -> {dst}...")
        with open(src) as f:
            c = f.read()
        res = convert_latex_to_typst(c)
        with open(dst, "w") as f:
            f.write(res)

    print("Converting proofs...")
    p1 = "proofs/theorem1_representation_collapse.tex"
    p2 = "proofs/theorem2_edge_blocking_nphardness.tex"
    with open(p1) as f:
        c1 = f.read()
    with open(p2) as f:
        c2 = f.read()

    # Strip redundant section tags from proof files since we create custom headings
    c1 = re.sub(r'\\section\*?(?:\[[^\]]*\])?\{[^}]+\}', '', c1)
    c1 = re.sub(r'\\label\{proof:theorem1\}', '', c1)
    c2 = re.sub(r'\\section\*?(?:\[[^\]]*\])?\{[^}]+\}', '', c2)
    c2 = re.sub(r'\\label\{proof:theorem2\}', '', c2)

    app_content = "= Formal Mathematical Proofs <app:proofs>\n\n"
    app_content += "== Proof of Theorem 1: Intrinsic Attribute Preservation and Non-Vanishing Gradient Bounds <proof:theorem1>\n\n"
    app_content += convert_latex_to_typst(c1).strip()
    app_content += "\n\n#pagebreak()\n\n"
    app_content += "== Proof of Theorem 2: NP-Hardness of Multi-Principal Access Interdiction in Enterprise Identity Graphs <proof:theorem2>\n\n"
    app_content += convert_latex_to_typst(c2).strip()

    with open("typst_chapters/app_proofs.typ", "w") as f:
        f.write(app_content)
    print("Done converting proofs.")
