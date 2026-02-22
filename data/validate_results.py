import json
import os
import re

def parse_to_float(val):
    if val is None:
        return None
    # Converte '1.234,56' ou '1234,56' para float 1234.56
    clean = str(val).lower().replace("r$", "").replace(" ", "").strip()
    if "," in clean:
        # Formato brasileiro: 1.234,56 -> 1234.56
        clean = clean.replace(".", "").replace(",", ".")
    elif "." in clean:
        # Se houver apenas pontos, pode ser separador de milhar (BR) ou decimal (US/INT)
        # Heurística: se tiver mais de um ponto, ou se tiver um ponto seguido de exatamente 3 dígitos e tiver mais de 4 caracteres
        # (ex: 1.000 -> 1000, mas 1.00 -> 1.00)
        parts = clean.split(".")
        if len(parts) > 2 or (len(parts[-1]) == 3 and len(clean) > 4):
            clean = clean.replace(".", "")
    
    try:
        return round(float(clean), 2)
    except ValueError:
        return None

def normalize_key(key):
    if key is None:
        return None
    # Remove tudo que não for alfanumérico para comparação robusta
    # (Ex: (011) vs 011)
    # Mas mantém email e UUID (letras e hífens)
    if "@" in key or "-" in key:
        return key.lower().strip()
    return re.sub(r'\D', '', key)

def validate():
    try:
        with open("data/dataset.json", "r", encoding="utf-8") as f:
            ground_truth = json.load(f)
        
        with open("data/resultados.json", "r", encoding="utf-8") as f:
            resultados = json.load(f)
    except FileNotFoundError as e:
        print(f"❌ Erro: Arquivo não encontrado - {e.filename}")
        return

    total = min(len(ground_truth), len(resultados))
    val_correct = 0
    key_correct = 0
    both_correct = 0
    errors = []

    for i in range(total):
        gt = ground_truth[i]
        res = resultados[i]

        gt_val = parse_to_float(gt["valor"])
        res_val = parse_to_float(res["valor"])
        
        gt_key = normalize_key(gt["chave"])
        res_key = normalize_key(res["chave"])

        v_ok = (gt_val == res_val)
        k_ok = (gt_key == res_key)

        if v_ok: val_correct += 1
        if k_ok: key_correct += 1
        if v_ok and k_ok: both_correct += 1
        else:
            if len(errors) < 5:
                errors.append({
                    "texto": gt["text"],
                    "esperado": {"valor": gt_val, "chave": gt_key},
                    "obtido": {"valor": res_val, "chave": res_key}
                })

    print("-" * 40)
    print(f"Total: {total}")
    print(f"Valor: {val_correct} ({val_correct/total:.2%})")
    print(f"Chave: {key_correct} ({key_correct/total:.2%})")
    print(f"Ambos: {both_correct} ({both_correct/total:.2%})")
    print("-" * 40)

    if errors:
        print("\nAlguns erros encontrados:")
        for err in errors:
            print(f"T: {err['texto']}")
            print(f"  Exp: {err['esperado']}")
            print(f"  Obt: {err['obtido']}")

if __name__ == "__main__":
    validate()
