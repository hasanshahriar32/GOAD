#!/usr/bin/env python3
"""
Enhance Figure 6.1: GOAD Multi-Forest Topology
Overlays crisp, publication-grade high-contrast extra-large text badges across:
- Servers: DC01, DC02, SRV02, DC03, SRV03 (with prominent ADCS CA badge)
- Domain Titles: sevenkingdoms.local, north.sevenkingdoms.local, essos.local
- Cross-Domain / Forest Trust Links: MSSQL Trusted Link, Two-Way Trust, One-Way Trust
- Tier-0 Domain Admins: Robert Baratheon, Eddard Stark, Daenerys Targaryen

Guarantees high visibility from a distance in thesis figures.
"""

import os
from PIL import Image, ImageDraw, ImageFont

def enhance_topology():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fig_path = os.path.join(base_dir, 'figures', 'goad_forest_topology.png')

    # Load clean base image if available, else fig_path
    clean_path = '/tmp/clean_goad_forest_topology.png'
    src = clean_path if os.path.exists(clean_path) else fig_path
    im = Image.open(src).convert('RGB')
    draw = ImageDraw.Draw(im)

    # -----------------------------------------------------------------
    # Extra Large Typography Setup
    # -----------------------------------------------------------------
    font_domain = ImageFont.truetype('/usr/share/fonts/liberation/LiberationSans-Bold.ttf', 48)
    font_srv_hdr = ImageFont.truetype('/usr/share/fonts/liberation/LiberationSans-Bold.ttf', 44)
    font_srv_mono = ImageFont.truetype('/usr/share/fonts/liberation/LiberationMono-Bold.ttf', 36)
    font_srv_sub = ImageFont.truetype('/usr/share/fonts/liberation/LiberationSans-Bold.ttf', 30)
    font_srv_sm = ImageFont.truetype('/usr/share/fonts/liberation/LiberationSans-Bold.ttf', 26)
    font_adcs = ImageFont.truetype('/usr/share/fonts/liberation/LiberationSans-Bold.ttf', 30)
    font_link = ImageFont.truetype('/usr/share/fonts/liberation/LiberationSans-Bold.ttf', 44)
    font_trust = ImageFont.truetype('/usr/share/fonts/liberation/LiberationSans-Bold.ttf', 32)
    font_user_da = ImageFont.truetype('/usr/share/fonts/liberation/LiberationSans-Bold.ttf', 28)

    # 1. DC01 - kingslanding
    draw.rectangle((1440, 520, 1980, 675), fill=(255, 255, 255), outline=(15, 23, 42), width=3)
    draw.text((1710, 555), 'DC01 - kingslanding', font=font_srv_hdr, fill=(15, 23, 42), anchor='mm')
    draw.text((1710, 602), '192.168.56.10', font=font_srv_mono, fill=(30, 41, 59), anchor='mm')
    draw.text((1710, 642), 'Windows Server 2019', font=font_srv_sub, fill=(71, 85, 105), anchor='mm')

    # 2. DC02 - winterfell
    draw.rectangle((800, 840, 1260, 1050), fill=(255, 255, 255), outline=(15, 23, 42), width=3)
    draw.text((1030, 875), 'DC02 - winterfell', font=font_srv_hdr, fill=(15, 23, 42), anchor='mm')
    draw.text((1030, 922), '192.168.56.11', font=font_srv_mono, fill=(30, 41, 59), anchor='mm')
    draw.text((1030, 962), 'Windows Server 2019', font=font_srv_sub, fill=(71, 85, 105), anchor='mm')
    draw.rounded_rectangle((870, 992, 1190, 1034), radius=8, fill=(254, 242, 242), outline=(239, 68, 68), width=2)
    draw.text((1030, 1013), 'rpc user enum', font=font_srv_sm, fill=(185, 28, 28), anchor='mm')

    # 3. SRV02 - castelblack
    draw.rectangle((760, 1190, 1340, 1410), fill=(255, 255, 255), outline=(15, 23, 42), width=3)
    draw.text((1050, 1222), 'SRV02 - castelblack', font=font_srv_hdr, fill=(15, 23, 42), anchor='mm')
    draw.text((1050, 1262), '192.168.56.22', font=font_srv_mono, fill=(30, 41, 59), anchor='mm')
    draw.text((1050, 1300), 'Windows Server 2019 (no defender)', font=font_srv_sub, fill=(71, 85, 105), anchor='mm')
    draw.text((1050, 1338), 'IIS + upload ASP', font=font_srv_sm, fill=(51, 65, 85), anchor='mm')
    draw.text((1050, 1376), 'MSSQL + execute as + trusted link', font=font_srv_sm, fill=(51, 65, 85), anchor='mm')

    # 4. DC03 - meereen
    draw.rectangle((2200, 840, 2680, 1050), fill=(255, 255, 255), outline=(15, 23, 42), width=3)
    draw.text((2440, 875), 'DC03 - meereen', font=font_srv_hdr, fill=(15, 23, 42), anchor='mm')
    draw.text((2440, 922), '192.168.56.12', font=font_srv_mono, fill=(30, 41, 59), anchor='mm')
    draw.text((2440, 962), 'Windows Server 2016', font=font_srv_sub, fill=(71, 85, 105), anchor='mm')
    draw.rounded_rectangle((2290, 992, 2590, 1034), radius=8, fill=(254, 242, 242), outline=(239, 68, 68), width=2)
    draw.text((2440, 1013), 'ntlm downgrade', font=font_srv_sm, fill=(185, 28, 28), anchor='mm')

    # 5. SRV03 - braavos
    draw.rectangle((2160, 1190, 2820, 1410), fill=(255, 255, 255), outline=(15, 23, 42), width=3)
    draw.text((2490, 1222), 'SRV03 - braavos', font=font_srv_hdr, fill=(15, 23, 42), anchor='mm')
    draw.text((2490, 1262), '192.168.56.23', font=font_srv_mono, fill=(30, 41, 59), anchor='mm')
    draw.text((2490, 1300), 'Windows Server 2016', font=font_srv_sub, fill=(71, 85, 105), anchor='mm')
    draw.rounded_rectangle((2200, 1324, 2780, 1368), radius=8, fill=(79, 70, 229), outline=(67, 56, 202), width=2)
    draw.text((2490, 1346), 'ADCS - ESSOS-CA (Certificate Authority)', font=font_adcs, fill=(255, 255, 255), anchor='mm')
    draw.text((2490, 1386), 'MSSQL + execute as + trusted link', font=font_srv_sm, fill=(51, 65, 85), anchor='mm')

    # 6. Domain Titles
    draw.rectangle((1440, 735, 1980, 805), fill=(255, 255, 255))
    draw.rounded_rectangle((1450, 737, 1970, 803), radius=10, fill=(248, 250, 252), outline=(15, 23, 42), width=3)
    draw.text((1710, 770), 'sevenkingdoms.local', font=font_domain, fill=(15, 23, 42), anchor='mm')

    draw.rectangle((740, 1425, 1360, 1495), fill=(255, 255, 255))
    draw.rounded_rectangle((750, 1427, 1350, 1493), radius=10, fill=(248, 250, 252), outline=(15, 23, 42), width=3)
    draw.text((1050, 1460), 'north.sevenkingdoms.local', font=font_domain, fill=(15, 23, 42), anchor='mm')

    draw.rectangle((2240, 1425, 2680, 1495), fill=(255, 255, 255))
    draw.rounded_rectangle((2250, 1427, 2670, 1493), radius=10, fill=(248, 250, 252), outline=(15, 23, 42), width=3)
    draw.text((2460, 1460), 'essos.local', font=font_domain, fill=(15, 23, 42), anchor='mm')

    # 7. Trust Links
    draw.rectangle((1440, 1115, 1980, 1180), fill=(255, 255, 255))
    draw.rounded_rectangle((1450, 1117, 1970, 1178), radius=10, fill=(240, 249, 255), outline=(2, 132, 199), width=3)
    draw.text((1710, 1148), 'MSSQL Trusted Link', font=font_link, fill=(3, 105, 161), anchor='mm')

    draw.rectangle((1240, 785, 1480, 840), fill=(255, 255, 255))
    draw.rounded_rectangle((1245, 787, 1475, 838), radius=8, fill=(248, 250, 252), outline=(71, 85, 105), width=2)
    draw.text((1360, 812), 'Two-Way Trust', font=font_trust, fill=(15, 23, 42), anchor='mm')

    draw.rectangle((1980, 805, 2220, 860), fill=(255, 255, 255))
    draw.rounded_rectangle((1985, 807, 2215, 858), radius=8, fill=(248, 250, 252), outline=(71, 85, 105), width=2)
    draw.text((2100, 832), 'One-Way Trust', font=font_trust, fill=(15, 23, 42), anchor='mm')

    # 8. Prominent Domain Admin accounts
    # Robert Baratheon (Root DA)
    draw.rectangle((1430, 50, 1990, 105), fill=(255, 255, 255))
    draw.rounded_rectangle((1435, 52, 1985, 103), radius=6, fill=(254, 242, 242), outline=(220, 38, 38), width=2)
    draw.text((1710, 77), 'sevenkingdoms\\robert.baratheon [Domain Admin]', font=font_user_da, fill=(185, 28, 28), anchor='mm')

    # Eddard Stark (Child DA)
    draw.rectangle((260, 240, 780, 295), fill=(255, 255, 255))
    draw.rounded_rectangle((265, 242, 775, 293), radius=6, fill=(254, 242, 242), outline=(220, 38, 38), width=2)
    draw.text((520, 267), 'north\\eddard.stark [Domain Admin]', font=font_user_da, fill=(185, 28, 28), anchor='mm')

    # Daenerys Targaryen (External DA)
    draw.rectangle((2650, 335, 3160, 390), fill=(255, 255, 255))
    draw.rounded_rectangle((2655, 337, 3155, 388), radius=6, fill=(254, 242, 242), outline=(220, 38, 38), width=2)
    draw.text((2905, 362), 'essos\\daenerys.targaryen [Domain Admin]', font=font_user_da, fill=(185, 28, 28), anchor='mm')

    im.save(fig_path, dpi=(300, 300))
    print(f"[✓] Enhanced Figure 6.1 saved successfully to {fig_path}")

if __name__ == '__main__':
    enhance_topology()
