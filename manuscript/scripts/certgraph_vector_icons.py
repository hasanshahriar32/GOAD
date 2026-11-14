"""Original 100-unit SVG glyphs for the CertGraph paper; no external artwork."""

INK = '#293e4e'
SYMBOLS = {
    'person': '''<circle cx="50" cy="24" r="16" fill="#e5edf3"/>
      <path d="M19 83V65q0-22 31-22t31 22v18Z" fill="#d5e5ed"/>
      <path d="m39 45 11 15 11-15M31 70v13m38-13v13" fill="none"/>
      <path d="M35 12q16-17 30 5l-12-4-13 8-6-1" fill="#a6bdcc"/>
      <rect x="58" y="65" width="13" height="8" fill="#00878b" stroke="none"/>''',
    'group': '''<g transform="translate(-4,6) scale(.65)"><use href="#person"/></g>
      <g transform="translate(42,6) scale(.65)"><use href="#person"/></g>
      <g transform="translate(17,26) scale(.68)"><use href="#person"/></g>''',
    'computer': '''<path d="M11 15h74l6 6v53H11Z" fill="#cedee8"/>
      <path d="M11 15h74v53H11Z" fill="#f7fafc"/>
      <path d="M18 23h59v36H18Z" fill="#e7f1f5"/>
      <path d="m35 35-8 7 8 7m27-14 8 7-8 7m-11-17-7 20" fill="none" stroke="#00878b"/>
      <path d="M43 74v10m15-10v10M29 86h44M10 92h80" fill="none"/>''',
    'server': '''<path d="m19 16 12-9h54v77l-12 10H19Z" fill="#cedee8"/>
      <path d="M19 16h54v78H19Z" fill="#eff5f8"/>
      <path d="m73 16 12-9M19 39h54M19 63h54M28 28h24m-24 23h24m-24 24h24" fill="none"/>
      <circle cx="62" cy="28" r="3" fill="#00878b" stroke="none"/>
      <circle cx="62" cy="51" r="3" fill="#00878b" stroke="none"/>
      <circle cx="62" cy="75" r="3" fill="#00878b" stroke="none"/>''',
    'template': '''<path d="M22 13h51v72H22Z" fill="#cedee8"/>
      <path d="M14 20h51l17 17v54H14Z" fill="#f7fafc"/>
      <path d="M65 20v17h17M26 48h43m-43 13h43m-43 13h27" fill="none"/>
      <path d="M27 44v35m16-35v35" fill="none" stroke="#7b9fb4"/>''',
    'certificate': '''<path d="M18 9h48l17 17v61H18Z" fill="#f7fafc"/>
      <path d="M66 9v17h17M29 39h40M29 49h31M29 59h19" fill="none"/>
      <path d="m60 76-5 18 10-5 8 5-2-20" fill="#e7d2a7"/>
      <circle cx="66" cy="69" r="12" fill="#d7ebe9" stroke="#00878b"/>
      <path d="m60 69 4 4 8-9" fill="none" stroke="#00878b"/>''',
    'domain': '''<path d="M15 18h70v58H15Z" fill="#eff5f8"/>
      <path d="M15 18h70v14H15Z" fill="#cedee8"/>
      <path d="M50 41v12M29 53h42M29 53v8m42-8v8M50 76v13M30 89h40" fill="none"/>
      <rect x="39" y="37" width="22" height="10" fill="#c6e5e3"/>
      <rect x="21" y="61" width="17" height="9" fill="#d5e5ed"/>
      <rect x="63" y="61" width="17" height="9" fill="#d5e5ed"/>''',
    'database': '''<path d="M16 23v55c0 18 68 18 68 0V23" fill="#cedee8"/>
      <ellipse cx="50" cy="23" rx="34" ry="13" fill="#f7fafc"/>
      <path d="M16 42c0 18 68 18 68 0M16 60c0 18 68 18 68 0" fill="none"/>
      <path d="M25 45q11 6 25 6m-25 12q11 6 25 6m-25 12q11 6 25 6" fill="none" stroke="#00878b"/>''',
    'report': '''<path d="M25 14h57v76H25Z" fill="#cedee8"/>
      <path d="M18 20h57v76H18Z" fill="#f7fafc"/>
      <path d="M35 13q0-9 11-9t11 9v8H35Z" fill="#d5e5ed"/>
      <path d="m28 39 4 4 7-9m-11 25 4 4 7-9M47 39h18M47 59h18M28 79h37" fill="none" stroke="#00878b"/>''',
    'cut': '''<circle cx="20" cy="20" r="7" fill="#d5e5ed"/>
      <circle cx="20" cy="80" r="7" fill="#d5e5ed"/>
      <circle cx="80" cy="50" r="9" fill="#d7ebe9"/>
      <path d="m26 24 18 10m14 8 14 6M26 76l46-23" fill="none"/>
      <path d="m43 28 11 16m-14-3 16-11" fill="none" stroke="#aa5943" stroke-width="4"/>''',
}


def definitions():
    return '<defs>' + ''.join(
        f'<symbol id="{name}" viewBox="0 0 100 100"><g stroke="{INK}" '
        'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">'
        f'{geometry}</g></symbol>' for name, geometry in SYMBOLS.items()) + '</defs>'
