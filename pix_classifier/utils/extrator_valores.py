import re

REGEX_VALUE = re.compile(
    r'''
    (?<!\d)
    (?:
        (?:r\$?\s*)
        (
            \d{1,3}(?:\.\d{3})*,\d{1,2}
            |
            \d{1,3}(?:,\d{3})*\.\d{1,2}
            |
            \d+[,.]\d{1,2}
            |
            \d{1,3}(?:\.\d{3})+
            |
            \d{1,3}(?:,\d{3})+
            |
            \d+
        )
        |
        (
            \d{1,3}(?:\.\d{3})*,\d{1,2}
            |
            \d{1,3}(?:,\d{3})*\.\d{1,2}
            |
            \d+[,.]\d{1,2}
            |
            \d{1,3}(?:\.\d{3})+
            |
            \d{1,3}(?:,\d{3})+
            |
            \d+(?=\s*reais?)
            |
            \d+
        )
    )
    (?!\d)
    ''',
    re.I | re.X
)

def extrair_valores(texto: str) -> list:
    # Coletamos todos os matches
    matches = []
    for m in REGEX_VALUE.finditer(texto):
        g1, g2 = m.groups()
        val = g1 or g2
        
        # Score básico
        score = 1
        if g1: # Foi precedido por R$
            score = 3
        elif ',' in val or '.' in val:
            score = 2
            
        # Verifica se 'reais' está logo após (mesmo que tenha sido convertido, 
        # o texto_para_numero pode ter mantido ou o regex de valor pode ter capturado)
        # No texto_para_numero, '10 reais' vira '10,00'
        if re.search(fr'{re.escape(val)}\s*reais?', texto, re.I):
            score = 3
            
        matches.append((val, score))
    
    # Ordena por score descendente
    if len(matches) > 1:
        matches.sort(key=lambda x: x[1], reverse=True)
        
    return [m[0] for m in matches]
