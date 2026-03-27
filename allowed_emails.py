# allowed_emails.py
import streamlit as st
import os
from database import get_connection, return_connection

# Detecta se está usando PostgreSQL (Railway) ou SQLite (local)
DB_TYPE = os.environ.get('DB_TYPE', 'sqlite')
DATABASE_URL = os.environ.get('DATABASE_URL', '')

# Se tiver DATABASE_URL, usa PostgreSQL
if DATABASE_URL:
    DB_TYPE = 'postgresql'

def _get_placeholder():
    """Retorna o placeholder correto para cada banco"""
    return '%s' if DB_TYPE == 'postgresql' else '?'

@st.cache_data(ttl=300)
def is_email_allowed(email):
    """Verifica se o email está autorizado"""
    if not email:
        return False
    
    email = email.lower().strip()
    placeholder = _get_placeholder()
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT id FROM allowed_emails WHERE LOWER(email) = {placeholder}", (email,))
        result = cursor.fetchone()
        cursor.close()
        return_connection(conn)
        return result is not None
    except Exception as e:
        print(f"Erro ao verificar email: {e}")
        return False

@st.cache_data(ttl=300)
def get_user_role(email):
    """Retorna o role do usuário"""
    if not email:
        return None
    
    email = email.lower().strip()
    placeholder = _get_placeholder()
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT role FROM allowed_emails WHERE LOWER(email) = {placeholder}", (email,))
        result = cursor.fetchone()
        cursor.close()
        return_connection(conn)
        return result[0] if result else None
    except Exception as e:
        print(f"Erro ao buscar role: {e}")
        return None

def is_admin(email):
    return get_user_role(email) == 'admin'

def is_viewer(email):
    return get_user_role(email) == 'viewer'

def can_edit(email):
    role = get_user_role(email)
    return role in ['admin', 'user']

def add_allowed_email(email, role='user', added_by=None):
    """Adiciona um email à lista de permitidos"""
    if role not in ['admin', 'user', 'viewer']:
        role = 'user'
    
    placeholder = _get_placeholder()
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if DB_TYPE == 'postgresql':
            cursor.execute("""
                INSERT INTO allowed_emails (email, role, added_by)
                VALUES (%s, %s, %s)
                ON CONFLICT (email) DO UPDATE SET role = EXCLUDED.role
            """, (email.lower().strip(), role, added_by))
        else:
            cursor.execute("""
                INSERT INTO allowed_emails (email, role, added_by)
                VALUES (?, ?, ?)
                ON CONFLICT(email) DO UPDATE SET role = excluded.role
            """, (email.lower().strip(), role, added_by))
        
        conn.commit()
        cursor.close()
        return_connection(conn)
        # Clear cache
        is_email_allowed.clear()
        get_user_role.clear()
        get_all_allowed_emails.clear()
        return True
    except Exception as e:
        print(f"Erro ao adicionar email: {e}")
        return False

def remove_allowed_email(email):
    """Remove um email da lista de permitidos"""
    placeholder = _get_placeholder()
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM allowed_emails WHERE LOWER(email) = {placeholder}", (email.lower().strip(),))
        conn.commit()
        cursor.close()
        return_connection(conn)
        # Clear cache
        is_email_allowed.clear()
        get_user_role.clear()
        get_all_allowed_emails.clear()
        return True
    except Exception as e:
        print(f"Erro ao remover email: {e}")
        return False

@st.cache_data(ttl=60)
def get_all_allowed_emails():
    """Retorna todos os emails permitidos"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT email, role, added_by, added_at FROM allowed_emails ORDER BY added_at DESC")
        results = cursor.fetchall()
        cursor.close()
        return_connection(conn)
        return results
    except Exception as e:
        print(f"Erro ao buscar emails: {e}")
        return []