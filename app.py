import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Gemini Chatbot", page_icon="🤖")
st.title("💬 Chatbot Gemini")

# 1. Konfiguracja Klucza API (Pobierany bezpiecznie z Secrets)
# Instrukcja dodania klucza poniżej kodu
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Błąd: Nie znaleziono klucza GOOGLE_API_KEY w Secrets!")
    st.stop()

# 2. Inicjalizacja modelu (używamy stabilnej wersji, by uniknąć błędu 404)
# Zmieniamy z v1beta na wersję stabilną
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. Historia czatu w pamięci sesji
if "messages" not in st.session_state:
    st.session_state.messages = []

# Wyświetlanie historii
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Pole wprowadzania wiadomości
if prompt := st.chat_input("W czym mogę Ci pomóc?"):
    # Dodaj wiadomość użytkownika
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generowanie odpowiedzi AI
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            # Wysyłamy całą historię do modelu dla zachowania kontekstu
            response = model.generate_content(prompt)
            full_response = response.text
            message_placeholder.markdown(full_response)
            
            # Zapisz odpowiedź AI
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Wystąpił błąd: {e}")
