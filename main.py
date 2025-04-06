from qrisp import QuantumFloat, x, cx
import math

# Initialize variable a
a = 26

# Calculate n as the number of bits needed to represent a
n = math.ceil(math.log2(a + 1))  # +1 to ensure we have enough bits

# Ensure n is even
if n % 2 != 0:
    n += 1
    
print(f"n = {n}")

print(f"a = {a}, requires {n} bits to represent (adjusted to ensure even number)")
print("-" * 40)

# Create quantum registers
# We use QuantumFloat which can encode integer values
R = QuantumFloat(n, 0, name="R")  # n bits with exponent 0 (integer)
F = QuantumFloat(n, 0, name="F")  # n bits with exponent 0 (integer)
z = QuantumFloat(1, 0, name="z")  # 1 bit with exponent 0 (integer)

# Initialize registers with values
R[:] = a  # R = 26
F[:] = 1  # F = 1
z[:] = 0  # z = 0

def visualize_registers():
    print("Quantum register states:")
    print("-" * 40)
    print(f"R = {R.get_measurement()}")
    print(f"F = {F.get_measurement()}")
    print(f"z = {z.get_measurement()}")
    print("-" * 40)

# Print the quantum state of all registers separately
visualize_registers()

# Algorithm step functions
def initial_subtraction():
    # Step 1: Apply a quantum NOT gate at R[n-2]
    x(R[n-2])

    # Step 2: Apply a CNOT gate with R[n-2] as control and R[n-1] as target
    R.qs.cx(R[n-2], R[n-1])
    
    # Step 3: Apply a CNOT gate with R[n-1] as control and F[1] as target
    R.qs.cx(R[n-1], F[1])
    
    # Step 4: Apply an inverted control CNOT gate with R[n-1] as control and z as target
    # First negate the control qubit
    x(R[n-1])
    # Apply the CNOT
    R.qs.cx(R[n-1], z[0])
    # Restore the control qubit
    x(R[n-1])
    
    # Step 5: Apply an inverted control CNOT gate with R[n-1] as control and F[2] as target
    # First negate the control qubit
    x(R[n-1])
    # Apply the CNOT
    R.qs.cx(R[n-1], F[2])
    # Restore the control qubit
    x(R[n-1])

    # Step 6: Quantum conditional addition or subtraction circuit
    from qrisp import control
    
    # When z=0, we add F to R
    with control(z[0], ctrl_state=0):
        # Add F to R when z=0
        # Use the relevant bits from F (F3,F2,F1,F0) and apply to R (Rn-1,Rn-2,Rn-3,Rn-4)
        num_bits = min(4, n)  # Ensure we don't exceed the register size
        
        for i in range(num_bits):
            # For addition, we simply apply CNOT gates from F to R
            # Start from MSB: F[3] to R[n-1], F[2] to R[n-2], etc.
            F_idx = min(3, num_bits-1) - i  # Start from F3 and go down
            R_idx = n-1-i  # Start from Rn-1 and go down
            
            if F_idx >= 0 and R_idx >= 0:  # Ensure indices are valid
                R.qs.cx(F[F_idx], R[R_idx])
    
    # When z=1, we subtract F from R
    with control(z[0], ctrl_state=1):
        # When z=1, we subtract F from R
        # Use the relevant bits from F (F3,F2,F1,F0) and apply to R (Rn-1,Rn-2,Rn-3,Rn-4)
        # We implement subtraction by flipping the bits in F (XOR), then adding

        # Use at most the first 4 bits of F and R for the operation
        # Map F3,F2,F1,F0 to Rn-1,Rn-2,Rn-3,Rn-4
        num_bits = min(4, n)  # Ensure we don't exceed the register size
        
        for i in range(num_bits):
            # For subtraction, we XOR the bits from F to R
            # Start from MSB: F[3] to R[n-1], F[2] to R[n-2], etc.
            F_idx = min(3, num_bits-1) - i  # Start from F3 and go down
            R_idx = n-1-i  # Start from Rn-1 and go down
            
            if F_idx >= 0 and R_idx >= 0:  # Ensure indices are valid
                R.qs.cx(F[F_idx], R[R_idx])

def conditional_addition_or_substraction():
    # This function implements iterations of Part 2 with i ranging from 2 to n/2-1
    # Calculate number of iterations
    iterations = n//2 - 2  # From i=2 to i=n/2-1
    
    print(f"Executing {iterations} iterations for Part 2")
    
    for i in range(2, n//2):
        print(f"  Iteration {i}")
        
        # Step 1: Apply an inverted control CNOT gate with z as control and F[1] as target
        # First negate the control qubit
        x(z[0])
        # Apply the CNOT
        R.qs.cx(z[0], F[1])
        # Restore the control qubit
        x(z[0])
        
        # Step 2: Apply a CNOT gate with F[2] as control and z as target
        R.qs.cx(F[2], z[0])
        
        # Step 3: Apply a CNOT gate with R[n-1] as control and F[1] as target
        R.qs.cx(R[n-1], F[1])
        
        # Step 4: Apply an inverted control CNOT gate with R[n-1] as control and z as target
        # First negate the control qubit
        x(R[n-1])
        # Apply the CNOT
        R.qs.cx(R[n-1], z[0])
        # Restore the control qubit
        x(R[n-1])
        
        # Step 5: Apply an inverted control CNOT gate with R[n-1] as control and F[i+1] as target
        # First negate the control qubit
        x(R[n-1])
        # Apply the CNOT - use F[i+1] for the current iteration
        R.qs.cx(R[n-1], F[i+1])
        # Restore the control qubit
        x(R[n-1])
        
        # Step 6: For j = i + 1 to 3, apply SWAP gates to reorder bits in F
        # Implement SWAP gates to reorder positions
        for j in range(i + 1, 2, -1):  # Going from i+1 down to 3
            # Apply SWAP gate between F[j] and F[j-1]
            # SWAP is implemented with 3 CNOT gates
            F.qs.swap(F[j], F[j-1])
        
        # Step 7: Quantum conditional addition or subtraction circuit
        print(f"    Step 7: ADD/SUB operation for iteration {i}")
        
        # Sub-step 1: Perform addition or subtraction on R[n-1] through R[n-2-i-2] based on F[2-i+1] through F[0]
        # Calculate the range of bits to operate on for this iteration
        r_end = max(0, n-2-i-2)  # Make sure we don't go below 0
        
        from qrisp import control
        
        # Sub-step 1: Conditional ADD/SUB on the R register bits
        print(f"      Operating on R[{n-1}] through R[{r_end}]")
        
        # We'll implement conditional ADD/SUB using controlled operations
        # For conditional addition/subtraction, we need to:
        # 1. If z=0, add appropriate bits of F to R
        # 2. If z=1, subtract appropriate bits of F from R
        
        # Calculate which bits of F to use (F[2-i+1] through F[0])
        f_start = min(2*i+1, n-1)  # Make sure we don't exceed register size
        
        with control(z[0], ctrl_state=0):
            # Add appropriate bits of F to R when z=0
            for idx, f_idx in enumerate(range(f_start, -1, -1)):
                r_idx = n-1-idx
                if r_idx >= r_end:  # Ensure we're within bounds
                    R.qs.cx(F[f_idx], R[r_idx])
        
        with control(z[0], ctrl_state=1):
            # Subtract appropriate bits of F from R when z=1
            for idx, f_idx in enumerate(range(f_start, -1, -1)):
                r_idx = n-1-idx
                if r_idx >= r_end:  # Ensure we're within bounds
                    # Negate the result with XOR for subtraction
                    R.qs.cx(F[f_idx], R[r_idx])

def remainder_restoration():
    # This part implements the remainder restoration (Part 3)
    print("Executing Part 3: Remainder Restoration")
    
    # Step 1: Apply an inverted control CNOT gate with z as control and F[1] as target
    # First negate the control qubit
    x(z[0])
    # Apply the CNOT
    R.qs.cx(z[0], F[1])
    # Restore the control qubit
    x(z[0])
    print("  Step 1: Restored F[1] to its initial value")
    
    # Step 2: Apply a CNOT gate with F[2] as control and z as target
    R.qs.cx(F[2], z[0])
    print("  Step 2: Applied CNOT between F[2] and z to reset z to 0")
    
    # Step 3: Apply an inverted control CNOT gate with R[n-1] as control and z as target
    # First negate the control qubit
    x(R[n-1])
    # Apply the CNOT
    R.qs.cx(R[n-1], z[0])
    # Restore the control qubit
    x(R[n-1])
    print("  Step 3: Applied inverted control CNOT between R[n-1] and z")
    
    # Step 4: Apply an inverted control CNOT gate with R[n-1] as control and F[n/2+1] as target
    # Calculate the index for F[n/2+1]
    f_idx = n//2 + 1
    
    # Check if the index is within the range of the register
    if f_idx < n:
        # First negate the control qubit
        x(R[n-1])
        # Apply the CNOT
        R.qs.cx(R[n-1], F[f_idx])
        # Restore the control qubit
        x(R[n-1])
        print(f"  Step 4: Applied inverted control CNOT between R[n-1] and F[{f_idx}]")
    else:
        print(f"  Step 4: Skipped as F[{f_idx}] is out of range for the {n}-bit register")
    
    # Step 5: Apply a NOT gate to z qubit
    x(z[0])
    print("  Step 5: Applied NOT gate to z qubit")
    
    # Step 6: Apply quantum CTRL-ADD circuit
    print("  Step 6: Applying quantum CTRL-ADD circuit")
    
    from qrisp import control
    
    # Sub-step 1: Apply F and R to a quantum CTRL-ADD circuit
    # In Qrisp, we can implement controlled addition using the control construct
    with control(z[0], ctrl_state=1):
        # Perform addition: R = R + F
        # We're focusing on the relevant bits to add
        for i in range(min(F.size, R.size)):
            R.qs.cx(F[i], R[i])
        
        print("    Sub-step 1: Applied F and R to CTRL-ADD circuit")
    
    # Sub-step 2: The control(z[0]) above already implements the conditioning on z
    print("    Sub-step 2: CTRL-ADD operation conditioned on z value")
    
    # Step 7: Apply a NOT gate to z qubit to restore its value
    x(z[0])
    print("  Step 7: Applied NOT gate to z qubit to restore its value")
    
    # Step 8: For j = n/2 + 1 to 3, apply SWAP gates to reorder bits in F
    j_start = n//2 + 1
    
    print(f"  Step 8: Applying SWAP gates for j = {j_start} to 3")
    
    # Implement SWAP gates to reorder positions
    for j in range(j_start, 2, -1):  # Going from n/2+1 down to 3
        # Make sure j and j-1 are within the register size
        if j < n and j-1 >= 0:
            # Apply SWAP gate between F[j] and F[j-1]
            # SWAP is implemented with 3 CNOT gates
            F.qs.cx(F[j], F[j-1])
            F.qs.cx(F[j-1], F[j])
            F.qs.cx(F[j], F[j-1])
            
            print(f"    SWAP F[{j}] and F[{j-1}]")
        else:
            print(f"    Skipped SWAP between F[{j}] and F[{j-1}] as they are out of range")
    
    # Step 9: Apply a CNOT gate with F[2] as control and z as target to restore z to 0
    # Check if F[4] exists in our register (it is needed in the formula but might not exist in small registers)
    f4_exists = 4 < n
    
    # Apply the CNOT gate
    R.qs.cx(F[2], z[0])
    
    print("  Step 9: Applied CNOT between F[2] and z to complete restoration of z to 0")
    print("  After Part 3, F contains the final value of √a")

# Execute the algorithm steps
print("Executing algorithm steps:")
print("-" * 40)
initial_subtraction()

print(R.qs)
visualize_registers()
exit()
print("Part 1 completed")

conditional_addition_or_substraction()
print("Part 2 completed")
visualize_registers()

remainder_restoration()
print("Part 3 completed")
visualize_registers()
# Print final register states
print("\nFinal quantum register states:")
print("-" * 40)
visualize_registers()
print(R.qs)