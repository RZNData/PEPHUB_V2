#!/usr/bin/env python3
"""Validate the generated FPD panel HTML for common JS syntax issues"""
import re

html = open('Painel_FPD_Regional_Norte.html', 'r', encoding='utf-8', errors='ignore').read()

# Extract all JS from <script> tags
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
print(f"Found {len(scripts)} <script> blocks")

for i, script in enumerate(scripts):
    if len(script) < 50:
        continue
    # Count braces
    open_brace = script.count('{')
    close_brace = script.count('}')
    open_paren = script.count('(')
    close_paren = script.count(')')
    open_bracket = script.count('[')
    close_bracket = script.count(']')
    
    print(f"\nScript block {i+1} ({len(script):,} chars):")
    print(f"  Braces:     {{ = {open_brace}, }} = {close_brace}, diff = {open_brace - close_brace}")
    print(f"  Parens:     ( = {open_paren}, ) = {close_paren}, diff = {open_paren - close_paren}")
    print(f"  Brackets:   [ = {open_bracket}, ] = {close_bracket}, diff = {open_bracket - close_bracket}")
    
    # Check for obvious issues
    if abs(open_brace - close_brace) > 2:
        print(f"  ⚠️ POSSIBLE BRACE MISMATCH!")
    if abs(open_paren - close_paren) > 2:
        print(f"  ⚠️ POSSIBLE PAREN MISMATCH!")

# Check for key FPD functions
key_fns = ['drawKpis', 'drawSafra', 'drawScatter', 'drawCid', 'drawRisco', 'drawMtx', 'drawRank', 'render_', 'init']
for fn in key_fns:
    count = html.count(f'function {fn}(')
    print(f"  function {fn}(): {count} definition(s)")

# Check that HELP is defined before init()
help_pos = html.find('const HELP = {')
init_pos = html.find('function init()')
if help_pos != -1 and init_pos != -1:
    print(f"\nHELP at pos {help_pos}, init() at pos {init_pos}")
    print(f"HELP before init: {'YES' if help_pos < init_pos else 'NO'}")

# Validate the tabsCid area is clean
lines = html.split('\n')
for i, line in enumerate(lines):
    if 'tabsCid' in line and i > 100:  # Skip HTML part
        print(f"\ntabsCid at L{i+1}: {line[:150]}")

# Check for the old broken pattern
old_pattern = "// old tabsCid"
if old_pattern in html:
    print(f"\n⚠️ Old broken tabsCid comment still present!")
else:
    print(f"\n✓ Old broken tabsCid comment removed.")

print(f"\n✓ Total HTML size: {len(html):,} chars")
