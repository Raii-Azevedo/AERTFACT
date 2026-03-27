#!/usr/bin/env python3
"""
Script para testar a conexão com PostgreSQL
Execute este script para verificar se a configuração do PostgreSQL está correta.
"""

import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def test_postgresql_connection():
    """Testa a conexão com PostgreSQL"""
    try:
        import psycopg2

        # Configurações do banco
        db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'ae_knowledge'),
            'user': os.getenv('DB_USER', ''),
            'password': os.getenv('DB_PASSWORD', '')
        }

        print("🔍 Testando conexão com PostgreSQL...")
        print(f"📍 Host: {db_config['host']}:{db_config['port']}")
        print(f"📊 Database: {db_config['database']}")
        print(f"👤 User: {db_config['user']}")

        # Tentar conectar
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # Testar query simples
        cursor.execute("SELECT version();")
        version = cursor.fetchone()

        print("✅ Conexão com PostgreSQL estabelecida com sucesso!")
        print(f"📋 Versão do PostgreSQL: {version[0][:50]}...")

        # Fechar conexão
        cursor.close()
        conn.close()

        return True

    except ImportError:
        print("❌ psycopg2 não está instalado. Execute: pip install psycopg2-binary")
        return False
    except psycopg2.Error as e:
        print(f"❌ Erro na conexão com PostgreSQL: {e}")
        print("\n🔧 Verifique:")
        print("   - PostgreSQL está rodando?")
        print("   - Credenciais no arquivo .env estão corretas?")
        print("   - Banco de dados existe?")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def test_sqlite_connection():
    """Testa a conexão com SQLite"""
    try:
        import sqlite3

        db_path = os.getenv('DB_PATH', 'ae_knowledge.db')
        print(f"🔍 Testando conexão com SQLite: {db_path}")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT sqlite_version();")
        version = cursor.fetchone()

        print("✅ Conexão com SQLite estabelecida com sucesso!")
        print(f"📋 Versão do SQLite: {version[0]}")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(f"❌ Erro na conexão com SQLite: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Teste de Conexão com Banco de Dados")
    print("=" * 50)

    db_type = os.getenv('DB_TYPE', 'sqlite').lower()

    if db_type == 'postgresql':
        success = test_postgresql_connection()
    else:
        success = test_sqlite_connection()

    print("\n" + "=" * 50)
    if success:
        print("🎉 Teste concluído com sucesso!")
        print("💡 O sistema está pronto para uso.")
    else:
        print("⚠️  Teste falhou. Verifique a configuração.")
        sys.exit(1)