# migrar_regras.py
import json
from database import supabase # Importa sua conexão já configurada

REGRAS_ID = 1
REGRAS_PATH = "config/regras.json" # Caminho para seu arquivo original

def migrar():
    print("Iniciando migração do regras.json para o Supabase...")
    try:
        # 1. Carrega o arquivo JSON local
        with open(REGRAS_PATH, "r", encoding="utf-8") as f:
            regras_json = json.load(f)

        print("Arquivo JSON carregado com sucesso.")

        # 2. Usa 'upsert' para inserir os dados no Supabase
        print("Enviando dados para o Supabase...")
        supabase.table("regras").upsert({
            "id": REGRAS_ID,
            "conteudo": regras_json
        }).execute()

        print("\n✅ Migração concluída com sucesso! Suas regras agora estão no banco de dados.")

    except FileNotFoundError:
        print(f"❌ ERRO: Arquivo de regras '{REGRAS_PATH}' não encontrado.")
        print("Verifique se o caminho para o arquivo regras.json está correto.")
    except Exception as e:
        print(f"❌ Ocorreu um erro inesperado durante a migração: {e}")

if __name__ == "__main__":
    migrar()
