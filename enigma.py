import streamlit as st
import random
import datetime

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Enigma Machine Simulator",
    page_icon="🔐",
    layout="wide"
)

# ============================================================
# CONSTANTS
# ============================================================

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

ROTOR_I = "EKMFLGDQVZNTOWYHXUSPAIBRCJ"
ROTOR_II = "AJDKSIRUXBLHWTMCQGZNPYFVOE"
ROTOR_III = "BDFHJLCPRTXVZNYEIWGAKMUSQO"
ROTOR_IV = "ESOVPZJAYQUIRHXLNFTGKDCMWB"
ROTOR_V = "VZBRGITYUPSDNHLXAWMJQOFECK"
REFLECTOR_B = "YRUHQSLDPXNGOKMIEBFZCWVJAT"

NOTCH_I = ["Q"]
NOTCH_II = ["E"]
NOTCH_III = ["V"]
NOTCH_IV = ["J"]
NOTCH_V = ["Z"]

ALL_ROTORS = [
    (ROTOR_I, NOTCH_I, "I"),
    (ROTOR_II, NOTCH_II, "II"),
    (ROTOR_III, NOTCH_III, "III"),
    (ROTOR_IV, NOTCH_IV, "IV"),
    (ROTOR_V, NOTCH_V, "V"),
]

MESSAGE_TYPES = [
    "MILITARY ORDER",
    "INTELLIGENCE REPORT",
    "DIPLOMATIC COMMUNICATION",
    "FIELD TRANSMISSION",
    "PERSONAL MESSAGE",
    "UNCLASSIFIED"
]

# ============================================================
# CLASSES
# ============================================================

class Rotor:
    def __init__(self, wiring, notch, ring_setting=0, position=0):
        self.wiring = wiring
        self.notch = notch
        self.ring_setting = ring_setting
        self.position = position

    def step(self):
        self.position = (self.position + 1) % 26

    def at_notch(self):
        return ALPHABET[self.position] in self.notch

    def encode_forward(self, letter_index):
        offset = self.position - self.ring_setting
        shifted = (letter_index + offset) % 26
        wired = ALPHABET.index(self.wiring[shifted])
        return (wired - offset) % 26

    def encode_backward(self, letter_index):
        offset = self.position - self.ring_setting
        shifted = (letter_index + offset) % 26
        wired = self.wiring.index(ALPHABET[shifted])
        return (wired - offset) % 26


class Plugboard:
    def __init__(self, pairs=None):
        self.wiring = list(ALPHABET)
        self.pairs = pairs or []

        for a, b in self.pairs:
            a = a.upper()
            b = b.upper()
            self.wiring[ALPHABET.index(a)] = b
            self.wiring[ALPHABET.index(b)] = a

    def encode(self, letter_index):
        return ALPHABET.index(self.wiring[letter_index])


class Reflector:
    def __init__(self, wiring=REFLECTOR_B):
        self.wiring = wiring

    def encode(self, letter_index):
        return ALPHABET.index(self.wiring[letter_index])


class EnigmaMachine:
    def __init__(self, rotors, reflector, plugboard):
        self.rotors = rotors
        self.reflector = reflector
        self.plugboard = plugboard

    def step_rotors(self):
        # left, middle, right = 0,1,2
        if self.rotors[1].at_notch():
            self.rotors[1].step()
            self.rotors[0].step()
        elif self.rotors[2].at_notch():
            self.rotors[1].step()
        self.rotors[2].step()

    def encrypt_letter(self, letter):
        if letter not in ALPHABET:
            return letter

        self.step_rotors()
        idx = ALPHABET.index(letter)

        idx = self.plugboard.encode(idx)
        idx = self.rotors[2].encode_forward(idx)
        idx = self.rotors[1].encode_forward(idx)
        idx = self.rotors[0].encode_forward(idx)
        idx = self.reflector.encode(idx)
        idx = self.rotors[0].encode_backward(idx)
        idx = self.rotors[1].encode_backward(idx)
        idx = self.rotors[2].encode_backward(idx)
        idx = self.plugboard.encode(idx)

        return ALPHABET[idx]

    def encrypt_message(self, message):
        return "".join(self.encrypt_letter(c) for c in message.upper())

# ============================================================
# HELPERS
# ============================================================

def generate_monthly_codebook():
    today = datetime.date.today()
    rng = random.Random(f"{today.year}-{today.month}")

    codebook = {}
    for day in range(1, 27):
        rotor_choices = rng.sample(range(5), 3)
        positions = [rng.randint(0, 25) for _ in range(3)]
        ring_settings = [rng.randint(0, 25) for _ in range(3)]

        letters = list(ALPHABET)
        rng.shuffle(letters)
        pairs = [(letters[i], letters[i + 1]) for i in range(0, 20, 2)]

        codebook[day] = {
            "rotors": rotor_choices,
            "positions": positions,
            "ring_settings": ring_settings,
            "plugboard": pairs,
        }
    return codebook


def get_todays_settings(codebook):
    today = datetime.date.today()
    day = min(today.day, 26)
    return codebook[day], day


def build_machine_from_settings(settings):
    rotors = []
    for i in range(3):
        rotor_data = ALL_ROTORS[settings["rotors"][i]]
        rotors.append(
            Rotor(
                wiring=rotor_data[0],
                notch=rotor_data[1],
                ring_setting=settings["ring_settings"][i],
                position=settings["positions"][i],
            )
        )

    reflector = Reflector(REFLECTOR_B)
    plugboard = Plugboard(settings["plugboard"])
    return EnigmaMachine(rotors, reflector, plugboard)


def parse_plugboard_input(text):
    """
    Input format example:
    AB CD EF GH
    """
    text = text.strip().upper()
    if not text:
        return []

    raw_pairs = text.split()
    pairs = []
    used = set()

    for pair in raw_pairs:
        if len(pair) != 2 or not pair.isalpha():
            raise ValueError(f"Invalid plugboard pair: {pair}")
        a, b = pair[0], pair[1]
        if a == b:
            raise ValueError(f"Plugboard pair cannot use same letter twice: {pair}")
        if a in used or b in used:
            raise ValueError(f"Letter repeated in plugboard: {pair}")
        used.add(a)
        used.add(b)
        pairs.append((a, b))

    return pairs


def build_manual_machine(rotor_indices, positions, ring_settings, plugboard_pairs):
    rotors = []
    for i in range(3):
        rotor_data = ALL_ROTORS[rotor_indices[i]]
        rotors.append(
            Rotor(
                wiring=rotor_data[0],
                notch=rotor_data[1],
                ring_setting=ring_settings[i],
                position=positions[i],
            )
        )

    reflector = Reflector(REFLECTOR_B)
    plugboard = Plugboard(plugboard_pairs)
    return EnigmaMachine(rotors, reflector, plugboard)


def format_settings(settings):
    rotor_names = [ALL_ROTORS[r][2] for r in settings["rotors"]]
    positions = [ALPHABET[p] for p in settings["positions"]]
    rings = settings["ring_settings"]
    plugboard = " ".join([a + b for a, b in settings["plugboard"]])

    return rotor_names, positions, rings, plugboard


def bombe_crack(encrypted, crib):
    """
    Simplified demo version:
    - only tests rotor positions
    - assumes Rotor I, II, III
    - no plugboard
    """
    encrypted_clean = encrypted.replace(" ", "").upper()
    crib_clean = crib.replace(" ", "").upper()

    attempts = 0

    for pos1 in range(26):
        for pos2 in range(26):
            for pos3 in range(26):
                attempts += 1

                rotors = [
                    Rotor(ROTOR_I, NOTCH_I, position=pos1),
                    Rotor(ROTOR_II, NOTCH_II, position=pos2),
                    Rotor(ROTOR_III, NOTCH_III, position=pos3),
                ]
                machine = EnigmaMachine(rotors, Reflector(), Plugboard([]))
                decrypted = machine.encrypt_message(encrypted_clean)

                if crib_clean in decrypted:
                    return {
                        "success": True,
                        "attempts": attempts,
                        "positions": f"{ALPHABET[pos1]} {ALPHABET[pos2]} {ALPHABET[pos3]}",
                        "decrypted": decrypted,
                    }

    return {"success": False, "attempts": attempts}

# ============================================================
# UI
# ============================================================

st.title("🔐 Enigma Machine Simulator")
st.caption("Educational Streamlit version with daily codebook, manual settings, and simplified Bombe demo.")

tab1, tab2, tab3 = st.tabs(["Encrypt / Decrypt", "Monthly Codebook", "Bombe Demo"])

# ============================================================
# TAB 1
# ============================================================

with tab1:
    st.subheader("Encrypt / Decrypt")

    mode = st.radio(
        "Choose configuration mode",
        ["Today's daily key", "Manual settings"],
        horizontal=True
    )

    codebook = generate_monthly_codebook()
    todays_settings, today_day = get_todays_settings(codebook)

    if mode == "Today's daily key":
        rotor_names, positions, rings, plugboard_str = format_settings(todays_settings)

        st.info(f"Using day {today_day} settings from this month's codebook.")

        with st.expander("View today's settings"):
            st.write(f"**Rotors:** {', '.join(rotor_names)}")
            st.write(f"**Start positions:** {', '.join(positions)}")
            st.write(f"**Ring settings:** {rings}")
            st.write(f"**Plugboard:** {plugboard_str}")

        machine_settings = todays_settings

    else:
        col1, col2, col3 = st.columns(3)

        rotor_options = {name: idx for idx, (_, _, name) in enumerate(ALL_ROTORS)}

        with col1:
            left_rotor_name = st.selectbox("Left rotor", list(rotor_options.keys()), index=0)
            middle_rotor_name = st.selectbox("Middle rotor", list(rotor_options.keys()), index=1)
            right_rotor_name = st.selectbox("Right rotor", list(rotor_options.keys()), index=2)

        with col2:
            left_pos = st.selectbox("Left position", list(ALPHABET), index=0)
            middle_pos = st.selectbox("Middle position", list(ALPHABET), index=0)
            right_pos = st.selectbox("Right position", list(ALPHABET), index=0)

        with col3:
            left_ring = st.number_input("Left ring", min_value=0, max_value=25, value=0)
            middle_ring = st.number_input("Middle ring", min_value=0, max_value=25, value=0)
            right_ring = st.number_input("Right ring", min_value=0, max_value=25, value=0)

        plugboard_text = st.text_input(
            "Plugboard pairs",
            placeholder="AB CD EF GH",
            help="Use space-separated 2-letter pairs. Example: AB CD EF"
        )

        try:
            plugboard_pairs = parse_plugboard_input(plugboard_text)
            machine_settings = {
                "rotors": [
                    rotor_options[left_rotor_name],
                    rotor_options[middle_rotor_name],
                    rotor_options[right_rotor_name],
                ],
                "positions": [
                    ALPHABET.index(left_pos),
                    ALPHABET.index(middle_pos),
                    ALPHABET.index(right_pos),
                ],
                "ring_settings": [left_ring, middle_ring, right_ring],
                "plugboard": plugboard_pairs,
            }
        except ValueError as e:
            st.error(str(e))
            machine_settings = None

    message_type = st.selectbox("Message type", MESSAGE_TYPES, index=0)
    message = st.text_area("Enter message", height=140, placeholder="Type your message here...")

    colA, colB = st.columns(2)

    with colA:
        run_encrypt = st.button("Encrypt and Decrypt", use_container_width=True)

    with colB:
        run_demo = st.button("Rotor Demo (AAAAA)", use_container_width=True)

    if run_encrypt:
        if not message.strip():
            st.warning("Enter a message first.")
        elif machine_settings is None:
            st.warning("Fix the settings first.")
        else:
            machine = build_machine_from_settings(machine_settings)
            encrypted = machine.encrypt_message(message)

            decrypt_machine = build_machine_from_settings(machine_settings)
            decrypted = decrypt_machine.encrypt_message(encrypted)

            st.success("Processing complete.")
            st.markdown("### Results")
            st.write(f"**Message type:** {message_type}")
            st.write(f"**Original:** {message.upper()}")
            st.write(f"**Encrypted:** {encrypted}")
            st.write(f"**Decrypted:** {decrypted}")

    if run_demo:
        if machine_settings is None:
            st.warning("Fix the settings first.")
        else:
            demo_machine = build_machine_from_settings(machine_settings)
            results = [demo_machine.encrypt_letter("A") for _ in range(5)]
            st.markdown("### Rotor Advancement Demo")
            st.write(f"**A A A A A → {' '.join(results)}**")
            st.caption("Same input changes because the rotors step after each keypress.")

# ============================================================
# TAB 2
# ============================================================

with tab2:
    st.subheader("Monthly Codebook")

    codebook = generate_monthly_codebook()

    rows = []
    for day in range(1, 27):
        s = codebook[day]
        rotor_names = ", ".join(ALL_ROTORS[r][2] for r in s["rotors"])
        positions = ", ".join(ALPHABET[p] for p in s["positions"])
        rings = ", ".join(str(r) for r in s["ring_settings"])
        plugboard = " ".join(a + b for a, b in s["plugboard"])

        rows.append({
            "Day": day,
            "Rotors": rotor_names,
            "Positions": positions,
            "Ring Settings": rings,
            "Plugboard": plugboard
        })

    st.dataframe(rows, use_container_width=True, hide_index=True)
    st.caption("The codebook is seeded by the current month, so it stays stable during the month and changes next month.")

# ============================================================
# TAB 3
# ============================================================

with tab3:
    st.subheader("Simplified Bombe Demo")
    st.warning("This is a teaching demo, not a full historical Bombe recreation.")

    encrypted_text = st.text_input("Encrypted text", value="KQFZLQ KX WQIU")
    crib = st.text_input("Expected crib", value="ATTACK")

    if st.button("Run Bombe Demo", use_container_width=True):
        if not encrypted_text.strip() or not crib.strip():
            st.warning("Enter both encrypted text and a crib.")
        else:
            with st.spinner("Testing rotor positions..."):
                result = bombe_crack(encrypted_text, crib)

            if result["success"]:
                st.success("Possible match found.")
                st.write(f"**Attempts:** {result['attempts']}")
                st.write(f"**Rotor positions:** {result['positions']}")
                st.write(f"**Decrypted text:** {result['decrypted']}")
            else:
                st.error("No match found with this simplified demo.")
                st.write(f"**Attempts:** {result['attempts']}")