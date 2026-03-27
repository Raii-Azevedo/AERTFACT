# importar_materiais.py
import os
import sys

# Adicionar diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import importar_materiais_do_excel

print("🚀 Iniciando importação de materiais...")
print(f"📁 Diretório atual: {os.getcwd()}")

# Verificar se a pasta assets existe
if os.path.exists("assets"):
    print("✅ Pasta 'assets' encontrada")
    print("📂 Arquivos na pasta assets:")
    for file in os.listdir("assets"):
        if file.endswith(('.xlsx', '.xls')):
            print(f"   - {file}")
else:
    print("❌ Pasta 'assets' não encontrada")
    print("📁 Criando pasta assets...")
    os.makedirs("assets", exist_ok=True)
    print("✅ Pasta 'assets' criada. Coloque o arquivo Excel lá.")

# Executar importação
print("\n📖 Importando materiais...")
resultado = importar_materiais_do_excel()

if resultado:
    print("\n✅ Importação concluída com sucesso!")
else:
    print("\n❌ Falha na importação. Verifique:")
    print("   1. Se o arquivo Excel está na pasta 'assets'")
    print("   2. Se o nome do arquivo está correto")
    print("   3. Se a sheet 'Content Library' existe")