
def create_dictionary():
    """
    Creates a dictionary used for encrypting letters.
    Each letter is shifted 3 positions forward.

    Returns:
        dict: dictionary with letter substitutions
    """

    alphabet = "abcdefghijklmnopqrstuvwxyz"
    cipher = {}

    shift = 3

    for i in range(len(alphabet)):
        new_index = (i + shift) % len(alphabet)
        cipher[alphabet[i]] = alphabet[new_index]

    return cipher


def encrypt_message(message, cipher):
    """
    Encrypts a message using the cipher dictionary.

    Parameters:
        message (str): the original text
        cipher (dict): dictionary used for encryption

    Returns:
        str: encrypted message
    """

    encrypted = ""

    for letter in message.lower():

        if letter in cipher:
            encrypted = encrypted + cipher[letter]
        else:
            encrypted = encrypted + letter

    return encrypted


def decrypt_message(message, cipher):
    """
    Decrypts an encrypted message.

    Parameters:
        message (str): encrypted text
        cipher (dict): dictionary used for encryption

    Returns:
        str: decrypted message
    """

    decrypted = ""

    for letter in message:

        found = False

        for key in cipher:
            if cipher[key] == letter:
                decrypted = decrypted + key
                found = True

        if found == False:
            decrypted = decrypted + letter

    return decrypted


def main():
    """
    Main function of the program.
    It asks the user for a message, encrypts it,
    and then shows the decrypted version.
    """

    cipher = create_dictionary()

    try:
        message = input("Enter a message to encrypt: ")

        if message == "":
            print("You must enter a message.")
            return

    except:
        print("Error reading the message.")
        return

    encrypted = encrypt_message(message, cipher)

    print("Encrypted message:")
    print(encrypted)

    decrypted = decrypt_message(encrypted, cipher)

    print("Decrypted message:")
    print(decrypted)


main()
#yes

