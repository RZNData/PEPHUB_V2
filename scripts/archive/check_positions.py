with open('Painel_Churn_Safra 28.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

s_mm = content.find("cv.addEventListener('mousemove',e=>{ if(drag)return;")
e_mm = content.find("cv.addEventListener('mouseleave'", s_mm)
print(f"s_mm: {s_mm}, e_mm: {e_mm}")
if s_mm != -1 and e_mm != -1:
    print("Start:", content[s_mm:s_mm+150])
    print("End:", content[e_mm-100:e_mm+100])
