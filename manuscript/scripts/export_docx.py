#!/usr/bin/env python3
"""Build an editable Word manuscript from LaTeX, with native Office equations.
Requirements: tectonic, pypandoc-binary, python-docx, lxml, pymupdf.
Run from any directory. --aux may reuse a previously compiled main.aux for layout work.
"""
from pathlib import Path
import argparse, collections, copy, hashlib, json, re, subprocess, tempfile, zipfile, uuid
import pypandoc
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from lxml import etree
ROOT=Path(__file__).resolve().parents[1]
SUPPORT=ROOT/'docx'
FONT='TeX Gyre TermesX'
MATHFONT='TeX Gyre Termes Math'
BLUE=RGBColor(10,35,75)
WIDTH=451.28

def group(s,pos):
 while s[pos].isspace():pos+=1
 assert s[pos]=='{',s[pos:pos+80]
 start=pos+1;depth=1;pos+=1
 while depth:
  if s[pos]=='\\':pos+=2;continue
  if s[pos]=='{':depth+=1
  if s[pos]=='}':depth-=1
  pos+=1
 return s[start:pos-1],pos

def xml(tag,**attrs):
 e=OxmlElement(tag)
 for k,v in attrs.items():e.set(qn('w:'+k),str(v))
 return e

def content_text(o):
 if isinstance(o,list):return ''.join(content_text(x) for x in o)
 if not isinstance(o,dict):return ''
 if o.get('t')=='Str':return o['c']
 if o.get('t') in ('Space','SoftBreak','LineBreak'):return ' '
 if o.get('t')=='Math':return o['c'][1]
 if o.get('t')=='Link':return content_text(o['c'][1])
 if o.get('t')=='Cite':return content_text(o['c'][1])
 return content_text(o.get('c',[]))

def style_run(run,size=None,bold=None,italic=None,color=None):
 run.font.name=FONT
 if size is not None:run.font.size=Pt(round(size*2)/2)
 if bold is not None:run.bold=bold
 if italic is not None:run.italic=italic
 if color is not None:run.font.color.rgb=color

def borders(table,booktabs=False):
 pr=table._tbl.tblPr
 for e in list(pr):
  if e.tag==qn('w:tblBorders'):pr.remove(e)
 b=xml('w:tblBorders')
 for side in ('top','bottom','left','right','insideH','insideV'):
  b.append(xml('w:'+side,val='single' if booktabs and side in ('top','bottom') else 'nil',sz=8,color='000000'))
 pr.append(b)

def preprocess(aux,sources):
 labels=dict(re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]+)\}',aux.read_text()))
 def flatten(path):
  sources[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
  return re.sub(r'\\input\{([^}]+)\}',lambda m:flatten(ROOT/(m[1] if m[1].endswith('.tex') else m[1]+'.tex')),path.read_text())
 s=flatten(ROOT/'main.tex')
 while '\\resizebox' in s:
  start=s.index('\\resizebox');pos=start+10
  _,pos=group(s,pos);_,pos=group(s,pos);body,pos=group(s,pos)
  s=s[:start]+body+s[pos:]
 def ref(m):
  val=labels[m[2]]
  return '('+val+')' if m[1]=='eqref' else val
 s=re.sub(r'\\(eqref|ref)\{([^}]+)\}',ref,s)
 section=0;counts=collections.Counter()
 def theorem(m):
  nonlocal section
  if m[0]=='\\section{':section+=1;counts.clear();return m[0]
  kind,title=m[1],m[2];counts[kind]+=1
  return '\\par\\noindent\\textbf{'+kind.title()+f' {section}.{counts[kind]}'+(' ('+title+')' if title else '')+'.} '
 s=re.sub(r'\\section\{|\\begin\{(definition|theorem|lemma|proposition|corollary|invariant|remark)\}(?:\[([^\]]*)\])?',theorem,s)
 s=re.sub(r'\\end\{(?:definition|theorem|lemma|proposition|corollary|invariant|remark)\}',r'\\par',s)
 def algorithm(m):
  body=m[1];cap=re.search(r'\\caption\{([^}]+)\}',body)[1]
  body=body.split('\\begin{algorithmic}[1]')[1].split('\\end{algorithmic}')[0]
  lines=['\\par\\textbf{Algorithm 1: '+cap+'}\\par']
  depth=0;number=0
  for line in body.splitlines():
   line=line.strip()
   if not line:continue
   match=re.match(r'\\(Require|For|If|ElsIf|State|EndIf|EndFor)\b',line)
   key=match[1];rest=line[match.end():].strip()
   if key in ('For','If','ElsIf'):rest,_=group(rest,0)
   if key in ('EndFor','EndIf','ElsIf'):depth-=1
   keyword={'Require':'Require:','For':'for','If':'if','ElsIf':'else if','State':'','EndIf':'end if','EndFor':'end for'}[key]
   number+=int(key!='Require')
   if key in ('If','ElsIf'):rest+=' \\textbf{then}'
   if key=='For':rest+=' \\textbf{do}'
   lines.append('\\par DOCXALG'+str(depth)+'X'+str(number)+'X '+('\\textbf{'+keyword+'} ' if keyword else '')+rest+'\\par')
   if key in ('For','If','ElsIf'):depth+=1
  return '\n'.join(lines)
 s=re.sub(r'\\begin\{algorithm\}(?:\[[^\]]*\])?(.*?)\\end\{algorithm\}',algorithm,s,flags=re.S)
 caps=collections.Counter()
 def caption(m):
  kind,body=m[1],m[2];caps[kind]+=1
  prefix={'figure':'Figure','table':'Table','lstlisting':'Listing'}[kind]+f' {caps[kind]}: '
  if kind=='lstlisting':body=body.replace('caption={','caption={'+prefix,1)
  else:body=body.replace('\\caption{','\\caption{'+prefix,1)
  return '\\begin{'+kind+'}'+body+'\\end{'+kind+'}'
 s=re.sub(r'\\begin\{(figure|table|lstlisting)\}(.*?)\\end\{\1\}',caption,s,flags=re.S)
 # Retain each numbered equation as a separate editable object and number.
 equation=0
 def equations(m):
  nonlocal equation
  kind,body=m[1],m[2]
  rows=re.split(r'\\\\(?:\[[^\]]*\])?',body) if kind=='align' else [body]
  out=[]
  pending=''
  for row in rows:
   row=re.sub(r'\\label\{[^}]+\}','',row).strip()
   if not row:continue
   if '\\nonumber' in row or '\\notag' in row:
    pending+=re.sub(r'\\(?:nonumber|notag)','',row)+' \\\\ '
    continue
   equation+=1
   formula=pending+row;pending=''
   # The source's longest expressions exceed even the PDF page width.
   # Keep all their content editable and visible by using native multi-line math.
   if '\\begin{cases}' in formula:
    def wrap_case(m):
     left=m[1].strip()
     return '& \\begin{gathered}'+left+' \\\\ \\text{('+m[2]+')}\\end{gathered}'
    formula=re.sub(r'&([^&]*?)\\text\{ \(([^}]+)\)\}',wrap_case,formula)
   if ', \\quad \\text{where} \\quad' in formula:
    formula=formula.replace(', \\quad \\text{where} \\quad',', \\\\ \\text{where} \\quad')
   if equation==31:
    formula=formula.replace(' = \\sum',' = \\\\ \\sum',1)

   if '\\begin{cases}' not in formula:
    formula=formula.replace('&','')
    if '\\\\' in formula:formula='\\begin{gathered}'+formula+'\\end{gathered}'
   out.append('\\par\\begin{equation*}'+formula+'\\end{equation*}\\par DOCXEQ'+str(equation)+'X\\par')
  return '\n'.join(out)
 s=re.sub(r'\\begin\{(equation|align)\}(.*?)\\end\{\1\}',equations,s,flags=re.S)
 s=s.replace('\\setminus','\\smallsetminus')
 return s,equation

def transform(blocks):
 result=[];i=0
 while i<len(blocks):
  b=blocks[i]
  if b['t']=='Header' and b['c'][0]>=4:
   inlines=[{'t':'Strong','c':b['c'][2]}]
   if i+1<len(blocks) and blocks[i+1]['t']=='Para':
    inlines += [{'t':'Space'}]+blocks[i+1]['c'];i+=1
   b={'t':'Div','c':[['',[],[['custom-style','Run-in Heading']]],[{'t':'Para','c':inlines}]]}
  elif b['t']=='Div':b['c'][1]=transform(b['c'][1])
  result.append(b);i+=1
 return result

def postprocess(raw,output,equations):
 d=Document(raw)
 for sec in d.sections:
  sec.page_width=Pt(595.28);sec.page_height=Pt(841.89)
  sec.top_margin=sec.bottom_margin=sec.left_margin=sec.right_margin=Pt(72)
  sec.header_distance=Pt(36);sec.footer_distance=Pt(36)
  sec.different_first_page_header_footer=True
  header=sec.header.paragraphs[0]
  header.paragraph_format.space_after=Pt(0)
  header.paragraph_format.tab_stops.add_tab_stop(Pt(WIDTH),2)
  r=header.add_run('CertGraph: Cryptographic Invariant Provenance & Gated Multigraph Interdiction');style_run(r,9.96,italic=True)
  header.add_run('\t');field=xml('w:fldSimple',instr='PAGE');header._p.append(field)
  pp=header._p.get_or_add_pPr();pb=xml('w:pBdr');pb.append(xml('w:bottom',val='single',sz=4,space=6));pp.append(pb)
  fp=sec.first_page_footer.paragraphs[0];fp.alignment=WD_ALIGN_PARAGRAPH.CENTER;fp._p.append(xml('w:fldSimple',instr='PAGE'))
 # Ensure native Office math uses a serif OpenType math font.
 settings=d.settings.element
 mp=settings.find(qn('m:mathPr'))
 if mp is None:mp=OxmlElement('m:mathPr');settings.append(mp)
 mf=OxmlElement('m:mathFont');mf.set(qn('m:val'),MATHFONT);mp.append(mf)
 for name in ('Normal','Body Text','First Paragraph','Compact'):
  st=d.styles[name];st.font.name=FONT;st.font.size=Pt(11);st.font.color.rgb=RGBColor(0,0,0)
  f=st.paragraph_format;f.line_spacing=Pt(15.61);f.space_before=Pt(0);f.space_after=Pt(0);f.first_line_indent=Pt(10.91)
  f.widow_control=True;f.line_spacing_rule=WD_LINE_SPACING.AT_LEAST
 for name in ('Verbatim Char','VerbatimChar'):
  if name in d.styles:d.styles[name].font.name='Latin Modern Mono'
 # Match actual PDF spacing, rather than generic Word heading defaults.
 for p in d.paragraphs:
  style=p.style.name;txt=p.text.strip();pf=p.paragraph_format
  if style in ('Normal','Body Text','First Paragraph','Compact'):
   p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
   pf.space_before=Pt(0);pf.space_after=Pt(0);pf.line_spacing=Pt(15.61)
   pf.first_line_indent=Pt(0) if style=='First Paragraph' else Pt(10.91)
   pf.line_spacing_rule=WD_LINE_SPACING.AT_LEAST
  if style=='Title':
   p.alignment=WD_ALIGN_PARAGRAPH.CENTER;pf.space_before=Pt(39);pf.space_after=Pt(12)
   pf.line_spacing=Pt(25.2);pf.first_line_indent=Pt(0)
   # Match the three title lines of the compiled PDF.
   p.clear()
   for i,line in enumerate(('CertGraph: Cryptographic Invariant Provenance and Multiplicative','Bilinear Gating for Active Directory Certificate Services Escalation','Interdiction')):
    if i:p.add_run().add_break()
    style_run(p.add_run(line),14.35,bold=True)
  elif style=='Author':
   p.alignment=WD_ALIGN_PARAGRAPH.CENTER;pf.first_line_indent=Pt(0);pf.space_after=Pt(12);pf.line_spacing=Pt(19)
   for r in p.runs:style_run(r,9.96)
   # Author names have their own larger baseline in the LaTeX title block.
   first=True
   for r in p.runs:
    if r.text==' ':r.text='\u2003'
   for r in p.runs:
    if 'Department' in r.text:first=False
    if first and r.text.strip():r.font.size=Pt(12)
  elif style=='Date':
   p.alignment=WD_ALIGN_PARAGRAPH.CENTER;pf.space_after=Pt(27);pf.first_line_indent=Pt(0)
   for r in p.runs:style_run(r,11.96)
  elif style=='Abstract Title':
   p.alignment=WD_ALIGN_PARAGRAPH.CENTER;pf.space_before=Pt(0);pf.space_after=Pt(8);pf.first_line_indent=Pt(0)
   for r in p.runs:style_run(r,9.96,bold=True)
  elif style=='Abstract':
   p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY;pf.left_indent=pf.right_indent=Pt(27.3);pf.first_line_indent=Pt(0)
   pf.line_spacing=Pt(13.74);pf.space_after=Pt(20)
   for r in p.runs:
    style_run(r,9.96);r._r.get_or_add_rPr().append(xml('w:w',val=98))
  elif style.startswith('Heading'):
   level=int(style.split()[-1]);pf.first_line_indent=Pt(0);pf.keep_with_next=True;pf.keep_together=True
   pf.space_before=Pt(20 if level==1 else 14);pf.space_after=Pt(10 if level==1 else 7)
   pf.line_spacing=Pt(14 if level==1 else 13);p.alignment=WD_ALIGN_PARAGRAPH.LEFT
   for r in p.runs:style_run(r,11.96 if level==1 else 10.91,bold=level<=2,italic=level==3,color=BLUE)
   if txt=='References':pf.page_break_before=True;pf.space_before=Pt(0)
  elif style=='Run-in Heading':
   p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY;pf.first_line_indent=Pt(0)
   pf.space_before=Pt(15.5);pf.space_after=Pt(0);pf.line_spacing=Pt(15.61)
   pf.line_spacing_rule=WD_LINE_SPACING.AT_LEAST;pf.keep_together=False
   for r in p.runs:style_run(r,10.91)
  elif style=='Bibliography':
   p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY;pf.left_indent=Pt(22);pf.first_line_indent=Pt(-22)
   pf.line_spacing=Pt(15.61);pf.space_after=Pt(5)
   for r in p.runs:style_run(r,10.91)
  elif style=='Source Code':
   pf.first_line_indent=Pt(0);pf.left_indent=Pt(12);pf.right_indent=Pt(8);pf.line_spacing=Pt(10.5)
   shade=xml('w:shd',fill='F8F9FA');p._p.get_or_add_pPr().append(shade)
   for r in p.runs:r.font.name='Latin Modern Mono';r.font.size=Pt(9)
  if p._p.xpath('./w:pPr/w:numPr'):
   pf.left_indent=Pt(27.3);pf.first_line_indent=Pt(-16.4)
  if txt.startswith('Keywords:'):
   pf.first_line_indent=Pt(0);pf.space_after=Pt(39)
  if re.match(r'^(Figure|Table) \d+:',txt):
   p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY;pf.first_line_indent=Pt(0);pf.left_indent=pf.right_indent=Pt(10)
   pf.line_spacing=Pt(13.74);pf.space_before=Pt(6);pf.space_after=Pt(6)
   pf.keep_with_next=txt.startswith('Table ')
   for r in p.runs:style_run(r,9.96,italic=False)
   # Only the label is bold, matching caption.sty.
   if p.runs:
    first=p.runs[0]
    if first.text.startswith(('Figure','Table')):
     label=re.match(r'^(?:Figure|Table) \d+:',first.text)
     if label:
      tail=copy.deepcopy(first._r);tail_text=first.text[label.end():]
      first.text=first.text[:label.end()];first.bold=True
      # Keep the complete caption editable, bolding only its numeric label.
      first._r.addnext(tail)
      from docx.text.run import Run
      tail_run=Run(tail,p);tail_run.text=tail_text;tail_run.bold=False
  if p._p.xpath('.//w:drawing'):
   p.alignment=WD_ALIGN_PARAGRAPH.CENTER;pf.first_line_indent=Pt(0);pf.space_before=Pt(8);pf.space_after=Pt(0);pf.keep_with_next=True;pf.line_spacing=1.0
  if txt.startswith('DOCXALG'):
   match=re.match(r'DOCXALG(\d+)X(\d+)X ?',p.runs[0].text)
   if match:
    p.runs[0].text=p.runs[0].text[match.end():]
    p.runs[0].text=(match[2]+':  ' if match[2]!='0' else '')+p.runs[0].text
    pf.left_indent=Pt(8+int(match[1])*11);pf.first_line_indent=Pt(0);pf.line_spacing=Pt(12);pf.keep_with_next=True
    for r in p.runs:style_run(r,9.5)
  for hyperlink in p._p.xpath('./w:hyperlink'):
   anchor=hyperlink.get(qn('w:anchor'),'')
   color='143C6E' if anchor.startswith('ref-') else 'A01423'
   for run in hyperlink.findall(qn('w:r')):
    pr=run.find(qn('w:rPr'))
    if pr is None:pr=xml('w:rPr');run.insert(0,pr)
    pr.append(xml('w:color',val=color));pr.append(xml('w:rFonts',ascii=FONT,hAnsi=FONT))
  # Set font size on math control properties, preserving editable OMML.
  for math in p._p.xpath('.//m:oMath'):
   for mr in math.iter(qn('m:r')):
    rpr=mr.find(qn('w:rPr'))
    if rpr is None:rpr=xml('w:rPr');mr.insert(0,rpr)
    rpr.append(xml('w:rFonts',ascii=MATHFONT,hAnsi=MATHFONT));rpr.append(xml('w:sz',val=22))
   for prop in math.iter():
    local=etree.QName(prop).localname
    if local.endswith('Pr') and local not in ('rPr','ctrlPr','oMathParaPr') and etree.QName(prop).namespace=='http://schemas.openxmlformats.org/officeDocument/2006/math':
     ctrl=prop.find(qn('m:ctrlPr'))
     if ctrl is None:ctrl=OxmlElement('m:ctrlPr');prop.append(ctrl)
     pr=ctrl.find(qn('w:rPr'))
     if pr is None:pr=xml('w:rPr');ctrl.append(pr)
     pr.append(xml('w:rFonts',ascii=MATHFONT,hAnsi=MATHFONT));pr.append(xml('w:sz',val=22))
 # Data tables remain real Word tables, with booktabs rules and no grid boxes.
 for t in list(d.tables):
  t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False;borders(t,True)
  n=len(t.columns)
  # Allocate width according to cell content rather than equal-width columns.
  weights=[]
  for c in range(n):
   values=[''.join(row.cells[c]._tc.xpath('.//w:t/text() | .//m:t/text()')) for row in t.rows]
   weights.append(max(3,max(len(v) for v in values))**0.65)
  total=sum(weights);widths=[WIDTH*w/total for w in weights]
  for i,col in enumerate(t.columns):col.width=Pt(widths[i])
  font=8.4 if n>=6 else 9.2
  for ri,row in enumerate(t.rows):
   row._tr.get_or_add_trPr().append(xml('w:cantSplit'))
   for ci,cell in enumerate(row.cells):
    cell.width=Pt(widths[ci]);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
    mar=xml('w:tcMar')
    for side in ('top','bottom','left','right'):mar.append(xml('w:'+side,w=40 if side in ('top','bottom') else 60,type='dxa'))
    cell._tc.get_or_add_tcPr().append(mar)
    for p in cell.paragraphs:
     pf=p.paragraph_format;pf.first_line_indent=Pt(0);pf.space_before=pf.space_after=Pt(0);pf.line_spacing=Pt(font*1.2)
     p.alignment=WD_ALIGN_PARAGRAPH.LEFT
     for r in p.runs:style_run(r,font,bold=True if ri==0 else None)
     for mr in p._p.xpath('.//m:r'):
      pr=mr.find(qn('w:rPr'))
      if pr is None:pr=xml('w:rPr');mr.insert(0,pr)
      pr.append(xml('w:sz',val=round(font*2)))
    if ri==0:
     cb=xml('w:tcBorders');cb.append(xml('w:bottom',val='single',sz=5));cell._tc.get_or_add_tcPr().append(cb)
   if ri==0:row._tr.get_or_add_trPr().append(xml('w:tblHeader'))
 # Number each display equation in a three-column borderless editable layout.
 paragraphs=list(d.paragraphs);numbered=0
 for p in paragraphs:
  match=re.fullmatch(r'DOCXEQ(\d+)X',p.text.strip())
  if not match:continue
  prev=p._p.getprevious()
  if prev is None or not prev.xpath('.//m:oMath'):raise ValueError('Missing equation before '+p.text)
  table=d.add_table(rows=1,cols=3);borders(table)
  table.alignment=WD_TABLE_ALIGNMENT.CENTER;table.autofit=False
  for ci,width in enumerate((18,WIDTH-48,30)):
   table.columns[ci].width=Pt(width);table.cell(0,ci).width=Pt(width)
  center=table.cell(0,1).paragraphs[0];center._p.getparent().replace(center._p,prev)
  center=table.cell(0,1).paragraphs[0]
  center.paragraph_format.first_line_indent=Pt(0);center.alignment=WD_ALIGN_PARAGRAPH.CENTER
  center.paragraph_format.space_before=center.paragraph_format.space_after=Pt(6)
  center.paragraph_format.line_spacing=1.0
  sizes={1:9,16:10,17:10,18:9,25:9,27:8,28:10,30:10,31:10}
  size=sizes.get(int(match[1]),11)
  rpr=center._p.get_or_add_pPr().find(qn('w:rPr'))
  if rpr is None:rpr=xml('w:rPr');center._p.get_or_add_pPr().append(rpr)
  rpr.append(xml('w:sz',val=round(size*2)))
  for pr in center._p.xpath('.//m:r/w:rPr | .//m:ctrlPr/w:rPr'):
   for oldsize in list(pr.findall(qn('w:sz'))):pr.remove(oldsize)
   pr.append(xml('w:sz',val=round(size*2)))
  right=table.cell(0,2);right.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
  rp=right.paragraphs[0];rp.alignment=WD_ALIGN_PARAGRAPH.RIGHT;rp.paragraph_format.first_line_indent=Pt(0)
  style_run(rp.add_run('('+match[1]+')'),10.91)
  table.rows[0]._tr.get_or_add_trPr().append(xml('w:cantSplit'))
  p._p.addprevious(table._tbl);p._p.getparent().remove(p._p);numbered+=1
 assert numbered==equations,(numbered,equations)
 # Office Math run order is m:rPr, w:rPr, then m:t. Preserve this ordering
 # so Word does not discard formatting while repairing a math run.
 for mr in d.element.iter(qn('m:r')):
  math_properties=mr.find(qn('m:rPr'));word_properties=mr.find(qn('w:rPr'))
  if math_properties is not None:mr.remove(math_properties);mr.insert(0,math_properties)
  if word_properties is not None:mr.remove(word_properties);mr.insert(1 if math_properties is not None else 0,word_properties)
 d.save(output)
 return numbered

def embed_fonts(output):
 # ECMA-376 font embedding: reverse GUID bytes and XOR the first 32 bytes.
 # Full editable fonts are embedded, so new text can use the same typeface.
 with zipfile.ZipFile(output) as z:parts={n:z.read(n) for n in z.namelist()}
 ns='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
 relns='http://schemas.openxmlformats.org/package/2006/relationships'
 tree=etree.fromstring(parts['word/fontTable.xml'])
 relpath='word/_rels/fontTable.xml.rels'
 rels=etree.fromstring(parts[relpath]) if relpath in parts else etree.Element('{'+relns+'}Relationships',nsmap={None:relns})
 types=etree.fromstring(parts['[Content_Types].xml'])
 ctns='http://schemas.openxmlformats.org/package/2006/content-types'
 if not any(x.get('Extension')=='odttf' for x in types):
  etree.SubElement(types,'{'+ctns+'}Default',Extension='odttf',ContentType='application/vnd.openxmlformats-officedocument.obfuscatedFont')
 configs=[(FONT,'Regular','TeXGyreTermesX-Regular.otf'),(FONT,'Bold','TeXGyreTermesX-Bold.otf'),(FONT,'Italic','TeXGyreTermesX-Italic.otf'),(FONT,'BoldItalic','TeXGyreTermesX-BoldItalic.otf'),(MATHFONT,'Regular','texgyretermes-math.otf'),('Latin Modern Mono','Regular','lmmono10-regular.otf')]
 for family,variant,filename in configs:
  font=next((x for x in tree if x.get('{'+ns+'}name')==family),None)
  if font is None:font=etree.SubElement(tree,'{'+ns+'}font',{'{'+ns+'}name':family})
  key=uuid.uuid5(uuid.NAMESPACE_URL,'certgraph-font:'+filename)
  data=bytearray((SUPPORT/'fonts'/filename).read_bytes());mask=key.bytes[::-1]
  for i in range(32):data[i]^=mask[i%16]
  number=len(rels)+1;rid='rIdFont'+str(number);target='fonts/font'+str(number)+'.odttf'
  etree.SubElement(rels,'{'+relns+'}Relationship',Id=rid,Type='http://schemas.openxmlformats.org/officeDocument/2006/relationships/font',Target=target)
  item=etree.SubElement(font,'{'+ns+'}embed'+variant)
  item.set('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id',rid)
  item.set('{'+ns+'}fontKey','{'+str(key).upper()+'}')
  item.set('{'+ns+'}subsetted','0');parts['word/'+target]=bytes(data)
 settings=etree.fromstring(parts['word/settings.xml'])
 for tag in ('embedTrueTypeFonts','embedSystemFonts'):
  if settings.find('{'+ns+'}'+tag) is None:etree.SubElement(settings,'{'+ns+'}'+tag)
 for tag in ('autoHyphenation',):
  e=etree.SubElement(settings,'{'+ns+'}'+tag);e.set('{'+ns+'}val','true')
 for path,element in [('word/fontTable.xml',tree),(relpath,rels),('[Content_Types].xml',types),('word/settings.xml',settings)]:parts[path]=etree.tostring(element,xml_declaration=True,encoding='UTF-8',standalone=True)
 with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
  for name,data in parts.items():z.writestr(name,data)

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--aux',type=Path);args=parser.parse_args()
 sources={};SUPPORT.mkdir(exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='certgraph-editable-word-') as temp:
  temp=Path(temp)
  if args.aux:aux=args.aux
  else:
   subprocess.run(['tectonic','--keep-intermediates','--outdir',str(temp),'main.tex'],cwd=ROOT,check=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);aux=temp/'main.aux'
  text,equations=preprocess(aux,sources);source=temp/'export.tex';source.write_text(text)
  pandoc=pypandoc.get_pandoc_path()
  ast=json.loads(subprocess.check_output([pandoc,str(source),'-f','latex','-t','json'],cwd=ROOT));ast['blocks']=transform(ast['blocks'])
  import pymupdf
  hyphens={}
  with pymupdf.open(ROOT/'main.pdf') as pdf:
   for page in pdf:
    for block in page.get_text('dict')['blocks']:
     if block['type']!=0:continue
     lines=[''.join(s['text'] for s in line['spans']) for line in block['lines']]
     for left,right in zip(lines,lines[1:]):
      a=re.search(r'([A-Za-z]+)-$',left);b=re.match(r'([A-Za-z]+)',right)
      if a and b:hyphens[a[1]+b[1]]=a[1]+'\u00ad'+b[1]
  def discretionary(o):
   if isinstance(o,dict):
    if o.get('t')=='Str':
     o['c']=re.sub(r'[A-Za-z]+',lambda m:hyphens.get(m[0],m[0]),o['c'])
    else:
     for v in o.values():discretionary(v)
   elif isinstance(o,list):
    for v in o:discretionary(v)
  discretionary(ast)
  astfile=temp/'export.json';astfile.write_text(json.dumps(ast))
  cited=json.loads(subprocess.check_output([pandoc,str(astfile),'-f','json','-t','json','--citeproc','--bibliography',str(ROOT/'references.bib'),'--csl',str(ROOT.parent/'thesis_paper/ieee.csl'),'-M','reference-section-title=References'],cwd=ROOT))
  bbl=aux.with_suffix('.bbl').read_text()
  entries=re.findall(r'\\bibitem\{([^}]+)\}(.*?)(?=\\bibitem|\\end\{thebibliography\})',bbl,flags=re.S)
  bib_blocks=[]
  for index,(key,entry) in enumerate(entries,1):
   entry=re.sub(r'\\BIBentry(?:ALTinterwordspacing|STDinterwordspacing)','',entry)
   entry=re.sub(r'\\hskip.*?\\relax',' ',entry,flags=re.S)
   entry=re.sub(r'\s+',' ',entry).strip()
   parsed=json.loads(subprocess.check_output([pandoc,'-f','latex','-t','json'],input=('['+str(index)+'] '+entry).encode()))
   bib_blocks.append({'t':'Div','c':[['ref-'+key,[],[['custom-style','Bibliography']]],parsed['blocks']]})
  for block in cited['blocks']:
   if block['t']=='Div' and block['c'][0][0]=='refs':block['c'][1]=bib_blocks
  astfile.write_text(json.dumps(cited))
  raw=temp/'raw.docx'
  subprocess.run([pandoc,str(astfile),'-f','json','-t','docx','--standalone','--number-sections','--resource-path',str(ROOT),'-o',str(raw)],cwd=ROOT,check=True)
  expected=collections.Counter()
  def count(o):
   if isinstance(o,dict):
    if o.get('t') in ('Math','Table','Image'):expected[o['t']]+=1
    for v in o.values():count(v)
   elif isinstance(o,list):
    for v in o:count(v)
  count(cited)
  output=ROOT/'main.docx';postprocess(raw,output,equations);embed_fonts(output)
  with zipfile.ZipFile(output) as z:
   tree=etree.fromstring(z.read('word/document.xml'));ns={'m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
   validation={'native_math_objects':len(tree.findall('.//m:oMath',ns)),'numbered_display_equations':equations,'embedded_images':sum(n.startswith('word/media/') for n in z.namelist()),'native_data_tables':len(Document(raw).tables)}
  assert validation['native_math_objects']==expected['Math'],(validation,expected)
  assert validation['native_data_tables']==expected['Table']==15
  assert validation['embedded_images']==expected['Image']==4
  assert not tree.xpath('//*[local-name()="t" and namespace-uri()="http://schemas.openxmlformats.org/officeDocument/2006/math" and text()="&"]')
  for path in [ROOT/'manuscript.sty',ROOT/'references.bib',*sorted((ROOT/'figures').glob('*.png')),*sorted((SUPPORT/'fonts').glob('*.otf'))]:sources[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
  manifest={'method':'LaTeX source to native Word text, tables and OMML equations','source_hashes':sources,'output_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'validation':validation,'visual_match':'See visual comparison report; exact Word/LaTeX pagination is not guaranteed.'}
  (SUPPORT/'export_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(validation,indent=2));print(output)
if __name__=='__main__':main()
