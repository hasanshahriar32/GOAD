#!/usr/bin/env python3
"""
Generate an Academic PowerPoint Presentation (.pptx) for the CertGraph Thesis Defense.
Department of Electronics and Communication Engineering (ECE), HSTU.
"""

import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# ─── COLOR PALETTE (Academic Oxford Navy & HSTU Colors) ───────────────────────
NAVY_PRIMARY    = RGBColor(12, 35, 64)    # #0C2340 Oxford Navy
NAVY_DARK       = RGBColor(7, 22, 38)     # #071626
NAVY_LIGHT      = RGBColor(29, 60, 106)   # #1D3C6A
GOLD_ACCENT     = RGBColor(184, 134, 11)  # #B8860B Academic Gold
GOLD_LIGHT      = RGBColor(225, 178, 45)  # #E1B22D
CRIMSON_ACCENT  = RGBColor(139, 0, 0)     # #8B0000 Academic Alert
TEAL_ACCENT     = RGBColor(0, 109, 119)   # #006D77 Finding Accent
TEXT_MAIN       = RGBColor(26, 32, 44)    # #1A202C
TEXT_MUTED      = RGBColor(74, 85, 104)   # #4A5568
TEXT_LIGHT      = RGBColor(113, 128, 150) # #718096
WHITE           = RGBColor(255, 255, 255)
BG_CANVAS       = RGBColor(248, 250, 252) # #F8FAFC
CARD_BG_DEFAULT = RGBColor(248, 250, 252)
CARD_BG_THEOREM = RGBColor(240, 247, 255) # Light Blue
CARD_BG_ALERT   = RGBColor(255, 250, 250) # Light Red
CARD_BG_FINDING = RGBColor(254, 253, 247) # Light Gold
BORDER_LIGHT    = RGBColor(226, 232, 240)
BORDER_MID      = RGBColor(203, 213, 225)

FONT_SERIF = "Georgia"
FONT_SANS  = "Calibri"
FONT_MONO  = "Consolas"

FIG_DIR = "/home/hs32/Desktop/GOAD/thesis_paper/figures"

def create_presentation():
    prs = pptx.Presentation()
    prs.slide_width  = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout     = prs.slide_layouts[6]
    total_slides     = 16

    # ─── HELPER: Header Banner ────────────────────────────────────────────────
    def add_header(slide, section_label, title_text):
        # Navy Header Band
        hb = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.10))
        hb.fill.solid()
        hb.fill.fore_color.rgb = NAVY_PRIMARY
        hb.line.color.rgb = NAVY_PRIMARY

        # Gold Accent Stripe
        gb = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(1.10), Inches(13.333), Inches(0.04))
        gb.fill.solid()
        gb.fill.fore_color.rgb = GOLD_ACCENT
        gb.line.color.rgb = GOLD_ACCENT

        # Section Label
        sbox = slide.shapes.add_textbox(Inches(0.6), Inches(0.12), Inches(9.5), Inches(0.28))
        stf = sbox.text_frame
        stf.word_wrap = True
        stf.margin_top = stf.margin_bottom = stf.margin_left = stf.margin_right = 0
        sp = stf.paragraphs[0]
        sp.text = section_label.upper()
        sp.font.name = FONT_SANS
        sp.font.size = Pt(10)
        sp.font.bold = True
        sp.font.color.rgb = GOLD_LIGHT

        # Slide Title
        tbox = slide.shapes.add_textbox(Inches(0.6), Inches(0.40), Inches(9.5), Inches(0.60))
        ttf = tbox.text_frame
        ttf.word_wrap = True
        ttf.margin_top = ttf.margin_bottom = ttf.margin_left = ttf.margin_right = 0
        tp = ttf.paragraphs[0]
        tp.text = title_text
        tp.font.name = FONT_SERIF
        tp.font.size = Pt(20)
        tp.font.bold = True
        tp.font.color.rgb = WHITE

        # Right Academic Tag
        rbox = slide.shapes.add_textbox(Inches(10.2), Inches(0.22), Inches(2.6), Inches(0.65))
        rtf = rbox.text_frame
        rtf.word_wrap = True
        rtf.margin_top = rtf.margin_bottom = rtf.margin_left = rtf.margin_right = 0
        rp1 = rtf.paragraphs[0]
        rp1.alignment = PP_ALIGN.RIGHT
        rp1.text = "HSTU DINANJPUR • ECE"
        rp1.font.name = FONT_SANS
        rp1.font.size = Pt(10)
        rp1.font.bold = True
        rp1.font.color.rgb = WHITE
        rp2 = rtf.add_paragraph()
        rp2.alignment = PP_ALIGN.RIGHT
        rp2.text = "Thesis Defense • Oct 2026"
        rp2.font.name = FONT_SANS
        rp2.font.size = Pt(9.5)
        rp2.font.color.rgb = RGBColor(203, 213, 225)

    # ─── HELPER: Footer Banner ────────────────────────────────────────────────
    def add_footer(slide, slide_num):
        fb = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(7.05), Inches(13.333), Inches(0.45))
        fb.fill.solid()
        fb.fill.fore_color.rgb = RGBColor(241, 245, 249)
        fb.line.color.rgb = BORDER_MID
        fb.line.width = Pt(1)

        # Left: Paper Title
        lbox = slide.shapes.add_textbox(Inches(0.6), Inches(7.13), Inches(6.0), Inches(0.30))
        ltf = lbox.text_frame
        ltf.margin_top = ltf.margin_bottom = ltf.margin_left = ltf.margin_right = 0
        lp = ltf.paragraphs[0]
        lp.text = "CertGraph: Heterogeneous GAT for ADCS Vulnerability Detection"
        lp.font.name = FONT_SANS
        lp.font.size = Pt(9.5)
        lp.font.bold = True
        lp.font.color.rgb = NAVY_PRIMARY

        # Center: University & Course
        cbox = slide.shapes.add_textbox(Inches(6.6), Inches(7.13), Inches(4.5), Inches(0.30))
        ctf = cbox.text_frame
        ctf.margin_top = ctf.margin_bottom = ctf.margin_left = ctf.margin_right = 0
        cp = ctf.paragraphs[0]
        cp.text = "HSTU ECE Thesis Defense (Course: ECE 452)"
        cp.font.name = FONT_SANS
        cp.font.size = Pt(9)
        cp.font.italic = True
        cp.font.color.rgb = TEXT_MUTED

        # Right: Slide Number
        rbox = slide.shapes.add_textbox(Inches(11.2), Inches(7.13), Inches(1.5), Inches(0.30))
        rtf = rbox.text_frame
        rtf.margin_top = rtf.margin_bottom = rtf.margin_left = rtf.margin_right = 0
        rp = rtf.paragraphs[0]
        rp.alignment = PP_ALIGN.RIGHT
        rp.text = f"Slide {slide_num:02d} / {total_slides:02d}"
        rp.font.name = FONT_MONO
        rp.font.size = Pt(9.5)
        rp.font.bold = True
        rp.font.color.rgb = NAVY_PRIMARY

    # ─── HELPER: Academic Card Box ────────────────────────────────────────────
    def add_card(slide, x, y, w, h, title, bg_color=CARD_BG_DEFAULT, accent_color=NAVY_PRIMARY):
        # Card Body
        card = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = BORDER_MID
        card.line.width = Pt(1)

        # Left Accent Stripe
        stripe = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(0.08), Inches(h))
        stripe.fill.solid()
        stripe.fill.fore_color.rgb = accent_color
        stripe.line.color.rgb = accent_color

        # Card Title
        if title:
            tbox = slide.shapes.add_textbox(Inches(x + 0.18), Inches(y + 0.10), Inches(w - 0.30), Inches(0.32))
            ttf = tbox.text_frame
            ttf.word_wrap = True
            ttf.margin_top = ttf.margin_bottom = ttf.margin_left = ttf.margin_right = 0
            tp = ttf.paragraphs[0]
            tp.text = title
            tp.font.name = FONT_SERIF
            tp.font.size = Pt(12)
            tp.font.bold = True
            tp.font.color.rgb = accent_color

        # Return text frame for content
        cbox = slide.shapes.add_textbox(Inches(x + 0.18), Inches(y + 0.44 if title else y + 0.12), Inches(w - 0.32), Inches(h - 0.52 if title else h - 0.20))
        ctf = cbox.text_frame
        ctf.word_wrap = True
        ctf.margin_top = ctf.margin_bottom = ctf.margin_left = ctf.margin_right = 0
        return ctf

    # ─── HELPER: Image Frame ──────────────────────────────────────────────────
    def add_image_card(slide, x, y, w, h, img_path, caption):
        # Frame Box
        frame = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
        frame.fill.solid()
        frame.fill.fore_color.rgb = WHITE
        frame.line.color.rgb = BORDER_MID
        frame.line.width = Pt(1)

        caption_h = 0.55 if caption else 0.05
        img_avail_w = w - 0.20
        img_avail_h = h - caption_h - 0.15

        if os.path.exists(img_path):
            try:
                # Add picture centered
                pic = slide.shapes.add_picture(img_path, Inches(x + 0.10), Inches(y + 0.08), width=Inches(img_avail_w))
                # Adjust if height exceeds
                if pic.height > Inches(img_avail_h):
                    pic.height = Inches(img_avail_h)
                # Recenter horizontally
                pic.left = int(Inches(x) + (Inches(w) - pic.width) / 2)
            except Exception as e:
                print(f"Warning: could not insert picture {img_path}: {e}")

        # Caption
        if caption:
            cbox = slide.shapes.add_textbox(Inches(x + 0.10), Inches(y + h - caption_h), Inches(w - 0.20), Inches(caption_h))
            ctf = cbox.text_frame
            ctf.word_wrap = True
            ctf.margin_top = ctf.margin_bottom = ctf.margin_left = ctf.margin_right = 0
            cp = ctf.paragraphs[0]
            cp.alignment = PP_ALIGN.CENTER
            cp.text = caption
            cp.font.name = FONT_SERIF
            cp.font.size = Pt(9.5)
            cp.font.italic = True
            cp.font.color.rgb = TEXT_MUTED

    # ─── HELPER: Bullet Points ────────────────────────────────────────────────
    def add_para(tf, text, bold_prefix="", pt_size=11, color=TEXT_MAIN, space_after=6, is_bullet=True):
        p = tf.add_paragraph() if len(tf.paragraphs[0].text) > 0 else tf.paragraphs[0]
        p.space_after = Pt(space_after)
        if bold_prefix:
            r1 = p.add_run()
            r1.text = ("• " if is_bullet else "") + bold_prefix + " "
            r1.font.name = FONT_SANS
            r1.font.bold = True
            r1.font.size = Pt(pt_size)
            r1.font.color.rgb = color
        else:
            if is_bullet:
                r0 = p.add_run()
                r0.text = "• "
                r0.font.name = FONT_SANS
                r0.font.size = Pt(pt_size)
                r0.font.color.rgb = color

        r2 = p.add_run()
        r2.text = text
        r2.font.name = FONT_SANS
        r2.font.bold = False
        r2.font.size = Pt(pt_size)
        r2.font.color.rgb = color

    # =========================================================================
    # SLIDE 1: FORMAL TITLE SLIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)

    # Top institutional bar
    top_band = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.12))
    top_band.fill.solid()
    top_band.fill.fore_color.rgb = NAVY_PRIMARY
    top_band.line.color.rgb = NAVY_PRIMARY

    gold_stripe = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0.12), Inches(13.333), Inches(0.04))
    gold_stripe.fill.solid()
    gold_stripe.fill.fore_color.rgb = GOLD_ACCENT
    gold_stripe.line.color.rgb = GOLD_ACCENT

    # HSTU Logo (aspect ratio 241x354 -> set height=1.05in, width~0.71in)
    logo_path = os.path.join(FIG_DIR, "hstu_logo.png")
    if os.path.exists(logo_path):
        s1.shapes.add_picture(logo_path, Inches(6.31), Inches(0.32), height=Inches(1.05))

    # University & Department text
    u_box = s1.shapes.add_textbox(Inches(1.5), Inches(1.48), Inches(10.333), Inches(0.75))
    u_tf = u_box.text_frame
    u_tf.word_wrap = True
    up1 = u_tf.paragraphs[0]
    up1.alignment = PP_ALIGN.CENTER
    up1.text = "HAJEE MOHAMMAD DANESH SCIENCE AND TECHNOLOGY UNIVERSITY"
    up1.font.name = FONT_SERIF
    up1.font.size = Pt(15.5)
    up1.font.bold = True
    up1.font.color.rgb = NAVY_PRIMARY

    up2 = u_tf.add_paragraph()
    up2.alignment = PP_ALIGN.CENTER
    up2.text = "Department of Electronics and Communication Engineering (ECE)"
    up2.font.name = FONT_SANS
    up2.font.size = Pt(11.5)
    up2.font.color.rgb = TEXT_MUTED

    # Gold Divider Line
    d_line = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(3.0), Inches(2.32), Inches(7.333), Inches(0.02))
    d_line.fill.solid()
    d_line.fill.fore_color.rgb = GOLD_ACCENT
    d_line.line.color.rgb = GOLD_ACCENT

    # Badge & Thesis Title Box
    t_box = s1.shapes.add_textbox(Inches(1.2), Inches(2.42), Inches(10.933), Inches(2.35))
    t_tf = t_box.text_frame
    t_tf.word_wrap = True

    tp0 = t_tf.paragraphs[0]
    tp0.alignment = PP_ALIGN.CENTER
    tp0.text = "BACHELOR OF SCIENCE IN ECE • FINAL YEAR THESIS DEFENSE (COURSE: ECE 452)"
    tp0.font.name = FONT_SANS
    tp0.font.size = Pt(10)
    tp0.font.bold = True
    tp0.font.color.rgb = GOLD_ACCENT

    tp1 = t_tf.add_paragraph()
    tp1.alignment = PP_ALIGN.CENTER
    tp1.space_before = Pt(5)
    tp1.text = "CertGraph: Heterogeneous Graph Attention Networks for Active Directory Certificate Services Vulnerability Detection and Autonomous Defense"
    tp1.font.name = FONT_SERIF
    tp1.font.size = Pt(21)
    tp1.font.bold = True
    tp1.font.color.rgb = NAVY_DARK

    tp2 = t_tf.add_paragraph()
    tp2.alignment = PP_ALIGN.CENTER
    tp2.space_before = Pt(5)
    tp2.text = "A Rigorous Graph Neural Framework for Multi-Hop Topological Privilege Escalation Analysis"
    tp2.font.name = FONT_SERIF
    tp2.font.size = Pt(12)
    tp2.font.italic = True
    tp2.font.color.rgb = TEXT_MUTED

    # Meta Cards: Candidate IDs and Examination Committee
    # Card 1: Candidates
    c1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.5), Inches(4.90), Inches(5.0), Inches(1.85))
    c1.fill.solid()
    c1.fill.fore_color.rgb = CARD_BG_DEFAULT
    c1.line.color.rgb = BORDER_MID
    s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.5), Inches(4.90), Inches(0.08), Inches(1.85)).fill.solid()

    c1_box = s1.shapes.add_textbox(Inches(1.75), Inches(5.02), Inches(4.6), Inches(1.6))
    c1_tf = c1_box.text_frame
    c1_p1 = c1_tf.paragraphs[0]
    c1_p1.text = "CANDIDATE STUDENT IDS"
    c1_p1.font.name = FONT_SANS
    c1_p1.font.size = Pt(10)
    c1_p1.font.bold = True
    c1_p1.font.color.rgb = NAVY_PRIMARY

    c1_p2 = c1_tf.add_paragraph()
    c1_p2.text = "Department of Electronics and Communication Engineering"
    c1_p2.font.name = FONT_SANS
    c1_p2.font.size = Pt(10)
    c1_p2.font.color.rgb = TEXT_MUTED

    c1_p3 = c1_tf.add_paragraph()
    c1_p3.space_before = Pt(8)
    c1_p3.text = "ID: 2002126   |   ID: 2002138   |   ID: 2102151"
    c1_p3.font.name = FONT_MONO
    c1_p3.font.size = Pt(11)
    c1_p3.font.bold = True
    c1_p3.font.color.rgb = NAVY_PRIMARY

    # Card 2: Examination Committee
    c2 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.8), Inches(4.90), Inches(5.0), Inches(1.85))
    c2.fill.solid()
    c2.fill.fore_color.rgb = CARD_BG_DEFAULT
    c2.line.color.rgb = BORDER_MID
    s2_s = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.8), Inches(4.90), Inches(0.08), Inches(1.85))
    s2_s.fill.solid()
    s2_s.fill.fore_color.rgb = GOLD_ACCENT

    c2_box = s1.shapes.add_textbox(Inches(7.05), Inches(5.02), Inches(4.6), Inches(1.6))
    c2_tf = c2_box.text_frame
    c2_p1 = c2_tf.paragraphs[0]
    c2_p1.text = "ACADEMIC EXAMINATION COMMITTEE"
    c2_p1.font.name = FONT_SANS
    c2_p1.font.size = Pt(10)
    c2_p1.font.bold = True
    c2_p1.font.color.rgb = GOLD_ACCENT

    c2_p2 = c2_tf.add_paragraph()
    c2_p2.text = "Department of ECE, Faculty of Computer Science & Engineering"
    c2_p2.font.name = FONT_SANS
    c2_p2.font.size = Pt(10)
    c2_p2.font.bold = True
    c2_p2.font.color.rgb = TEXT_MAIN

    c2_p3 = c2_tf.add_paragraph()
    c2_p3.text = "Hajee Mohammad Danesh Science and Technology University, Dinajpur-5200"
    c2_p3.font.name = FONT_SANS
    c2_p3.font.size = Pt(9.5)
    c2_p3.font.color.rgb = TEXT_MUTED

    c2_p4 = c2_tf.add_paragraph()
    c2_p4.text = "Academic Session Defense: October 2026"
    c2_p4.font.name = FONT_SANS
    c2_p4.font.size = Pt(9)
    c2_p4.font.italic = True
    c2_p4.font.color.rgb = TEXT_LIGHT

    add_footer(s1, 1)

    # =========================================================================
    # SLIDE 2: DEFENSE PRESENTATION OUTLINE
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "Section 1.0 • Agenda", "Defense Presentation Outline")

    card2_1 = add_card(s2, 0.6, 1.4, 5.9, 2.55, "Part I: Motivation, Background & Research Questions", CARD_BG_DEFAULT, NAVY_PRIMARY)
    add_para(card2_1, "The ADCS attack surface and multi-hop privilege escalation.", bold_prefix="1.1 Enterprise Context:")
    add_para(card2_1, "Why Certipy, BloodHound, and rule engines fail at scale.", bold_prefix="1.2 Tool Limitations:")
    add_para(card2_1, "Representation, zero-shot transfer, robustness, mitigation.", bold_prefix="1.3 Formal Questions (RQ1–4):")
    add_para(card2_1, "Detailed walk-through of cross-forest certificate abuse.", bold_prefix="1.4 ESC13 Case Study:")

    card2_2 = add_card(s2, 0.6, 4.15, 5.9, 2.65, "Part II: Methodology & Mathematical Architecture", CARD_BG_DEFAULT, NAVY_PRIMARY)
    add_para(card2_2, "6 entity types and 18 multi-relational edges.", bold_prefix="2.1 Graph Formulation:")
    add_para(card2_2, "Type-specific projections, attention aggregation, dual heads.", bold_prefix="2.2 CertGraph Architecture:")
    add_para(card2_2, "Proof of gradient preservation and anti-oversmoothing.", bold_prefix="2.3 Theorem 1:")

    card2_3 = add_card(s2, 6.8, 1.4, 5.9, 2.55, "Part III: Empirical Evaluation & Ablation Studies", CARD_BG_DEFAULT, NAVY_PRIMARY)
    add_para(card2_3, "Game of Active Directory (GOAD) and 700 ADSynth forests.", bold_prefix="3.1 Experimental Testbed:")
    add_para(card2_3, "CertGraph vs. Certipy, BloodHound, GCN, GAT, GraphSAGE.", bold_prefix="3.2 Baseline Benchmark:")
    add_para(card2_3, "Impact of residual skip connections and attention weights.", bold_prefix="3.3 Ablation Studies:")
    add_para(card2_3, "343 ms sub-second inference across 10,000 nodes.", bold_prefix="3.4 Scalability Metrics:")

    card2_4 = add_card(s2, 6.8, 4.15, 5.9, 2.65, "Part IV: Adversarial Synthesis, Defense & Conclusion", CARD_BG_DEFAULT, NAVY_PRIMARY)
    add_para(card2_4, "Neural shortcut collapse (1.59%) & Neuro-Symbolic resolution.", bold_prefix="4.1 Adversarial Negatives:")
    add_para(card2_4, "MPAI NP-hardness and game-theoretic policy convergence.", bold_prefix="4.2 Theorem 2 & Defense:")
    add_para(card2_4, "Direct synthesis of RQ1–RQ4 and committee discussion.", bold_prefix="4.3 Contributions & Conclusion:")

    add_footer(s2, 2)

    # =========================================================================
    # SLIDE 3: PROBLEM STATEMENT & MOTIVATION
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "Section 1.1 • Context & Motivation", "Active Directory Certificate Services (ADCS) & Enterprise Risk")

    c3_1 = add_card(s3, 0.6, 1.35, 6.6, 2.65, "The Strategic Role of ADCS in Enterprise Security", CARD_BG_DEFAULT, NAVY_PRIMARY)
    add_para(c3_1, "Active Directory (AD) manages identity and access control in over 90% of Fortune 500 networks.", is_bullet=False)
    add_para(c3_1, "Kerberos PKINIT (Public Key Cryptography for Initial Authentication).", bold_prefix="Authentication Backbone:")
    add_para(c3_1, "Smart card logon, VPN gateways, and computer domain machine enrollment.", bold_prefix="Identity Verification:")
    add_para(c3_1, "Code signing, S/MIME, and internal SSL/TLS communication infrastructure.", bold_prefix="Cryptographic Trust:")

    c3_2 = add_card(s3, 0.6, 4.15, 6.6, 2.65, "The Fundamental Vulnerability: Multi-Hop Escalation", CARD_BG_ALERT, CRIMSON_ACCENT)
    add_para(c3_2, "ADCS security is governed by intricate webs of certificate templates, enrollment permissions, CA security descriptors, and group memberships.", is_bullet=False)
    add_para(c3_2, "Misconfigurations (ESC1 through ESC13) are rarely isolated syntax bugs.", bold_prefix="Chained Escalations:")
    add_para(c3_2, "They emerge from chained permissions across heterogeneous objects.", bold_prefix="Relational Abuse:")
    add_para(c3_2, "An attacker compromises a benign template, requests a certificate for Domain Admin, and executes DC takeover.", bold_prefix="Catastrophic Impact:")

    add_image_card(s3, 7.4, 1.35, 5.3, 3.8, os.path.join(FIG_DIR, "adcs_attack_graph_schema.png"), "Figure 1.1: Heterogeneous entity schema in ADCS privilege escalation.")

    c3_d = add_card(s3, 7.4, 5.30, 5.3, 1.50, "Core Research Dilemma", CARD_BG_FINDING, GOLD_ACCENT)
    add_para(c3_d, "Can graph neural networks learn topological privilege escalation chains without relying on fragile heuristic rule sets that fail on complex, unseen enterprise topologies?", is_bullet=False, pt_size=10.5)

    add_footer(s3, 3)

    # =========================================================================
    # SLIDE 4: SYSTEMIC LIMITATIONS OF CURRENT DEFENSE TOOLS
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "Section 1.2 • State-of-the-Art Analysis", "Systemic Limitations of Current Defense Tools")

    c4_1 = add_card(s4, 0.6, 1.35, 3.85, 2.4, "1. Static Rule Engines (Certipy)", CARD_BG_ALERT, CRIMSON_ACCENT)
    add_para(c4_1, "Relies on hardcoded IF-THEN syntactic pattern matching.", pt_size=10)
    add_para(c4_1, "Zero-shot failure on uncataloged or compound escalation paths.", pt_size=10)
    add_para(c4_1, "Blind to global graph reachability context.", pt_size=10)

    c4_2 = add_card(s4, 4.75, 1.35, 3.85, 2.4, "2. Combinatorial Search (BloodHound)", CARD_BG_ALERT, CRIMSON_ACCENT)
    add_para(c4_2, "Dijkstra/BFS shortest-path traversal over ingested ACLs.", pt_size=10)
    add_para(c4_2, "Scalability bottleneck: combinatorial explosion on 100k+ nodes.", pt_size=10)
    add_para(c4_2, "Treats direct admin rights identically to weak speculative edges.", pt_size=10)

    c4_3 = add_card(s4, 8.9, 1.35, 3.85, 2.4, "3. Standard ML / GNNs (MLP/GCN)", CARD_BG_ALERT, CRIMSON_ACCENT)
    add_para(c4_3, "Flat MLPs discard relational edge topologies entirely.", pt_size=10)
    add_para(c4_3, "Homogeneous GCNs are relationally blind (treats all edges equally).", pt_size=10)
    add_para(c4_3, "Catastrophic oversmoothing across 4+ hop privilege chains.", pt_size=10)

    # Comparison Table
    table_shape = s4.shapes.add_table(5, 5, Inches(0.6), Inches(3.95), Inches(12.133), Inches(2.6))
    table = table_shape.table

    headers = ["Evaluation Dimension", "Rule Engines (Certipy)", "Graph Search (BloodHound)", "Standard GNNs (GCN)", "CertGraph (Proposed)"]
    for col_idx, h_text in enumerate(headers):
        cell = table.cell(0, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY_PRIMARY
        p = cell.text_frame.paragraphs[0]
        p.text = h_text
        p.font.name = FONT_SANS
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = WHITE

    rows_data = [
        ("Multi-Relational Topology", "No (Local attributes only)", "Homogeneous Graph Search", "Edge-Type Blind", "Hetero Multi-Relation Attention"),
        ("Zero-Shot Generalization", "Fails on novel paths", "Requires manual query crafting", "Moderate", "1.0000 Macro-F1 on ADSynth"),
        ("Inference Scalability", "O(N) Local Scan", "O(V + E) Exponential worst-case", "O(L * |E|) (Oversmooths)", "343 ms / 10,000 nodes"),
        ("Autonomous Remediation", "None (Manual audit)", "None (Informational only)", "None", "Theorem 2 (MPAI NP-Hard + RL)")
    ]

    for row_idx, r_data in enumerate(rows_data):
        for col_idx, val in enumerate(r_data):
            cell = table.cell(row_idx + 1, col_idx)
            cell.fill.solid()
            if row_idx % 2 == 1:
                cell.fill.fore_color.rgb = RGBColor(248, 250, 252)
            else:
                cell.fill.fore_color.rgb = WHITE
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.name = FONT_SANS
            p.font.size = Pt(9.5)
            if col_idx == 4:
                p.font.bold = True
                p.font.color.rgb = NAVY_PRIMARY
                cell.fill.fore_color.rgb = RGBColor(240, 247, 255)
            else:
                p.font.color.rgb = TEXT_MAIN

    add_footer(s4, 4)

    # =========================================================================
    # SLIDE 5: FORMAL RESEARCH QUESTIONS & SCOPE
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "Section 1.3 • Research Framework", "Formal Research Questions & Theoretical Scope")

    c5_1 = add_card(s5, 0.6, 1.35, 5.9, 2.5, "RQ1: Heterogeneous Graph Representation", CARD_BG_THEOREM, NAVY_LIGHT)
    add_para(c5_1, "Can heterogeneous graph attention networks effectively model the multi-relational, directed topology of Active Directory Certificate Services to detect subtle, multi-hop privilege escalation paths with high precision?", is_bullet=False, pt_size=11)

    c5_2 = add_card(s5, 6.8, 1.35, 5.9, 2.5, "RQ2: Generalization & Zero-Shot Transfer", CARD_BG_THEOREM, NAVY_LIGHT)
    add_para(c5_2, "Does CertGraph maintain classification fidelity across diverse, unseen enterprise forest topologies without catastrophic forgetting or reliance on domain-specific node identifiers?", is_bullet=False, pt_size=11)

    c5_3 = add_card(s5, 0.6, 4.05, 5.9, 2.5, "RQ3: Adversarial Robustness & Hybrid Synthesis", CARD_BG_THEOREM, NAVY_LIGHT)
    add_para(c5_3, "How do pure neural graph models behave against adversarially crafted hard negatives (syntactically valid templates with disabled enrollment flags), and can a hybrid neuro-symbolic pipeline resolve neural blind spots?", is_bullet=False, pt_size=11)

    c5_4 = add_card(s5, 6.8, 4.05, 5.9, 2.5, "RQ4: Remediation Complexity & Autonomous Policy", CARD_BG_THEOREM, NAVY_LIGHT)
    add_para(c5_4, "What is the computational complexity of computing the minimum-privilege perturbation cut to interdict all escalation paths, and can autonomous reinforcement learning synthesize cost-bounded mitigation policies?", is_bullet=False, pt_size=11)

    add_footer(s5, 5)

    # =========================================================================
    # SLIDE 6: CASE STUDY: ESC13 MULTI-HOP ESCALATION
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Section 2.0 • ADCS Attack Mechanics", "Multi-Hop Escalation Mechanics: The ESC13 Attack Vector")

    c6_1 = add_card(s6, 0.6, 1.35, 5.4, 3.8, "Anatomy of an ESC13 Abuse Vector", CARD_BG_DEFAULT, NAVY_PRIMARY)
    add_para(c6_1, "ESC13 exploits OID group link specifications and enrollment delegation:", is_bullet=False, space_after=4)
    add_para(c6_1, "Attacker finds template with issuance policy linked to an administrative group.", bold_prefix="1. Discovery:", pt_size=10)
    add_para(c6_1, "Low-privilege user enrolls and specifies Subject Alternative Name (SAN).", bold_prefix="2. Enrollment:", pt_size=10)
    add_para(c6_1, "Certificate submitted to KDC via PKINIT, obtaining high-privilege TGT.", bold_prefix="3. PKINIT:", pt_size=10)
    add_para(c6_1, "DCSync replay grants full Active Directory Domain Controller replication.", bold_prefix="4. Compromise:", pt_size=10)

    c6_2 = add_card(s6, 0.6, 5.30, 5.4, 1.50, "Why Single-Node Inspection Fails", CARD_BG_ALERT, CRIMSON_ACCENT)
    add_para(c6_2, "No individual node contains the vulnerability! The compromise only exists as a path closure across the user principal, template ACL, issuance policy OID, and the Target DC.", is_bullet=False, pt_size=10)

    add_image_card(s6, 6.2, 1.35, 6.5, 5.45, os.path.join(FIG_DIR, "esc13_attack_path_diagram.png"), "Figure 2.2: Formal attack graph trajectory for ESC13 privilege escalation chain.")

    add_footer(s6, 6)

    # =========================================================================
    # SLIDE 7: PROPOSED METHODOLOGY: CERTGRAPH ARCHITECTURE
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "Section 3.1 • System Architecture", "CertGraph: End-to-End Heterogeneous Graph Attention Network")

    add_image_card(s7, 0.6, 1.35, 6.8, 5.45, os.path.join(FIG_DIR, "certgraph_architecture_diagram.png"), "Figure 3.1: End-to-end architecture of CertGraph Heterogeneous Graph Attention Network.")

    c7_1 = add_card(s7, 7.6, 1.35, 5.1, 3.2, "Formal Heterogeneous Multigraph Formulation", CARD_BG_DEFAULT, NAVY_PRIMARY)
    add_para(c7_1, "G = (V, E, τ_v, φ_e)", bold_prefix="Graph Definition:", pt_size=11, is_bullet=False)
    add_para(c7_1, "User, Computer, Group, Domain, CA, CertTemplate.", bold_prefix="6 Node Types τ_v:", pt_size=10)
    add_para(c7_1, "MemberOf, GenericAll, WriteDacl, Enroll, ManageCA, ManageCertificates, ExtendedRight, etc.", bold_prefix="18 Edge Relations φ_e:", pt_size=10)
    add_para(c7_1, "Cryptographic flags, enrollment parameters, user account control (UAC) bits.", bold_prefix="Feature Vectors x_v:", pt_size=10)

    c7_2 = add_card(s7, 7.6, 4.70, 5.1, 2.1, "Three Architectural Pillars", CARD_BG_FINDING, GOLD_ACCENT)
    add_para(c7_2, "Projects disparate attributes into shared d-dimensional space.", bold_prefix="1. Type Projections:", pt_size=10)
    add_para(c7_2, "Learns distinct relational attention weights α_ij^(r).", bold_prefix="2. Relational Attention:", pt_size=10)
    add_para(c7_2, "Guarantees gradient flow across 4+ hop escalation chains.", bold_prefix="3. Residual Skips:", pt_size=10)

    add_footer(s7, 7)

    # =========================================================================
    # SLIDE 8: MATHEMATICAL FORMULATION & THEOREM 1
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "Section 3.2 • Mathematical Formulation", "Heterogeneous Attention & Theorem 1 (Anti-Oversmoothing)")

    c8_1 = add_card(s8, 0.6, 1.35, 5.9, 3.2, "Relational Heterogeneous Attention Mechanism", CARD_BG_DEFAULT, NAVY_PRIMARY)
    add_para(c8_1, "For node i with neighbor j in N_i^r under relation r in R:", is_bullet=False, pt_size=10.5)
    add_para(c8_1, "α_ij^(r) = Softmax( LeakyReLU( a_r^T [ W_τi h_i || W_τj h_j ] ) )", bold_prefix="Attention Weight:", is_bullet=False, pt_size=11)
    add_para(c8_1, "h_i^(l+1) = σ( Σ_r Σ_j α_ij^(r) W_r^(l) h_j^(l) + W_skip^(l) h_i^(l) )", bold_prefix="Layer Update:", is_bullet=False, pt_size=11)
    add_para(c8_1, "Residual skip projection W_skip ensures input features directly reach layer l+1.", is_bullet=False, pt_size=10, color=TEXT_MUTED)

    c8_2 = add_card(s8, 0.6, 4.70, 5.9, 2.1, "Class-Imbalance Aware Focal Loss", CARD_BG_ALERT, CRIMSON_ACCENT)
    add_para(c8_2, "Because vulnerable templates constitute <1% of enterprise objects:", is_bullet=False, pt_size=10)
    add_para(c8_2, "L_focal = - Σ_v α_t (1 - p_v,t)^γ log(p_v,t),   γ = 2.0", bold_prefix="Focal Loss Formulation:", is_bullet=False, pt_size=11)

    c8_3 = add_card(s8, 6.8, 1.35, 5.9, 5.45, "Theorem 1 (Gradient Preservation & Anti-Oversmoothing)", CARD_BG_THEOREM, NAVY_LIGHT)
    add_para(c8_3, "Statement: Let G be a heterogeneous multigraph with L message passing layers. If each layer preserves an orthogonal residual skip projection W_skip^(l) such that σ_min(W_skip^(l)) ≥ c > 0, then the Jacobian of node representation h_v^(L) with respect to input x_v satisfies:", is_bullet=False, pt_size=10.5)
    add_para(c8_3, "‖∂h_v^(L) / ∂x_v‖  ≥  Π_(l=1)^L σ_min(W_skip^(l))  ≥  c^L  >  0", bold_prefix="Lower Bound:", is_bullet=False, pt_size=11)
    add_para(c8_3, "In standard GNNs without skip connections, as layer depth L → ∞, the Dirichlet energy E(H^(L)) → 0 (all node representations collapse into identical embeddings).", bold_prefix="Theoretical Significance:", is_bullet=False, pt_size=10.5)
    add_para(c8_3, "Theorem 1 mathematically guarantees that CertGraph avoids oversmoothing across deep 4 to 8 hop ADCS delegation chains!", bold_prefix="Practical Impact:", is_bullet=False, pt_size=10.5)

    add_footer(s8, 8)

    # =========================================================================
    # SLIDE 9: EXPERIMENTAL TESTBED (GOAD & ADSYNTH)
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "Section 4.1 • Experimental Methodology", "Enterprise Testbed: Game of Active Directory & ADSynth")

    c9_1 = add_card(s9, 0.6, 1.35, 5.9, 3.8, "Dual Evaluation Environments", CARD_BG_DEFAULT, NAVY_PRIMARY)
    add_para(c9_1, "Multi-forest enterprise testbed featuring 5 Windows Server Domain Controllers and real BloodHound/SharpHound telemetry.", bold_prefix="1. Game of Active Directory (GOAD):")
    add_para(c9_1, "Contains ground-truth ESC1, ESC2, ESC3, ESC6, ESC8, and ESC13 configurations.", is_bullet=True, pt_size=10)
    add_para(c9_1, "Synthesized 700 distinct enterprise topologies ranging from 1,000 to 50,000 nodes.", bold_prefix="2. ADSynth Generator:")
    add_para(c9_1, "Modeled power-law degree distributions matching Fortune 500 Active Directory logs.", is_bullet=True, pt_size=10)

    c9_2 = add_card(s9, 0.6, 5.30, 5.9, 1.5, "Evaluation Protocol", CARD_BG_FINDING, GOLD_ACCENT)
    add_para(c9_2, "Evaluated using 5-Fold Stratified Cross-Validation across held-out topologies. Zero-shot transfer tested on completely unseen domain forests.", is_bullet=False, pt_size=10.5)

    add_image_card(s9, 6.8, 1.35, 5.9, 5.45, os.path.join(FIG_DIR, "goad_forest_topology.png"), "Figure 4.1: Multi-domain Active Directory forest topology from the GOAD laboratory testbed.")

    add_footer(s9, 9)

    # =========================================================================
    # SLIDE 10: EMPIRICAL RESULTS & BASELINE COMPARISON
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "Section 4.2 • Benchmark Performance", "Empirical Results & Baseline Performance Comparison")

    # Table on left
    t10_shape = s10.shapes.add_table(7, 5, Inches(0.6), Inches(1.35), Inches(6.8), Inches(3.2))
    t10 = t10_shape.table

    t10_headers = ["Model / Defense Tool", "Precision", "Recall", "Macro-F1", "ROC-AUC"]
    for col_idx, h_text in enumerate(t10_headers):
        cell = t10.cell(0, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY_PRIMARY
        p = cell.text_frame.paragraphs[0]
        p.text = h_text
        p.font.name = FONT_SANS
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = WHITE

    bench_rows = [
        ("Certipy (Rule-Based)", "0.7420", "0.6921", "0.7162 ± 0.041", "0.8410"),
        ("Multilayer Perceptron (MLP)", "0.8512", "0.8240", "0.8374 ± 0.022", "0.9124"),
        ("Homogeneous GCN", "0.8741", "0.8504", "0.8621 ± 0.019", "0.9340"),
        ("Homogeneous GAT", "0.8992", "0.8702", "0.8845 ± 0.016", "0.9512"),
        ("Hetero-GraphSAGE", "0.9480", "0.9345", "0.9412 ± 0.011", "0.9780"),
        ("CertGraph (Proposed)", "0.9988", "0.9984", "0.9986 ± 0.0029", "0.9998")
    ]

    for row_idx, r_data in enumerate(bench_rows):
        is_best = (row_idx == 5)
        for col_idx, val in enumerate(r_data):
            cell = t10.cell(row_idx + 1, col_idx)
            cell.fill.solid()
            if is_best:
                cell.fill.fore_color.rgb = RGBColor(240, 247, 255)
            elif row_idx % 2 == 1:
                cell.fill.fore_color.rgb = RGBColor(248, 250, 252)
            else:
                cell.fill.fore_color.rgb = WHITE
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.name = FONT_SANS
            p.font.size = Pt(9.5)
            if is_best:
                p.font.bold = True
                p.font.color.rgb = NAVY_PRIMARY
            else:
                p.font.color.rgb = TEXT_MAIN

    c10_f = add_card(s10, 0.6, 4.75, 6.8, 2.05, "Key Benchmark Findings", CARD_BG_FINDING, GOLD_ACCENT)
    add_para(c10_f, "+28.24% F1-score improvement over industry-standard Certipy (p < 1.31 × 10^-6).", bold_prefix="Performance Margin:", pt_size=10)
    add_para(c10_f, "Tested on completely disjoint ADSynth forests, CertGraph achieved F1 = 1.0000 without fine-tuning.", bold_prefix="Zero-Shot Generalization:", pt_size=10)

    # Figures on right
    add_image_card(s10, 7.6, 1.35, 5.1, 2.65, os.path.join(FIG_DIR, "confusion_matrix.png"), "Figure 4.2: 5-fold CV confusion matrix (99.86% accuracy).")
    add_image_card(s10, 7.6, 4.15, 5.1, 2.65, os.path.join(FIG_DIR, "tool_comparison_f1.png"), "Figure 4.3: Comparative Macro-F1 across defense tools.")

    add_footer(s10, 10)

    # =========================================================================
    # SLIDE 11: ABLATION STUDY & MODEL INTERPRETABILITY
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    add_header(s11, "Section 4.3 • Ablation & Explainability", "Ablation Studies & Attention Interpretability")

    add_image_card(s11, 0.6, 1.35, 5.9, 2.8, os.path.join(FIG_DIR, "ablation_comparison.png"), "Figure 4.4: Component-wise ablation showing critical impact of skip connections.")

    # Ablation table
    t11_shape = s11.shapes.add_table(5, 4, Inches(0.6), Inches(4.30), Inches(5.9), Inches(2.5))
    t11 = t11_shape.table
    t11_headers = ["Ablated Variant", "Macro-F1", "Δ F1", "Empirical Impact"]
    for col_idx, h_text in enumerate(t11_headers):
        cell = t11.cell(0, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY_PRIMARY
        p = cell.text_frame.paragraphs[0]
        p.text = h_text
        p.font.name = FONT_SANS
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = WHITE

    abl_rows = [
        ("Full CertGraph", "0.9986", "—", "Optimal convergence"),
        ("w/o Residual Skip", "0.4768", "-52.18%", "Oversmoothing collapse"),
        ("w/o Hetero Relations", "0.8621", "-13.65%", "Relational ambiguity"),
        ("w/o Focal Loss", "0.9104", "-8.82%", "Imbalance sensitivity")
    ]
    for row_idx, r_data in enumerate(abl_rows):
        is_collapse = (row_idx == 1)
        for col_idx, val in enumerate(r_data):
            cell = t11.cell(row_idx + 1, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(255, 250, 250) if is_collapse else WHITE
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.name = FONT_SANS
            p.font.size = Pt(9)
            if is_collapse and col_idx == 2:
                p.font.bold = True
                p.font.color.rgb = CRIMSON_ACCENT
            else:
                p.font.color.rgb = TEXT_MAIN

    add_image_card(s11, 6.8, 1.35, 5.9, 3.4, os.path.join(FIG_DIR, "attention_explainability.png"), "Figure 4.5: Learned attention weights α_ij^(r) aligning with ground-truth escalation edges.")

    c11_f = add_card(s11, 6.8, 4.90, 5.9, 1.9, "Validation of Theorem 1", CARD_BG_FINDING, GOLD_ACCENT)
    add_para(c11_f, "Removing residual skip connections caused Macro-F1 to plummet from 0.9986 to 0.4768 (p = 1.31 × 10^-6). This directly validates Theorem 1: without skip projections, representation oversmoothing makes 4-hop escalation paths indistinguishable.", is_bullet=False, pt_size=10.5)

    add_footer(s11, 11)

    # =========================================================================
    # SLIDE 12: ADVERSARIAL HARD NEGATIVES & NEURO-SYMBOLIC PIPELINE
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    add_header(s12, "Section 5.1 • Advanced Robustness", "Adversarial Hard Negatives & Neuro-Symbolic Synthesis")

    c12_1 = add_card(s12, 0.6, 1.35, 5.4, 2.7, "The Discovery: Neural Model Vulnerability", CARD_BG_ALERT, CRIMSON_ACCENT)
    add_para(c12_1, "Constructed adversarial hard negatives: templates identical to ESC1 in features, but with enrollment flags disabled or disconnected ACLs.", is_bullet=False, pt_size=10)
    add_para(c12_1, "Pure Neural Model Accuracy on Hard Negatives: Only 1.59%!", bold_prefix="Critical Vulnerability:", is_bullet=False, pt_size=10.5, color=CRIMSON_ACCENT)
    add_para(c12_1, "The neural model is deceived by local syntactic similarity and flags benign objects as vulnerable.", is_bullet=False, pt_size=10)

    c12_2 = add_card(s12, 0.6, 4.20, 5.4, 2.6, "The Hybrid Neuro-Symbolic Solution", CARD_BG_DEFAULT, NAVY_PRIMARY)
    add_para(c12_2, "CertGraph GNN prunes 99.8% of benign nodes in milliseconds.", bold_prefix="Stage 1 (Neural Filter):", pt_size=10)
    add_para(c12_2, "Formal BFS validator checks cryptographic invariants on candidate subgraphs.", bold_prefix="Stage 2 (Symbolic Engine):", pt_size=10)
    add_para(c12_2, "99.91% with 0% false positive escape!", bold_prefix="Combined System Accuracy:", pt_size=10.5, color=NAVY_PRIMARY)

    add_image_card(s12, 6.2, 1.35, 6.5, 2.7, os.path.join(FIG_DIR, "neuro_symbolic_pipeline.png"), "Figure 8.1: The integrated Neuro-Symbolic Pipeline.")
    add_image_card(s12, 6.2, 4.20, 6.5, 2.6, os.path.join(FIG_DIR, "hard_negatives_comparison.png"), "Figure 8.2: Hard Negatives Accuracy: Neural (1.59%) vs Symbolic (84.13%) vs Hybrid (99.91%).")

    add_footer(s12, 12)

    # =========================================================================
    # SLIDE 13: SUB-SECOND SCALABILITY & DEPLOYMENT
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    add_header(s13, "Section 5.2 • Operational Scalability", "Sub-Second Scalability Across Enterprise Forest Graphs")

    add_image_card(s13, 0.6, 1.35, 6.5, 5.45, os.path.join(FIG_DIR, "scalability_metrics.png"), "Figure 5.1: Inference latency scaling linearly O(|V| + |E|) with node count.")

    c13_1 = add_card(s13, 7.3, 1.35, 5.4, 3.4, "Computational Complexity Comparison", CARD_BG_DEFAULT, NAVY_PRIMARY)
    add_para(c13_1, "In enterprise environments exceeding 100,000 principals, graph traversal algorithms like Dijkstra exhibit worst-case super-linear scaling.", is_bullet=False, pt_size=10.5)
    add_para(c13_1, "42 ms latency", bold_prefix="1,000 Nodes:", pt_size=10)
    add_para(c13_1, "343 ms latency (Sub-second enterprise defense!)", bold_prefix="10,000 Nodes:", pt_size=10.5, color=NAVY_PRIMARY)
    add_para(c13_1, "1.62 seconds latency across multi-forest boundaries.", bold_prefix="50,000 Nodes:", pt_size=10)

    c13_2 = add_card(s13, 7.3, 4.95, 5.4, 1.85, "Operational Deployment Realization", CARD_BG_FINDING, GOLD_ACCENT)
    add_para(c13_2, "Because CertGraph executes as sparse tensor operations on GPUs, SOC teams can run continuous real-time audits every 60 seconds without impacting production LDAP/RPC traffic.", is_bullet=False, pt_size=10.5)

    add_footer(s13, 13)

    # =========================================================================
    # SLIDE 14: AUTONOMOUS REMEDIATION & THEOREM 2
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    add_header(s14, "Section 6.0 • Autonomous Remediation", "Autonomous Remediation & Theorem 2 (NP-Hardness)")

    c14_1 = add_card(s14, 0.6, 1.35, 5.9, 3.4, "Theorem 2 (Complexity of Attack Interdiction)", CARD_BG_THEOREM, NAVY_LIGHT)
    add_para(c14_1, "Statement: Let G = (V, E) be an Active Directory multigraph, S be entry points, and T be Domain Admin targets. The Minimum Perturbation Attack Interdiction (MPAI) problem:", is_bullet=False, pt_size=10)
    add_para(c14_1, "min Σ_(e in C) w(e)   s.t.   dist_(G \\ C)(s, t) = ∞,   ∀ s in S, t in T", bold_prefix="MPAI Formulation:", is_bullet=False, pt_size=10.5)
    add_para(c14_1, "is NP-hard.", bold_prefix="Complexity Bound:", is_bullet=False, pt_size=11, color=NAVY_PRIMARY)
    add_para(c14_1, "Proof Sketch: Reduced from Directed Multiway Cut. Demonstrates that global exact optimal remediation cannot be solved in polynomial time.", is_bullet=False, pt_size=10)

    c14_2 = add_card(s14, 0.6, 4.95, 5.9, 1.85, "Operational Challenge", CARD_BG_ALERT, CRIMSON_ACCENT)
    add_para(c14_2, "Naively revoking permissions breaks business workflows. Autonomous defense must synthesize a minimal-cost cut that preserves legitimate user operations.", is_bullet=False, pt_size=10)

    add_image_card(s14, 6.8, 1.35, 5.9, 3.4, os.path.join(FIG_DIR, "game_theoretic_convergence.png"), "Figure 6.1: Reinforcement learning policy convergence achieving 100% path interdiction.")

    c14_3 = add_card(s14, 6.8, 4.95, 5.9, 1.85, "Reinforcement Learning Policy Synthesis", CARD_BG_FINDING, GOLD_ACCENT)
    add_para(c14_3, "We model remediation as an MDP solved via PPO, synthesizing minimal ACL adjustments that sever all attack paths with <0.5% operational disruption.", is_bullet=False, pt_size=10)

    add_footer(s14, 14)

    # =========================================================================
    # SLIDE 15: SYNTHESIS OF RESEARCH QUESTIONS & CONTRIBUTIONS
    # =========================================================================
    s15 = prs.slides.add_slide(blank_layout)
    add_header(s15, "Section 7.0 • Thesis Contributions", "Synthesis of Answers to Research Questions")

    c15_1 = add_card(s15, 0.6, 1.35, 5.9, 5.45, "Direct Answers to Formal Research Questions", CARD_BG_DEFAULT, NAVY_PRIMARY)
    add_para(c15_1, "Heterogeneous GAT achieves 0.9986 Macro-F1, outperforming flat MLPs (+16.1%) and rule engines (+28.2%).", bold_prefix="RQ1 (Representation):", pt_size=10)
    add_para(c15_1, "Achieved 1.0000 Zero-Shot F1 across 700 synthetic ADSynth topologies without requiring domain retraining.", bold_prefix="RQ2 (Generalization):", pt_size=10)
    add_para(c15_1, "Uncovered 1.59% neural hard-negative blind spot; resolved via Neuro-Symbolic pipeline reaching 99.91% accuracy.", bold_prefix="RQ3 (Robustness):", pt_size=10)
    add_para(c15_1, "Proved MPAI is NP-Hard via Directed Multiway Cut reduction; trained RL policy to interdict attack paths.", bold_prefix="RQ4 (Remediation):", pt_size=10)

    c15_2 = add_card(s15, 6.8, 1.35, 5.9, 5.45, "Summary of 6 Tangible Academic Contributions", CARD_BG_FINDING, GOLD_ACCENT)
    add_para(c15_2, "First formal multigraph schema capturing all 13 ADCS escalation classes.", bold_prefix="1. Multigraph Formulation:", pt_size=10)
    add_para(c15_2, "Mathematical proof of gradient lower-bounds preventing oversmoothing.", bold_prefix="2. Theorem 1:", pt_size=10)
    add_para(c15_2, "700 topologies and 5-fold cross-validation on realistic GOAD testbeds.", bold_prefix="3. Empirical Benchmark:", pt_size=10)
    add_para(c15_2, "Direct visual interpretation linking attention to critical escalation edges.", bold_prefix="4. Explainable Attention:", pt_size=10)
    add_para(c15_2, "Production-ready hybrid eliminating false positives on hard negatives.", bold_prefix="5. Neuro-Symbolic Pipeline:", pt_size=10)
    add_para(c15_2, "Formal NP-hardness proof and convergent remediation RL agent.", bold_prefix="6. Theorem 2 & Remediation:", pt_size=10)

    add_footer(s15, 15)

    # =========================================================================
    # SLIDE 16: CONCLUSION & ORAL DEFENSE Q&A
    # =========================================================================
    s16 = prs.slides.add_slide(blank_layout)
    add_header(s16, "Section 8.0 • Conclusion", "Conclusion & Examination Committee Q&A")

    c16_1 = add_card(s16, 1.5, 1.60, 10.333, 2.0, "Concluding Summary", CARD_BG_FINDING, GOLD_ACCENT)
    add_para(c16_1, "CertGraph establishes that heterogeneous graph neural networks, reinforced by provable residual skip connections and symbolic verification, bridge the critical gap between brute-force graph search and fragile heuristic rules.", is_bullet=False, pt_size=12)
    add_para(c16_1, "It delivers the first scalable (343 ms / 10k nodes), theoretically bounded, and autonomous defense system for enterprise Active Directory Certificate Services.", is_bullet=False, pt_size=12)

    # Thank you box
    ty_box = s16.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.5), Inches(3.90), Inches(10.333), Inches(2.80))
    ty_box.fill.solid()
    ty_box.fill.fore_color.rgb = CARD_BG_DEFAULT
    ty_box.line.color.rgb = BORDER_MID
    ty_box.line.width = Pt(1.5)

    ty_tf = ty_box.text_frame
    ty_tf.word_wrap = True

    typ1 = ty_tf.paragraphs[0]
    typ1.alignment = PP_ALIGN.CENTER
    typ1.space_before = Pt(14)
    typ1.text = "Thank You for Your Time and Consideration"
    typ1.font.name = FONT_SERIF
    typ1.font.size = Pt(24)
    typ1.font.bold = True
    typ1.font.color.rgb = NAVY_PRIMARY

    typ2 = ty_tf.add_paragraph()
    typ2.alignment = PP_ALIGN.CENTER
    typ2.space_before = Pt(8)
    typ2.text = "We respectfully invite questions, comments, and evaluation from the Honorable Examination Committee."
    typ2.font.name = FONT_SANS
    typ2.font.size = Pt(13)
    typ2.font.color.rgb = TEXT_MUTED

    typ3 = ty_tf.add_paragraph()
    typ3.alignment = PP_ALIGN.CENTER
    typ3.space_before = Pt(16)
    typ3.text = "UNDERGRADUATE CANDIDATES:   ID: 2002126   |   ID: 2002138   |   ID: 2102151"
    typ3.font.name = FONT_MONO
    typ3.font.size = Pt(11)
    typ3.font.bold = True
    typ3.font.color.rgb = NAVY_PRIMARY

    typ4 = ty_tf.add_paragraph()
    typ4.alignment = PP_ALIGN.CENTER
    typ4.space_before = Pt(4)
    typ4.text = "Degree & Course: B.Sc. in ECE • Course: ECE 452 (Undergraduate Final Year Thesis)"
    typ4.font.name = FONT_SANS
    typ4.font.size = Pt(10.5)
    typ4.font.color.rgb = TEXT_LIGHT

    add_footer(s16, 16)

    # ─── SAVE PRESENTATION ────────────────────────────────────────────────────
    out_dir = "/home/hs32/Desktop/GOAD/thesis_paper/presentation"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "certgraph_thesis_defense.pptx")
    prs.save(out_path)
    print(f"Successfully generated PowerPoint presentation at: {out_path}")

    # Also copy to thesis_paper root for convenience
    root_path = "/home/hs32/Desktop/GOAD/thesis_paper/certgraph_thesis_defense.pptx"
    prs.save(root_path)
    print(f"Also saved convenience copy at: {root_path}")

if __name__ == "__main__":
    create_presentation()
