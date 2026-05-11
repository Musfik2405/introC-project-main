from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import time

# --- Algorithm Imports (Ensure these files exist in your directory structure) ---
from classical.substitution import encrypt as sub_e, decrypt as sub_d, is_valid_key
from classical.double_transposition import encrypt_double_transposition, decrypt_double_transposition
from symmetric.des import auto_generate_des_key, generate_round_keys, des_process, bin_to_hex
from symmetric.aes import get_aes_variant, auto_generate_aes_key, aes_encrypt_long_text, aes_decrypt_long_text, get_round_keys_hex
from public_key.rsa import generate_rsa_keys, rsa_encrypt_text, rsa_decrypt_text, factorization_attack_demo
from public_key.ecc import get_all_points, run_ecdh_exchange

app = FastAPI(title="CryptoDeck Arena API")

# --- CORS Configuration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models ---
class CipherRequest(BaseModel):
    text: Optional[str] = ""
    mode: str = "encrypt"
    key: Optional[str] = None
    key1: Optional[str] = None
    key2: Optional[str] = None
    rsa_keys: Optional[Dict[str, Any]] = None
    rsa_cipher: Optional[List[Any]] = None
    # ECC Parameters
    p: Optional[int] = 97
    a: Optional[int] = 2
    b: Optional[int] = 3
    gx: Optional[int] = 0
    gy: Optional[int] = 10
    priv_a: Optional[int] = 9
    priv_b: Optional[int] = 14
    bits: Optional[int] = 512

# --- 1. Classical Ciphers ---



@app.post("/api/classical/substitution")
def run_substitution(req: CipherRequest):
    from classical.substitution import (
        encrypt, decrypt, is_valid_key, 
        substitution_attack_report, ranked_bruteforce_substitution
    )
    
    # 1. Standard Encrypt/Decrypt (Manual)
    manual_result = ""
    if req.mode.lower() == "encrypt":
        if is_valid_key(req.key):
            manual_result = encrypt(req.text, req.key)
    elif req.mode.lower() == "decrypt":
        if is_valid_key(req.key):
            manual_result = decrypt(req.text, req.key)

    # 2. Attack Analysis (The Cracking Logic)
    attack_report = substitution_attack_report(req.text)
    brute_force = ranked_bruteforce_substitution(req.text)

    return {
        "title": "--- Substitution Implementation ---",
        "mode": req.mode.upper(),
        "manual_result": manual_result,
        "complexity": attack_report["complexity_message"],
        "letter_freq": attack_report["letter_frequencies"],
        "bigrams": attack_report["bigrams"],
        "trigrams": attack_report["trigrams"],
        "best_guess": attack_report["best_candidate_text"],
        "candidates": brute_force["candidates"]
    }

@app.post("/api/classical/transposition")
def run_transposition(req: CipherRequest):
    """Matches the terminal trace for Round 1 and Rev Round 2 labels."""
    if not req.key1 or not req.key2:
        raise HTTPException(status_code=400, detail="Both keys are required for Double Transposition.")
    
    if req.mode.lower() == "decrypt" or req.mode.lower() == "d":
        round_info, res = decrypt_double_transposition(req.text, req.key1, req.key2)
        return {
            "title": "--- Double Transposition ---",
            "mode": "D",
            "text": req.text,
            "key1": req.key1,
            "key2": req.key2,
            "round_label": "Rev Round 2",
            "round_text": round_info,
            "final_label": "Plaintext",
            "result": res
        }
    else:
        round_info, res = encrypt_double_transposition(req.text, req.key1, req.key2)
        return {
            "title": "--- Double Transposition ---",
            "mode": "E",
            "text": req.text,
            "key1": req.key1,
            "key2": req.key2,
            "round_label": "Round 1",
            "round_text": round_info,
            "final_label": "Final",
            "result": res
        }

# --- 2. Symmetric Ciphers ---

@app.post("/api/symmetric/des")
def run_des(req: CipherRequest):
    key = req.key if (req.key and len(req.key) == 16) else auto_generate_des_key()
    subkeys = generate_round_keys(key)
    rounds = {f"Round Key {i+1:02d}": bin_to_hex(rk) for i, rk in enumerate(subkeys)}
    
    start_enc = time.perf_counter()
    ciphertext = des_process(req.text, key, mode="encrypt")
    time_enc = time.perf_counter() - start_enc
    
    start_dec = time.perf_counter()
    decrypted = des_process(ciphertext, key, mode="decrypt")
    time_dec = time.perf_counter() - start_dec
    
    return {
        "title": "--- DES Implementation ---", 
        "key_label": "Auto-generated 64-bit Key",
        "key": key, 
        "round_keys": rounds, 
        "encryption": {"ciphertext": ciphertext, "time": f"{time_enc:.6f} seconds"}, 
        "decryption": {"original": decrypted, "time": f"{time_dec:.6f} seconds"}
    }

@app.post("/api/symmetric/aes")
def run_aes(req: CipherRequest):
    key = req.key if (req.key and len(req.key) == 32) else auto_generate_aes_key()
    round_keys = get_round_keys_hex(key)
    rounds = {f"Round Key {i:02d}": rk for i, rk in enumerate(round_keys)}
    
    start_enc = time.perf_counter()
    ciphertext = aes_encrypt_long_text(req.text, key)
    time_enc = time.perf_counter() - start_enc
    
    start_dec = time.perf_counter()
    decrypted = aes_decrypt_long_text(ciphertext, key)
    time_dec = time.perf_counter() - start_dec
    
    return {
        "title": f"--- {get_aes_variant()} Implementation ---", 
        "key_label": f"Auto-generated {get_aes_variant().split('-')[1]}-bit Key",
        "key": key, 
        "round_keys": rounds, 
        "encryption": {"ciphertext": ciphertext, "time": f"{time_enc:.6f} seconds"}, 
        "decryption": {"original": decrypted, "time": f"{time_dec:.6f} seconds"}
    }

# --- 3. Public Key Ciphers ---

@app.get("/api/public_key/rsa/setup")
def setup_rsa(bits: int = 512):
    start = time.perf_counter()
    keys = generate_rsa_keys(bits)
    gen_time = time.perf_counter() - start
    
    # Large numbers are sent as strings for JavaScript compatibility
    safe_keys = {
        "public_key": [str(keys["public_key"][0]), str(keys["public_key"][1])],
        "private_key": [str(keys["private_key"][0]), str(keys["private_key"][1])],
        "n": str(keys["n"])
    }
    
    attack = factorization_attack_demo(keys["n"])
    return {
        "title": "--- RSA Implementation ---",
        "bits": bits,
        "time": f"{gen_time:.6f} seconds",
        "full_keys_object": safe_keys, 
        "attack": attack["message"]
    }

@app.post("/api/public_key/rsa/execute")
def execute_rsa(req: CipherRequest):
    if not req.rsa_keys:
        raise HTTPException(status_code=400, detail="RSA keys not found. Run Setup first.")
    
    pub = (int(req.rsa_keys["public_key"][0]), int(req.rsa_keys["public_key"][1]))
    priv = (int(req.rsa_keys["private_key"][0]), int(req.rsa_keys["private_key"][1]))
    
    start = time.perf_counter()
    if req.mode.lower() == "decrypt":
        if not req.rsa_cipher:
            raise HTTPException(status_code=400, detail="No ciphertext provided for decryption.")
        res = rsa_decrypt_text([int(b) for b in req.rsa_cipher], priv)
        dec_time = time.perf_counter() - start
        return {
            "title": "--- RSA Implementation ---", 
            "result": res["plaintext"], 
            "time": f"{dec_time:.6f} seconds"
        }
    else:
        res = rsa_encrypt_text(req.text, pub)
        enc_time = time.perf_counter() - start
        return {
            "title": "--- RSA Implementation ---",
            "hex": res["cipher_hex_blocks"], 
            "raw_blocks": [str(b) for b in res["cipher_blocks"]], 
            "time": f"{enc_time:.6f} seconds"
        }

@app.post("/api/public_key/ecc/execute")
def execute_ecc(req: CipherRequest):
    G = (req.gx, req.gy)
    all_ps = get_all_points(req.p, req.a, req.b)
    pub_a, pub_b, s_a, s_b = run_ecdh_exchange(req.p, req.a, req.b, G, req.priv_a, req.priv_b)
    
    return {
        "title": "--- ECC Analysis & Key Exchange ---",
        "curve": f"y^2 = x^3 + {req.a}x + {req.b} (mod {req.p})",
        "all_points_Ps": all_ps,
        "exchange": {
            "user_a": {"private": req.priv_a, "public": pub_a},
            "user_b": {"private": req.priv_b, "public": pub_b},
            "shared_secret": s_a if s_a == s_b else "Error"
        }
    }

if __name__ == "__main__":
    import uvicorn
    # Start the server on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)