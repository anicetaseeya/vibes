import streamlit as st


def create_dictionary():
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    cipher = {}
    shift = 3

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

    for letter in message:
        found = False

        for key in cipher:
            if cipher[key] == letter:
                decrypted += key
                found = True
                break

        if not found:
            decrypted += letter

    return decrypted


def main():
    st.title("Encryption Machine")
    st.subheader("Caesar Cipher: Shift by 3")

    cipher = create_dictionary()

    message = st.text_area("Enter a message:")

    if st.button("Encrypt"):
        if message.strip() == "":
            st.warning("You must enter a message.")
        else:
            encrypted = encrypt_message(message, cipher)
            st.success("Encrypted message:")
            st.code(encrypted)

    if st.button("Decrypt"):
        if message.strip() == "":
            st.warning("You must enter a message.")
        else:
            decrypted = decrypt_message(message.lower(), cipher)
            st.success("Decrypted message:")
            st.code(decrypted)


main()

