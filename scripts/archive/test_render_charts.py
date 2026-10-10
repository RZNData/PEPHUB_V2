import json

with open('public/churn-bl-total/data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print("Testing data presence:")
print("Invol history points:", len(d['involuntaria_proj']['history']))
print("CC history points:", len(d['callcenter']['history']))
print("CC motives matrix:", len(d['callcenter']['motivos_matriz']))
