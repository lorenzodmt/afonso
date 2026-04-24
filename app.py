import streamlit as st
import google.generativeai as genai

# Configuração da chave (peça para os alunos gerarem no Google AI Studio)
genai.configure(api_key=st.secrets["general"]["api_key"])

# Para ver quais versões são aceitas
# for m in genai.list_models():
#   if 'generateContent' in m.supported_generation_methods:
#     print(m.name)

# Usando a versão estável mais recente da lista
model = genai.GenerativeModel('models/gemini-3.1-flash-lite-preview')

# Configuração da página
st.set_page_config(page_title="CineIA", page_icon="🎬")
st.title("🎬 CineIA: Seu Próximo Filme")
st.markdown("Descubra filmes baseados no seu estado de espírito atual.")

# --- INTERFACE ---
with st.sidebar:
    st.header("Preferências")
    genero = st.multiselect("Gêneros favoritos:",
                            ["Ação", "Drama", "Sci-Fi", "Comédia", "Terror", "Documentário"])
    tempo = st.slider("Duração máxima (minutos):", 60, 240, 120)

mood = st.text_area("Descreva como você está se sentindo ou o que busca no filme:",
                    placeholder="Ex: Quero um filme de ficção científica com reviravoltas na história.")

botao_recomendar = st.button("Buscar Recomendações")

# --- LÓGICA DE PROCESSAMENTO ---
if botao_recomendar:
    if not mood:
        st.warning("Por favor, descreva o que você deseja assistir!")
    else:
        with st.spinner("Analisando catálogo cinematográfico..."):
            prompt = f"""
            Você é um especialista em cinema.
            Recomende 3 filmes para alguém que gosta de {', '.join(genero)} e que durem até {tempo} minutos.
            O usuário descreveu o clima do filme como: '{mood}'.
            Para cada filme, forneça: Título, Ano e uma frase curta do porquê combina com o pedido.
            """

            try:
                response = model.generate_content(prompt)
                st.success("Aqui estão minhas sugestões:")
                st.markdown("---")                
                st.write(response.text)
                #trecho para coletar feedback para o RLHF (Reinforcement Learning from Human Feedback)
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("👍 Gostei"): 
                        with open("feedback.csv", "a") as f:
                            f.write(f"{mood},{genero},{tempo},Gostei\n")
                        st.success("Obrigado pelo seu feedback positivo!")
                with col2:
                    if st.button("👎 Não gostei"): 
                        with open("feedback.csv", "a") as f:
                            f.write(f"{mood},{genero},{tempo},Não gostei\n")
                        st.info("Feedback registrado. Vamos melhorar!")

            except Exception as e:
                st.error(f"Erro ao conectar com a IA: {e}")

st.caption("Desenvolvido na disciplina de IHC - Graduação em IA e Ciência de Dados - Universidade Franciscana (UFN)")

#streamlit run app.py
