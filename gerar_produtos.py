#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lê produtos.csv (catálogo real da Lira) → produtos.js limpo para os templates.
Normaliza categorias em departamentos, extrai tamanho da fralda, formata preço."""
import csv, json, re, os

SRC = os.path.expanduser("~/Documentos/Audex/Lira Fraldas/produtos.csv")
OUT = os.path.expanduser("~/Documentos/Audex/Lira Fraldas/site-templates/produtos.js")
MAPA = os.path.expanduser("~/Documentos/Audex/Lira Fraldas/fotos_mapa.json")

# EAN -> tem foto? (fotos copiadas para site-templates/fotos/{ean}.jpg)
FOTOS = set()
try:
    for it in json.load(open(MAPA, encoding="utf-8")):
        ean = str(it.get("ean") or "").strip()
        if ean:
            FOTOS.add(ean)
except (FileNotFoundError, ValueError):
    pass

JUNK = {"taxas", "2", ""}  # categorias que não são produto de vitrine

# raw category (lower) -> (departamento, emoji). Ordem de prioridade na loja.
DEPTS = [
    ("Fraldas",              "🧷", {"fralda","fraldas","fralda rn","fralda p","fralda m","fraldas g","fraldas xg","fralda xg","fralda xxg","fralda xxxg","fralda de piscina"}),
    ("Fralda Geriátrica",    "🧓", {"fralda geriatrica"}),
    ("Lenços Umedecidos",    "🧻", {"lenços","lencos"}),
    ("Pomadas & Assaduras",  "🧴", {"pomadas"}),
    ("Sabonetes",            "🧼", {"sabonete","sabonete refil"}),
    ("Cremes & Hidratantes", "🧴", {"creme","hidratantes","oleo corporal","óleo corporal"}),
    ("Cabelo",               "💇", {"shampoo","condicionador","oléo cabelos","oleo cabelos"}),
    ("Colônias & Perfumes",  "🌸", {"colônias","colonias"}),
    ("Higiene Bucal",        "🪥", {"higiene bucal"}),
    ("Talco & Algodão",      "☁️", {"talco","algodão e cotonetes","algodao e cotonetes"}),
    ("Fórmulas & Leites",    "🍼", {"leite"}),
    ("Alimentação",          "🥣", {"gelatinas"}),
    ("Chupetas",             "👶", {"chupetas"}),
    ("Amamentação",          "🤱", {"absorvente para seios"}),
    ("Repelentes",           "🦟", {"repelentes"}),
    ("Farmacinha",           "💊", {"farmacinha kids"}),
    ("Brinquedos",           "🧸", {"brinquedos"}),
    ("Roupas",               "👕", {"roupas femininas","roupas masculinas"}),
    ("Cosméticos Adulto",    "💄", {"cosmetico adulto","desodorante"}),
    ("Casa & Limpeza",       "🧺", {"sabão e amaciante","sabao e amaciante"}),
    ("Kits & Presentes",     "🎁", {"kit"}),
    ("Diversos",             "🛍️", {"geral"}),
]
# Emoji para departamentos auto-criados (categorias do CSV fora do DEPTS acima).
# Evita a fileira de 🛒 repetidos. Chave = nome do dept (raw.title()).
EMOJI_EXTRA = {
    "Absorvente Pós Parto": "🩹",
    "Laços De Bebê":        "🎀",
    "Brinco Infatil":       "💎",
    "Embalagem":            "📦",
    "Protetor Solar":       "☀️",
    "Bolsas":               "👜",
}
RAW2DEPT = {}
DEPT_EMOJI = {}
DEPT_ORDER = []
for nome, emoji, raws in DEPTS:
    DEPT_ORDER.append(nome); DEPT_EMOJI[nome] = emoji
    for r in raws: RAW2DEPT[r] = nome

def tamanho_fralda(raw):
    m = re.sub(r"^fraldas?\s*", "", raw).strip().upper()
    mapa = {"RN":"RN","P":"P","M":"M","G":"G","XG":"XG","XXG":"XXG","XXXG":"XXXG",
            "DE PISCINA":"Piscina","GERIATRICA":"Geriátrica"}
    return mapa.get(m, "")

def preco_fmt(v):
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

prods, counts = [], {}
with open(SRC, encoding="utf-8") as f:
    for row in csv.DictReader(f):
        raw = (row.get("categoria") or "").strip()
        rl = raw.lower()
        if rl in JUNK: continue
        try: pv = float(row.get("preco_venda") or 0)
        except ValueError: pv = 0
        if pv <= 0: continue
        dept = RAW2DEPT.get(rl, raw.title())
        if dept not in DEPT_EMOJI: DEPT_EMOJI[dept] = EMOJI_EXTRA.get(dept, "🛍️"); DEPT_ORDER.append(dept)
        try: est = int(float(row.get("estoque") or 0))
        except ValueError: est = 0
        nome = (row.get("nome") or "").strip().title()
        ean = (row.get("ean") or "").strip()
        prods.append({
            "sku": (row.get("sku") or "").strip(),
            "n": nome,
            "p": preco_fmt(pv),
            "v": round(pv, 2),
            "e": max(est, 0),
            "d": dept,
            "t": tamanho_fralda(rl) if dept == "Fraldas" else "",
            "f": f"{ean}.jpg" if ean in FOTOS else "",
        })
        counts[dept] = counts.get(dept, 0) + 1

# Enxuga a cauda: departamentos com poucos produtos são fundidos em "Diversos"
# (evita o excesso de discos que poluía a home). Limiar = 10 produtos.
MERGE_MIN = 10
small = {d for d, c in counts.items() if c < MERGE_MIN and d != "Diversos"}
if small:
    for p in prods:
        if p["d"] in small:
            p["d"] = "Diversos"; p["t"] = ""
    counts = {}
    for p in prods:
        counts[p["d"]] = counts.get(p["d"], 0) + 1
    if "Diversos" not in DEPT_EMOJI:
        DEPT_EMOJI["Diversos"] = "🛍️"; DEPT_ORDER.append("Diversos")
    DEPT_ORDER = [d for d in DEPT_ORDER if d not in small]
    print(f"Fundidos em Diversos ({len(small)}): " + ", ".join(sorted(small)))

cats = [{"nome": d, "emoji": DEPT_EMOJI[d], "n": counts[d]}
        for d in DEPT_ORDER if counts.get(d)]

with open(OUT, "w", encoding="utf-8") as f:
    f.write("// Gerado por gerar_produtos.py a partir de produtos.csv (catálogo real Lira Fraldas)\n")
    f.write("window.LIRA = ")
    json.dump({"cats": cats, "prods": prods}, f, ensure_ascii=False)
    f.write(";\n")

print(f"OK: {len(prods)} produtos, {len(cats)} departamentos -> {OUT}")
print("Top depts:", ", ".join(f"{c['nome']}({c['n']})" for c in cats[:8]))
