import re

REGEX_EMAIL = re.compile(r'[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}', re.I)
REGEX_CPF = re.compile(r'(?<!\d)\d{3}\.?\d{3}\.?\d{3}-?\d{2}(?!\d)')
REGEX_UUID = re.compile(r'\b[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}\b', re.I)
REGEX_PHONE = re.compile(
    r'''
    (?<![\d,])
    (?:
        (?:\+55\s*)?
        (?:
            # Long number (10-14 digits)
            \d{10,14}
            |
            # Service: 0[3589]00 ...
            0[3589]00[-\s]?\d{3}[-\s]?\d{4}
            |
            # Standard: (XX) XXXX-XXXX or XX XXXX-XXXX
            (?:\(?0?\d{2}\)?\s*)\d{4,5}[-\s]?\d{4}
        )
    )
    (?!\d)
    ''',
    re.I | re.X
)

def validar_cpf(cpf: str) -> bool:
    cpf = re.sub(r'\D', '', cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    for i in [9, 10]:
        soma = sum(int(cpf[num]) * ((i + 1) - num) for num in range(i))
        dig = (soma * 10) % 11
        dig = 0 if dig == 10 else dig
        if dig != int(cpf[i]): return False
    return True

def extrair_chaves(texto: str) -> list:
    chaves = []
    for m in REGEX_EMAIL.finditer(texto):
        chaves.append({"valor": m.group(), "tipo": "email"})
    for m in REGEX_UUID.finditer(texto):
        chaves.append({"valor": m.group(), "tipo": "uuid"})
    for m in REGEX_CPF.finditer(texto):
        if validar_cpf(m.group()):
            chaves.append({"valor": m.group(), "tipo": "cpf"})
    for m in REGEX_PHONE.finditer(texto):
        chaves.append({"valor": m.group(), "tipo": "telefone"})
    return chaves
