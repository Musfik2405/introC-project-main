import random

# --- Core ECC Operations (Scratch Implementation) ---

def mod_inverse(n, prime):
    """Modular inverse using Fermat's Little Theorem (requires prime p)."""
    return pow(n, prime - 2, prime)

def point_addition(P, Q, a, p):
    """Adds two points on the curve y^2 = x^3 + ax + b (mod p).""" 
    if P is None: return Q
    if Q is None: return P
    
    x1, y1 = P
    x2, y2 = Q
    
    # Check for point at infinity
    if x1 == x2 and (y1 + y2) % p == 0:
        return None 
    
    if P != Q:
        # Standard Addition slope calculation
        num = (y2 - y1) % p
        den = mod_inverse(x2 - x1, p)
        m = (num * den) % p
    else:
        # Point Doubling slope calculation
        num = (3 * x1**2 + a) % p
        den = mod_inverse(2 * y1, p)
        m = (num * den) % p
        
    x3 = (m**2 - x1 - x2) % p
    y3 = (m * (x1 - x3) - y1) % p
    return (x3, y3)

def scalar_multiplication(k, P, a, p):
    """Computes k * P using the Double-and-Add algorithm."""
    result = None
    addend = P
    while k:
        if k & 1:
            result = point_addition(result, addend, a, p)
        addend = point_addition(addend, addend, a, p)
        k >>= 1
    return result

# --- Requirement Implementations  ---

def get_all_points(p, a, b):
    """Generates a list of all points (Ps) on the curve."""
    points = []
    # Exhaustive search for all points on the curve y^2 = x^3 + ax + b
    for x in range(p):
        for y in range(p):
            if (y**2) % p == (x**3 + a*x + b) % p:
                points.append((x, y))
    # Requirement: Must include the Point at Infinity
    return points + ["Point at Infinity"]

def run_ecdh_exchange(p, a, b, G, priv_a, priv_b):
    """Performs ECDH Key Exchange."""
    # Requirement: Public Key generation (Public = Private * G)
    pub_a = scalar_multiplication(priv_a, G, a, p)
    pub_b = scalar_multiplication(priv_b, G, a, p)
    
    # Shared Key generation logic
    shared_a = scalar_multiplication(priv_a, pub_b, a, p)
    shared_b = scalar_multiplication(priv_b, pub_a, a, p)
    
    return pub_a, pub_b, shared_a, shared_b