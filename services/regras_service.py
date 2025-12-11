# services/regras_service.py
import json
import os

# Caminho do arquivo de regras (ajuste se quiser colocar em outra pasta)
REGRAS_PATH = "config/regras.json"

def carregar_regras():
    """
    Carrega o arquivo regras.json.
    Lança exceção se o arquivo não existir ou estiver malformado.
    """
    if not os.path.exists(REGRAS_PATH):
        raise FileNotFoundError("Arquivo 'regras.json' não encontrado na raiz do projeto.")
    
    try:
        with open(REGRAS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Erro ao decodificar 'regras.json': {e}")

def salvar_regras(regras):
    """
    Salva o dicionário `regras` no arquivo regras.json.
    """
    try:
        with open(REGRAS_PATH, "w", encoding="utf-8") as f:
            json.dump(regras, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        raise RuntimeError(f"Erro ao salvar regras: {e}")