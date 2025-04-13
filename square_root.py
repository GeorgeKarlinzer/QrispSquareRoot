def non_restoring_square_root(a, n):
    """
    Non-restoring square root algorithm implementation
    
    Algorithm from pseudocode:
    1. R = 0^(n-2)a_(n-1)a_(n-2) //where 0^(n-2) are n-2 zeros. a_(n-1) is the most significant bit of a
    2. F = 0^(n-2)01 //where 0^(n-2) are n-2 zeros
    3. R = R - F
    4. Loop from i = n/2 - 1 down to 1:
       a. If R < 0:
          i. Y_i = 0
          ii. R = 0^(2i-2)R_(n-1-2i)...R_0a_(2i-1)a_(2i-2)
          iii. F = 0^(i+n/2-2)Y_(n/2-1)...Y_(i+1)Y_i11
          iv. R = R + F
       b. Else:
          i. Y_i = 1
          ii. R = 0^(2i-2)R_(n-1-2i)...R_0a_(2i-1)a_(2i-2)
          iii. F = 0^(i+n/2-2)Y_(n/2-1)...Y_(i+1)Y_i01
          iv. R = R - F
    5. If R < 0:
       a. Y_0 = 0
       b. F = 0^(n/2-2)Y_(n/2-1)...Y_1Y_001
       c. R = R + F
    6. Else:
       a. Y_0 = 1
    7. Return Y, R
    
    Args:
        a: A positive binary value in 2's complement with even bit length n
        n: Bit length of a
    
    Returns:
        Y: Square root of a (n/2 bits)
        R: Remainder
    """
    if n % 2 != 0:
        raise ValueError("Input bit length must be even")
    
    # Extract bits of a in MSB to LSB order
    a_bits = [(a >> i) & 1 for i in range(n-1, -1, -1)]
    
    # Initialize Y array for result (will have n/2 bits)
    Y = [0] * (n // 2)
    
    # Line 1: R = 0^(n-2)a_(n-1)a_(n-2)
    R = (a_bits[0] << 1) | a_bits[1]
    
    # Line 2: F = 0^(n-2)01
    F = 1
    
    # Line 3: R = R - F
    R = R - F

    print("After initialization:")
    print(f"R: {R:0{n}b}")
    print(f"F: {F:0{n}b}")
    print("--------------------------------")
    
    # Line 4: Main loop from i = n/2 - 1 down to 1
    for i in range(n//2 - 1, 0, -1):
        print(f"Iteration {i}:")
        # Calculate index in Y array
        idx = n//2 - 1 - i
        
        if R < 0:
            print("R < 0")
            # Line 4a.i: Y_i = 0
            Y[idx] = 0
            print(f"Y{i} = 0")            
            # Line 4a.ii: R = 0^(2i-2)R_(n-1-2i)...R_0a_(2i-1)a_(2i-2)
            # Shift in 2 more bits from a
            bit_idx = 2*i
            next_bits = (a_bits[n-bit_idx] << 1) | (a_bits[n-bit_idx+1] if n-bit_idx+1 < n else 0)
            R = (R << 2) | next_bits
            print(f"R after shift = {R:0{n}b}")
            
            # Line 4a.iii: F = 0^(i+n/2-2)Y_(n/2-1)...Y_(i+1)Y_i11
            F = 0
            # First insert all computed Y bits up to Y_i
            for j in range(idx+1):
                F = (F << 1) | Y[j]
            # Then append 11
            F = (F << 2) | 3
            print(f"F after shift = {F:0{n}b}")
            # Line 4a.iv: R = R + F

            R = R + F
        else:
            print("R >= 0")
            # Line 4b.i: Y_i = 1
            Y[idx] = 1
            print(f"Y{i} = 1")

            # Line 4b.ii: R = 0^(2i-2)R_(n-1-2i)...R_0a_(2i-1)a_(2i-2)
            # Shift in 2 more bits from a
            bit_idx = 2*i
            next_bits = (a_bits[n-bit_idx] << 1) | (a_bits[n-bit_idx+1] if n-bit_idx+1 < n else 0)
            R = (R << 2) | next_bits
            print(f"R after shift = {R:0{n}b}")
            # Line 4b.iii: F = 0^(i+n/2-2)Y_(n/2-1)...Y_(i+1)Y_i01
            F = 0
            # First insert all computed Y bits up to Y_i
            for j in range(idx+1):
                F = (F << 1) | Y[j]
            # Then append 01
            F = (F << 2) | 1
            print(f"F after shift = {F:0{n}b}")
            # Line 4b.iv: R = R - F
            R = R - F
            
        print(f"R: {R:0{n}b}")
        print(f"F: {F:0{n}b}")
        print("--------------------------------")
    
    # Handle final bit (Y_0)
    if R < 0:
        print("R < 0")
        # Line 5a: Y_0 = 0
        Y[n//2-1] = 0
        
        # Line 5b: F = 0^(n/2-2)Y_(n/2-1)...Y_1Y_001
        print(Y)
        F = 0
        for j in range(n//2):
            F = (F << 1) | Y[j]
        F = (F << 2) | 1  # Append 01
        print(f"F after shift = {F:0{n}b}")
        # Line 5c: R = R + F
        R = R + F
    else:
        print("R >= 0")
        # Line 6a: Y_0 = 1
        Y[n//2-1] = 1
        # No need to update R here as per the algorithm
    
    # Convert Y bit array to integer
    Y_value = 0
    for bit in Y:
        Y_value = (Y_value << 1) | bit
    
    # Line 7: Return Y, R
    return Y_value, R


# Example usage
if __name__ == "__main__":
    # Test cases with different values
    test_cases = [
        # (16, 8),    # perfect square: 4^2 = 16
        # (25, 8),    # perfect square: 5^2 = 25
        # (36, 8),    # perfect square: 6^2 = 36
        # (15, 8),    # non-perfect square between 3^2 and 4^2
        (321131, 20),    # non-perfect square
        # (26, 6),    # non-perfect square
        # (197691, 20),    # non-perfect square
        # (100, 8),   # perfect square: 10^2 = 100
    ]
    
    for test_value, bit_length in test_cases:
        # Compute square root and remainder
        sqrt_result, remainder = non_restoring_square_root(test_value, bit_length)
        
        # Display results
        print(f"Input: {test_value}")
        print(f"Square Root:   {sqrt_result}")
        print(f"Expected sqrt: {int(test_value**0.5)}")
        print(f"Remainder:          {remainder}")
        print(f"Expected remainder: {test_value - int(test_value**0.5)**2}")
        print("-" * 50)
