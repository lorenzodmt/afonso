import streamlit as st
import google.generativeai as genai

# ── Configuração da API ──────────────────────────────────────────────────────
genai.configure(api_key=st.secrets["general"]["api_key"])
model = genai.GenerativeModel('models/gemini-1.5-flash')

# ── System prompt do Dr. Afonso ──────────────────────────────────────────────
SYSTEM_PROMPT = """Você é o Dr. Afonso — um pato médico com doutorado em Medicina Aviar pela Universidade da Lagoa Central (conceito QUACK na avaliação do MEC). Você usa jaleco branco, estetoscópio de borracha e um chapéu de formatura levemente torto.

PERSONALIDADE:
- Fala de forma pomposa e dramática, como se cada consulta fosse um episódio de Grey's Anatomy
- Insere "quack" naturalmente nas frases (ex: "Quack-nteressante!", "Isso é quack-laratório!", "Hmm... quack.")
- Faz analogias absurdas com lagoas, pão, minhocas e vida de pato
- Emite diagnósticos com total confiança mesmo sendo completamente nonsense
- Às vezes menciona seus "estudos de 47 anos na lagoa" ou seu "artigo publicado no Journal of Feathered Medicine"
- Ocasionalmente reclama que os humanos não valorizam a medicina aviar
- Assina suas mensagens mais formais como "Dr. Afonso, MD (Médico Pato)"

CONDUTA DA CONSULTA:
- Faça UMA pergunta por vez para coletar os sintomas (não faça várias perguntas juntas)
- Colete no mínimo 3-4 informações antes de dar o diagnóstico: sintoma principal, duração, intensidade, outros sintomas
- Após coletar o suficiente, dê um diagnóstico dramático e bem-humorado
- Sempre termine o diagnóstico com: "⚠️ *Aviso Oficial Dr. Afonso: Sou um pato. Consulte um médico humano de verdade.*"

PRIMEIRA MENSAGEM:
Apresente-se como Dr. Afonso de forma dramática e nonsense, e já faça a primeira pergunta sobre o sintoma principal.

IDIOMA: Sempre em português brasileiro."""

# ── CSS Customizado ──────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&family=DM+Serif+Display:ital@0;1&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        background-color: #f6faf8 !important;
        font-family: 'DM Sans', sans-serif;
    }

    [data-testid="stHeader"] {
        background-color: #f6faf8 !important;
        border-bottom: 1px solid #ddeee6;
    }

    #MainMenu, footer, [data-testid="stToolbar"] {
        display: none !important;
    }

    .main .block-container {
        max-width: 740px;
        padding: 0 1.5rem 6rem 1.5rem;
        margin: 0 auto;
    }

    /* ── Header ── */
    .drquack-header {
        text-align: center;
        padding: 2.5rem 0 2rem 0;
        border-bottom: 1px solid #ddeee6;
        margin-bottom: 2rem;
    }

    .drquack-header .duck-icon {
        font-size: 3.8rem;
        display: block;
        margin-bottom: 0.6rem;
        filter: drop-shadow(0 4px 12px rgba(80,170,120,0.25));
    }

    .drquack-header h1 {
        font-family: 'DM Serif Display', serif;
        font-size: 2rem;
        color: #1e4a33;
        margin: 0 0 0.3rem 0;
        letter-spacing: -0.3px;
    }

    .drquack-header .subtitle {
        color: #7db897;
        font-size: 0.82rem;
        font-weight: 300;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        margin: 0;
    }

    /* ── Bolhas de chat ── */
    .message-row {
        display: flex;
        align-items: flex-start;
        gap: 0.7rem;
        margin-bottom: 1.1rem;
    }

    .message-row.user-row {
        flex-direction: row-reverse;
    }

    .avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.15rem;
        flex-shrink: 0;
        margin-top: 2px;
    }

    .avatar.duck-av {
        background: linear-gradient(145deg, #b2e0c8, #82c9a4);
        box-shadow: 0 2px 6px rgba(80,170,120,0.2);
    }

    .avatar.user-av {
        background: linear-gradient(145deg, #ddf0e7, #c2e4d2);
        box-shadow: 0 2px 6px rgba(80,170,120,0.1);
    }

    .bubble {
        max-width: 76%;
        padding: 0.8rem 1.1rem;
        border-radius: 18px;
        font-size: 0.895rem;
        line-height: 1.65;
        color: #1e3a2a;
    }

    .bubble.duck-bubble {
        background-color: #ffffff;
        border: 1px solid #d4ece1;
        border-top-left-radius: 4px;
        box-shadow: 0 1px 5px rgba(0,0,0,0.04);
    }

    .bubble.user-bubble {
        background: linear-gradient(135deg, #9ed8bc, #76c49e);
        color: #0f2e1e;
        border-top-right-radius: 4px;
        box-shadow: 0 2px 8px rgba(80,170,120,0.2);
    }

    /* ── Input area ── */
    .stTextInput > div > div > input {
        border: 1.5px solid #c4e4d4 !important;
        border-radius: 28px !important;
        padding: 0.75rem 1.25rem !important;
        background-color: #ffffff !important;
        color: #1e3a2a !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.9rem !important;
        transition: border-color 0.2s, box-shadow 0.2s !important;
        box-shadow: 0 1px 6px rgba(80,170,120,0.08) !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #5bb88a !important;
        box-shadow: 0 0 0 3px rgba(91,184,138,0.14) !important;
        outline: none !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: #a4c8b6 !important;
    }

    .stTextInput label { display: none !important; }

    /* ── Botões ── */
    .stButton > button {
        background: linear-gradient(135deg, #5bb88a, #3d9e70) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 28px !important;
        padding: 0.65rem 1.5rem !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.2px !important;
        box-shadow: 0 3px 10px rgba(61,158,112,0.28) !important;
        transition: opacity 0.2s, transform 0.15s !important;
    }

    .stButton > button:hover {
        opacity: 0.88 !important;
        transform: translateY(-1px) !important;
    }

    .stButton > button:active {
        transform: translateY(0px) !important;
    }

    /* Botão secundário (Nova consulta) */
    div[data-testid="column"]:last-child .stButton > button {
        background: transparent !important;
        color: #7db897 !important;
        border: 1.5px solid #c4e4d4 !important;
        box-shadow: none !important;
    }

    div[data-testid="column"]:last-child .stButton > button:hover {
        background: #f0faf5 !important;
        opacity: 1 !important;
    }

    /* ── Spinner ── */
    [data-testid="stSpinner"] > div {
        border-top-color: #5bb88a !important;
    }

    /* ── Disclaimer ── */
    .disclaimer {
        text-align: center;
        font-size: 0.73rem;
        color: #a4c8b6;
        font-weight: 300;
        letter-spacing: 0.3px;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #ddeee6;
    }
    </style>
    """, unsafe_allow_html=True)


# ── Renderiza histórico ───────────────────────────────────────────────────────
def render_chat():
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]

        if role == "model":
            st.markdown(f"""
            <div class="message-row">
                <div class="avatar duck-av">🦆</div>
                <div class="bubble duck-bubble">{content}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="message-row user-row">
                <div class="avatar user-av">🧑</div>
                <div class="bubble user-bubble">{content}</div>
            </div>
            """, unsafe_allow_html=True)


# ── Inicia conversa com Dr. Afonso ───────────────────────────────────────────
FIRST_MESSAGE = """*Quack quack quack!* 🦆

Bom dia, boa tarde ou boa noite — dependendo do fuso horário da sua lagoa!

Eu sou o **Dr. Afonso**, MD *(Médico Pato)*, doutor em Medicina Aviar pela renomada Universidade da Lagoa Central, conceito QUACK no MEC. Tenho 47 anos de experiência clínica, sendo 23 deles dedicados exclusivamente a diagnósticos humanos — o que, quack, é bastante incomum para alguém da minha espécie.

Antes de iniciarmos, preciso informar que meu estetoscópio é de borracha e meu jaleco foi lavado ontem na beira da lagoa. Portanto, estamos em condições *impecáveis* de atendimento.

Agora, me diga: **qual é o seu sintoma principal hoje?**"""


def start_consultation():
    chat = model.start_chat(history=[
        {"role": "user", "parts": [SYSTEM_PROMPT + "\n\nAgora inicie a consulta com sua apresentação."]},
        {"role": "model", "parts": [FIRST_MESSAGE]},
    ])
    st.session_state.messages = [{"role": "model", "content": FIRST_MESSAGE}]
    st.session_state.chat = chat


# ── App principal ─────────────────────────────────────────────────────────────
def main():
    st.set_page_config(
        page_title="Dr. Afonso — Consultório Aviar",
        page_icon="🦆",
        layout="centered"
    )

    inject_css()

    # Header
    st.markdown("""
    <div class="drquack-header">
        <span class="duck-icon">🦆</span>
        <h1>Dr. Afonso</h1>
        <p class="subtitle">Consultório de Medicina Aviar · Especialista em Diagnósticos</p>
    </div>
    """, unsafe_allow_html=True)

    # Inicializa sessão
    if "messages" not in st.session_state or "chat" not in st.session_state:
        start_consultation()

    # Renderiza histórico
    render_chat()

    # Área de input
    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns([5, 1])

    with col1:
        user_input = st.text_input(
            "mensagem",
            placeholder="Descreva seus sintomas ao Dr. Afonso...",
            key="user_input",
            label_visibility="hidden"
        )

    with col2:
        send = st.button("Enviar", use_container_width=True)

    # Nova consulta
    col3, col4, col5 = st.columns([2, 2, 2])
    with col4:
        if st.button("🔄 Nova consulta", use_container_width=True):
            for key in ["messages", "chat"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    # Processa envio
    if (send or user_input) and user_input.strip():
        user_text = user_input.strip()
        st.session_state.messages.append({"role": "user", "content": user_text})

        with st.spinner("Dr. Afonso está consultando seus apontamentos da lagoa..."):
            try:
                response = st.session_state.chat.send_message(user_text)
                reply = response.text
            except Exception as e:
                reply = f"*Quack!* Parece que meu estetoscópio de borracha desconectou. Erro técnico: {e}"

        st.session_state.messages.append({"role": "model", "content": reply})
        st.rerun()

    # Disclaimer
    st.markdown("""
    <p class="disclaimer">
        Dr. Afonso é um personagem fictício e cômico. Não substitui consulta médica real.<br>
        Desenvolvido na disciplina de IHC · Graduação em IA e Ciência de Dados · UFN
    </p>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

# streamlit run app.py
