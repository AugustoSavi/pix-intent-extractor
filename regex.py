import re
import json
from typing import List, Dict
from utils.conversor_extenso import texto_para_numero_e_substituir

# =========================================================
# REGEX
# =========================================================

REGEX_VALUE = re.compile(
    r'''
    (?<!\d)
    (?:r\$?\s*)?
    (
        \d{1,3}(?:\.\d{3})*,\d{2}   # BR
        |
        \d+(?:\.\d{2})             # US
    )
    (?!\d)
    ''',
    re.I | re.X
)

REGEX_EMAIL = re.compile(
    r'[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}', re.I
)

REGEX_CPF = re.compile(
    r'(?<!\d)\d{3}\.?\d{3}\.?\d{3}-?\d{2}(?!\d)'
)

REGEX_PHONE = re.compile(
    r'(?:\+55\s*)?(?:\(?\d{2}\)?\s*)?\d{4,5}[-\s]?\d{4}'
)

REGEX_UUID = re.compile(
    r'\b[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}\b', re.I
)

REGEX_NUMERIC_FALLBACK = re.compile(
    r'(?<!\d)\d{9,14}(?!\d)'
)

# =========================================================
# NORMALIZAÇÃO
# =========================================================

def normalizar_texto(texto: str) -> str:
    texto = texto.lower()
    return texto


# =========================================================
# CPF
# =========================================================

def validar_cpf(cpf: str) -> bool:
    cpf = re.sub(r'\D', '', cpf)

    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    for i in [9, 10]:
        soma = sum(int(cpf[num]) * ((i + 1) - num) for num in range(i))
        dig = (soma * 10) % 11
        dig = 0 if dig == 10 else dig
        if dig != int(cpf[i]):
            return False

    return True


# =========================================================
# EXTRAÇÃO
# =========================================================

def extrair_valores(texto: str) -> List[str]:
    return REGEX_VALUE.findall(texto)


def extrair_chaves(texto: str) -> List[Dict]:
    chaves = []

    for m in REGEX_EMAIL.finditer(texto):
        chaves.append({"valor": m.group(), "tipo": "email"})

    for m in REGEX_UUID.finditer(texto):
        chaves.append({"valor": m.group(), "tipo": "uuid"})

    for m in REGEX_CPF.finditer(texto):
        chaves.append({"valor": m.group(), "tipo": "cpf"})

    for m in REGEX_PHONE.finditer(texto):
        chaves.append({"valor": m.group(), "tipo": "telefone"})

    return chaves


# =========================================================
# AMBIGUIDADE
# =========================================================

def detectar_ambiguidade_numerica(numeros: List[str]) -> bool:
    cpfs_validos = []

    for n in numeros:
        if validar_cpf(n):
            cpfs_validos.append(n)

    return len(cpfs_validos) >= 2


# =========================================================
# PIPELINE PRINCIPAL
# =========================================================

def extrair_pix(texto: str) -> Dict:
    original = texto
    normalizado = normalizar_texto(texto)
    texto_para_numero = texto_para_numero_e_substituir(normalizado)
    valores = extrair_valores(texto_para_numero)
    chaves = extrair_chaves(texto_para_numero)

    # fallback: números longos sem máscara
    numericos = REGEX_NUMERIC_FALLBACK.findall(texto)
    ambiguo = detectar_ambiguidade_numerica(numericos)
    resultado = {
        "texto_original": original,
        "normalizado": normalizado,
        "texto_para_numero": texto_para_numero,
        "valor": valores[0] if valores else None,
        "chave": None,
        "tipo_chave": None,
        "ambiguo": ambiguo
    }

    # prioridade de chave
    prioridade = ["email", "uuid", "cpf", "telefone"]

    for tipo in prioridade:
        for c in chaves:
            if c["tipo"] == tipo:
                if tipo == "cpf" and not validar_cpf(c["valor"]):
                    continue
                resultado["chave"] = c["valor"]
                resultado["tipo_chave"] = tipo
                return resultado

    return resultado

# =========================================================
# EXEMPLO DE USO
# =========================================================

if __name__ == "__main__":

    resultados = []

    with open("data/dataset.txt", "r", encoding="utf-8") as f:
        for linha in f:
            texto = linha.strip()
            if not texto:
                continue

            resultado = extrair_pix(texto)
            resultados.append(resultado)

    with open("data/resultados.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)