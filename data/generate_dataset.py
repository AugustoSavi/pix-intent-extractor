import sys
import os
import random
import json
from faker import Faker
from num2words import num2words

# Adiciona o diretório raiz do projeto ao sys.path para importações
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ------------------ SETUP ------------------

TEMPLATES = [
    "Enviar {valor} para {chave}",
    "Pode mandar {valor} no pix do {chave}",
    "Pix de {valor} chave {chave}",
    "Minha chave é {chave} valor {valor}",
    "manda {valor} pra esse pix aqui {chave}",
    "Minha chave: {chave} Valor: {valor}",
    "faz um pix de {valor} pra {chave}",
    "me transfere {valor} usando a chave {chave}",
    "pix no valor de {valor} para a chave {chave}",
    "envia {valor} nesse pix {chave}",
    "pode fazer o pix de {valor} pra chave {chave}",
    "preciso receber {valor}, chave pix {chave}",
    "pix {chave} no valor {valor}",
    "manda um pix aí: {valor} – {chave}",
    "transferência via pix de {valor} para {chave}",
    "segue a chave {chave} pra enviar {valor}",
    "me manda {valor} nesse pix {chave}",
    "faz o pix aí de {valor} pra {chave}",
    "manda um pix de {valor} no {chave}",
    "pix {valor} chave {chave} por favor",
    "me transfere {valor} pra essa chave {chave}",
    "envia {valor} pra {chave} no pix",
    "passa {valor} nesse pix aqui ó {chave}",
    "manda {valor} nesse número {chave}",
    "pix de {valor} pra chave {chave}",
    "me paga no pix {valor} chave {chave}",
    "faz um pix pra mim {valor} usando {chave}",
    "consegue mandar {valor} no pix {chave}?",
    "pix pra {chave} no valor de {valor}",
    "manda o pix {valor} pra {chave}",
    "transferência pix {valor} {chave}",
    "{valor} {chave}",
    "{chave} {valor}",
    "[{timestamp}] {nome}: Me manda {valor} no pix\\n[{timestamp}] {nome}: {chave}",
    "[{timestamp}] {nome}: Me manda {valor}\\n[{timestamp}] {nome}: {chave}",
    "[{timestamp}] {nome}: {chave}\\n[{timestamp}] {nome}: Me manda {valor}",
    "{chave}",
    "{valor}"
]

# ------------------ GERADORES ------------------

def gerar_valor_com_meta():
    if random.choice([True, False]):
        valor = float(random.randint(1, 1000)) # Valores menores para evitar ambiguidades com pontos de milhar por enquanto
    else:
        valor = round(random.uniform(0.01, 1_000_000), 2)

    reais = int(valor)
    centavos = int(round((valor - reais) * 100))

    if random.choice([True, False]):
        # Formato numérico
        if centavos == 0 and random.choice([True, False]):
            fmt = f"{reais:,}".replace(",", ".")
        else:
            fmt = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        if random.choice([True, False]):
            txt = fmt
        else:
            txt = f"R$ {fmt}"
    else:
        # Formato extenso
        txt = num2words(reais, lang="pt_BR") + " reais"
        if centavos > 0:
            txt += " e " + num2words(centavos, lang="pt_BR") + " centavos"
    
    # O valor esperado para o validador deve ser a string formatada BR que o regex extrai
    valor_esperado = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return txt, valor_esperado


def gerar_chave_pix(fake: Faker):
    tipo = random.choice(["free_email","email", "telefone", "cpf", "uuid"])

    if tipo == "free_email":
        return fake.email()
    if tipo == "email":
        return fake.free_email()
    if tipo == "telefone":
        number = fake.phone_number()
        if random.choice([True, False]):
            return "".join(filter(str.isdigit, number))
        return number
    if tipo == "cpf":
        cpf = fake.cpf()
        if random.choice([True, False]):
            return "".join(filter(str.isdigit, cpf))
        return cpf

    return fake.uuid4()

# ------------------ WORKER ------------------

def build_batch(size: int):
    fake = Faker("pt_BR")
    batch = []

    for _ in range(size):
        texto_valor, valor_esperado = gerar_valor_com_meta()
        chave = gerar_chave_pix(fake)
        nome = fake.name()
        timestamp = fake.date_time_this_year().strftime("%d/%m, %H:%M")
        template = random.choice(TEMPLATES)

        text = template.format(valor=texto_valor, chave=chave, nome=nome, timestamp=timestamp)

        # Determina o que realmente está no texto para o ground truth
        valor_gt = valor_esperado if "{valor}" in template or template == "{valor}" else None
        chave_gt = chave if "{chave}" in template or template == "{chave}" else None

        batch.append({
            "text": text,
            "valor": valor_gt,
            "chave": chave_gt
        })

    return batch

# ------------------ MAIN ------------------

if __name__ == "__main__":
    print("🚀 Gerando dataset...")

    data = build_batch(10_000)

    # Salvar o ground truth para validação
    with open("data/dataset.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("✅ Dataset e Ground Truth gerados com sucesso.")
