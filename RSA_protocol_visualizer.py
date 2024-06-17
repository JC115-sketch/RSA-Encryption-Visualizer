import sys
import math
import random
import prime_numbers
import cryptomath
import os

SYMBOLS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890 !?.'


def main():
    mode = input("Please enter 'encrypt' or 'decrypt' to select mode: ").strip().lower()
    if mode == 'exit':
        sys.exit()

    if mode == 'encrypt':
        message = input("Please enter the message to encrypt: ")
        print(f"Original plaintext message: {message}")
        if not continue_prompt():
            sys.exit()

        public_key, private_key = generate_key(1024)
        save_keys(public_key, private_key)
        print("Generated public and private keys.")
        print(f"Public key (n, e): {public_key}")
        print(f"Private key (n, d): {private_key}")

        if not continue_prompt():
            sys.exit()

        print('Encrypting...')
        encrypted_text = encrypt_and_return(public_key, message)
        print('Encrypted text:')
        print(encrypted_text)

    elif mode == 'decrypt':
        public_key, private_key = load_keys()

        encrypted_message = input("Please enter the encrypted message: ")
        encrypted_blocks = [int(block) for block in encrypted_message.split(';')]
        print("Encrypted blocks:")
        print(encrypted_blocks)

        if not continue_prompt():
            sys.exit()

        print("Decrypting...")
        decrypted_text = decrypt_from_input(private_key, encrypted_message)
        print('Decrypted text:')
        print(decrypted_text)

    else:
        print("Invalid mode selected. Please enter 'encrypt' or 'decrypt'.")

    delete_keys = input("Would you like to generate new public and private key files? (yes/no) ")
    if delete_keys == 'yes':
        delete_key_files()


def generate_key(key_size):
    p = 0
    q = 0
    while p == q:
        p = prime_numbers.generate_large_prime_num(key_size)
        q = prime_numbers.generate_large_prime_num(key_size)

    print(f"Generated prime numbers p: {p} and q: {q} ")

    n = p * q
    print(f"Calculated n = p * q: {n}")
    if not continue_prompt():
        sys.exit()

    while True:
        e = random.randrange(2 ** (key_size - 1), 2 ** (key_size))
        if cryptomath.gcd(e, (p - 1) * (q - 1)) == 1:
            break

    d = cryptomath.findModInverse(e, (p - 1) * (q - 1))
    print(f"Selected e: {e}")
    print(f"Calculated d: {d}")

    public_key = (n, e)
    private_key = (n, d)

    return public_key, private_key


def save_keys(public_key, private_key):
    with open('public_key.txt', 'w') as f:
        f.write(f'{public_key[0]},{public_key[1]}')
    with open('private_key.txt', 'w') as f:
        f.write(f'{private_key[0]},{private_key[1]}')
    print("Public and private keys saved as text file in current directory")


def load_keys():
    with open('public_key.txt', 'r') as f:
        n, e = map(int, f.read().split(','))
        public_key = (n, e)
    with open('private_key.txt', 'r') as f:
        n, d = map(int, f.read().split(','))
        private_key = (n, d)
    return public_key, private_key


def get_blocks_from_text(message, block_size):
    for character in message:
        if character not in SYMBOLS:
            print('Error - invalid character')
            sys.exit()
    block_ints = []
    for block_start in range(0, len(message), block_size):
        block_integer = 0
        for i in range(block_start, min(block_start + block_size, len(message))):
            block_integer += (SYMBOLS.index(message[i])) * (len(SYMBOLS)) ** (i % block_size)
        block_ints.append(block_integer)
        print(f"Created block: {block_integer}")
    if not continue_prompt():
        sys.exit()
    return block_ints


def get_text_from_blocks(block_ints, message_length, block_size):
    message = []
    for block_integer in block_ints:
        block_message = []
        for i in range(block_size - 1, -1, -1):
            if len(message) + i < message_length:
                char_index = block_integer // (len(SYMBOLS) ** i)
                block_integer = block_integer % (len(SYMBOLS) ** i)
                if char_index < len(SYMBOLS):
                    block_message.insert(0, SYMBOLS[char_index])
                else:
                    print(f"Error - char_index {char_index} out of range for SYMBOLS")
                    sys.exit()
        message.extend(block_message)
    return ''.join(message)


def encrypt_message(message, key, block_size):
    encrypted_blocks = []
    n, e = key
    for block in get_blocks_from_text(message, block_size):
        encrypted_blocks.append(pow(block, e, n))
    return encrypted_blocks


def decrypt_message(encrypted_blocks, message_length, key, block_size):
    decrypted_blocks = []
    n, d = key
    for block in encrypted_blocks:
        decrypted_blocks.append(pow(block, d, n))
        print(f"Block {block} decrypted to {decrypted_blocks}")
    return get_text_from_blocks(decrypted_blocks, message_length, block_size)


def encrypt_and_return(public_key, message, block_size=None):
    n, e = public_key
    key_size = len(bin(n)) - 2

    if block_size is None:
        block_size = int(math.log(2 ** key_size, len(SYMBOLS)))
    if not (math.log(2 ** key_size, len(SYMBOLS)) >= block_size):
        sys.exit('Error - Block size is too large for key and symbol set size')

    encrypted_blocks = encrypt_message(message, (n, e), block_size)

    for i in range(len(encrypted_blocks)):
        encrypted_blocks[i] = str(encrypted_blocks[i])
    encrypted_content = ','.join(encrypted_blocks)

    encrypted_content = '%s;%s;%s' % (len(message), block_size, encrypted_content)

    return encrypted_content


def decrypt_from_input(private_key, encrypted_content):
    n, d = private_key
    key_size = len(bin(n)) - 2

    print("Encrypted content:", encrypted_content)
    message_length, block_size, encrypted_message = encrypted_content.strip().split(';')
    message_length = int(message_length)
    block_size = int(block_size)

    if not (math.log(2 ** key_size, len(SYMBOLS)) >= block_size):
        sys.exit('Error - Block size is too large for key and symbol set size')

    encrypted_blocks = [int(block) for block in encrypted_message.split(',')]

    print("Encrypted blocks:", encrypted_blocks)
    print("Decrypting with key:", private_key)
    print("Message length:", message_length)
    print("Block size:", block_size)

    return decrypt_message(encrypted_blocks, message_length, (n, d), block_size)


def delete_key_files():
    try:
        os.remove('public_key.txt')
        os.remove('private_key.txt')
        print("Key files deleted successfully.")
    except FileNotFoundError:
        print("Key files not found. Nothing to delete.")
    except Exception as e:
        print(f"An error occurred while deleting key files: {e}")


def continue_prompt():
    response = input("Do you want to continue? (yes/no): ").strip().lower()
    return response == 'yes'


if __name__ == '__main__':
    main()


