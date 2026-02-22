import re
import unicodedata

def remover_acentos(txt):
    return ''.join(c for c in unicodedata.normalize('NFD', txt)
                  if unicodedata.category(c) != 'Mn')

UNIDADES = {"zero":0,"um":1,"uma":1,"dois":2,"duas":2,"tres":3,"quatro":4,"cinco":5,"seis":6,"sete":7,"oito":8,"nove":9}
DEZENAS = {"dez":10,"onze":11,"doze":12,"treze":13,"quatorze":14,"catorze":14,"quinze":15,"dezesseis":16,"dezessete":17,"dezoito":18,"dezenove":19,"vinte":20,"trinta":30,"quarenta":40,"cinquenta":50,"sessenta":60,"setenta":70,"oitenta":80,"noventa":90}
CENTENAS = {"cem":100,"cento":100,"duzentos":200,"trezentos":300,"quatrocentos":400,"quinhentos":500,"seiscentos":600,"setecentos":700,"oitocentos":800,"novecentos":900}
MULTS = {"mil":1000,"milhao":1000000,"milhoes":1000000,"bilhao":1000000000,"bilhoes":1000000000}
LITERAL_NUMS = set(UNIDADES.keys()) | set(DEZENAS.keys()) | set(CENTENAS.keys()) | set(MULTS.keys())
ALL_NUMS = LITERAL_NUMS | {"real", "reais", "centavo", "centavos", "e", "de"}

def is_simple_digit(s):
    c = re.sub(r'^(?:r\$)?\s*', '', s, flags=re.I)
    if not re.match(r'^\d+(?:[.,]\d+)*$', c): return False
    if len(c) >= 10 and '.' not in c and ',' not in c: return False
    return True

def parse_block(tokens):
    total = 0.0
    current = 0.0
    cents = 0.0
    in_cents = False
    
    for t in tokens:
        t_clean = remover_acentos(t.lower())
        t_norm = re.sub(r'\W+', '', t_clean)
        
        if is_simple_digit(t):
            v_str = t.lower().replace('r$', '').strip()
            try:
                v = float(v_str.replace('.', '').replace(',', '.')) if ',' in v_str else float(v_str.replace('.', ''))
            except: v = 0.0
            if in_cents: cents += v
            else: current += v
        elif t_norm in UNIDADES: current += UNIDADES[t_norm]
        elif t_norm in DEZENAS: current += DEZENAS[t_norm]
        elif t_norm in CENTENAS: current += CENTENAS[t_norm]
        elif t_norm in MULTS:
            total += (current or 1.0) * MULTS[t_norm]
            current = 0
        elif t_norm in ("real", "reais"):
            total += current
            current = 0
        elif t_norm in ("centavo", "centavos"):
            cents += current
            current = 0
            in_cents = True
        elif t_norm == "de":
            continue
            
    total += current
    return total + (cents / 100.0 if in_cents else 0.0)

def texto_para_numero_e_substituir(texto: str):
    if not texto: return texto
    # Remove vírgulas entre termos numéricos (ex: mil, novecentos)
    texto = re.sub(r'(\w+),\s*(\w+)', lambda m: f"{m.group(1)} {m.group(2)}" if remover_acentos(m.group(1).lower()) in ALL_NUMS and remover_acentos(m.group(2).lower()) in ALL_NUMS else m.group(0), texto)
    
    tokens = texto.split()
    tokens_match = [re.sub(r'\W+', '', remover_acentos(t.lower())) for t in tokens]
    
    blocks = []
    i = 0
    while i < len(tokens_match):
        if tokens_match[i] in ALL_NUMS or is_simple_digit(tokens[i]):
            start = i
            has_literal = False
            while i < len(tokens_match):
                if not (tokens_match[i] in ALL_NUMS or is_simple_digit(tokens[i])): break
                if i > start and is_simple_digit(tokens[i-1]) and is_simple_digit(tokens[i]): break
                if tokens_match[i] in LITERAL_NUMS or tokens_match[i] in {"real", "reais", "centavo", "centavos"}:
                    has_literal = True
                i += 1
            if has_literal:
                end = i - 1
                if not (start == end and tokens_match[start] in ["um", "uma", "e"]):
                    blocks.append((start, end))
        else: i += 1

    for start, end in reversed(blocks):
        val = parse_block(tokens[start:end+1])
        suffix = re.search(r'(\W+)$', tokens[end]).group(1) if re.search(r'(\W+)$', tokens[end]) else ""
        res = f"{val:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') + suffix
        tokens[start:end+1] = [res]
    return " ".join(tokens)
