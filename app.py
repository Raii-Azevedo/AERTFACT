import streamlit as st
import os
import time
from datetime import datetime

from allowed_emails import is_email_allowed, get_user_role
from database import init_database

init_database()

st.set_page_config(
    page_title="AE Knowledge Hub",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================== CSS ==================
st.markdown("""
<style>

/* RESET */
#MainMenu, header, footer {visibility: hidden;}
.stApp > header {display: none;}

/* BACKGROUND ANIMADO */
.stApp {
    background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #1a1a40);
    background-size: 400% 400%;
    animation: gradientBG 12s ease infinite;

    display: flex;
    justify-content: center;
    align-items: center;
}

/* ANIMAÇÃO FUNDO */
@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* CONTAINER ROOT */
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* MAIN */
.main-container {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
}

.content-wrapper {
    max-width: 520px;
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
}

/* LOGO */
.logo-container {
    margin-bottom: 2rem;
    animation: fadeInDown 0.8s ease-out;
}

.logo-container img {
    max-width: 220px;
    filter: drop-shadow(0 15px 25px rgba(0,0,0,0.3));
}

/* TITLE */
.title {
    text-align: center;
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(135deg, #ffffff, #a8c0ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
    animation: fadeInUp 0.8s ease-out 0.1s both;
}

/* SUBTITLE */
.subtitle {
    text-align: center;
    font-size: 0.95rem;
    color: rgba(255,255,255,0.7);
    margin-bottom: 2rem;
    animation: fadeInUp 0.8s ease-out 0.2s both;
}

/* CARD */
.login-card {
    background: rgba(255,255,255,0.07);
    backdrop-filter: blur(14px);
    border-radius: 18px;
    padding: 2rem;
    width: 100%;
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: 0 25px 50px rgba(0,0,0,0.35);
    animation: fadeInUp 0.8s ease-out 0.3s both;
}

/* INPUT COM ÍCONE */
.input-container {
    position: relative;
}

.input-container input {
    padding-left: 2.5rem !important;
}

.input-icon {
    position: absolute;
    left: 12px;
    top: 10px;
    font-size: 1rem;
    opacity: 0.6;
}

/* INPUT */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    color: white !important;
}

/* BUTTON */
.stButton {
    margin-top: 0.8rem;
}

.stButton > button {
    background: linear-gradient(135deg, #667eea, #764ba2);
    border-radius: 12px;
    font-weight: 600;
    padding: 0.85rem;
    width: 100%;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(102,126,234,0.5);
}

/* BADGES */
.badges-container {
    margin-top: 1.5rem;
    display: flex;
    gap: 0.6rem;
    flex-wrap: wrap;
    justify-content: center;
    opacity: 0.75;
}

.badge {
    background: rgba(255,255,255,0.08);
    padding: 0.4rem 0.9rem;
    border-radius: 30px;
    font-size: 0.75rem;
}

/* ANIMAÇÕES */
@keyframes fadeInUp {
    from {opacity:0; transform:translateY(20px);}
    to {opacity:1; transform:translateY(0);}
}

@keyframes fadeInDown {
    from {opacity:0; transform:translateY(-20px);}
    to {opacity:1; transform:translateY(0);}
}

</style>
""", unsafe_allow_html=True)

# ================== SESSION ==================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "loading" not in st.session_state:
    st.session_state["loading"] = False

if st.session_state["authenticated"]:
    st.switch_page("pages/dashboard.py")

# ================== UI ==================
st.markdown('<div class="main-container"><div class="content-wrapper">', unsafe_allow_html=True)

# LOGO
st.markdown('<div class="logo-container">', unsafe_allow_html=True)
if os.path.exists("assets/logo.png"):
    st.image("assets/logo.png")
else:
    st.markdown("## 🚀")
st.markdown('</div>', unsafe_allow_html=True)

# TITLE
st.markdown('<div class="title">AE Knowledge Hub</div>', unsafe_allow_html=True)

# SUBTITLE
st.markdown('<div class="subtitle">Repositório de Inteligência em Analytics Engineering</div>', unsafe_allow_html=True)

# CARD
st.markdown('<div class="login-card">', unsafe_allow_html=True)

st.markdown("### ✨ Acesso ao Hub")
st.caption("Use seu email corporativo")

# INPUT COM ÍCONE
st.markdown('<div class="input-container">', unsafe_allow_html=True)
st.markdown('<div class="input-icon">📧</div>', unsafe_allow_html=True)
user_email = st.text_input("", placeholder="nome.sobrenome@artefact.com", label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# BOTÃO COM LOADING
button_label = "🚀 Entrar no Hub"
if st.session_state["loading"]:
    button_label = "⏳ Entrando..."

if st.button(button_label, use_container_width=True):
    st.session_state["loading"] = True
    time.sleep(0.8)  # simula loading

    if user_email:
        if is_email_allowed(user_email):
            st.session_state["authenticated"] = True
            st.session_state["user_email"] = user_email.lower()
            st.session_state["user_name"] = user_email.split("@")[0].replace(".", " ").title()
            st.session_state["user_role"] = get_user_role(user_email)
            st.rerun()
        else:
            st.error("❌ Email não autorizado.")
    else:
        st.warning("⚠️ Informe seu email")

    st.session_state["loading"] = False

st.caption("🔒 Apenas emails autorizados")

st.markdown('</div>', unsafe_allow_html=True)

# BADGES
st.markdown("""
<div class="badges-container">
<span class="badge">📚 100+ materiais</span>
<span class="badge">🎥 Pílulas</span>
<span class="badge">🏆 Gamificação</span>
<span class="badge">⭐ AE do Mês</span>
<span class="badge">🚀 Roadmap</span>
</div>
""", unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)