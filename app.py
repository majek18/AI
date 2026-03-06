import streamlit as st
import google.generativeai as genai

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Gemini Chat Pro", page_icon="🤖", layout="centered")

# Stylizacja nagłówka
st.markdown("<h1 style='text-align: center;'>💬 Chatbot Gemini AI</h1>", unsafe_allow_html=True)
st.markdown("---")

# --- KONFIGURACJA API ---
# Upewnij się, że w Streamlit Cloud -> Settings -> Secrets masz:
# GOOGLE_API_KEY = "twój_klucz"
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("❌ Brakuje klucza API! Dodaj GOOGLE_API_KEY w ustawieniach Secrets.")
    st.stop()

# --- INICJALIZACJA MODELU ---
# Używamy modelu flash, który jest szybki i darmowy w ramach limitów
@st.cache_resource
def load_model():
    return genai.GenerativeModel('gemini-1.5-flash')

model = load_model()

# --- ZARZĄDZANIE HISTORIĄ ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Przycisk do resetowania czatu w sidebarze
with st.sidebar:
    st.title("⚙️ Opcje")
    if st.button("🗑️ Wyczyść historię", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.info("Model: Gemini 1.5 Flash")

# Wyświetlanie dotychczasowych wiadomości
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- OBSŁUGA CZATU ---
if prompt := st.chat_input("W czym mogę Ci dzisiaj pomóc?"):
    # 1. Wyświetl wiadomość użytkownika
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Generowanie odpowiedzi przez AI
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        response_placeholder.markdown("*(Myślę...)*")
        
        try:
            # Przekazujemy prompt do modelu
            # Uwaga: dla zachowania pełnej pamięci długich rozmów należałoby użyć start_chat()
            response = model.generate_content(prompt)
            
            if response.text:
                full_response = response.text
                response_placeholder.markdown(full_response)
                # Zapisz odpowiedź w historii
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                st.warning("⚠️ Model nie wygenerował tekstu (możliwa blokada treści).")
                
        except Exception as e:
            # Obsługa błędów (np. 404 lub 429)
            error_msg = str(e)
            if "404" in error_msg:
                st.error("❌ Błąd 404: Model nie został znaleziony. Spróbuj zmienić nazwę modelu w kodzie na 'gemini-pro'.")
            elif "429" in error_msg:
                st.error("⏳ Przekroczono limit zapytań (Quota). Poczekaj chwilę.")
            else:
                st.error(f"❌ Wystąpił nieoczekiwany błąd: {e}")
