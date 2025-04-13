import math


def non_restoring_square_root(a, n):
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

    # Line 4: Main loop from i = n/2 - 1 down to 1
    for i in range(n//2 - 1, 0, -1):
        # Calculate index in Y array
        idx = n//2 - 1 - i
        
        if R < 0:
            # Line 4a.i: Y_i = 0
            Y[idx] = 0
            # Line 4a.ii: R = 0^(2i-2)R_(n-1-2i)...R_0a_(2i-1)a_(2i-2)
            # Shift in 2 more bits from a
            bit_idx = 2*i
            next_bits = (a_bits[n-bit_idx] << 1) | (a_bits[n-bit_idx+1] if n-bit_idx+1 < n else 0)
            R = (R << 2) | next_bits
            
            # Line 4a.iii: F = 0^(i+n/2-2)Y_(n/2-1)...Y_(i+1)Y_i11
            F = 0
            # First insert all computed Y bits up to Y_i
            for j in range(idx+1):
                F = (F << 1) | Y[j]
            # Then append 11
            F = (F << 2) | 3
            # Line 4a.iv: R = R + F

            R = R + F
        else:
            # Line 4b.i: Y_i = 1
            Y[idx] = 1

            # Line 4b.ii: R = 0^(2i-2)R_(n-1-2i)...R_0a_(2i-1)a_(2i-2)
            # Shift in 2 more bits from a
            bit_idx = 2*i
            next_bits = (a_bits[n-bit_idx] << 1) | (a_bits[n-bit_idx+1] if n-bit_idx+1 < n else 0)
            R = (R << 2) | next_bits
            # Line 4b.iii: F = 0^(i+n/2-2)Y_(n/2-1)...Y_(i+1)Y_i01
            F = 0
            # First insert all computed Y bits up to Y_i
            for j in range(idx+1):
                F = (F << 1) | Y[j]
            # Then append 01
            F = (F << 2) | 1
            # Line 4b.iv: R = R - F
            R = R - F
            
    
    # Handle final bit (Y_0)
    if R < 0:
        # Line 5a: Y_0 = 0
        Y[n//2-1] = 0
        
        # Line 5b: F = 0^(n/2-2)Y_(n/2-1)...Y_1Y_001
        F = 0
        for j in range(n//2):
            F = (F << 1) | Y[j]
        F = (F << 1) | 1  # Append 1
        # Line 5c: R = R + F
        R = R + F
    else:
        # Line 6a: Y_0 = 1
        Y[n//2-1] = 1
        # No need to update R here as per the algorithm
    
    # Convert Y bit array to integer
    Y_value = 0
    for bit in Y:
        Y_value = (Y_value << 1) | bit
    
    # Line 7: Return Y, R
    return Y_value, R


def non_restoring_square_root_without_garbage(a):
    n = math.ceil(math.log2(a + 1))
    if(n % 2 == 1):
        n += 1
    elif(a & (1 << (n - 1))):
        n += 2

    R = 0 
    F = 1
        
    

# Example usage
if __name__ == "__main__":
    # Test cases with different values
    test_cases = [i for i in range(1, 111111)]
    
    for test_value in test_cases:
        n = math.ceil(math.log2(test_value + 1))

        if(n % 2 == 1):
            n += 1
        elif(test_value & (1 << (n - 1))):
            n += 2

        # Compute square root and remainder
        sqrt_result, remainder = non_restoring_square_root(test_value, n)
        expected_sqrt = int(test_value**0.5)
        expected_remainder = test_value - expected_sqrt**2
        if sqrt_result != expected_sqrt or remainder != expected_remainder:
            print(f"\033[91mError for {test_value}\033[0m")
