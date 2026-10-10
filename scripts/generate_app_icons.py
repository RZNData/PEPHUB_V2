#!/usr/bin/env python3
"""
Gera os ícones oficiais do PEP HUB em alta resolução (PNG e SVG)
para o Progressive Web App (PWA) e empacotamento Mobile (Android / iOS):
- icon-192.png (192x192)
- icon-512.png (512x512)
- icon-maskable-192.png (192x192 com padding de segurança para Android)
- icon-maskable-512.png (512x512 com padding de segurança para Android)
- apple-touch-icon.png (180x180)
- favicon.png (32x32)
- icon.svg (vetorial puro)
"""

import os
import sys
import math
from PIL import Image, ImageDraw

# Ensure UTF-8 output on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

OUTPUT_DIR = os.path.join("public", "icons")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Claro Brand Gradient stops
# #8a0f18 -> #c0191f -> #e23a1e -> #f47a1f -> #f9b233
GRAD_COLORS = [
    (138, 15, 24),
    (192, 25, 31),
    (226, 58, 30),
    (244, 122, 31),
    (249, 178, 51)
]

def interpolate_color(t):
    # t from 0.0 to 1.0
    scaled = t * (len(GRAD_COLORS) - 1)
    idx = int(scaled)
    frac = scaled - idx
    if idx >= len(GRAD_COLORS) - 1:
        return GRAD_COLORS[-1]
    c1 = GRAD_COLORS[idx]
    c2 = GRAD_COLORS[idx + 1]
    return (
        int(c1[0] + (c2[0] - c1[0]) * frac),
        int(c1[1] + (c2[1] - c1[1]) * frac),
        int(c1[2] + (c2[2] - c1[2]) * frac)
    )

def create_gradient_canvas(size):
    img = Image.new("RGBA", (size, size))
    for x in range(size):
        t = x / (size - 1)
        col = interpolate_color(t)
        for y in range(size):
            img.putpixel((x, y), (col[0], col[1], col[2], 255))
    return img

def render_pephub_icon(size, is_maskable=False, rounded_radius=None):
    # High resolution supersampling for smooth antialiasing
    scale = 2
    actual_size = size * scale
    
    # 1. Base Gradient Canvas
    base_grad = create_gradient_canvas(actual_size)
    
    # 2. Mask for rounded rectangle or circle if specified
    mask = Image.new("L", (actual_size, actual_size), 255)
    if rounded_radius:
        mask = Image.new("L", (actual_size, actual_size), 0)
        draw_mask = ImageDraw.Draw(mask)
        rad = rounded_radius * scale
        draw_mask.rounded_rectangle([(0, 0), (actual_size, actual_size)], radius=rad, fill=255)
        base_grad.putalpha(mask)

    draw = ImageDraw.Draw(base_grad)
    
    # Safe zone scale for maskable icons (Android adds circular mask, requires ~15-20% margin)
    content_scale = 0.65 if is_maskable else 0.82
    center = actual_size / 2
    r_outer = (actual_size * content_scale) / 2
    
    # Outer ring
    ring_width = max(3, int(actual_size * 0.045))
    draw.ellipse(
        [center - r_outer, center - r_outer, center + r_outer, center + r_outer],
        outline=(255, 255, 255, 240),
        width=ring_width
    )
    
    # Subtle inner dark shadow circle to elevate emblem
    inner_r = r_outer - ring_width * 1.5
    inner_mask = Image.new("RGBA", (actual_size, actual_size), (0, 0, 0, 0))
    inner_draw = ImageDraw.Draw(inner_mask)
    inner_draw.ellipse(
        [center - inner_r, center - inner_r, center + inner_r, center + inner_r],
        fill=(0, 0, 0, 45)
    )
    base_grad = Image.alpha_composite(base_grad, inner_mask)
    draw = ImageDraw.Draw(base_grad)
    
    # Compass needle rhombus (Official Pephub emblem)
    # Coordinates in 48x48: (31.5, 16.5) -> (26.5, 26.5) -> (16.5, 31.5) -> (21.5, 21.5)
    # Normalized: (0.656, 0.344) -> (0.552, 0.552) -> (0.344, 0.656) -> (0.448, 0.448)
    needle_r = r_outer * 0.72
    p1 = (center + needle_r * 0.68, center - needle_r * 0.68)   # Top right point
    p2 = (center + needle_r * 0.18, center + needle_r * 0.18)   # Center inner right
    p3 = (center - needle_r * 0.68, center + needle_r * 0.68)   # Bottom left point
    p4 = (center - needle_r * 0.18, center - needle_r * 0.18)   # Center inner left
    
    # Compass needle shape in crisp pure white
    draw.polygon([p1, p2, p3, p4], fill=(255, 255, 255, 255))
    
    # Compass center pivot point
    center_dot_r = max(2, int(actual_size * 0.03))
    draw.ellipse(
        [center - center_dot_r, center - center_dot_r, center + center_dot_r, center + center_dot_r],
        fill=(138, 15, 24, 255)
    )
    
    # Downsample using high-quality Lanczos filter
    final_img = base_grad.resize((size, size), Image.Resampling.LANCZOS)
    return final_img

def main():
    print("=" * 60)
    print("🎨 GERANDO ASSETS E ÍCONES OFICIAIS DO APP PEP HUB")
    print("=" * 60)
    
    # 1. icon-192.png
    img_192 = render_pephub_icon(192, is_maskable=False, rounded_radius=36)
    p192 = os.path.join(OUTPUT_DIR, "icon-192.png")
    img_192.save(p192, "PNG")
    print(f"✅ Gerado: {p192}")
    
    # 2. icon-512.png
    img_512 = render_pephub_icon(512, is_maskable=False, rounded_radius=96)
    p512 = os.path.join(OUTPUT_DIR, "icon-512.png")
    img_512.save(p512, "PNG")
    print(f"✅ Gerado: {p512}")
    
    # 3. icon-maskable-192.png (full bleed square for Android adaptive icons)
    img_m192 = render_pephub_icon(192, is_maskable=True, rounded_radius=None)
    pm192 = os.path.join(OUTPUT_DIR, "icon-maskable-192.png")
    img_m192.save(pm192, "PNG")
    print(f"✅ Gerado: {pm192}")
    
    # 4. icon-maskable-512.png (full bleed square)
    img_m512 = render_pephub_icon(512, is_maskable=True, rounded_radius=None)
    pm512 = os.path.join(OUTPUT_DIR, "icon-maskable-512.png")
    img_m512.save(pm512, "PNG")
    print(f"✅ Gerado: {pm512}")
    
    # 5. apple-touch-icon.png (180x180)
    img_apple = render_pephub_icon(180, is_maskable=False, rounded_radius=32)
    p_apple = os.path.join(OUTPUT_DIR, "apple-touch-icon.png")
    img_apple.save(p_apple, "PNG")
    print(f"✅ Gerado: {p_apple}")
    
    # 6. favicon.png (32x32)
    img_fav = render_pephub_icon(32, is_maskable=False, rounded_radius=6)
    pfav = os.path.join(OUTPUT_DIR, "favicon.png")
    img_fav.save(pfav, "PNG")
    print(f"✅ Gerado: {pfav}")
    
    # 7. icon.svg (Vetor puro)
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="100%" height="100%">
  <defs>
    <linearGradient id="claroGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#8a0f18"/>
      <stop offset="26%" stop-color="#c0191f"/>
      <stop offset="50%" stop-color="#e23a1e"/>
      <stop offset="74%" stop-color="#f47a1f"/>
      <stop offset="100%" stop-color="#f9b233"/>
    </linearGradient>
    <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="8" stdDeviation="16" flood-opacity="0.35"/>
    </filter>
  </defs>
  <rect width="512" height="512" rx="110" fill="url(#claroGrad)"/>
  <circle cx="256" cy="256" r="170" fill="none" stroke="#ffffff" stroke-width="22" opacity="0.95" filter="url(#shadow)"/>
  <circle cx="256" cy="256" r="140" fill="rgba(0,0,0,0.12)"/>
  <path d="M336 176 L283 283 L176 336 L229 229 Z" fill="#ffffff" filter="url(#shadow)"/>
  <circle cx="256" cy="256" r="12" fill="#8a0f18"/>
</svg>"""
    p_svg = os.path.join(OUTPUT_DIR, "icon.svg")
    with open(p_svg, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"✅ Gerado: {p_svg}")
    print("=" * 60)

if __name__ == "__main__":
    main()
