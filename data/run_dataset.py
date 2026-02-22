import json
import sys
import os

# Adiciona o diretório raiz do projeto ao sys.path para importações
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pix_classifier import extrair_pix

if __name__ == "__main__":
    resultados = []
    print("🚀 processando dataset...")
    try:
        with open("data/dataset.json", "r", encoding="utf-8") as f:
            dataset = json.load(f)
            for item in dataset:
                texto = item["text"]
                if not texto: # estourar erro para identificar casos de texto vazio
                    raise ValueError(f"Texto vazio encontrado no item: {item}")
                resultados.append(extrair_pix(texto))
        with open("data/resultados.json", "w", encoding="utf-8") as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)
        print("✅ Textos processados e resultados salvos")
    except FileNotFoundError:
        print("❌ Arquivo data/dataset.json não encontrado. Execute generate_dataset.py primeiro.")
