import re

UNIDADES = {
    "zero": 0, "um": 1, "uma": 1,
    "dois": 2, "duas": 2,
    "tres": 3, "quatro": 4, "cinco": 5,
    "seis": 6, "sete": 7, "oito": 8, "nove": 9
}

DEZENAS = {
    "dez": 10, "onze": 11, "doze": 12, "treze": 13,
    "quatorze": 14, "catorze": 14, "quinze": 15,
    "dezesseis": 16, "dezessete": 17,
    "dezoito": 18, "dezenove": 19,
    "vinte": 20, "trinta": 30, "quarenta": 40,
    "cinquenta": 50, "sessenta": 60,
    "setenta": 70, "oitenta": 80, "noventa": 90
}

CENTENAS = {
    "cem": 100, "cento": 100,
    "duzentos": 200, "trezentos": 300,
    "quatrocentos": 400, "quinhentos": 500,
    "seiscentos": 600, "setecentos": 700,
    "oitocentos": 800, "novecentos": 900
}

MULTIPLICADORES = {
    "mil": 1_000,
    "milhao": 1_000_000,
    "milhoes": 1_000_000,
    "bilhao": 1_000_000_000,
    "bilhoes": 1_000_000_000
}

NUMERIC_TOKENS = (
    set(UNIDADES.keys())
    | set(DEZENAS.keys())
    | set(CENTENAS.keys())
    | set(MULTIPLICADORES.keys())
    | {"real", "reais", "centavo", "centavos", "e"}
)

def tokenize(texto):
    return re.findall(r"\w+", texto)


def texto_para_numero_e_substituir(texto: str):
    tokens = tokenize(texto)
    original_tokens = texto.split()

    inteiro = 0
    atual = 0
    centavos = 0

    inicio = None
    fim = None

    for i, token in enumerate(tokens):
        if token in NUMERIC_TOKENS:
            if inicio is None:
                inicio = i
            fim = i

            if token in UNIDADES:
                atual += UNIDADES[token]

            elif token in DEZENAS:
                atual += DEZENAS[token]

            elif token in CENTENAS:
                atual += CENTENAS[token]

            elif token in MULTIPLICADORES:
                atual = max(1, atual) * MULTIPLICADORES[token]
                inteiro += atual
                atual = 0

            elif token in ("real", "reais"):
                inteiro += atual
                atual = 0

            elif token in ("centavo", "centavos"):
                centavos = atual
                atual = 0

        elif inicio is not None:
            break

    inteiro += atual
    valor = round(inteiro + (centavos / 100), 2)

    if inicio is None:
        return texto

    # reconstrói o trecho original respeitando pontuação
    trecho_original = " ".join(original_tokens[inicio:fim + 1])
    texto_final = texto.replace(trecho_original, f"{valor:.2f}", 1)

    return texto_final
