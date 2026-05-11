import math

def parse_permutation_key(key_str):
    """
    Parses various input formats (e.g., '4132', '4 1 3 2', or '4,1,3,2') 
    into a list of integers.
    """
    key_str = key_str.strip()
    if " " in key_str:
        parts = key_str.split()
    elif "," in key_str:
        parts = [p.strip() for p in key_str.split(",")]
    else:
        parts = list(key_str)

    if not parts or not all(part.isdigit() for part in parts):
        return None
    return [int(part) for part in parts]

def is_valid_permutation_key(key_str):
    """Checks if the key is a valid permutation of 1 to N."""
    key = parse_permutation_key(key_str)
    if not key:
        return False
    n = len(key)
    return sorted(key) == list(range(1, n + 1))

def single_transposition_encrypt(text, key):
    """Standard Columnar Transposition Encryption."""
    # Project logic: remove spaces to create a clean matrix
    text = text.replace(" ", "")
    cols = len(key)
    rows = math.ceil(len(text) / cols)
    
    # Padding with 'X' to complete the matrix rectangle
    padded_text = text + "X" * (rows * cols - len(text))
    
    # Create rows
    matrix = [padded_text[i:i+cols] for i in range(0, len(padded_text), cols)]
    
    # Read columns based on key order
    column_order = sorted(range(cols), key=lambda i: key[i])
    
    ciphertext = ""
    for col in column_order:
        for row in range(rows):
            ciphertext += matrix[row][col]
    return ciphertext

def single_transposition_decrypt(ciphertext, key):
    """Standard Columnar Transposition Decryption."""
    cols = len(key)
    rows = len(ciphertext) // cols
    
    # Create empty matrix
    matrix = [["" for _ in range(cols)] for _ in range(rows)]
    
    # Find the order columns were written in
    column_order = sorted(range(cols), key=lambda i: key[i])
    
    # Fill the matrix column by column
    index = 0
    for col in column_order:
        for row in range(rows):
            matrix[row][col] = ciphertext[index]
            index += 1
            
    # Read out row by row
    plaintext = ""
    for row in range(rows):
        plaintext += "".join(matrix[row])
    return plaintext

def encrypt_double_transposition(plaintext, key1_str, key2_str):
    """Applies two rounds of columnar transposition."""
    k1 = parse_permutation_key(key1_str)
    k2 = parse_permutation_key(key2_str)
    
    # Round 1
    round1 = single_transposition_encrypt(plaintext, k1)
    # Round 2
    final_ciphertext = single_transposition_encrypt(round1, k2)
    
    return round1, final_ciphertext

def decrypt_double_transposition(ciphertext, key1_str, key2_str):
    """Reverses two rounds of columnar transposition."""
    # Critical Fix: Clean up user input to prevent shifting errors
    ciphertext = ciphertext.strip()
    
    k1 = parse_permutation_key(key1_str)
    k2 = parse_permutation_key(key2_str)
    
    # Step 1: Reverse Round 2 (using Key 2)
    second_reversed = single_transposition_decrypt(ciphertext, k2)
    # Step 2: Reverse Round 1 (using Key 1)
    original_plaintext = single_transposition_decrypt(second_reversed, k1)
    
    return second_reversed, original_plaintext