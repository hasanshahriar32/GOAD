"""Render CertGraph paper figures as editable SVG, vector PDF and PNG.

Run with the project's Python environment; requires matplotlib and rsvg-convert.
Diagrams are explanatory schematics. Numerical marks use frozen saved results.
"""
from __future__ import annotations

from html import escape
import hashlib
import json
import os
from pathlib import Path
import subprocess

from certgraph_vector_icons import definitions

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'manuscript/figures'
DATA = ROOT / 'thesis_research/results/lineage_constraints/2026-11-10/interdiction_recheck_statistics/results.json'
INK, MUTED, BLUE, TEAL, GOLD, RUST = '#293e4e', '#637786', '#386e96', '#00878b', '#a67529', '#aa5943'
GRAY, BORDER = '#8595a1', '#cbd8e1'
EPOCH = '1794614400'


class Drawing:
    def __init__(self, width, height, inches, title, description):
        self.width, self.height, self.inches = width, height, inches
        self.title, self.description, self.parts = title, description, []

    def add(self, value):
        self.parts.append(value)

    def text(self, x, y, value, size=20, color=INK, weight=400, anchor='start'):
        self.add(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" '
                 f'font-weight="{weight}" text-anchor="{anchor}">{escape(value)}</text>')

    def rect(self, x, y, width, height, fill='#f7fafc', stroke=BORDER, dashed=False, radius=3):
        dash = ' stroke-dasharray="7 5"' if dashed else ''
        self.add(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{radius}" '
                 f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"{dash}/>')

    def icon(self, name, x, y, size=75):
        self.add(f'<use href="#{name}" x="{x}" y="{y}" width="{size}" height="{size}"/>')

    def route(self, points, color=GRAY, dashed=False, arrow=True, width=2.5):
        coords = ' '.join(f'{x},{y}' for x, y in points)
        dash = ' stroke-dasharray="7 5"' if dashed else ''
        end = f' marker-end="url(#arrow{color[1:]})"' if arrow else ''
        self.add(f'<polyline points="{coords}" fill="none" stroke="{color}" '
                 f'stroke-width="{width}" stroke-linejoin="round"{dash}{end}/>')

    def circle(self, x, y, radius=12, fill='#e7f0f5', color=BLUE):
        self.add(f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{fill}" stroke="{color}" stroke-width="2"/>')

    def section(self, x, y, letter, label, color=BLUE):
        self.text(x, y, letter, 23, color, 700)
        self.text(x + 28, y, label, 22, INK, 700)

    def svg(self):
        arrows = ''.join(
            f'<marker id="arrow{c[1:]}" viewBox="0 0 12 10" refX="10" refY="5" '
            f'markerWidth="7" markerHeight="6" orient="auto-start-reverse">'
            f'<path d="M1 1 10 5 1 9" fill="none" stroke="{c}" stroke-width="1.5"/></marker>'
            for c in (INK, MUTED, BLUE, TEAL, GOLD, RUST, GRAY))
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.inches}in" '
                f'height="{self.inches*self.height/self.width:.6f}in" viewBox="0 0 {self.width} {self.height}" '
                'role="img" aria-labelledby="title desc">'
                f'<title id="title">{escape(self.title)}</title><desc id="desc">{escape(self.description)}</desc>'
                + definitions() + '<defs>' + arrows + '</defs>'
                f'<rect width="{self.width}" height="{self.height}" fill="white"/>'
                '<g font-family="Noto Sans,sans-serif">' + ''.join(self.parts) + '</g></svg>\n')


def schema():
    d = Drawing(600, 590, 3.5, 'Identity and certificate-services multigraph',
                'Schematic topology illustrating six formal node types, membership and PKI relations, '
                'and a separate permission relation key. This is not an empirical graph instance.')
    d.text(12, 24, 'Identity and PKI relations', 22, weight=700)
    d.text(588, 24, 'Schematic', 18, MUTED, anchor='end')
    d.route([(103, 104), (258, 104)], BLUE)
    d.text(180, 89, 'MemberOf', 19, BLUE, anchor='middle')
    d.route([(283, 66), (283, 45), (333, 45), (333, 66)], BLUE)
    d.route([(300, 170), (300, 281)], TEAL)
    d.text(312, 221, 'Enroll', 19, TEAL)
    d.route([(104, 328), (257, 328)], TEAL)
    d.text(180, 311, 'Enroll', 19, TEAL, anchor='middle')
    d.route([(343, 306), (484, 306)], BLUE)
    d.text(413, 289, 'IssuedBy', 19, BLUE, anchor='middle')
    d.route([(484, 356), (343, 356)], TEAL)
    d.text(414, 412, 'EnablesEnrollment', 18, TEAL, anchor='middle')
    d.route([(529, 281), (529, 170)], GOLD)
    d.text(513, 210, 'TrustedFor', 18, GOLD, anchor='end')
    d.text(513, 234, 'NTAuth', 18, GOLD, anchor='end')
    d.route([(64, 170), (64, 224), (228, 224), (275, 281)], RUST, dashed=True)
    d.text(80, 210, 'ACL permission', 18, RUST)
    for icon, x, y, label in [
        ('person', 64, 105, 'User'), ('group', 300, 105, 'Group'),
        ('domain', 529, 105, 'Domain'), ('computer', 64, 330, 'Computer'),
        ('template', 300, 330, 'CertificateTemplate'), ('server', 529, 330, 'EnterpriseCA')]:
        d.icon(icon, x-37, y-43, 74)
        d.text(x, y+57, label, 18.5, weight=600, anchor='middle')
    d.route([(12, 435), (588, 435)], BORDER, arrow=False, width=1.3)
    d.text(12, 463, 'Permission relation vocabulary', 20, weight=700)
    d.route([(13, 487), (49, 487)], RUST, dashed=True)
    d.text(61, 493, 'GenericAll · GenericWrite · WriteOwner', 18)
    d.text(61, 522, 'WriteDacl · ExtendedRight', 18)
    d.text(12, 563, 'Six node types · ten relation types in the formal definition', 18, MUTED)
    return d


def heads(d, x, y):
    for i, c in enumerate((BLUE, TEAL, BLUE, TEAL)):
        d.rect(x+i*7, y-i*7, 48, 96, '#eef5f8', c)
    for yy in (y+17, y+39, y+61):
        d.circle(x+37, yy, 4, '#d5e5ed', BLUE)


def architecture():
    d = Drawing(1200, 600, 7.16, 'CertGraph relational attention and bilinear gating',
                'Typed graph features pass through two four-head relational attention layers and a template '
                'readout. An inset explains the bilinear message gate and self skip. Learned scores '
                'are separate from symbolic authorization checks.')
    d.section(18, 30, 'A', 'Typed graph')
    d.section(390, 30, 'B', 'Two-layer relational attention')
    d.section(973, 30, 'C', 'Readout')
    d.rect(13, 51, 306, 273, '#fbfcfd', dashed=True)
    for a, b in [((97, 110), (193, 110)), ((224, 160), (224, 197)), ((101, 240), (193, 240))]:
        d.route([a, b], BLUE)
    for icon, x, y, label in [('person', 37, 72, 'user'), ('group', 194, 72, 'group'),
                             ('server', 37, 198, 'CA'), ('template', 194, 198, 'template')]:
        d.icon(icon, x, y, 64)
        d.text(x+32, y+83, label, 19, anchor='middle')
    d.text(166, 306, 'Illustrative input', 18, MUTED, anchor='middle')
    d.route([(324, 185), (389, 185)], GRAY)
    d.text(353, 156, 'encode', 18, MUTED, anchor='middle')
    for y in (130, 185, 240):
        d.circle(420, y, 13)
        d.route([(434, y), (490, 185)], BLUE)
    heads(d, 502, 142)
    d.route([(572, 185), (626, 185)], BLUE)
    d.circle(645, 185, 15, '#d7ebe9', TEAL)
    d.route([(662, 185), (715, 185)], BLUE)
    heads(d, 728, 142)
    d.route([(799, 185), (850, 185)], BLUE)
    d.circle(868, 185, 15, '#d7ebe9', TEAL)
    d.route([(420, 112), (420, 83), (620, 83), (620, 150), (635, 170)], TEAL, dashed=True)
    d.route([(658, 176), (681, 154), (681, 83), (868, 83), (868, 167)], TEAL, dashed=True)
    d.text(646, 69, 'Gated self-skips', 19, TEAL, anchor='middle')
    d.text(420, 281, 'h⁽⁰⁾', 22, anchor='middle')
    d.text(537, 281, 'Layer 1', 20, weight=600, anchor='middle')
    d.text(763, 281, 'Layer 2', 20, weight=600, anchor='middle')
    d.text(537, 309, '4 heads', 19, MUTED, anchor='middle')
    d.text(763, 309, '4 heads', 19, MUTED, anchor='middle')
    d.route([(885, 185), (932, 185), (932, 136), (972, 136)], GRAY)
    for i in range(6):
        d.rect(983+i*17, 101, 11, 72, '#d7ebe9' if i%2 else '#d5e5ed', 'none', radius=0)
    d.text(1036, 213, 'Template state', 19, anchor='middle')
    d.route([(1036, 229), (1036, 256)], GRAY)
    d.rect(975, 269, 187, 49, '#eef5f8', BLUE)
    d.text(1068, 301, 'Binary class scores', 19, anchor='middle')
    d.text(1167, 350, 'Literal matched ESC1 study', 19, MUTED, anchor='end')
    d.rect(14, 378, 1172, 208, '#f8fbfc', BORDER)
    d.section(31, 410, 'D', 'Bilinear message mechanism', TEAL)
    d.text(50, 469, 'Source hᵤ', 21, weight=600)
    d.text(50, 551, 'Target hᵥ', 21, weight=600)
    d.route([(170, 462), (224, 462)], BLUE)
    d.rect(231, 437, 164, 46, '#eaf1f6', BLUE)
    d.text(313, 467, 'Relation map Wᵣ', 20, anchor='middle')
    d.route([(398, 460), (646, 460)], BLUE)
    d.route([(188, 460), (188, 514), (442, 514)], TEAL)
    d.route([(171, 543), (413, 543), (413, 536), (442, 536)], TEAL)
    d.rect(449, 494, 198, 63, '#e6f2ef', TEAL)
    d.text(548, 520, 'gᵤᵥ = sigmoid', 20, TEAL, 600, 'middle')
    d.text(548, 546, '(hᵤᵀ Wg hᵥ + b)', 20, TEAL, anchor='middle')
    d.route([(647, 525), (680, 525), (680, 480)], TEAL)
    d.circle(680, 460, 19, '#e6f2ef', TEAL)
    d.text(680, 468, '×', 28, TEAL, anchor='middle')
    d.route([(701, 460), (750, 460)], BLUE)
    d.text(766, 468, 'Attention-weighted aggregation', 20, weight=600)
    d.text(766, 503, 'plus gated self-skip', 20, TEAL)
    d.text(766, 551, 'Authorization is checked separately.', 19, MUTED)
    return d


def pipeline():
    d = Drawing(1200, 655, 7.16, 'CIPG evidence collection and revisable certificate lineage',
                'Directory, CA and KDC observations enter retained evidence independently of neural scores. '
                'Issuer-scoped identifiers support revisable linkage and timing explanations. Investigation '
                'and budgeted remediation are separate logical outputs, not automatic LDAP actuation.')
    d.section(18, 30, 'A', 'Audit sources')
    d.section(366, 30, 'B', 'Issuer-scoped certificate lineage')
    d.section(959, 30, 'C', 'Analysis outputs')
    for icon, y, title, first, second in [
        ('domain', 81, 'Directory changes', '5136 · object / actor', 'attribute / operation / time'),
        ('server', 260, 'CA issuance + export', '4887 · request / requester', 'issuer / certificate identifiers'),
        ('server', 438, 'KDC authentication', '4768 · target / outcome', 'issuer / serial / thumbprint')]:
        d.icon(icon, 16, y, 77)
        d.text(104, y+21, title, 20, weight=600)
        d.text(104, y+53, first, 18.5, MUTED)
        d.text(18, y+107, second, 18.5, MUTED)
    d.route([(322, 138), (342, 138), (342, 321), (367, 321)])
    d.route([(322, 317), (367, 341)])
    d.route([(322, 495), (351, 495), (351, 366), (367, 366)])
    d.icon('database', 367, 293, 91)
    d.text(412, 413, 'Retain', 19, weight=600, anchor='middle')
    d.text(412, 440, 'observations', 18, MUTED, anchor='middle')
    d.route([(457, 340), (494, 340)], GRAY)
    d.rect(504, 69, 419, 443, '#fbfcfd', BORDER, dashed=True)
    d.text(525, 102, 'Compatible candidates', 22, weight=600)
    d.icon('certificate', 526, 122, 77)
    d.text(620, 149, 'Issuer + request', 20, weight=600)
    d.text(620, 180, 'serial / thumbprint / SKID', 18, MUTED)
    d.route([(565, 207), (565, 243)], TEAL)
    d.text(591, 233, 'agree on shared identifiers', 18, TEAL)
    d.icon('certificate', 526, 256, 77)
    d.text(620, 280, 'Certificate use', 20, weight=600)
    d.text(620, 311, 'target + authentication result', 18, MUTED)
    d.route([(565, 341), (565, 368)], GOLD)
    d.text(592, 359, 'check justified time bounds', 18, GOLD)
    d.rect(526, 385, 374, 103, '#eef5f8', BORDER)
    d.text(544, 415, 'Mutation context', 20, weight=600)
    d.text(544, 446, 'mutator ≠ requester may be valid', 18, MUTED)
    d.text(544, 475, 'rollback does not erase issuance', 18, MUTED)
    d.route([(924, 225), (945, 225)], TEAL)
    d.icon('report', 987, 89, 86)
    d.text(949, 201, 'Investigation', 21, weight=600)
    d.text(949, 255, 'Possible / definite overlap', 18.5)
    d.text(949, 284, 'Conflicting evidence', 18.5)
    d.text(949, 313, 'Authentication outcome', 18.5)
    d.route([(924, 436), (945, 436)], RUST, dashed=True)
    d.icon('cut', 987, 353, 86)
    d.text(949, 474, 'Remediation planning', 20, weight=600)
    d.text(949, 508, 'Blockable permissions', 18.5)
    d.text(949, 537, 'Disruption budget', 18.5)
    d.route([(887, 513), (887, 564), (480, 564), (480, 154), (505, 154)], TEAL, dashed=True)
    d.text(679, 551, 'Late evidence → revise linkage', 19, TEAL, anchor='middle')
    d.route([(18, 589), (1182, 589)], BORDER, arrow=False, width=1.3)
    d.text(18, 619, 'Collection is independent of neural predictions.', 20, weight=600)
    d.text(18, 647, 'Raw-source integrity, retained evidence and justified time bounds remain explicit assumptions.', 18.5, MUTED)
    return d


def export_drawing(d, name):
    source = OUT / f'{name}.svg'
    source.write_text(d.svg())
    env = dict(os.environ, SOURCE_DATE_EPOCH=EPOCH)
    subprocess.run(['rsvg-convert', '--format=pdf1.5', '--output', str(OUT/f'{name}.pdf'), str(source)], check=True, env=env)
    subprocess.run(['rsvg-convert', '--format=png', '--width', str(round(d.inches*300)),
                    '--output', str(OUT/f'{name}.png'), str(source)], check=True, env=env)


def results_chart():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MultipleLocator
    rows = json.loads(DATA.read_text())['rows']
    assert [r['budget'] for r in rows] == [6, 12, 18, 24]
    assert all(r['graphs'] == 30 for r in rows)
    for r in rows:
        assert abs(r['corrected_mean_pct'] - r['greedy_mean_pct'] - r['mean_gain_percentage_points']) < 1e-10
    plt.rcParams.update({'font.family': 'Noto Sans', 'font.size': 8, 'pdf.fonttype': 42,
                         'svg.fonttype': 'none', 'axes.labelcolor': INK, 'text.color': INK,
                         'xtick.color': MUTED, 'ytick.color': MUTED, 'axes.edgecolor': BORDER,
                         'axes.linewidth': .7})
    fig, (ax, gain) = plt.subplots(2, 1, figsize=(3.5, 3.55),
                                 gridspec_kw={'height_ratios': [2.2, 1], 'hspace': .65})
    fig.subplots_adjust(left=.17, right=.97, bottom=.13, top=.88)
    budgets = [r['budget'] for r in rows]
    for label, mean, sd, marker, color, shift in [
        ('Static greedy', 'greedy_mean_pct', 'greedy_population_sd_pct', 'o', BLUE, -.18),
        ('Adaptive sequential', 'corrected_mean_pct', 'corrected_population_sd_pct', 's', TEAL, .18)]:
        ax.errorbar([b+shift for b in budgets], [r[mean] for r in rows], yerr=[r[sd] for r in rows],
                    fmt=marker+'-', color=color, capsize=2.5, linewidth=1.2, elinewidth=.8,
                    markersize=4, markeredgecolor='white', markeredgewidth=.4, label=label, zorder=3)
    ax.set(xlim=(4, 26), ylim=(48, 115), xticks=budgets, ylabel='Disconnected pairs (%)')
    ax.yaxis.set_major_locator(MultipleLocator(20))
    ax.axhline(100, color=GRAY, linestyle=(0, (2, 3)), linewidth=.8)
    ax.grid(axis='y', color='#e8eef2', linewidth=.65)
    ax.set_axisbelow(True)
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(length=3, width=.6)
    fig.legend(loc='upper center', bbox_to_anchor=(.55, 1.0), fontsize=7.5,
               frameon=False, ncol=1, labelspacing=.4)
    ax.text(-.18, 1.04, '(a)', transform=ax.transAxes, weight='bold')
    values = [r['mean_gain_percentage_points'] for r in rows]
    gain.bar(budgets, values, width=2.0, color=TEAL, alpha=.9, zorder=3)
    for b, value in zip(budgets, values):
        gain.text(b, value+.45, f'+{value:.2f}', ha='center', va='bottom', fontsize=7.5)
    gain.set(xlim=(4, 26), ylim=(0, 12.8), xticks=budgets, yticks=[0, 5, 10],
             xlabel='Assigned disruption budget', ylabel='Gain (pp)')
    gain.grid(axis='y', color='#e8eef2', linewidth=.65)
    gain.set_axisbelow(True)
    gain.spines[['top', 'right']].set_visible(False)
    gain.tick_params(length=3, width=.6)
    gain.text(-.18, 1.06, '(b)', transform=gain.transAxes, weight='bold')
    name = OUT / 'verified_interdiction_results'
    fig.savefig(name.with_suffix('.pdf'), metadata={'CreationDate': None, 'ModDate': None})
    with matplotlib.rc_context({'svg.hashsalt': 'certgraph-20261114'}):
        fig.savefig(name.with_suffix('.svg'), metadata={'Date': None})
    fig.savefig(name.with_suffix('.png'), dpi=300)
    plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True)
    names = ['verified_identity_schema', 'certgraph_learning_architecture',
             'verified_evidence_pipeline', 'verified_interdiction_results']
    for make, name in zip((schema, architecture, pipeline), names):
        export_drawing(make(), name)
    results_chart()
    sources = [Path(__file__), Path(__file__).with_name('certgraph_vector_icons.py'), DATA,
               ROOT/'thesis_research/src/lineage_constraints/literal_bilinear.py']
    sources += [ROOT/'manuscript/sections'/name for name in (
        '02_threat_model_and_blindspots.tex', '03_certgraph_architecture.tex',
        '04_cipg_provenance_automaton.tex', '06_empirical_evaluation.tex')]
    manifest = {'scope': 'Illustrative formal diagrams and saved synthetic-graph measurements; no new experiments.',
                'authoritative_source': str(Path(__file__).relative_to(ROOT)),
                'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
                'output_sha256': {f'{name}.{ext}': hashlib.sha256((OUT/f'{name}.{ext}').read_bytes()).hexdigest()
                                  for name in names for ext in ('svg', 'pdf', 'png')}}
    (OUT/'verified_figures_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print('Rendered four figures: editable SVG, vector PDF, and 300 dpi PNG.')


if __name__ == '__main__':
    main()
