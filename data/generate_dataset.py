import random
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from faker import Faker
from num2words import num2words

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
    "{chave} {valor}"
]


# ------------------ GERADORES ------------------

def gerar_valor():
    valor = round(random.uniform(0.01, 1_000_000), 2)
    reais = int(valor)
    centavos = int(round((valor - reais) * 100))

    if random.choice([True, False]):
        if random.choice([True, False]):
            return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    else:
        texto = num2words(reais, lang="pt_BR") + " reais"
        if centavos > 0:
            texto += " e " + num2words(centavos, lang="pt_BR") + " centavos"
        return texto


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

def build_batch(batch_size: int):
    fake = Faker("pt_BR")
    batch = []

    for _ in range(batch_size):
        valor = gerar_valor()
        chave = gerar_chave_pix(fake)
        template = random.choice(TEMPLATES)

        text = template.format(valor=valor, chave=chave)

        valor_start = text.find(valor)
        chave_start = text.find(chave)

        # segurança extra
        if valor_start == -1 or chave_start == -1:
            continue

        entities = [
            (valor_start, valor_start + len(valor), "PIX_VALUE"),
            (chave_start, chave_start + len(chave), "PIX_KEY"),
        ]

        batch.append((text, {"entities": entities}))

    return batch

# ------------------ DATASET MULTIPROCESS ------------------

def build_examples_multiprocess(
    total=50_000,
    workers=8,
    batch_size=500
):
    examples = []

    batches = total // batch_size
    remainder = total % batch_size

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(build_batch, batch_size)
            for _ in range(batches)
        ]

        if remainder:
            futures.append(executor.submit(build_batch, remainder))

        for future in as_completed(futures):
            examples.extend(future.result())

    return examples

# ------------------ MAIN ------------------

if __name__ == "__main__":
    print("🚀 Gerando dataset...")

    data = build_examples_multiprocess(
        total=10_000,
        workers=min(8, os.cpu_count()),
        batch_size=500
    )

    random.shuffle(data)
    # Salvar o resultado em arquivo txt
    open("data/dataset.txt", "w").write(
        "\n".join([f"{text}" for text, annot in data])
    )

    print("✅ Dataset gerado com sucesso.")
