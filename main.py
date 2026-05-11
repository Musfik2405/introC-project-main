from backend.classical.substitution import encrypt as sub_e, decrypt as sub_d, is_valid_key
from backend.classical.double_transposition import (
    encrypt_double_transposition,
    decrypt_double_transposition,
    is_valid_permutation_key,
)
from backend.symmetric.des import auto_generate_des_key, generate_round_keys, des_process, bin_to_hex
from backend.symmetric.aes import (
    get_aes_variant,
    auto_generate_aes_key,
    aes_encrypt_long_text,
    aes_decrypt_long_text,
    get_round_keys_hex,
)
from backend.public_key.rsa import (
    generate_rsa_keys,
    rsa_encrypt_text,
    rsa_decrypt_text,
    factorization_attack_demo,
)
import time


def main():
    rsa_keys = None
    rsa_cipher = None

    while True:
        print("\n=== CryptoLab Menu ===")
        print("1. Substitution Cipher")
        print("2. Double Transposition")
        print("3. DES (Data Encryption Standard)")
        print("4. AES (Advanced Encryption Standard)")
        print("5. RSA")
        print("6. Exit")

        choice = input("\nEnter choice: ").strip()

        if choice == "1":
            mode = input("(E)ncrypt or (D)ecrypt: ").strip().upper()
            text = input("Text: ")
            key = input("26-letter key: ")

            if not is_valid_key(key):
                print("Invalid Key.")
                continue

            if mode == "E":
                print(f"Result: {sub_e(text, key)}")
            elif mode == "D":
                print(f"Result: {sub_d(text, key)}")
            else:
                print("Invalid mode. Use E or D.")

        elif choice == "2":
            mode = input("(E)ncrypt or (D)ecrypt: ").strip().upper()
            text = input("Text: ")
            k1 = input("Key 1: ")
            k2 = input("Key 2: ")

            if not (is_valid_permutation_key(k1) and is_valid_permutation_key(k2)):
                print("Invalid permutation key.")
                continue

            if mode == "E":
                r1, final = encrypt_double_transposition(text, k1, k2)
                print(f"Round 1: {r1}")
                print(f"Final: {final}")
            elif mode == "D":
                s1, orig = decrypt_double_transposition(text, k1, k2)
                print(f"Rev Round 2: {s1}")
                print(f"Plaintext: {orig}")
            else:
                print("Invalid mode. Use E or D.")

        elif choice == "3":
            print("\n--- DES Implementation ---")
            plaintext = input("Enter plaintext (long text allowed): ").strip()

            if not plaintext:
                print("Plaintext cannot be empty.")
                continue

            key = auto_generate_des_key()
            print(f"Auto-generated Key: {key}")

            subkeys = generate_round_keys(key)
            print("\n--- 16 Round Keys ---")
            for i, rk in enumerate(subkeys, 1):
                print(f"Round {i:02d}: {bin_to_hex(rk)}")

            start_encrypt = time.perf_counter()
            ciphertext = des_process(plaintext, key, mode="encrypt")
            end_encrypt = time.perf_counter()

            print(f"\nOutput (Encryption) Ciphertext: {ciphertext}")
            print(f"Encryption Time: {(end_encrypt - start_encrypt):.6f} seconds")

            start_decrypt = time.perf_counter()
            decrypted = des_process(ciphertext, key, mode="decrypt")
            end_decrypt = time.perf_counter()

            print(f"Output (Decryption) Original: {decrypted}")
            print(f"Decryption Time: {(end_decrypt - start_decrypt):.6f} seconds")

        elif choice == "4":
            print(f"\n--- {get_aes_variant()} Implementation ---")
            plaintext = input("Enter plaintext (long text allowed): ").strip()

            if not plaintext:
                print("Plaintext cannot be empty.")
                continue

            key = auto_generate_aes_key()
            print(f"Auto-generated 128-bit Key: {key}")

            round_keys = get_round_keys_hex(key)
            print(f"\n--- {get_aes_variant()} Round Keys ---")
            for i, rk in enumerate(round_keys):
                print(f"Round Key {i:02d}: {rk}")

            start_encrypt = time.perf_counter()
            ciphertext = aes_encrypt_long_text(plaintext, key)
            end_encrypt = time.perf_counter()

            print(f"\nOutput (Encryption) Ciphertext: {ciphertext}")
            print(f"Encryption Time: {(end_encrypt - start_encrypt):.6f} seconds")

            start_decrypt = time.perf_counter()
            decrypted = aes_decrypt_long_text(ciphertext, key)
            end_decrypt = time.perf_counter()

            print(f"Output (Decryption) Original: {decrypted}")
            print(f"Decryption Time: {(end_decrypt - start_decrypt):.6f} seconds")

        elif choice == "5":
            print("\n--- RSA Implementation ---")
            print("1. Generate Keys")
            print("2. Encrypt")
            print("3. Decrypt")

            rsa_choice = input("Enter RSA choice: ").strip()

            if rsa_choice == "1":
                try:
                    key_size = int(input("Enter key size (e.g. 512 or 1024): ").strip())
                    rsa_keys = generate_rsa_keys(key_size)

                    print(f"\nKey Size: {rsa_keys['key_size']} bits")
                    print(f"Key Generation Time: {rsa_keys['generation_time']:.6f} seconds")

                    print("\nPublic Key (e, n):")
                    print(rsa_keys["public_key"])

                    print("\nPrivate Key (d, n):")
                    print(rsa_keys["private_key"])

                    attack = factorization_attack_demo(rsa_keys["n"])
                    print(f"\nFactorization Attack Demo: {attack['message']}")
                    if attack.get("success"):
                        print(f"Recovered p = {attack['p']}")
                        print(f"Recovered q = {attack['q']}")
                        print(f"Attack Time: {attack['time']:.6f} seconds")

                except Exception as e:
                    print(f"Error: {e}")

            elif rsa_choice == "2":
                if rsa_keys is None:
                    print("Generate keys first.")
                    continue

                plaintext = input("Enter plaintext string: ").strip()
                try:
                    result = rsa_encrypt_text(plaintext, rsa_keys["public_key"])
                    rsa_cipher = result["cipher_blocks"]

                    print("\nCiphertext blocks (integer):")
                    for i, block in enumerate(result["cipher_blocks"], start=1):
                        print(f"Block {i}: {block}")

                    print("\nCiphertext blocks (hex):")
                    for i, block in enumerate(result["cipher_hex_blocks"], start=1):
                        print(f"Block {i}: {block}")

                    print(f"\nEncryption Time: {result['encryption_time']:.6f} seconds")

                except Exception as e:
                    print(f"Error: {e}")

            elif rsa_choice == "3":
                if rsa_keys is None:
                    print("Generate keys first.")
                    continue

                if rsa_cipher is None:
                    print("Encrypt something first.")
                    continue

                try:
                    result = rsa_decrypt_text(rsa_cipher, rsa_keys["private_key"])
                    print("\nDecrypted message:")
                    print(result["plaintext"])
                    print(f"\nDecryption Time: {result['decryption_time']:.6f} seconds")

                except Exception as e:
                    print(f"Error: {e}")

            else:
                print("Invalid RSA choice.")

        elif choice == "6":
            print("Exiting...")
            break

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()