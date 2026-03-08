import streamlit as st
import random
from collections import Counter


st.set_page_config(
    page_title="Enigma Cracker Simulator",
    page_icon="🔐",
    layout="centered"
)


# ============================================================
# STYLING
# ============================================================

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a, #111827, #1e293b);
        color: white;
    }

    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 3rem;
        max-width: 950px;
    }

    .main-title {
        text-align: center;
        font-size: 3rem;
        font-weight: 800;
        color: #f8fafc;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        text-align: center;
        font-size: 1.1rem;
        color: #cbd5e1;
        margin-bottom: 2rem;
    }

    .section-box {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 18px;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }

    .result-box {
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid #334155;
        padding: 1rem;
        border-radius: 14px;
        color: #f8fafc;
        font-size: 1.02rem;
        word-wrap: break-word;
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
    }

    div.stButton > button:hover {
        opacity: 0.95;
        transform: scale(1.01);
    }

    .small-note {
        color: #cbd5e1;
        font-size: 0.95rem;
    }

    .step-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 0.5rem;
    }

    .footer-text {
        text-align: center;
        color: #94a3b8;
        margin-top: 1.5rem;
        font-size: 0.9rem;
    }

    label {
        color: #cbd5e1 !important;
    }

    .stTextArea textarea, .stTextInput input {
        background: rgba(255,255,255,0.95) !important;
        color: #111827 !important;
        border-radius: 12px !important;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# ENIGMA FUNCTIONS
# ============================================================

def create_dictionary(shift):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    cipher = {}
    for i in range(len(alphabet)):
        new_index = (i + shift) % len(alphabet)
        cipher[alphabet[i]] = alphabet[new_index]
    return cipher


def create_plugboard():
    alphabet = list("abcdefghijklmnopqrstuvwxyz")
    plugboard = {}
    pairs = random.sample(alphabet, 10)

    for i in range(0, 10, 2):
        a, b = pairs[i], pairs[i + 1]
        plugboard[a] = b
        plugboard[b] = a

    for letter in alphabet:
        if letter not in plugboard:
            plugboard[letter] = letter

    return plugboard


def encrypt_enigma(message, rotors, plugboard):
    encrypted = ""
    for letter in message.lower():
        if letter.isalpha():
            c = plugboard[letter]
            c = rotors[0][c]
            c = rotors[1][c]
            c = rotors[2][c]
            c = plugboard[c]
            encrypted += c
        else:
            encrypted += letter
    return encrypted


def decrypt_enigma(message, rotors, plugboard):
    reverse_rotors = [{v: k for k, v in rotor.items()} for rotor in rotors]
    decrypted = ""
    for letter in message.lower():
        if letter.isalpha():
            c = plugboard[letter]
            c = reverse_rotors[2][c]
            c = reverse_rotors[1][c]
            c = reverse_rotors[0][c]
            c = plugboard[c]
            decrypted += c
        else:
            decrypted += letter
    return decrypted


# ============================================================
# CRACKING FUNCTIONS
# ============================================================

def frequency_analysis(encrypted_message):
    letters_only = [c for c in encrypted_message.lower() if c.isalpha()]
    total = len(letters_only)

    if total == 0:
        return [], None

    counts = Counter(letters_only)
    rows = []

    for letter, count in sorted(counts.items(), key=lambda x: -x[1])[:10]:
        freq = (count / total) * 100
        rows.append((letter, count, round(freq, 1)))

    most_common = counts.most_common(1)[0][0]
    return rows, most_common


def crib_drag(encrypted_message, crib):
    encrypted_clean = encrypted_message.replace(" ", "").lower()
    crib = crib.replace(" ", "").lower()
    results = []

    if len(crib) == 0 or len(crib) > len(encrypted_clean):
        return results

    for i in range(len(encrypted_clean) - len(crib) + 1):
        segment = encrypted_clean[i:i + len(crib)]

        no_self_encrypt = all(segment[j] != crib[j] for j in range(len(crib)))

        results.append({
            "position": i,
            "segment": segment,
            "possible": no_self_encrypt
        })

    return results


def bombe_attack(encrypted_message, crib, max_attempts_display=3000):
    crib = crib.replace(" ", "").lower()
    encrypted_clean = encrypted_message.replace(" ", "").lower()

    attempts = 0
    progress_placeholder = st.empty()

    for shift1 in range(1, 26):
        for shift2 in range(1, 26):
            for shift3 in range(1, 26):
                attempts += 1

                test_rotors = [
                    create_dictionary(shift1),
                    create_dictionary(shift2),
                    create_dictionary(shift3)
                ]
                test_plugboard = {c: c for c in "abcdefghijklmnopqrstuvwxyz"}

                test_decrypt = decrypt_enigma(encrypted_clean, test_rotors, test_plugboard)

                if attempts % 1000 == 0:
                    progress_placeholder.info(f"Tested {attempts} rotor combinations...")

                if crib in test_decrypt:
                    progress_placeholder.success(f"Match found after {attempts} attempts.")
                    return {
                        "shift1": shift1,
                        "shift2": shift2,
                        "shift3": shift3,
                        "decrypted": test_decrypt,
                        "attempts": attempts
                    }

    progress_placeholder.error("No rotor match found.")
    return None


def check_english(decrypted_message):
    common_words = [
        "the", "and", "for", "are", "but", "not", "you", "all",
        "can", "her", "was", "one", "our", "out", "day", "get",
        "has", "him", "his", "how", "its", "may", "new", "now",
        "old", "see", "two", "way", "who", "did", "attack", "at",
        "dawn", "send", "troops", "report", "enemy", "base", "fire"
    ]

    words_in_message = decrypted_message.lower().split()
    found_words = [word for word in words_in_message if word in common_words]

    if len(words_in_message) == 0:
        score = 0
    else:
        score = len(found_words) / len(words_in_message) * 100

    return found_words, score


# ============================================================
# UI
# ============================================================

st.markdown('<div class="main-title">🔐 Enigma Cracker Simulator</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Encrypt a message, then crack it with a simplified Bombe-style attack</div>',
    unsafe_allow_html=True
)

st.markdown('<div class="section-box">', unsafe_allow_html=True)

message = st.text_area(
    "Enter a message to encrypt",
    height=140,
    placeholder="Example: attack at dawn"
)

message_type = st.selectbox(
    "Message type",
    [
        "MILITARY ORDER",
        "INTELLIGENCE REPORT",
        "DIPLOMATIC COMMUNICATION",
        "FIELD TRANSMISSION",
        "PERSONAL MESSAGE",
        "UNCLASSIFIED"
    ]
)

use_random_plugboard = st.checkbox("Use random plugboard", value=False)

crib = st.text_input("Known crib / guessed phrase for cracking", value="attack")

col1, col2 = st.columns(2)

with col1:
    encrypt_clicked = st.button("Encrypt Message")

with col2:
    crack_clicked = st.button("Crack Message")

st.markdown('</div>', unsafe_allow_html=True)

# session storage
if "encrypted_message" not in st.session_state:
    st.session_state.encrypted_message = ""

if "original_message" not in st.session_state:
    st.session_state.original_message = ""

if "plugboard_used" not in st.session_state:
    st.session_state.plugboard_used = None

if "rotors_used" not in st.session_state:
    st.session_state.rotors_used = None


# ============================================================
# ENCRYPT
# ============================================================

if encrypt_clicked:
    if message.strip() == "":
        st.warning("Please enter a message first.")
    else:
        rotors = [create_dictionary(3), create_dictionary(7), create_dictionary(19)]

        if use_random_plugboard:
            plugboard = create_plugboard()
        else:
            plugboard = {c: c for c in "abcdefghijklmnopqrstuvwxyz"}

        encrypted = encrypt_enigma(message, rotors, plugboard)
        decrypted = decrypt_enigma(encrypted, rotors, plugboard)

        st.session_state.encrypted_message = encrypted
        st.session_state.original_message = message
        st.session_state.plugboard_used = plugboard
        st.session_state.rotors_used = (3, 7, 19)

        st.markdown("### Encrypted Transmission")
        st.markdown(
            f"""
<div class="result-box">
<b>Message Type:</b> {message_type}<br><br>
<b>Original:</b> {message}<br>
<b>Encrypted:</b> {encrypted}<br>
<b>Decrypted check:</b> {decrypted}<br><br>
<b>Rotor shifts:</b> 3, 7, 19
</div>
""",
            unsafe_allow_html=True
        )

        if use_random_plugboard:
            swaps = {k: v for k, v in plugboard.items() if k != v}
            st.write("Plugboard swaps:")
            st.json(swaps)


# ============================================================
# CRACK
# ============================================================

if crack_clicked:
    encrypted_message = st.session_state.encrypted_message

    if encrypted_message == "":
        st.warning("Encrypt a message first so the cracker has something to attack.")
    elif crib.strip() == "":
        st.warning("Please enter a crib phrase.")
    else:
        st.markdown("## Bletchley Park Crack Attempt")

        # Step 1
        st.markdown('<div class="step-title">Step 1: Frequency Analysis</div>', unsafe_allow_html=True)
        rows, most_common = frequency_analysis(encrypted_message)

        if rows:
            st.write("Most frequent letters in the encrypted text:")
            st.table({
                "Letter": [r[0] for r in rows],
                "Count": [r[1] for r in rows],
                "Frequency %": [r[2] for r in rows]
            })
            st.info(f"Most frequent encrypted letter: '{most_common}'. In English, 'e' is often most common.")
        else:
            st.info("No letters found to analyse.")

        # Step 2
        st.markdown('<div class="step-title">Step 2: Crib Dragging</div>', unsafe_allow_html=True)
        crib_results = crib_drag(encrypted_message, crib)

        if crib_results:
            possible_positions = [r["position"] for r in crib_results if r["possible"]]

            preview_rows = []
            for r in crib_results:
                preview_rows.append({
                    "Position": r["position"],
                    "Segment": r["segment"],
                    "Possible": "Yes" if r["possible"] else "No"
                })

            st.table(preview_rows)

            if possible_positions:
                st.success(f"Possible crib positions: {possible_positions}")
            else:
                st.error("No valid crib positions found using the no-self-encrypt rule.")
        else:
            possible_positions = []
            st.error("Crib is empty or longer than the encrypted message.")

        # Step 3
        st.markdown('<div class="step-title">Step 3: Bombe Attack</div>', unsafe_allow_html=True)
        st.write("Testing rotor combinations with no plugboard, like a simplified Bombe demo...")

        if possible_positions:
            result = bombe_attack(encrypted_message, crib)

            # Step 4
            if result:
                st.markdown('<div class="step-title">Step 4: English Language Check</div>', unsafe_allow_html=True)
                found_words, score = check_english(result["decrypted"])

                st.markdown(
                    f"""
<div class="result-box">
<b>Rotor shifts found:</b> {result["shift1"]}, {result["shift2"]}, {result["shift3"]}<br>
<b>Attempts:</b> {result["attempts"]}<br>
<b>Decrypted output:</b> {result["decrypted"]}<br>
<b>Recognised English words:</b> {", ".join(found_words) if found_words else "None"}<br>
<b>English confidence score:</b> {score:.0f}%
</div>
""",
                    unsafe_allow_html=True
                )

                if score > 50:
                    st.success("High confidence: this looks like real English.")
                elif score > 20:
                    st.warning("Possible match: might be correct.")
                else:
                    st.error("Low confidence: probably wrong settings.")

                st.markdown("### Crack Summary")
                st.markdown(
                    f"""
<div class="result-box">
<b>Encrypted message:</b> {encrypted_message}<br>
<b>Cracked message:</b> {result["decrypted"]}<br>
<b>Recovered rotor shifts:</b> {result["shift1"]}, {result["shift2"]}, {result["shift3"]}
</div>
""",
                    unsafe_allow_html=True
                )
            else:
                st.error("The Bombe attack did not find a matching rotor combination.")
        else:
            st.warning("Skipping Bombe attack because crib dragging found no plausible positions.")

st.markdown(
    '<div class="footer-text">Built with Streamlit • Simplified Enigma + Bombe demonstration</div>',
    unsafe_allow_html=True
)