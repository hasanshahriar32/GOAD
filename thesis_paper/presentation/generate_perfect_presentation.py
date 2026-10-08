#!/usr/bin/env python3
"""
Generate the perfect academic PowerPoint defense presentation for CertGraph
using the exact UI theme, geometry, typography, and styling from old.pptx.
"""

import os
import shutil
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

# Paths
WORKSPACE = "/home/hs32/Desktop/GOAD/thesis_paper"
OLD_PPTX = os.path.join(WORKSPACE, "presentation/old.pptx")
OUTPUT_PPTX = os.path.join(WORKSPACE, "presentation/certgraph_thesis_defense.pptx")
OUTPUT_PPTX_CONV = os.path.join(WORKSPACE, "certgraph_thesis_defense.pptx")
THEME_DIR = os.path.join(WORKSPACE, "presentation/theme")
FIGURES_DIR = os.path.join(WORKSPACE, "presentation/figures_presentation")

# Assets
BG_TEXTURE = os.path.join(THEME_DIR, "bg_landscape.jpg")
HSTU_LOGO = os.path.join(THEME_DIR, "image2.png")

# Theme styling constants
FONT_FAMILY = "Times New Roman"
BLACK = RGBColor(0, 0, 0)
DARK_BLUE = RGBColor(16, 44, 87)
GRAY_LINE = RGBColor(60, 60, 60)
TABLE_HEADER_BG = RGBColor(230, 235, 245)
TABLE_ALT_BG = RGBColor(245, 247, 252)

TOTAL_PAGES = 15

def create_badge(slide, left, top, width, height, text, icon_path=None):
    """Creates a rectangular badge with outline and optional icon, matching old.pptx."""
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.background()
    shape.line.color.rgb = BLACK
    shape.line.width = Pt(1.5)
    
    # Text
    tf = shape.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.text = text
    p.font.name = FONT_FAMILY
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = BLACK
    p.alignment = PP_ALIGN.CENTER
    
    if icon_path and os.path.exists(icon_path):
        icon_size = height - Inches(0.16)
        slide.shapes.add_picture(icon_path, left + Inches(0.12), top + Inches(0.08), width=icon_size, height=icon_size)
        p.alignment = PP_ALIGN.LEFT
        tf.margin_left = icon_size + Inches(0.2)
        
    return shape

def add_header_and_chrome(slide, page_num, title_text):
    """Adds the standard top-left HSTU logo, bold title, page number, and footer."""
    # Logo
    slide.shapes.add_picture(HSTU_LOGO, Inches(1.31), Inches(0.91), width=Inches(0.99), height=Inches(1.26))
    
    # Title
    tb_title = slide.shapes.add_textbox(Inches(2.57), Inches(1.07), Inches(14.2), Inches(0.91))
    tf_title = tb_title.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text.upper()
    p_title.font.name = FONT_FAMILY
    p_title.font.size = Pt(38) if len(title_text) > 35 else Pt(42)
    p_title.font.bold = True
    p_title.font.color.rgb = BLACK
    
    # Page Number
    tb_num = slide.shapes.add_textbox(Inches(17.04), Inches(0.48), Inches(1.95), Inches(0.43))
    tf_num = tb_num.text_frame
    p_num = tf_num.paragraphs[0]
    p_num.text = f"{page_num:02d}/{TOTAL_PAGES}"
    p_num.font.name = FONT_FAMILY
    p_num.font.size = Pt(22)
    p_num.alignment = PP_ALIGN.RIGHT
    p_num.font.color.rgb = BLACK
    
    # Footer
    tb_foot = slide.shapes.add_textbox(Inches(6.5), Inches(10.06), Inches(7.0), Inches(0.40))
    tf_foot = tb_foot.text_frame
    p_foot = tf_foot.paragraphs[0]
    p_foot.text = "Course Title: Project and Thesis"
    p_foot.font.name = FONT_FAMILY
    p_foot.font.size = Pt(22)
    p_foot.font.bold = True
    p_foot.alignment = PP_ALIGN.CENTER
    p_foot.font.color.rgb = BLACK

def clear_slide_content(slide):
    """Removes all shapes except Freeform 2 (the background texture) from slide."""
    shapes_to_remove = [sh for sh in slide.shapes if sh.name != "Freeform 2"]
    for sh in shapes_to_remove:
        slide.shapes._spTree.remove(sh._element)

def add_bullets(tf, items, font_size=21, space_after=10, bold_prefix=True):
    """Helper to populate bullet points into a text frame with clean styling."""
    tf.word_wrap = True
    for i, item in enumerate(items):
        if i == 0 and len(tf.paragraphs) == 1 and not tf.paragraphs[0].text.strip():
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.space_after = Pt(space_after)
        
        # Check if item has a bold lead-in prefix (e.g. "Phase 1: Description")
        if bold_prefix and ":" in item:
            prefix, rest = item.split(":", 1)
            r1 = p.add_run()
            r1.text = prefix + ":"
            r1.font.name = FONT_FAMILY
            r1.font.size = Pt(font_size)
            r1.font.bold = True
            r1.font.color.rgb = BLACK
            
            r2 = p.add_run()
            r2.text = rest
            r2.font.name = FONT_FAMILY
            r2.font.size = Pt(font_size)
            r2.font.bold = False
            r2.font.color.rgb = BLACK
        elif bold_prefix and "—" in item:
            prefix, rest = item.split("—", 1)
            r1 = p.add_run()
            r1.text = prefix + "—"
            r1.font.name = FONT_FAMILY
            r1.font.size = Pt(font_size)
            r1.font.bold = True
            r1.font.color.rgb = BLACK
            
            r2 = p.add_run()
            r2.text = rest
            r2.font.name = FONT_FAMILY
            r2.font.size = Pt(font_size)
            r2.font.bold = False
            r2.font.color.rgb = BLACK
        else:
            r = p.add_run()
            r.text = item
            r.font.name = FONT_FAMILY
            r.font.size = Pt(font_size)
            r.font.color.rgb = BLACK

def build_presentation():
    print("Loading base presentation template from:", OLD_PPTX)
    prs = Presentation(OLD_PPTX)
    
    # Ensure presentation has 15 slides:
    # old.pptx has 14 slides (0..13). Slide 13 is Thank You.
    # Add 15th slide and insert it right before Thank You slide.
    if len(prs.slides) == 14:
        new_slide = prs.slides.add_slide(prs.slide_layouts[6])
        prs.slides._sldIdLst.insert(13, prs.slides._sldIdLst[14])
        print("Inserted Slide 14 before Thank You slide. Total slides now:", len(prs.slides))

    # =========================================================================
    # SLIDE 1: TITLE SLIDE (index 0)
    # =========================================================================
    s1 = prs.slides[0]
    for sh in s1.shapes:
        if sh.has_text_frame:
            t = sh.text_frame.text.strip()
            if "BLOCKCHAIN" in t.upper() or "FEDERATED" in t.upper() or "DECENTRALIZED" in t.upper() or "CERTGRAPH" in t.upper() or "HISTOPATHOLOGICAL" in t.upper():
                sh.top = Inches(1.05)
                sh.height = Inches(2.30)
                sh.text_frame.word_wrap = True
                sh.text_frame.text = (
                    "CertGraph: Heterogeneous Graph Attention Networks\n"
                    "for Active Directory Certificate Services Vulnerability\n"
                    "Detection and Autonomous Defense"
                )
                for p in sh.text_frame.paragraphs:
                    p.alignment = PP_ALIGN.CENTER
                    p.font.name = FONT_FAMILY
                    p.font.size = Pt(36)
                    p.font.bold = True
                    p.font.color.rgb = BLACK
            elif "Course Code:" in t:
                sh.text_frame.text = "Course Code: ECE 452\nCourse Title: Project and Thesis"
                for p in sh.text_frame.paragraphs:
                    p.alignment = PP_ALIGN.CENTER
                    p.font.name = FONT_FAMILY
                    p.font.size = Pt(26)
                    p.font.bold = True
                    p.font.color.rgb = BLACK
            elif "Student ID:" in t:
                sh.text_frame.text = (
                    "Student ID: 2002126 Level:4, Semester:II\n"
                    "Student ID: 2002138 Level:4, Semester:II\n"
                    "Student ID: 2102151 Level:4, Semester:II"
                )
                for p in sh.text_frame.paragraphs:
                    p.alignment = PP_ALIGN.CENTER
                    p.font.name = FONT_FAMILY
                    p.font.size = Pt(24)
                    p.font.color.rgb = BLACK
            elif "Date:" in t:
                sh.text_frame.text = "Date: October 2026"
                for p in sh.text_frame.paragraphs:
                    p.alignment = PP_ALIGN.CENTER
                    p.font.name = FONT_FAMILY
                    p.font.size = Pt(24)
                    p.font.color.rgb = BLACK
            elif "Department of Electronics" in t:
                for p in sh.text_frame.paragraphs:
                    p.alignment = PP_ALIGN.CENTER
                    p.font.name = FONT_FAMILY
                    p.font.size = Pt(24)
                    p.font.color.rgb = BLACK
            elif "Hajee Mohammad Danesh" in t:
                for p in sh.text_frame.paragraphs:
                    p.alignment = PP_ALIGN.CENTER
                    p.font.name = FONT_FAMILY
                    p.font.size = Pt(22)
                    p.font.color.rgb = BLACK
    print("Slide 1 (Title) configured.")

    # =========================================================================
    # SLIDE 2: PROBLEM STATEMENT & SOLUTION (index 1)
    # =========================================================================
    s2 = prs.slides[1]
    clear_slide_content(s2)
    add_header_and_chrome(s2, 2, "PROBLEM STATEMENT & SOLUTION")
    
    # Left Column - The Problem
    create_badge(s2, Inches(1.3), Inches(2.4), Inches(7.8), Inches(0.65), "The Problem", os.path.join(THEME_DIR, "image7.png"))
    tb_prob = s2.shapes.add_textbox(Inches(1.3), Inches(3.2), Inches(7.8), Inches(6.4))
    tf_prob = tb_prob.text_frame
    p_lead = tf_prob.paragraphs[0]
    p_lead.text = "Active Directory Certificate Services (ADCS) manages enterprise PKI in 90%+ Fortune 500 networks. However, exploitability requires both misconfiguration and effective access — vulnerabilities exist as multi-hop authorization paths."
    p_lead.font.name = FONT_FAMILY
    p_lead.font.size = Pt(22)
    p_lead.font.bold = True
    p_lead.font.color.rgb = BLACK
    p_lead.space_after = Pt(14)
    
    add_bullets(tf_prob, [
        "• Multi-Hop Escalation Chains: Relational permission graphs spanning 4 to 8 hops (ESC1–ESC13).",
        "• Weaponized Identity Spoofing: Unprivileged accounts abuse Subject Alternative Names (SAN / UPN).",
        "• Forest-Wide Domination: DCSync replication grants immediate Domain Controller compromise."
    ], font_size=21, space_after=12, bold_prefix=True)
    
    # Right Column - The Solution & Research Gap
    create_badge(s2, Inches(10.2), Inches(2.4), Inches(8.5), Inches(0.65), "The Solution", os.path.join(THEME_DIR, "image9.png"))
    tb_sol = s2.shapes.add_textbox(Inches(10.2), Inches(3.2), Inches(8.5), Inches(2.6))
    tf_sol = tb_sol.text_frame
    add_bullets(tf_sol, [
        "1. Heterogeneous Graph Attention Networks (HAN) modeling multi-relational enterprise topologies.",
        "2. Orthogonal residual skip connections preventing representation oversmoothing over deep paths.",
        "3. Neuro-Symbolic synthesis guaranteeing 100% formal mathematical soundness."
    ], font_size=21, space_after=10, bold_prefix=False)
    
    create_badge(s2, Inches(10.2), Inches(6.0), Inches(8.5), Inches(0.65), "Research Gap", os.path.join(THEME_DIR, "image5.png"))
    tb_gap = s2.shapes.add_textbox(Inches(10.2), Inches(6.8), Inches(8.5), Inches(2.8))
    tf_gap = tb_gap.text_frame
    add_bullets(tf_gap, [
        "1. Rule engines (Certipy) fail zero-shot on novel composite escalation paths.",
        "2. Graph search (BloodHound) combinatorial state explosion on 100k+ enterprise nodes.",
        "3. Complete lack of autonomous, disruption-bounded automated remediation mechanisms."
    ], font_size=21, space_after=10, bold_prefix=False)
    print("Slide 2 configured.")

    # =========================================================================
    # SLIDE 3: OBJECTIVES (index 2)
    # =========================================================================
    s3 = prs.slides[2]
    clear_slide_content(s3)
    add_header_and_chrome(s3, 3, "OBJECTIVES")
    
    # Top primary goal statement
    tb_goal = s3.shapes.add_textbox(Inches(1.3), Inches(2.3), Inches(17.4), Inches(1.2))
    tf_goal = tb_goal.text_frame
    p_g = tf_goal.paragraphs[0]
    p_g.text = "The primary goal is to resolve the conflict between combinatorial scalability and relational security in enterprise Active Directory by developing a mathematically bounded, real-time Heterogeneous Graph Neural Network framework."
    p_g.font.name = FONT_FAMILY
    p_g.font.size = Pt(24)
    p_g.font.bold = True
    p_g.font.color.rgb = BLACK
    
    # 5 Objective Cards
    card_w = Inches(3.25)
    gap = Inches(0.29)
    card_top = Inches(3.7)
    card_h = Inches(5.9)
    
    objectives_data = [
        ("1", os.path.join(THEME_DIR, "image11.png"), "Relational Graph Modeling", 
         "Model 6 entity types and 18 multi-relational edges spanning users, groups, templates, CAs, and domains."),
        ("2", os.path.join(THEME_DIR, "image9.png"), "Gradient Preservation", 
         "Mathematically prove Theorem 1 to eliminate representation oversmoothing across deep privilege chains."),
        ("3", os.path.join(THEME_DIR, "image15.png"), "Zero-Shot Enterprise Transfer", 
         "Achieve near-perfect generalization across 700 unseen synthetic and realistic forest topologies."),
        ("4", os.path.join(THEME_DIR, "image22.png"), "Neuro-Symbolic Synthesis", 
         "Eliminate pure neural blind spots on adversarially crafted hard negatives (disabled enrollment flags)."),
        ("5", os.path.join(THEME_DIR, "image26.png"), "Autonomous Mitigation", 
         "Formulate Minimum Perturbation Attack Interdiction (MPAI), prove NP-hardness (Theorem 2), and train PPO remediation.")
    ]
    
    for idx, (num, icon, heading, desc) in enumerate(objectives_data):
        c_left = Inches(1.3) + idx * (card_w + gap)
        
        # Border box
        box = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, c_left, card_top, card_w, card_h)
        box.fill.background()
        box.line.color.rgb = BLACK
        box.line.width = Pt(1.5)
        
        # Number badge inside box at top
        num_tb = s3.shapes.add_textbox(c_left, card_top + Inches(0.15), card_w, Inches(0.45))
        np = num_tb.text_frame.paragraphs[0]
        np.text = f"({num})"
        np.font.name = FONT_FAMILY
        np.font.size = Pt(26)
        np.font.bold = True
        np.alignment = PP_ALIGN.CENTER
        np.font.color.rgb = BLACK
        
        # Icon
        if os.path.exists(icon):
            s3.shapes.add_picture(icon, c_left + (card_w - Inches(1.1))/2, card_top + Inches(0.7), width=Inches(1.1), height=Inches(1.1))
            
        # Heading
        head_tb = s3.shapes.add_textbox(c_left + Inches(0.15), card_top + Inches(2.0), card_w - Inches(0.3), Inches(0.9))
        head_tf = head_tb.text_frame
        head_tf.word_wrap = True
        hp = head_tf.paragraphs[0]
        hp.text = heading
        hp.font.name = FONT_FAMILY
        hp.font.size = Pt(20)
        hp.font.bold = True
        hp.alignment = PP_ALIGN.CENTER
        hp.font.color.rgb = BLACK
        
        # Description
        desc_tb = s3.shapes.add_textbox(c_left + Inches(0.15), card_top + Inches(3.0), card_w - Inches(0.3), Inches(2.7))
        desc_tf = desc_tb.text_frame
        desc_tf.word_wrap = True
        dp = desc_tf.paragraphs[0]
        dp.text = desc
        dp.font.name = FONT_FAMILY
        dp.font.size = Pt(19)
        dp.alignment = PP_ALIGN.LEFT
        dp.font.color.rgb = BLACK
    print("Slide 3 configured.")

    # =========================================================================
    # SLIDE 4: LITERATURE SURVEY & SOTA MODELS (index 3)
    # =========================================================================
    s4 = prs.slides[3]
    clear_slide_content(s4)
    add_header_and_chrome(s4, 4, "LITERATURE SURVEY & SOTA MODELS")
    
    # Left Column: Figure & Caption
    fig_sota = os.path.join(FIGURES_DIR, "tool_comparison_f1.png")
    if os.path.exists(fig_sota):
        s4.shapes.add_picture(fig_sota, Inches(1.3), Inches(2.4), width=Inches(8.5), height=Inches(4.27))
        
    tb_cap = s4.shapes.add_textbox(Inches(1.3), Inches(6.8), Inches(8.5), Inches(0.5))
    p_cap = tb_cap.text_frame.paragraphs[0]
    p_cap.text = "Figure: Macro-F1 Comparison Across Detection Paradigms"
    p_cap.font.name = FONT_FAMILY
    p_cap.font.size = Pt(20)
    p_cap.font.italic = True
    p_cap.alignment = PP_ALIGN.CENTER
    p_cap.font.color.rgb = BLACK
    
    tb_sota_bullets = s4.shapes.add_textbox(Inches(1.3), Inches(7.4), Inches(8.5), Inches(2.2))
    tf_sb = tb_sota_bullets.text_frame
    add_bullets(tf_sb, [
        "• Certipy Rule Engine: 0.7791 Macro-F1 (fails zero-shot on unseen paths).",
        "• Symbolic BFS Traversal: 0.9082 Macro-F1 (suffers severe combinatorial latency).",
        "• CertGraph (Ours): 0.9986 Macro-F1 (+28.24% improvement over heuristic baselines)."
    ], font_size=20, space_after=8, bold_prefix=True)
    
    # Right Column: Research Gap & Innovations
    create_badge(s4, Inches(10.3), Inches(2.4), Inches(8.4), Inches(0.65), "Research Gap", os.path.join(THEME_DIR, "image7.png"))
    tb_rg = s4.shapes.add_textbox(Inches(10.3), Inches(3.2), Inches(8.4), Inches(2.0))
    tf_rg = tb_rg.text_frame
    p_rg = tf_rg.paragraphs[0]
    p_rg.text = "Existing enterprise tools rely on brittle syntactic regexes (Certipy) or unweighted graph traversal (BloodHound). They fail to identify multi-hop composite vulnerabilities and suffer state explosion on graphs with >100,000 entities."
    p_rg.font.name = FONT_FAMILY
    p_rg.font.size = Pt(21)
    p_rg.font.color.rgb = BLACK
    
    create_badge(s4, Inches(10.3), Inches(5.4), Inches(8.4), Inches(0.65), "Proposed Innovations", os.path.join(THEME_DIR, "image9.png"))
    tb_pi = s4.shapes.add_textbox(Inches(10.3), Inches(6.2), Inches(8.4), Inches(3.4))
    tf_pi = tb_pi.text_frame
    add_bullets(tf_pi, [
        "• Heterogeneous Relational GAT: Multi-relational attention aggregation capturing subtle structural dependencies.",
        "• Residual Skip Projections: Preserves gradient bounds ||dh_v / dx_v|| >= sigma_min(W_skip) > 0 to eliminate oversmoothing.",
        "• Sub-Second Scalability: 343 ms inference on 10,000 nodes (12.4x faster than Dijkstra shortest-path)."
    ], font_size=21, space_after=10, bold_prefix=True)
    print("Slide 4 configured.")

    # =========================================================================
    # SLIDE 5: METHODOLOGICAL WORKFLOW (index 4)
    # =========================================================================
    s5 = prs.slides[4]
    clear_slide_content(s5)
    add_header_and_chrome(s5, 5, "METHODOLOGICAL WORKFLOW")
    
    # Left Column: Research Framework & Phases
    create_badge(s5, Inches(1.3), Inches(2.4), Inches(8.2), Inches(0.65), "Core Methodological Framework")
    tb_mf = s5.shapes.add_textbox(Inches(1.3), Inches(3.2), Inches(8.2), Inches(1.6))
    p_mf = tb_mf.text_frame.paragraphs[0]
    p_mf.text = "Integrating Heterogeneous Graph Attention Networks with formal symbolic verification to enable real-time, zero-shot ADCS vulnerability detection."
    p_mf.font.name = FONT_FAMILY
    p_mf.font.size = Pt(21)
    p_mf.font.bold = True
    p_mf.font.color.rgb = BLACK
    
    create_badge(s5, Inches(1.3), Inches(4.9), Inches(8.2), Inches(0.65), "3-Phase Execution Pipeline")
    tb_phases = s5.shapes.add_textbox(Inches(1.3), Inches(5.7), Inches(8.2), Inches(4.0))
    tf_ph = tb_phases.text_frame
    add_bullets(tf_ph, [
        "• Phase 1: Multigraph Construction — Ingests LDAP, RPC, and BloodHound JSON into heterogeneous multigraph G = (V, E, tau_V, phi_E) with 6 node types and 18 edge relations.",
        "• Phase 2: Relational GNN Embedding — Type-specific linear projection, relational multi-head attention, and residual skip connections.",
        "• Phase 3: Neuro-Symbolic Verification & Action — Fast GNN screening followed by symbolic soundness check and LDAP actuation."
    ], font_size=21, space_after=12, bold_prefix=True)
    
    # Right Column: Metagraph Schema Figure
    fig_schema = os.path.join(FIGURES_DIR, "adcs_attack_graph_schema.png")
    if os.path.exists(fig_schema):
        s5.shapes.add_picture(fig_schema, Inches(10.0), Inches(2.6), width=Inches(8.7), height=Inches(4.97))
    tb_sc_cap = s5.shapes.add_textbox(Inches(10.0), Inches(7.8), Inches(8.7), Inches(0.5))
    p_scc = tb_sc_cap.text_frame.paragraphs[0]
    p_scc.text = "Figure: Active Directory Heterogeneous Metagraph Schema"
    p_scc.font.name = FONT_FAMILY
    p_scc.font.size = Pt(20)
    p_scc.font.italic = True
    p_scc.alignment = PP_ALIGN.CENTER
    p_scc.font.color.rgb = BLACK
    print("Slide 5 configured.")

    # =========================================================================
    # SLIDE 6: ADCS ATTACK MECHANICS: ESC13 CASE STUDY (index 5)
    # =========================================================================
    s6 = prs.slides[5]
    clear_slide_content(s6)
    add_header_and_chrome(s6, 6, "ADCS ATTACK MECHANICS: ESC13 CASE STUDY")
    
    # Left Column: Attack Progression & Insight
    create_badge(s6, Inches(1.3), Inches(2.4), Inches(8.2), Inches(0.65), "Attack Chain Progression")
    tb_att = s6.shapes.add_textbox(Inches(1.3), Inches(3.2), Inches(8.2), Inches(3.9))
    tf_att = tb_att.text_frame
    add_bullets(tf_att, [
        "• Phase 1: Target Discovery — Attacker identifies certificate template with issuance policy OID linked to privileged administrative group.",
        "• Phase 2: Enrollment Abuse — Low-privilege user enrolls and specifies Subject Alternative Name (SAN).",
        "• Phase 3: PKINIT Exchange — Submits X.509 certificate to KDC via Kerberos PKINIT, obtaining high-privilege TGT.",
        "• Phase 4: Domain Domination — DCSync replay grants immediate Domain Controller replication privileges."
    ], font_size=20, space_after=10, bold_prefix=True)
    
    # Callout Box
    callout = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.3), Inches(7.3), Inches(8.2), Inches(2.3))
    callout.fill.background()
    callout.line.color.rgb = BLACK
    callout.line.width = Pt(1.5)
    tf_co = callout.text_frame
    tf_co.word_wrap = True
    p_co_head = tf_co.paragraphs[0]
    p_co_head.text = "Why Single-Node Inspection Fails:"
    p_co_head.font.name = FONT_FAMILY
    p_co_head.font.size = Pt(21)
    p_co_head.font.bold = True
    p_co_head.font.color.rgb = BLACK
    p_co_head.space_after = Pt(6)
    
    p_co_body = tf_co.add_paragraph()
    p_co_body.text = "The vulnerability exists solely as a multi-hop path closure across disparate objects. Every individual node and permission appears completely benign in isolation!"
    p_co_body.font.name = FONT_FAMILY
    p_co_body.font.size = Pt(20)
    p_co_body.font.color.rgb = BLACK
    
    # Right Column: Attack Diagram
    fig_esc13 = os.path.join(FIGURES_DIR, "esc13_attack_path_diagram.png")
    if os.path.exists(fig_esc13):
        s6.shapes.add_picture(fig_esc13, Inches(10.0), Inches(2.5), width=Inches(8.7), height=Inches(5.03))
    tb_e13_cap = s6.shapes.add_textbox(Inches(10.0), Inches(7.8), Inches(8.7), Inches(0.5))
    p_e13 = tb_e13_cap.text_frame.paragraphs[0]
    p_e13.text = "Figure: Two-Hop ESC13 Privilege Escalation Attack Chain"
    p_e13.font.name = FONT_FAMILY
    p_e13.font.size = Pt(20)
    p_e13.font.italic = True
    p_e13.alignment = PP_ALIGN.CENTER
    p_e13.font.color.rgb = BLACK
    print("Slide 6 configured.")

    # =========================================================================
    # SLIDE 7: SYSTEM ARCHITECTURE: CERTGRAPH GNN (index 6)
    # =========================================================================
    s7 = prs.slides[6]
    clear_slide_content(s7)
    add_header_and_chrome(s7, 7, "SYSTEM ARCHITECTURE: CERTGRAPH GNN")
    
    fig_arch = os.path.join(FIGURES_DIR, "certgraph_architecture_diagram.png")
    if os.path.exists(fig_arch):
        s7.shapes.add_picture(fig_arch, Inches(1.8), Inches(2.3), width=Inches(16.4), height=Inches(5.3))
        
    # 3 Summary Cards Below Figure
    card3_w = Inches(5.2)
    card3_gap = Inches(0.4)
    card3_top = Inches(7.9)
    card3_h = Inches(1.8)
    
    arch_cards = [
        ("1. Input Multigraph & Projections", 
         "6 entity types projected via type-specific weights W_tau into unified 64-dim space. Accommodates arbitrary enterprise graph scale."),
        ("2. Relational Hetero-GAT Layers", 
         "4 attention heads per relation. Residual skip connection h_v <- h_v + W_skip h_v directly preserves input gradients across deep hops."),
        ("3. Readout & Classification Head", 
         "Template node readout followed by MLP classifier predicting 7 classes (Safe, ESC1, ESC2, ESC3, ESC4, ESC9, ESC13).")
    ]
    
    for idx, (title, text) in enumerate(arch_cards):
        c_left = Inches(1.8) + idx * (card3_w + card3_gap)
        box = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, c_left, card3_top, card3_w, card3_h)
        box.fill.background()
        box.line.color.rgb = BLACK
        box.line.width = Pt(1.5)
        
        tf = box.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(20)
        p_t.font.bold = True
        p_t.font.color.rgb = BLACK
        p_t.space_after = Pt(4)
        
        p_b = tf.add_paragraph()
        p_b.text = text
        p_b.font.name = FONT_FAMILY
        p_b.font.size = Pt(18)
        p_b.font.color.rgb = BLACK
    print("Slide 7 configured.")

    # =========================================================================
    # SLIDE 8: THEORETICAL FOUNDATION: THEOREM 1 (index 7)
    # =========================================================================
    s8 = prs.slides[7]
    clear_slide_content(s8)
    add_header_and_chrome(s8, 8, "THEORETICAL FOUNDATION: THEOREM 1")
    
    # Left Column: Formulation
    create_badge(s8, Inches(1.3), Inches(2.4), Inches(8.3), Inches(0.65), "Relational Attention Formulation")
    tb_form = s8.shapes.add_textbox(Inches(1.3), Inches(3.2), Inches(8.3), Inches(6.5))
    tf_form = tb_form.text_frame
    add_bullets(tf_form, [
        "• Attention Weight Formulation:\n  alpha_ij^(r) = Softmax_j( LeakyReLU( a_r^T [W_tau(i) h_i || W_tau(j) h_j] ) )",
        "• Layer Update with Residual Skip Connection:\n  h_i^(l+1) = sigma( sum_r sum_j alpha_ij^(r) W_r^(l) h_j^(l) + W_skip^(l) h_i^(l) )",
        "• Class-Imbalance Aware Focal Loss (gamma = 2.0):\n  L_focal = - sum_v alpha_t (1 - p_v,t)^gamma log(p_v,t)",
        "• Relational Context: Allows dynamic reweighting between benign organizational structure (MemberOf) and critical attack primitives (WriteDacl, Enroll)."
    ], font_size=20, space_after=14, bold_prefix=True)
    
    # Right Column: Theorem 1
    create_badge(s8, Inches(10.2), Inches(2.4), Inches(8.5), Inches(0.65), "Theorem 1: Gradient Preservation Guarantee")
    tb_thm = s8.shapes.add_textbox(Inches(10.2), Inches(3.2), Inches(8.5), Inches(6.5))
    tf_thm = tb_thm.text_frame
    add_bullets(tf_thm, [
        "• Theorem Statement:\nLet G be a heterogeneous multigraph with L message passing layers. If each layer preserves an orthogonal residual skip projection W_skip^(l) with sigma_min(W_skip^(l)) >= c > 0, then the Jacobian satisfies:\n\n    || dh_v^(L) / dx_v || >= prod_{l=1}^L sigma_min(W_skip^(l)) >= c^L > 0",
        "• Elimination of Oversmoothing Collapse:\nIn standard GNNs as layer depth L -> inf, the Dirichlet energy E(H^(L)) -> 0, causing all node representations to become indistinguishable.",
        "• Formal Guarantee:\nTheorem 1 mathematically proves that CertGraph preserves distinct structural identities across 4 to 8 hop ADCS delegation chains!"
    ], font_size=20, space_after=14, bold_prefix=True)
    print("Slide 8 configured.")

    # =========================================================================
    # SLIDE 9: EXPERIMENTAL TESTBED (GOAD & ADSYNTH) (index 8)
    # =========================================================================
    s9 = prs.slides[8]
    clear_slide_content(s9)
    add_header_and_chrome(s9, 9, "EXPERIMENTAL TESTBED (GOAD & ADSYNTH)")
    
    # Left Column: Dual Environments & Composition
    create_badge(s9, Inches(1.3), Inches(2.4), Inches(8.5), Inches(0.65), "Dual Experimental Environments")
    tb_env = s9.shapes.add_textbox(Inches(1.3), Inches(3.2), Inches(8.5), Inches(2.6))
    tf_env = tb_env.text_frame
    add_bullets(tf_env, [
        "• Game of Active Directory (GOAD): Multi-forest enterprise environment with 5 Domain Controllers, nested OUs, and real-world Kerberos/ADCS attack primitives.",
        "• ADSynth Synthetic Generator: Generates 700 enterprise topologies with 100 to 100,000 nodes for combinatorial scalability stress testing."
    ], font_size=21, space_after=12, bold_prefix=True)
    
    create_badge(s9, Inches(1.3), Inches(6.0), Inches(8.5), Inches(0.65), "Dataset Composition & Validation")
    tb_ds = s9.shapes.add_textbox(Inches(1.3), Inches(6.8), Inches(8.5), Inches(2.8))
    tf_ds = tb_ds.text_frame
    add_bullets(tf_ds, [
        "• 28,450 total nodes across 6 entity classes.",
        "• 142,890 multi-relational edges spanning DACLs, group nestings, and PKI.",
        "• Rigorous 5-fold cross-validation with non-overlapping forest partitions."
    ], font_size=21, space_after=10, bold_prefix=True)
    
    # Right Column: GOAD Forest Topology Figure
    fig_topo = os.path.join(FIGURES_DIR, "goad_forest_topology.png")
    if os.path.exists(fig_topo):
        s9.shapes.add_picture(fig_topo, Inches(10.3), Inches(2.6), width=Inches(8.4), height=Inches(4.48))
    tb_topo_cap = s9.shapes.add_textbox(Inches(10.3), Inches(7.4), Inches(8.4), Inches(0.5))
    p_tc = tb_topo_cap.text_frame.paragraphs[0]
    p_tc.text = "Figure: GOAD Multi-Forest Enterprise Topology"
    p_tc.font.name = FONT_FAMILY
    p_tc.font.size = Pt(20)
    p_tc.font.italic = True
    p_tc.alignment = PP_ALIGN.CENTER
    p_tc.font.color.rgb = BLACK
    
    tb_topo_sub = s9.shapes.add_textbox(Inches(10.3), Inches(8.0), Inches(8.4), Inches(1.5))
    tf_ts = tb_topo_sub.text_frame
    add_bullets(tf_ts, [
        "• Authentic enterprise complexity: Multiple trust relationships, gMSA service accounts, and cross-domain PKI issuance policies."
    ], font_size=20, space_after=6, bold_prefix=True)
    print("Slide 9 configured.")

    # =========================================================================
    # SLIDE 10: RESULTS: BENCHMARK EVALUATION (index 9)
    # =========================================================================
    s10 = prs.slides[9]
    clear_slide_content(s10)
    add_header_and_chrome(s10, 10, "RESULTS: BENCHMARK EVALUATION")
    
    create_badge(s10, Inches(1.3), Inches(2.4), Inches(9.2), Inches(0.65), "Quantitative Performance Summary")
    
    # Table on Left
    table_shape = s10.shapes.add_table(6, 4, Inches(1.3), Inches(3.2), Inches(9.2), Inches(4.3))
    table = table_shape.table
    table.columns[0].width = Inches(2.4)
    table.columns[1].width = Inches(2.2)
    table.columns[2].width = Inches(2.3)
    table.columns[3].width = Inches(2.3)
    
    headers = ["Metric", "Certipy (Rule)", "Homogeneous GCN", "CertGraph (Ours)"]
    rows = [
        ["Precision", "74.20%", "87.41%", "99.88%"],
        ["Recall", "69.21%", "85.04%", "99.84%"],
        ["Macro-F1", "71.62%", "86.21%", "99.86%"],
        ["ROC-AUC", "0.8410", "0.9340", "0.9998"],
        ["Zero-Shot F1", "Fails (0%)", "64.12%", "100.00%"]
    ]
    
    for c, h in enumerate(headers):
        cell = table.cell(0, c)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = TABLE_HEADER_BG
        p = cell.text_frame.paragraphs[0]
        p.font.name = FONT_FAMILY
        p.font.size = Pt(20)
        p.font.bold = True
        p.alignment = PP_ALIGN.CENTER
        p.font.color.rgb = BLACK
        
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell = table.cell(r + 1, c)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = TABLE_ALT_BG if r % 2 == 1 else RGBColor(255, 255, 255)
            p = cell.text_frame.paragraphs[0]
            p.font.name = FONT_FAMILY
            p.font.size = Pt(20)
            p.font.bold = (c == 3 or c == 0)
            p.alignment = PP_ALIGN.LEFT if c == 0 else PP_ALIGN.CENTER
            p.font.color.rgb = DARK_BLUE if c == 3 else BLACK

    # Callout text below table
    tb_sig = s10.shapes.add_textbox(Inches(1.3), Inches(7.8), Inches(9.2), Inches(1.8))
    p_sig = tb_sig.text_frame.paragraphs[0]
    p_sig.text = "Significance: CertGraph achieves 0.9986 Macro-F1 across 700 topologies and 0.9941 on imbalanced 96% Safe templates (PR-AUC: 0.9982), outperforming rule heuristics by +28.24% (p < 1.31e-6)."
    p_sig.font.name = FONT_FAMILY
    p_sig.font.size = Pt(21)
    p_sig.font.bold = True
    p_sig.font.color.rgb = BLACK
    
    # Right Column: Confusion Matrix
    fig_cm = os.path.join(FIGURES_DIR, "confusion_matrix.png")
    if os.path.exists(fig_cm):
        s10.shapes.add_picture(fig_cm, Inches(11.2), Inches(2.4), width=Inches(7.5), height=Inches(6.62))
    tb_cm_cap = s10.shapes.add_textbox(Inches(11.2), Inches(9.1), Inches(7.5), Inches(0.4))
    p_cm = tb_cm_cap.text_frame.paragraphs[0]
    p_cm.text = "Figure: Multi-Class Confusion Matrix (Test Set, N=200)"
    p_cm.font.name = FONT_FAMILY
    p_cm.font.size = Pt(19)
    p_cm.font.italic = True
    p_cm.alignment = PP_ALIGN.CENTER
    p_cm.font.color.rgb = BLACK
    print("Slide 10 configured.")

    # =========================================================================
    # SLIDE 11: ABLATION STUDY & MODEL INTERPRETABILITY (index 10)
    # =========================================================================
    s11 = prs.slides[10]
    clear_slide_content(s11)
    add_header_and_chrome(s11, 11, "ABLATION STUDY & MODEL INTERPRETABILITY")
    
    # Top Row: 2 Charts Side by Side
    fig_abl = os.path.join(FIGURES_DIR, "ablation_comparison.png")
    if os.path.exists(fig_abl):
        s11.shapes.add_picture(fig_abl, Inches(1.3), Inches(2.4), width=Inches(8.4), height=Inches(4.18))
    tb_ab_cap = s11.shapes.add_textbox(Inches(1.3), Inches(6.65), Inches(8.4), Inches(0.4))
    p_abc = tb_ab_cap.text_frame.paragraphs[0]
    p_abc.text = "Figure: Architectural Ablation Study (5-Fold CV)"
    p_abc.font.name = FONT_FAMILY
    p_abc.font.size = Pt(19)
    p_abc.font.italic = True
    p_abc.alignment = PP_ALIGN.CENTER
    p_abc.font.color.rgb = BLACK
    
    fig_att = os.path.join(FIGURES_DIR, "attention_explainability.png")
    if os.path.exists(fig_att):
        s11.shapes.add_picture(fig_att, Inches(10.3), Inches(2.4), width=Inches(8.4), height=Inches(4.18))
    tb_at_cap = s11.shapes.add_textbox(Inches(10.3), Inches(6.65), Inches(8.4), Inches(0.4))
    p_atc = tb_at_cap.text_frame.paragraphs[0]
    p_atc.text = "Figure: Relational Attention Weights in ESC13 Chain"
    p_atc.font.name = FONT_FAMILY
    p_atc.font.size = Pt(19)
    p_atc.font.italic = True
    p_atc.alignment = PP_ALIGN.CENTER
    p_atc.font.color.rgb = BLACK
    
    # Bottom Row: Analytical Takeaways
    create_badge(s11, Inches(1.3), Inches(7.15), Inches(17.4), Inches(0.55), "Key Analytical Takeaways")
    tb_ab_bullets = s11.shapes.add_textbox(Inches(1.3), Inches(7.8), Inches(17.4), Inches(2.0))
    tf_abb = tb_ab_bullets.text_frame
    add_bullets(tf_abb, [
        "• Validation of Theorem 1: Removing residual skip connections drops Macro-F1 from 0.9986 to 0.4768 (-52.18% collapse, p = 1.31e-6), empirically verifying representation oversmoothing over deep paths.",
        "• Attention Interpretability: High relational attention weights (alpha > 0.85) align precisely with ground-truth escalation edges (GenericAll, WriteDacl, Enroll), providing instant visual proof for security analysts."
    ], font_size=21, space_after=10, bold_prefix=True)
    print("Slide 11 configured.")

    # =========================================================================
    # SLIDE 12: NEURO-SYMBOLIC HYBRID VERIFICATION (index 11)
    # =========================================================================
    s12 = prs.slides[11]
    clear_slide_content(s12)
    add_header_and_chrome(s12, 12, "NEURO-SYMBOLIC HYBRID VERIFICATION")
    
    # Left Column: Shortcut Collapse & Solution
    create_badge(s12, Inches(1.3), Inches(2.4), Inches(8.2), Inches(0.65), "Neural Shortcut Collapse Discovery")
    tb_sc = s12.shapes.add_textbox(Inches(1.3), Inches(3.2), Inches(8.2), Inches(2.3))
    tf_sc = tb_sc.text_frame
    add_bullets(tf_sc, [
        "• Adversarial Hard Negatives: Dangerous template flags paired with admin-only DACLs (ground-truth Safe).",
        "• Neural Shortcut Collapse: Pure GNN accuracy drops to 1.59% (1/63)! The network is tricked by local syntactic similarity."
    ], font_size=20, space_after=10, bold_prefix=True)
    
    create_badge(s12, Inches(1.3), Inches(5.6), Inches(8.2), Inches(0.65), "Two-Tier Neuro-Symbolic Solution")
    tb_tt = s12.shapes.add_textbox(Inches(1.3), Inches(6.4), Inches(8.2), Inches(3.4))
    tf_tt = tb_tt.text_frame
    add_bullets(tf_tt, [
        "• Tier 1 (Neural Filter): Fast GNN screening prunes 99.8% of benign candidates in milliseconds.",
        "• Tier 2 (Symbolic Engine): Formal BFS validator verifies cryptographic reachability on candidate subgraphs.",
        "• Outcome: 99.91% verified accuracy, 0% false alarm escape, and 128 ms latency at threshold 0.50."
    ], font_size=20, space_after=10, bold_prefix=True)
    
    # Right Column: Pipeline Diagram + Bar Chart
    fig_nsp = os.path.join(FIGURES_DIR, "neuro_symbolic_pipeline.png")
    if os.path.exists(fig_nsp):
        s12.shapes.add_picture(fig_nsp, Inches(9.8), Inches(2.4), width=Inches(8.9), height=Inches(4.1))
        
    fig_hn = os.path.join(FIGURES_DIR, "hard_negatives_comparison.png")
    if os.path.exists(fig_hn):
        s12.shapes.add_picture(fig_hn, Inches(10.0), Inches(6.6), width=Inches(8.5), height=Inches(3.2))
    print("Slide 12 configured.")

    # =========================================================================
    # SLIDE 13: SCALABILITY & AUTONOMOUS REMEDIATION (index 12)
    # =========================================================================
    s13 = prs.slides[12]
    clear_slide_content(s13)
    add_header_and_chrome(s13, 13, "SCALABILITY & AUTONOMOUS REMEDIATION")
    
    # Left Column: Scalability & Theorem 2
    create_badge(s13, Inches(1.3), Inches(2.4), Inches(8.2), Inches(0.65), "Sub-Second Operational Scalability")
    tb_scale = s13.shapes.add_textbox(Inches(1.3), Inches(3.2), Inches(8.2), Inches(2.6))
    tf_scale = tb_scale.text_frame
    add_bullets(tf_scale, [
        "• 1,000 Nodes: 42 ms latency",
        "• 10,000 Nodes: 343 ms latency (12.4x faster than Dijkstra)",
        "• 50,000 Nodes: 1.62 seconds across forest boundaries",
        "• Real-Time Auditing: Enables background scans every 60s without disrupting production authentication traffic."
    ], font_size=20, space_after=8, bold_prefix=True)
    
    create_badge(s13, Inches(1.3), Inches(5.9), Inches(8.2), Inches(0.65), "Theorem 2 (MPAI NP-Hardness) & Remediation")
    tb_thm2 = s13.shapes.add_textbox(Inches(1.3), Inches(6.7), Inches(8.2), Inches(3.1))
    tf_thm2 = tb_thm2.text_frame
    add_bullets(tf_thm2, [
        "• Theorem 2 Statement:\nThe Minimum Perturbation Attack Interdiction (MPAI) problem in ADCS multigraphs is NP-hard (reduced from Directed Multiway Cut).",
        "• Budgeted Path Remediation:\nGreedy path-based interdiction severs 68.6% ± 11.7% of critical attack paths at budget B_ops = 24 with minimal operational disruption."
    ], font_size=20, space_after=10, bold_prefix=True)
    
    # Right Column: Scalability + PPO Dynamics Figures
    fig_sm = os.path.join(FIGURES_DIR, "scalability_metrics.png")
    if os.path.exists(fig_sm):
        s13.shapes.add_picture(fig_sm, Inches(10.5), Inches(2.3), width=Inches(7.8), height=Inches(3.8))
        
    fig_gt = os.path.join(FIGURES_DIR, "game_theoretic_convergence.png")
    if os.path.exists(fig_gt):
        s13.shapes.add_picture(fig_gt, Inches(10.0), Inches(6.3), width=Inches(8.8), height=Inches(3.5))
    print("Slide 13 configured.")

    # =========================================================================
    # SLIDE 14: CONCLUSION & CONTRIBUTIONS (index 13)
    # =========================================================================
    s14 = prs.slides[13]
    clear_slide_content(s14)
    # Add background landscape picture for Slide 14
    s14.shapes.add_picture(BG_TEXTURE, Inches(0), Inches(0), width=Inches(20), height=Inches(11.25))
    add_header_and_chrome(s14, 14, "CONCLUSION & CONTRIBUTIONS")
    
    # Left Column: 6 Tangible Academic Contributions
    create_badge(s14, Inches(1.3), Inches(2.4), Inches(9.2), Inches(0.65), "6 Tangible Academic Contributions")
    tb_cont = s14.shapes.add_textbox(Inches(1.3), Inches(3.2), Inches(9.2), Inches(6.6))
    tf_cont = tb_cont.text_frame
    add_bullets(tf_cont, [
        "1. Heterogeneous Multigraph Formalization: First formal multigraph schema capturing all 13 ADCS escalation classes across users, groups, templates, CAs, and domains.",
        "2. Mathematical Bounds (Theorem 1): Proved gradient preservation lower bounds, mathematically guaranteeing anti-oversmoothing across 4+ hops.",
        "3. Empirical Benchmark Suite: 0.9986 Macro-F1 across 700 topologies and 5-fold cross-validation on realistic GOAD multi-forest testbeds.",
        "4. Attention Explainability: Direct visual interpretation linking high relational attention weights to critical escalation edges.",
        "5. Neuro-Symbolic Pipeline: Production-ready hybrid eliminating false positives on adversarial hard negatives (99.91% verified accuracy).",
        "6. Theorem 2 & Autonomous Interdiction: Formal NP-hardness proof via Directed Multiway Cut and convergent PPO remediation agent."
    ], font_size=19, space_after=12, bold_prefix=True)
    
    # Right Column: Future Directions & Milestones
    create_badge(s14, Inches(11.0), Inches(2.4), Inches(7.7), Inches(0.65), "Future Research Directions")
    tb_fut = s14.shapes.add_textbox(Inches(11.0), Inches(3.2), Inches(7.7), Inches(3.0))
    tf_fut = tb_fut.text_frame
    add_bullets(tf_fut, [
        "• Real-time honeypot certificate injection for active deception and automated attacker quarantine.",
        "• Extension to cloud-hybrid Microsoft Entra ID (Azure AD) identity multigraphs and cross-tenant sync mechanisms.",
        "• Integration of zero-knowledge proof (ZKP) verification for cross-domain certificate issuance validation."
    ], font_size=20, space_after=12, bold_prefix=True)
    
    create_badge(s14, Inches(11.0), Inches(6.4), Inches(7.7), Inches(0.65), "Project & Thesis Milestones")
    tb_mil = s14.shapes.add_textbox(Inches(11.0), Inches(7.2), Inches(7.7), Inches(2.4))
    tf_mil = tb_mil.text_frame
    add_bullets(tf_mil, [
        "• Course Code: ECE 452 (Project and Thesis)",
        "• Department: Electronics & Communication Engineering (ECE)",
        "• Institution: Hajee Mohammad Danesh Science and Technology University (HSTU)",
        "• Defense Session: October 2026"
    ], font_size=20, space_after=8, bold_prefix=True)
    print("Slide 14 configured.")

    # =========================================================================
    # SLIDE 15: THANK YOU / Q&A (index 14)
    # =========================================================================
    s15 = prs.slides[14]
    # Slide 15 is the Thank You slide from old.pptx, already verified perfect!
    print("Slide 15 (Thank You & Q&A) preserved.")

    # Save outputs
    prs.save(OUTPUT_PPTX)
    shutil.copy(OUTPUT_PPTX, OUTPUT_PPTX_CONV)
    print("Successfully built and saved presentation to:")
    print("  ->", OUTPUT_PPTX)
    print("  ->", OUTPUT_PPTX_CONV)

if __name__ == "__main__":
    build_presentation()
