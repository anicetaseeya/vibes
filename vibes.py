import streamlit as st


st.set_page_config(
    page_title="Encryption Machine",
    page_icon="🔐",
    layout="centered"
)


def create_dictionary(shift):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    cipher = {}

    for i in range(len(alphabet)):
        new_index = (i + shift) % len(alphabet)
        cipher[alphabet[i]] = alphabet[new_index]

    return cipher


def encrypt_message(message, cipher):
    encrypted = ""

    for letter in message.lower():
        if letter in cipher:
            encrypted += cipher[letter]
        else:
            encrypted += letter

    return encrypted


def decrypt_message(message, cipher):
    decrypted = ""

    for letter in message.lower():
        found = False

        for key in cipher:
            if cipher[key] == letter:
                decrypted += key
                found = True
                break

        if not found:
            decrypted += letter

    return decrypted


st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a, #111827, #1e293b);
        color: white;
    }

    .block-container {
        padding-top: 3rem;
        padding-bottom: 3rem;
        max-width: 900px;
    }

    .main-title {
        text-align: center;
        font-size: 3.2rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
        color: #f8fafc;
        letter-spacing: 1px;
    }

    .subtitle {
        text-align: center;
        font-size: 1.1rem;
        color: #cbd5e1;
        margin-bottom: 2rem;
    }

    .card {
        background: rgba(255, 255, 255, 0.06);
        padding: 2rem;
        border-radius: 22px;
        border: 1px solid rgba(255,255,255,0.12);
        box-shadow: 0 8px 30px rgba(0,0,0,0.35);
        backdrop-filter: blur(8px);
    }

    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        font-weight: 600;
        border: none;
        background: linear-gradient(90deg, #2563eb, #7c3aed);
        color: white;
        transition: 0.2s ease-in-out;
    }

    div.stButton > button:hover {
        transform: scale(1.02);
        opacity: 0.95;
    }

    .result-title {
        color: #e2e8f0;
        font-size: 1.1rem;
        font-weight: 700;
        margin-top: 1.2rem;
        margin-bottom: 0.6rem;
    }

    .result-box {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid #334155;
        padding: 1rem;
        border-radius: 14px;
        font-size: 1.05rem;
        color: #f8fafc;
        word-wrap: break-word;
    }

    .footer-text {
        text-align: center;
        color: #94a3b8;
        margin-top: 1.5rem;
        font-size: 0.9rem;
    }

    label {
        color: #cbd5e1 !important;
        font-weight: 500 !important;
    }

    .stTextArea textarea {
        background: rgba(255,255,255,0.92) !important;
        color: #111827 !important;
        border-radius: 14px !important;
        border: none !important;
        padding: 1rem !important;
        font-size: 1.05rem !important;
    }

    .stSlider label {
        color: #cbd5e1 !important;
    }
</style>
""", unsafe_allow_html=True)


st.markdown('<div class="main-title">🔐 Encryption Machine</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Caesar Cipher Tool — encrypt and decrypt your secret messages</div>',
    unsafe_allow_html=True
)

st.markdown('<div class="card">', unsafe_allow_html=True)

message = st.text_area(
    "Enter your message",
    height=180,
    placeholder="Type your secret message here..."
)

shift = st.slider("Choose shift value", min_value=1, max_value=25, value=3)

cipher = create_dictionary(shift)

col1, col2 = st.columns(2)

result = None
result_title = ""

with col1:
    encrypt_clicked = st.button("Encrypt")

with col2:
    decrypt_clicked = st.button("Decrypt")

if encrypt_clicked:
    if message.strip() == "":
        st.warning("Please enter a message first.")
    else:
        result = encrypt_message(message, cipher)
        result_title = "Encrypted Message"

if decrypt_clicked:
    if message.strip() == "":
        st.warning("Please enter a message first.")
    else:
        result = decrypt_message(message, cipher)
        result_title = "Decrypted Message"

if result is not None:
    st.markdown(f'<div class="result-title">{result_title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown(
    '<div class="footer-text">Built with Streamlit • Caesar Cipher Visual Tool</div>',
    unsafe_allow_html=True
)