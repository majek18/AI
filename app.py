import streamlit as st
import google.generativeai as genai

# --- KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="Gemini Chat Pro",
    page_icon="🤖",
    layout="centered"
)

st.markdown("<h1 style='text-align: center;'>💬 Chatbot Gemini AI</h1>", unsafe_allow_html=True)
st.markdown("---")

# --- KONFIGURACJA API ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("❌ Brakuje klucza API! Dodaj GOOGLE_API_KEY w Streamlit Secrets.")
    st.stop()

# --- ŁADOWANIE MODELU ---
@st.cache_resource
def load_model():
    return genai.GenerativeModel("gemini-2.5-flash")

model = load_model()

# --- HISTORIA ROZMOWY ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Opcje")

    if st.button("🗑️ Wyczyść historię", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.info("Model: Gemini 2.5 Flash")

# --- WYŚWIETLANIE HISTORII ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- CZAT ---
if prompt := st.chat_input("W czym mogę Ci dzisiaj pomóc?"):

    # zapisz wiadomość użytkownika
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # odpowiedź AI
    with st.chat_message("assistant"):

        response_placeholder = st.empty()
        response_placeholder.markdown("*(Myślę...)*")

        try:

            # budujemy historię dla modelu
            history = []
            for msg in st.session_state.messages:
                role = "user" if msg["role"] == "user" else "model"
                history.append({
                    "role": role,
                    "parts": [msg["content"]]
                })

            chat = model.start_chat(history=history[:-1])

            response = chat.send_message(prompt)

            if response.text:
                full_response = response.text
                response_placeholder.markdown(full_response)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response
                })

            else:
                response_placeholder.warning("⚠️ Model nie wygenerował odpowiedzi.")

        except Exception as e:

            error = str(e)

            if "404" in error:
                st.error("❌ Model nie istnieje lub API jest nieaktywne.")
            elif "429" in error:
                st.error("⏳ Przekroczono limit zapytań. Spróbuj za chwilę.")
            else:
                st.error(f"❌ Błąd: {error}")
