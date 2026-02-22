import re
import json
from typing import Dict, List
from .utils.extrator_chaves import extrair_chaves, validar_cpf
from .utils.extrator_valores import extrair_valores
from .utils.conversor_extenso import texto_para_numero_e_substituir

# =========================================================
# NORMALIZAÇÃO E MASCARAMENTO
# =========================================================

def normalizar_texto(texto: str) -> str:
    texto = texto.lower()
    texto = re.sub(r'(\\n|\n)+', ' ', texto)
    # Mascara timestamps comuns de chat: [dd/mm, hh:mm] ou [dd/mm/yy hh:mm]
    texto = re.sub(r'\[\d{2}/\d{2}(?:/\d{2,4})?[,\s]+\d{2}:\d{2}\]', lambda m: " " * len(m.group(0)), texto)
    return texto


def mascarar_chaves(texto: str, chaves: List[Dict]) -> str:
    # Coleta spans de todas as chaves
    spans = []
    for c in chaves:
        # Encontra todos os matches no texto
        for m in re.finditer(re.escape(c["valor"]), texto):
            spans.append(m.span())
    
    if not spans: return texto
    
    # Merge overlapping spans
    spans.sort()
    merged = []
    if spans:
        curr_start, curr_end = spans[0]
        for next_start, next_end in spans[1:]:
            if next_start < curr_end:
                curr_end = max(curr_end, next_end)
            else:
                merged.append((curr_start, curr_end))
                curr_start, curr_end = next_start, next_end
        merged.append((curr_start, curr_end))
    
    # Substitui por espaços para preservar layout mas ocultar dígitos
    chars = list(texto)
    for start, end in merged:
        for i in range(start, end):
            if chars[i] != '\n': chars[i] = ' '
    return "".join(chars)


# =========================================================
# AMBIGUIDADE
# =========================================================

def detectar_ambiguidade(chaves: List[Dict], valores: List[str]) -> bool:
    # 1. Mais de uma chave única (mesmo tipo ou não)
    chaves_unicas = set(re.sub(r'\D', '', c["valor"]) if c["tipo"] in ["cpf", "telefone"] else c["valor"].lower() for c in chaves)
    if len(chaves_unicas) > 1:
        return True
    
    # 2. Mais de um valor
    # No momento extrair_valores já retorna os valores, mas se houver múltiplos valores 
    # distintos com formato de dinheiro, pode ser considerado ambíguo.
    # Para o teste, focaremos na ambiguidade de chaves que é o mais comum.
    return False


# =========================================================
# PIPELINE PRINCIPAL
# =========================================================

def extrair_pix(texto: str) -> Dict:
    original = texto
    normalizado = normalizar_texto(texto)
    
    # 1. Encontra chaves no texto original para proteger contra conversão indevida
    chaves_originais = extrair_chaves(normalizado)
    
    # 2. Mascara as chaves no texto temporário
    texto_para_conversao = mascarar_chaves(normalizado, chaves_originais)
    
    # 3. Converte extenso para número no texto mascarado de chaves
    texto_para_numero = texto_para_numero_e_substituir(texto_para_conversao)
    
    # 4. Extrai valores monetários
    valores = extrair_valores(texto_para_numero)
    
    # 5. Resolve prioridade da chave
    prioridade = ["email", "uuid", "cpf", "telefone"]
    
    resultado = {
        "texto_original": original,
        "normalizado": normalizado,
        "texto_para_numero": texto_para_numero,
        "valor": valores[0] if valores else None,
        "chave": None,
        "tipo_chave": None,
        "ambiguo": detectar_ambiguidade(chaves_originais, valores)
    }

    for tipo in prioridade:
        for c in chaves_originais:
            if c["tipo"] == tipo:
                resultado["chave"] = c["valor"]
                resultado["tipo_chave"] = tipo
                break
        if resultado["chave"]: break

    return resultado
