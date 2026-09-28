import re, sys, os

def latex_to_typst(text):
    # Comments
    text = re.sub(r'(?<!\\)%.*$', '', text, flags=re.MULTILINE)

    # Chapters, sections
    text = re.sub(r'\\chapter\*?\{([^}]+)\}', r'= \1', text)
    text = re.sub(r'\\section\*?\{([^}]+)\}', r'== \1', text)
    text = re.sub(r'\\subsection\*?\{([^}]+)\}', r'=== \1', text)
    text = re.sub(r'\\subsubsection\*?\{([^}]+)\}', r'==== \1', text)

    # Labels and refs
    text = re.sub(r'\\label\{([^}]+)\}', r'<\1>', text)
    text = re.sub(r'\\ref\{([^}]+)\}', r'@\1', text)
    text = re.sub(r'\\autoref\{([^}]+)\}', r'@\1', text)
    text = re.sub(r'\\pageref\{([^}]+)\}', r'@\1', text)

    # Citations: \cite{a, b} -> @a @b
    def replace_cite(m):
        keys = [k.strip() for k in m.group(1).split(',')]
        return ' '.join(f'@{k}' for k in keys if k)
    text = re.sub(r'\\cite\{([^}]+)\}', replace_cite, text)

    # Text styles
    text = re.sub(r'\\textbf\{((?:[^{}]|\{[^{}]*\})*)\}', r'*\1*', text)
    text = re.sub(r'\\textit\{((?:[^{}]|\{[^{}]*\})*)\}', r'_\1_', text)
    text = re.sub(r'\\texttt\{((?:[^{}]|\{[^{}]*\})*)\}', r'`\1`', text)
    text = re.sub(r'\\nolinkurl\{((?:[^{}]|\{[^{}]*\})*)\}', r'`\1`', text)
    text = re.sub(r'\\url\{((?:[^{}]|\{[^{}]*\})*)\}', r'`\1`', text)

    # Quotes: ``...'' -> "..."
    text = re.sub(r'``([^"]*?)\'\'', r'"\1"', text)
    text = re.sub(r'`([^"]*?)\'', r'"\1"', text)

    # Formatting cleanups
    text = text.replace(r'\%', '%')
    text = text.replace(r'\&', '&')
    text = text.replace(r'\_', '_')
    text = text.replace(r'\#', '#')
    text = text.replace(r'\$', r'\$')
    text = text.replace(r'\allowbreak', '')
    text = text.replace(r'\quad', ' ')
    text = text.replace(r'\qquad', '  ')
    text = text.replace(r'\noindent', '')
    text = text.replace(r'\clearpage', '#pagebreak()')
    text = text.replace(r'\newpage', '#pagebreak()')

    # Lists: \begin{enumerate} ... \item ... \end{enumerate}
    # Convert \item inside enumerate to + 
    lines = text.split('\n')
    out_lines = []
    in_enumerate = False
    for line in lines:
        s = line.strip()
        if '\\begin{enumerate}' in s:
            in_enumerate = True
            continue
        elif '\\end{enumerate}' in s:
            in_enumerate = False
            continue
        if in_enumerate and s.startswith(r'\item'):
            content = s[5:].strip()
            out_lines.append(f'+ {content}')
        else:
            out_lines.append(line)
    text = '\n'.join(out_lines)

    return text

if __name__ == '__main__':
    src = sys.argv[1]
    with open(src) as f:
        content = f.read()
    converted = latex_to_typst(content)
    if len(sys.argv) > 2:
        with open(sys.argv[2], 'w') as f:
            f.write(converted)
    else:
        print(converted)
