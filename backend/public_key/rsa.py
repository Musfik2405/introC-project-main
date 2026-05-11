import random
import math
import time


def gcd(a, b):
    """Compute greatest common divisor."""
    while b != 0:
        a, b = b, a % b
    return a


def extended_gcd(a, b):
    """Return (g, x, y) such that ax + by = g = gcd(a, b)."""
    if b == 0:
        return a, 1, 0
    g, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return g, x, y


def mod_inverse(e, phi):
    """Compute modular inverse d = e^-1 mod phi."""
    g, x, _ = extended_gcd(e, phi)
    if g != 1:
        raise ValueError("Modular inverse does not exist.")
    return x % phi


def is_probable_prime(n, k=10):
    """Miller-Rabin primality test."""
    if n < 2:
        return False

    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    for p in small_primes:
        if n == p:
            return True
        if n % p == 0:
            return False

    r = 0
    d = n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    for _ in range(k):
        a = random.randrange(2, n - 2)
        x = pow(a, d, n)

        if x == 1 or x == n - 1:
            continue

        composite = True
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                composite = False
                break

        if composite:
            return False

    return True


def generate_prime(bits):
    """Generate a probable prime with the given bit length."""
    if bits < 8:
        raise ValueError("Bit length too small.")

    while True:
        candidate = random.getrandbits(bits)
        candidate |= (1 << (bits - 1))  # force top bit
        candidate |= 1  # force odd
        if is_probable_prime(candidate):
            return candidate


def generate_rsa_keys(key_size=512):
    """
    Generate RSA public/private keys.
    Returns a dictionary with timing info too.
    """
    if key_size < 256:
        raise ValueError("Use at least 256 bits for project demo.")
    if key_size % 2 != 0:
        raise ValueError("Key size should be even.")

    start = time.perf_counter()

    half_bits = key_size // 2
    p = generate_prime(half_bits)
    q = generate_prime(half_bits)

    while q == p:
        q = generate_prime(half_bits)

    n = p * q
    phi = (p - 1) * (q - 1)

    e = 65537
    if gcd(e, phi) != 1:
        e = 3
        while gcd(e, phi) != 1:
            e += 2

    d = mod_inverse(e, phi)

    end = time.perf_counter()

    return {
        "p": p,
        "q": q,
        "n": n,
        "phi": phi,
        "public_key": (e, n),
        "private_key": (d, n),
        "generation_time": end - start,
        "key_size": key_size,
    }


def max_block_length_bytes(n):
    """Largest k such that 256^k < n."""
    k = 1
    while (256 ** k) < n:
        k += 1
    return max(1, k - 1)


def text_to_blocks(plaintext, n):
    """Split UTF-8 text into integer blocks smaller than n."""
    data = plaintext.encode("utf-8")
    block_len = max_block_length_bytes(n) - 1
    if block_len < 1:
        raise ValueError("Modulus too small for text encryption.")

    blocks = []
    for i in range(0, len(data), block_len):
        chunk = data[i:i + block_len]
        blocks.append(int.from_bytes(chunk, byteorder="big"))

    return blocks


def blocks_to_text(blocks):
    """Convert integer blocks back to UTF-8 text."""
    data = b""
    for block in blocks:
        if block == 0:
            chunk = b"\x00"
        else:
            chunk = block.to_bytes((block.bit_length() + 7) // 8, byteorder="big")
        data += chunk
    return data.decode("utf-8", errors="ignore")


def rsa_encrypt_blocks(blocks, public_key):
    """Encrypt integer blocks with RSA."""
    e, n = public_key
    return [pow(block, e, n) for block in blocks]


def rsa_decrypt_blocks(cipher_blocks, private_key):
    """Decrypt integer blocks with RSA."""
    d, n = private_key
    return [pow(block, d, n) for block in cipher_blocks]


def rsa_encrypt_text(plaintext, public_key):
    """Encrypt text and return ciphertext blocks with timing."""
    if not plaintext:
        raise ValueError("Plaintext cannot be empty.")

    start = time.perf_counter()

    e, n = public_key
    plain_blocks = text_to_blocks(plaintext, n)
    cipher_blocks = rsa_encrypt_blocks(plain_blocks, public_key)

    end = time.perf_counter()

    return {
        "plain_blocks": plain_blocks,
        "cipher_blocks": cipher_blocks,
        "cipher_hex_blocks": [format(c, "X") for c in cipher_blocks],
        "encryption_time": end - start,
    }


def rsa_decrypt_text(cipher_blocks, private_key):
    """Decrypt ciphertext blocks and return plaintext with timing."""
    if not cipher_blocks:
        raise ValueError("Ciphertext blocks are empty.")

    start = time.perf_counter()

    plain_blocks = rsa_decrypt_blocks(cipher_blocks, private_key)
    plaintext = blocks_to_text(plain_blocks)

    end = time.perf_counter()

    return {
        "plain_blocks": plain_blocks,
        "plaintext": plaintext,
        "decryption_time": end - start,
    }


def factorization_attack_demo(n, limit=10**7):
    """
    Educational factorization demo.
    Only tries trial division for small moduli.
    """
    if n > limit:
        return {
            "success": False,
            "message": "Skipped: modulus too large for simple factorization demo."
        }

    start = time.perf_counter()

    for i in range(2, int(math.isqrt(n)) + 1):
        if n % i == 0:
            end = time.perf_counter()
            return {
                "success": True,
                "p": i,
                "q": n // i,
                "time": end - start,
                "message": "Factorization succeeded."
            }

    end = time.perf_counter()
    return {
        "success": False,
        "time": end - start,
        "message": "No factors found."
    }