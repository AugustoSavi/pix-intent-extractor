# 🔑 Extrator de PIX (Valor + Chave)

Projeto em **Python** para **extração automática de pedidos de PIX** a partir de texto livre (mensagens informais, WhatsApp, etc.), identificando:

* 💰 **Valor do PIX** (número ou por extenso)
* 🧾 **Chave PIX** (email, CPF, telefone ou UUID)
* ⚠️ **Ambiguidade numérica** (ex: múltiplos CPFs no texto)

O projeto combina **regex**, **normalização linguística** e **conversão de números por extenso**, além de um **gerador de dataset sintético** para NLP.

---

## ✨ Funcionalidades

* ✅ Detecta valores em formato brasileiro e americano
* ✅ Converte valores escritos por extenso para número (`"dez reais e cinquenta centavos" → 10.50`)
* ✅ Identifica chaves PIX dos tipos:

  * Email
  * CPF (com validação)
  * Telefone
  * UUID
* ✅ Prioriza automaticamente o tipo de chave mais confiável
* ✅ Detecta ambiguidade quando múltiplos CPFs válidos aparecem
* ✅ Geração de dataset sintético realista para treinamento NLP

---

## 🧠 Pipeline de Extração

Fluxo principal (`extrair_pix`):

1. Normaliza o texto
2. Converte números por extenso em valores numéricos
3. Extrai valores monetários via regex
4. Extrai possíveis chaves PIX
5. Valida CPF quando aplicável
6. Resolve prioridade da chave
7. Marca ambiguidade numérica, se houver

---

## 📦 Estrutura do Projeto

```text
.
├── regex.py                     # Pipeline principal de extração PIX
├── utils/
│   └── conversor_extenso.py     # Conversão de números por extenso
├── data/
│   ├── generate_dataset.py      # Gerador de dataset sintético
│   ├── dataset.txt              # Mensagens geradas
│   └── resultados.json          # Saída da extração
```

---

## 🚀 Exemplo de Uso

```python
from regex import extrair_pix

texto = "faz um pix de dez reais e cinquenta centavos pra teste@email.com"

resultado = extrair_pix(texto)
print(resultado)
```

### 📤 Saída esperada

```json
{
  "texto_original": "faz um pix de dez reais e cinquenta centavos pra teste@email.com",
  "normalizado": "faz um pix de dez reais e cinquenta centavos pra teste@email.com",
  "texto_para_numero": "faz um pix de 10.50 pra teste@email.com",
  "valor": "10,50",
  "chave": "teste@email.com",
  "tipo_chave": "email",
  "ambiguo": false
}
```

---

## 🧪 Geração de Dataset Sintético

O script `generate_dataset.py` cria milhares de mensagens realistas de PIX com:

* Valores entre **R$ 0,01 e R$ 1.000.000**
* Valores numéricos e por extenso
* Diferentes formatos de chave PIX
* Templates variados de linguagem informal

### Executar:

```bash
python data/generate_dataset.py
```

Isso irá gerar:

* `data/dataset.txt` → mensagens cruas

---

## 🧩 Casos Tratados

* `R$ 1.234,56`
* `1234.56`
* `mil duzentos reais`
* `dois reais e cinquenta centavos`
* CPF com ou sem máscara
* Telefone com ou sem DDI / pontuação

---

## ⚠️ Ambiguidade Numérica

Se o texto contiver **dois ou mais CPFs válidos**, o campo:

```json
"ambiguo": true
```

será marcado para indicar necessidade de validação adicional.

---

## 🛠 Dependências

Principais libs usadas:

* `num2words`
