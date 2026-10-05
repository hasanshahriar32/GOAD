#!/usr/bin/env python3
"""
Enhance Figure 6.1: GOAD Multi-Forest Topology
Overlays crisp, publication-grade high-contrast text badges and labels across:
- Servers: DC01, DC02, SRV02, DC03, SRV03 (with prominent ADCS CA badge)
- Domain Titles: sevenkingdoms.local, north.sevenkingdoms.local, essos.local
- Cross-Domain / Forest Trust Links: MSSQL Trusted Link, Two-Way Trust, One-Way Trust

Ensures zero collisions, zero clipping, and maximum visual impact in sidewaysfigure.
"""

import os
from PIL import Image, ImageDraw, ImageFont

def enhance_topology():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fig_path = os.path.join(base_dir, 'figures', 'goad_forest_topology.png')

    if not os.path.exists(fig_path):
        raise FileNotFoundError(f"Target image not found at {fig_path}")

    im = Image.open(fig_path).convert('RGB')
    draw = ImageDraw.Draw(im)

    # -----------------------------------------------------------------
    # Typography Setup (Liberation Sans & Mono)
    # -----------------------------------------------------------------
    font_domain = ImageFont.truetype('/usr/share/fonts/liberation/LiberationSans-Bold.ttf', 32)
    font_srv_hdr = ImageFont.truetype('/usr/share/fonts/liberation/LiberationSans-Bold.ttf', 26)
    font_srv_mono = ImageFont.truetype('/usr/share/fonts/liberation/LiberationMono-Bold.ttf', 22)
    font_srv_sub = ImageFont.truetype('/usr/share/fonts/liberation/LiberationSans-Bold.ttf', 19)
    font_srv_sm = ImageFont.truetype('/usr/share/fonts/liberation/LiberationSans-Bold.ttf', 17)
    font_adcs = ImageFont.truetype('/usr/share/fonts/liberation/LiberationSans-Bold.ttf', 17)
    font_link = ImageFont.truetype('/usr/share/fonts/liberation/LiberationSans-Bold.ttf', 24)
    font_trust = ImageFont.truetype('/usr/share/fonts/liberation/LiberationSans-Bold.ttf', 17)

    # -----------------------------------------------------------------
    # 1. DC01 - kingslanding (Parent Forest Root DC)
    # -----------------------------------------------------------------
    draw.rectangle((1480, 540, 1940, 645), fill=(255, 255, 255))
    draw.text((1710, 560), 'DC01 - kingslanding', font=font_srv_hdr, fill=(15, 23, 42), anchor='mm')
    draw.text((1710, 592), '192.168.56.10', font=font_srv_mono, fill=(30, 41, 59), anchor='mm')
    draw.text((1710, 622), 'Windows Server 2019', font=font_srv_sub, fill=(71, 85, 105), anchor='mm')

    # -----------------------------------------------------------------
    # 2. DC02 - winterfell (Child Domain DC)
    # -----------------------------------------------------------------
    draw.rectangle((850, 862, 1180, 1025), fill=(255, 255, 255))
    draw.text((1050, 882), 'DC02 - winterfell', font=font_srv_hdr, fill=(15, 23, 42), anchor='mm')
    draw.text((1050, 914), '192.168.56.11', font=font_srv_mono, fill=(30, 41, 59), anchor='mm')
    draw.text((1050, 944), 'Windows Server 2019', font=font_srv_sub, fill=(71, 85, 105), anchor='mm')
    # Vulnerability pill
    draw.rounded_rectangle((940, 966, 1160, 998), radius=6, fill=(254, 242, 242), outline=(239, 68, 68), width=1)
    draw.text((1050, 982), 'rpc user enum', font=font_srv_sm, fill=(185, 28, 28), anchor='mm')

    # -----------------------------------------------------------------
    # 3. SRV02 - castelblack (Child Domain Member Server)
    # -----------------------------------------------------------------
    # Cover text without clipping the incoming purple arrow
    draw.rectangle((925, 1220, 1280, 1260), fill=(255, 255, 255))
    draw.rectangle((800, 1260, 1280, 1405), fill=(255, 255, 255))
    # Redraw purple connection line seamlessly:
    draw.line((715, 1360, 920, 1238), fill=(108, 48, 130), width=2)
    # Redraw clean triangle base line:
    draw.line((613, 1360, 1365, 1360), fill=(0, 0, 0), width=3)

    draw.text((1050, 1235), 'SRV02 - castelblack', font=font_srv_hdr, fill=(15, 23, 42), anchor='mm')
    draw.text((1050, 1262), '192.168.56.22', font=font_srv_mono, fill=(30, 41, 59), anchor='mm')
    draw.text((1050, 1288), 'Windows Server 2019 (no defender)', font=font_srv_sub, fill=(71, 85, 105), anchor='mm')
    draw.text((1050, 1314), 'IIS + upload ASP', font=font_srv_sm, fill=(51, 65, 85), anchor='mm')
    draw.text((1050, 1338), 'MSSQL + execute as + trusted link', font=font_srv_sm, fill=(51, 65, 85), anchor='mm')

    # -----------------------------------------------------------------
    # 4. DC03 - meereen (External Forest DC)
    # -----------------------------------------------------------------
    draw.rectangle((2250, 862, 2600, 1038), fill=(255, 255, 255))
    draw.text((2440, 882), 'DC03 - meereen', font=font_srv_hdr, fill=(15, 23, 42), anchor='mm')
    draw.text((2440, 914), '192.168.56.12', font=font_srv_mono, fill=(30, 41, 59), anchor='mm')
    draw.text((2440, 944), 'Windows Server 2016', font=font_srv_sub, fill=(71, 85, 105), anchor='mm')
    # Vulnerability pill
    draw.rounded_rectangle((2320, 966, 2560, 998), radius=6, fill=(254, 242, 242), outline=(239, 68, 68), width=1)
    draw.text((2440, 982), 'ntlm downgrade', font=font_srv_sm, fill=(185, 28, 28), anchor='mm')

    # -----------------------------------------------------------------
    # 5. SRV03 - braavos (External Forest Member Server & ADCS CA)
    # -----------------------------------------------------------------
    draw.rectangle((2210, 1220, 2730, 1405), fill=(255, 255, 255))
    # Redraw clean triangle base line:
    draw.line((2048, 1360, 2770, 1360), fill=(0, 0, 0), width=3)

    draw.text((2480, 1234), 'SRV03 - braavos', font=font_srv_hdr, fill=(15, 23, 42), anchor='mm')
    draw.text((2480, 1260), '192.168.56.23', font=font_srv_mono, fill=(30, 41, 59), anchor='mm')
    draw.text((2480, 1285), 'Windows Server 2016', font=font_srv_sub, fill=(71, 85, 105), anchor='mm')

    # ADCS Certificate Authority Highlight Badge
    draw.rounded_rectangle((2235, 1302, 2725, 1330), radius=6, fill=(79, 70, 229), outline=(67, 56, 202), width=1)
    draw.text((2480, 1316), 'ADCS - ESSOS-CA (Certificate Authority)', font=font_adcs, fill=(255, 255, 255), anchor='mm')

    draw.text((2480, 1344), 'MSSQL + execute as + trusted link', font=font_srv_sm, fill=(51, 65, 85), anchor='mm')

    # -----------------------------------------------------------------
    # 6. Domain Titles
    # -----------------------------------------------------------------
    # sevenkingdoms.local: base line at 742
    draw.rectangle((1500, 746, 1922, 795), fill=(255, 255, 255))
    draw.rounded_rectangle((1515, 748, 1907, 792), radius=8, fill=(248, 250, 252), outline=(15, 23, 42), width=2)
    draw.text((1711, 770), 'sevenkingdoms.local', font=font_domain, fill=(15, 23, 42), anchor='mm')

    # north.sevenkingdoms.local: base line at 1360
    draw.rectangle((800, 1416, 1300, 1472), fill=(255, 255, 255))
    draw.rounded_rectangle((812, 1418, 1288, 1468), radius=8, fill=(248, 250, 252), outline=(15, 23, 42), width=2)
    draw.text((1050, 1443), 'north.sevenkingdoms.local', font=font_domain, fill=(15, 23, 42), anchor='mm')

    # essos.local: base line at 1360
    draw.rectangle((2320, 1416, 2580, 1472), fill=(255, 255, 255))
    draw.rounded_rectangle((2330, 1418, 2570, 1468), radius=8, fill=(248, 250, 252), outline=(15, 23, 42), width=2)
    draw.text((2450, 1443), 'essos.local', font=font_domain, fill=(15, 23, 42), anchor='mm')

    # -----------------------------------------------------------------
    # 7. Trust Links
    # -----------------------------------------------------------------
    # MSSQL Trusted Link: horizontal line around 1148
    draw.rectangle((1480, 1125, 1920, 1172), fill=(255, 255, 255))
    draw.rounded_rectangle((1490, 1127, 1910, 1169), radius=8, fill=(240, 249, 255), outline=(2, 132, 199), width=2)
    draw.text((1700, 1148), 'MSSQL Trusted Link', font=font_link, fill=(3, 105, 161), anchor='mm')

    # Two-Way Trust: North <-> SK (covers old trust word at 1365, 812)
    draw.rectangle((1275, 792, 1455, 832), fill=(255, 255, 255))
    draw.rounded_rectangle((1280, 794, 1450, 830), radius=6, fill=(248, 250, 252), outline=(71, 85, 105), width=2)
    draw.text((1365, 812), 'Two-Way Trust', font=font_trust, fill=(15, 23, 42), anchor='mm')

    # One-Way Trust: SK <-> Essos (covers old trust word at 2115, 828)
    draw.rectangle((2025, 808, 2205, 848), fill=(255, 255, 255))
    draw.rounded_rectangle((2030, 810, 2200, 846), radius=6, fill=(248, 250, 252), outline=(71, 85, 105), width=2)
    draw.text((2115, 828), 'One-Way Trust', font=font_trust, fill=(15, 23, 42), anchor='mm')

    # Save enhanced figure
    im.save(fig_path)
    print(f"[+] Enhanced Figure 6.1 saved successfully to {fig_path}")

if __name__ == '__main__':
    enhance_topology()
