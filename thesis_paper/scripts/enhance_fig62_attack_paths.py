#!/usr/bin/env python3
"""
Enhance Figure 6.2: GOAD Attack Paths
Overlays high-visibility numbered stage banners and crisp server badges across
the complex multi-hop compromise graph so that the entire privilege escalation
narrative is effortlessly readable from a distant view.
"""

import os
from PIL import Image, ImageDraw, ImageFont

def enhance_attack_paths():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fig_path = os.path.join(base_dir, 'figures', 'goad_attack_paths.png')

    im = Image.open(fig_path).convert('RGB')
    draw = ImageDraw.Draw(im)

    font_stage_hdr = ImageFont.truetype('/usr/share/fonts/liberation/LiberationSans-Bold.ttf', 30)
    font_stage_sub = ImageFont.truetype('/usr/share/fonts/liberation/LiberationSans-Bold.ttf', 24)
    font_srv_hdr = ImageFont.truetype('/usr/share/fonts/liberation/LiberationSans-Bold.ttf', 26)
    font_srv_ip = ImageFont.truetype('/usr/share/fonts/liberation/LiberationMono-Bold.ttf', 22)

    # ─────────────────────────────────────────────────────────────
    # 1. FIVE CRITICAL ATTACK PHASES
    # ─────────────────────────────────────────────────────────────
    # Stage 1: Initial Foothold (Top Left)
    draw.rounded_rectangle((30, 480, 500, 575), radius=8, fill=(254, 242, 242), outline=(220, 38, 38), width=3)
    draw.text((265, 510), 'STAGE 1: INITIAL FOOTHOLD', font=font_stage_hdr, fill=(185, 28, 28), anchor='mm')
    draw.text((265, 545), 'Password Spray & NTLM Relay', font=font_stage_sub, fill=(15, 23, 42), anchor='mm')

    # Stage 2: SRV02 Lateral Movement (Middle Top)
    draw.rounded_rectangle((620, 200, 1160, 295), radius=8, fill=(255, 251, 235), outline=(217, 119, 6), width=3)
    draw.text((890, 230), 'STAGE 2: SRV02 COMPROMISE', font=font_stage_hdr, fill=(180, 83, 9), anchor='mm')
    draw.text((890, 265), 'IIS ASP Upload + SeImpersonate', font=font_stage_sub, fill=(15, 23, 42), anchor='mm')

    # Stage 3: ADCS CA Exploitation (Bottom Center)
    draw.rounded_rectangle((560, 1370, 1160, 1465), radius=8, fill=(245, 243, 255), outline=(126, 34, 206), width=3)
    draw.text((860, 1400), 'STAGE 3: ADCS CA (ESSOS-CA)', font=font_stage_hdr, fill=(107, 33, 168), anchor='mm')
    draw.text((860, 1435), 'MSSQL Link -> ESC1/ESC8 Exploit', font=font_stage_sub, fill=(15, 23, 42), anchor='mm')

    # Stage 4: External Forest DA / DC03 (Middle Right)
    draw.rounded_rectangle((1250, 930, 1750, 1025), radius=8, fill=(240, 253, 244), outline=(22, 163, 74), width=3)
    draw.text((1500, 960), 'STAGE 4: EXTERNAL FOREST DA', font=font_stage_hdr, fill=(21, 128, 61), anchor='mm')
    draw.text((1500, 995), 'Certificate Auth -> DC03 Admin', font=font_stage_sub, fill=(15, 23, 42), anchor='mm')

    # Stage 5: Enterprise Root Dominance (Top Right)
    draw.rounded_rectangle((1680, 50, 2220, 145), radius=8, fill=(254, 226, 226), outline=(185, 28, 28), width=3)
    draw.text((1950, 80), 'STAGE 5: FULL FOREST TAKEOVER', font=font_stage_hdr, fill=(153, 27, 27), anchor='mm')
    draw.text((1950, 115), 'Inter-Forest Trust -> DC01 Root DA', font=font_stage_sub, fill=(15, 23, 42), anchor='mm')

    # ─────────────────────────────────────────────────────────────
    # 2. KEY SERVER IDENTIFIERS
    # ─────────────────────────────────────────────────────────────
    # DC01 - kingslanding
    draw.rectangle((1700, 480, 2040, 545), fill=(255, 255, 255), outline=(15, 23, 42), width=2)
    draw.text((1870, 500), 'DC01 - kingslanding', font=font_srv_hdr, fill=(15, 23, 42), anchor='mm')
    draw.text((1870, 526), '192.168.56.10', font=font_srv_ip, fill=(30, 41, 59), anchor='mm')

    # DC02 - winterfell
    draw.rectangle((900, 290, 1180, 350), fill=(255, 255, 255), outline=(15, 23, 42), width=2)
    draw.text((1040, 308), 'DC02 - winterfell', font=font_srv_hdr, fill=(15, 23, 42), anchor='mm')
    draw.text((1040, 332), '192.168.56.11', font=font_srv_ip, fill=(30, 41, 59), anchor='mm')

    # SRV02 - castelblack
    draw.rectangle((580, 545, 870, 608), fill=(255, 255, 255), outline=(15, 23, 42), width=2)
    draw.text((725, 564), 'SRV02 - castelblack', font=font_srv_hdr, fill=(15, 23, 42), anchor='mm')
    draw.text((725, 590), '192.168.56.22', font=font_srv_ip, fill=(30, 41, 59), anchor='mm')

    # DC03 - meereen
    draw.rectangle((940, 785, 1220, 848), fill=(255, 255, 255), outline=(15, 23, 42), width=2)
    draw.text((1080, 804), 'DC03 - meereen', font=font_srv_hdr, fill=(15, 23, 42), anchor='mm')
    draw.text((1080, 830), '192.168.56.12', font=font_srv_ip, fill=(30, 41, 59), anchor='mm')

    # SRV03 - braavos
    draw.rectangle((580, 785, 860, 848), fill=(255, 255, 255), outline=(15, 23, 42), width=2)
    draw.text((720, 804), 'SRV03 - braavos', font=font_srv_hdr, fill=(15, 23, 42), anchor='mm')
    draw.text((720, 830), '192.168.56.23', font=font_srv_ip, fill=(30, 41, 59), anchor='mm')

    im.save(fig_path, dpi=(300, 300))
    print(f"[✓] Enhanced Figure 6.2 saved successfully to {fig_path}")

if __name__ == '__main__':
    enhance_attack_paths()
