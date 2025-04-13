from qrisp import QuantumFloat, x, cx, QuantumCircuit, control, Operation, QuantumSession, XGate, Qubit
import math

def peres_gate():
    qc = QuantumCircuit(3)
    qc.ccx(0, 1, 2)
    qc.cx(0, 1)
    return qc.to_gate(name="peres")

def add_wo_overflow_circuit(n):
    qc = QuantumCircuit(2 * n)
    B = [i for i in range(0, n, 1)]
    A = [i for i in range(n, 2 * n, 1)]
    
    # Step 1
    for i in range(1, n, 1):
        qc.cx(A[i], B[i])
        
    # Step 2
    for i in range(n-2, 0, -1):
        qc.cx(A[i], A[i+1])

    # Step 3
    for i in range(0, n-1, 1):
        qc.ccx(A[i], B[i], A[i+1])

    # Step 4
    for i in range(n-1, -1, -1):
        if(i == n - 1):
            qc.cx(A[i], B[i])
        else:
            qc.append(peres_gate(), [A[i], B[i], A[i+1]])

    # Step 5
    for i in range(1, n-1, 1):
        qc.cx(A[i], A[i+1])

    # Step 6
    for i in range(1, n, 1):
        qc.cx(A[i], B[i])

    return qc.to_gate(name="ADD")

def sub_wo_overflow_circuit(n):
    qc = QuantumCircuit(2 * n)
    A = [i for i in range(0, n, 1)]
    B = [i for i in range(n, 2 * n, 1)]

    for i in A:
        qc.x(i)
    
    qc.append(add_wo_overflow_circuit(n), A + B)

    for i in A:
        qc.x(i)

    return qc.to_gate(name="SUB")

def control_add_sub_circuit(n):
    qc = QuantumCircuit(0)
    z = 0
    A = [i for i in range(1, n + 1, 1)]
    B = [i for i in range(n + 1, 2 * n + 1, 1)]

    qc.add_qubit(Qubit(f'z'))

    for i in A:
        qc.add_qubit(Qubit(f'A_{i - 1}'))

    for i in B:
        qc.add_qubit(Qubit(f'B_{i - n - 1}'))
    
    add_circuit = add_wo_overflow_circuit(n)
    sub_circuit = sub_wo_overflow_circuit(n)

    controlled_add = add_circuit.control(ctrl_state=0)
    controlled_sub = sub_circuit.control(ctrl_state=1)

    qc.append(controlled_add, [z] + A + B)
    qc.append(controlled_sub, [z] + A + B)

    return qc.to_gate(name="CTRL ADD/SUB")

def control_add_circuit(n):
    qc = QuantumCircuit(0)
    z = 0
    A = [i for i in range(1, n + 1, 1)]
    B = [i for i in range(n + 1, 2 * n + 1, 1)]

    qc.add_qubit(Qubit(f'z'))

    for i in A:
        qc.add_qubit(Qubit(f'A_{i - 1}'))

    for i in B:
        qc.add_qubit(Qubit(f'B_{i - n - 1}'))


    controlled_add = add_wo_overflow_circuit(n).control(ctrl_state=1)

    qc.append(controlled_add, [z] + A + B)

    return qc.to_gate(name="CTRL ADD")



def initial_subtraction_circuit(n):
    qc = QuantumCircuit()
    R = [i for i in range(0, n, 1)]
    F = [i for i in range(n, 2 * n, 1)]
    z = 2 * n

    for i in R:
        qc.add_qubit(Qubit(f'R_{i}'))

    for i in F:
        qc.add_qubit(Qubit(f'F_{i - n}'))

    qc.add_qubit(Qubit(f'z'))

    # Step 1
    qc.x(R[n-2])

    # Step 2
    qc.cx(R[n-2], R[n-1])

    # Step 3
    qc.cx(R[n-1], F[1])

    # Step 4
    qc.append(XGate().control(ctrl_state=0), [R[n-1], z])
    
    # Step 5
    qc.append(XGate().control(ctrl_state=0), [R[n-1], F[2]])

    # Step 6
    qc.append(control_add_sub_circuit(4), [z, R[n-4], R[n-3], R[n-2], R[n-1], F[0], F[1], F[2], F[3]])

    return qc.to_gate(name="INITIAL SUBTRACTION")

def conditional_addition_or_subtraction_circuit(n):
    qc = QuantumCircuit()
    R = [i for i in range(0, n, 1)]
    F = [i for i in range(n, 2 * n, 1)]
    z = 2 * n

    for i in R:
        qc.add_qubit(Qubit(f'R_{i}'))

    for i in F:
        qc.add_qubit(Qubit(f'F_{i - n}'))

    qc.add_qubit(Qubit(f'z'))
    

    for i in range(2, n // 2):
        # Step 1
        qc.append(XGate().control(ctrl_state=0), [z, F[1]])

        # Step 2
        qc.cx(F[2], z)

        # Step 3
        qc.cx(R[n-1], F[1])

        # Step 4
        qc.append(XGate().control(ctrl_state=0), [R[n-1], z])

        # Step 5
        qc.append(XGate().control(ctrl_state=0), [R[n-1], F[i+1]])

        # Step 6
        for j in range(i + 1, 4, 1):
            qc.swap(F[j], F[j-1])

        # Step 7
        R_sum_qubits = [R[j] for j in range(n - 2 * i - 2, n, 1)]
        F_sum_qubits = [F[j] for j in range(0, 2 * i + 2, 1)]
        qc.append(control_add_sub_circuit(len(R_sum_qubits)), [z] + R_sum_qubits + F_sum_qubits)
        
    return qc.to_gate(name="CONDITIONAL ADDITION OR SUBTRACTION")

def remainder_restoration_circuit(n):
    qc = QuantumCircuit()
    R = [i for i in range(0, n, 1)]
    F = [i for i in range(n, 2 * n, 1)]
    z = 2 * n

    for i in R:
        qc.add_qubit(Qubit(f'R_{i}'))

    for i in F:
        qc.add_qubit(Qubit(f'F_{i - n}'))

    qc.add_qubit(Qubit(f'z'))

    # Step 1
    qc.append(XGate().control(ctrl_state=0), [z, F[1]])

    # Step 2
    qc.cx(F[2], z)

    # Step 3
    qc.append(XGate().control(ctrl_state=0), [R[n-1], z])

    # Step 4
    qc.append(XGate().control(ctrl_state=0), [R[n-1], F[n//2+1]])

    # Step 5
    qc.x(z)

    # Step 6
    qc.append(control_add_circuit(n), [z] + R[:] + F[:])

    # Step 7
    qc.x(z)

    # Step 8
    for j in range(n//2 + 1, 2, -1):
        qc.swap(F[j], F[j-1])

    # Step 9
    qc.cx(F[2], z)
    
    return qc.to_gate(name="REMAINDER RESTORATION")

def debug(R: QuantumFloat, F: QuantumFloat, z: QuantumFloat):
    R_value = int(list(R.get_measurement().keys())[0])
    F_value = int(list(F.get_measurement().keys())[0])
    z_value = int(list(z.get_measurement().keys())[0])
    print(f'R = {R_value:0{8}b}')
    print(f'F = {F_value:0{8}b}')
    print(f'z = {z_value:0b}')

def initial_subtraction(qs: QuantumSession, R: QuantumFloat, F: QuantumFloat, z: QuantumFloat, n: int):
     # Step 1
    qs.x(R[n-2])
    print('Part 1 Step 1')
    debug(R, F, z)
    print('--------------------------------')
    # Step 2
    qs.cx(R[n-2], R[n-1])
    print('Part 1 Step 2')
    debug(R, F, z)
    print('--------------------------------')
    # Step 3
    qs.cx(R[n-1], F[1])
    print('Part 1 Step 3')
    debug(R, F, z)
    print('--------------------------------')
    # Step 4
    qs.append(XGate().control(ctrl_state=0), [R[n-1], z])
    print('Part 1 Step 4')
    debug(R, F, z)
    print('--------------------------------')
    # Step 5
    qs.append(XGate().control(ctrl_state=0), [R[n-1], F[2]])
    print('Part 1 Step 5')
    debug(R, F, z)
    print('--------------------------------')
    # Step 6
    qs.append(control_add_sub_circuit(4), [z, R[n-4], R[n-3], R[n-2], R[n-1], F[0], F[1], F[2], F[3]])
    print('Part 1 Step 6')
    debug(R, F, z)
    print('--------------------------------')

def conditional_addition_or_subtraction(qs: QuantumSession, R: QuantumFloat, F: QuantumFloat, z: QuantumFloat, n: int):
    for i in range(n//2-1, 1, -1):
        # Step 1
        qs.append(XGate().control(ctrl_state=0), [z, F[1]])
        print(f'Part 2 Step 1 {i}')
        debug(R, F, z)
        print('--------------------------------')
        # Step 2
        qs.cx(F[2], z)
        print(f'Part 2 Step 2 {i}')
        debug(R, F, z)
        print('--------------------------------')

        # Step 3
        qs.cx(R[n-1], F[1])
        print(f'Part 2 Step 3 {i}')
        debug(R, F, z)
        print('--------------------------------')
        # Step 4
        qs.append(XGate().control(ctrl_state=0), [R[n-1], z])
        print(f'Part 2 Step 4 {i}')
        debug(R, F, z)
        print('--------------------------------')
        # Step 5
        qs.append(XGate().control(ctrl_state=0), [R[n-1], F[i+1]])
        print(f'Part 2 Step 5 {i}')
        debug(R, F, z)
        print('--------------------------------')
        # Step 6
        for j in range(i + 1, 4, 1):
            qs.swap(F[j], F[j-1])
            print(f'Part 2 Step 6 {i} {j}')
            debug(R, F, z)
            print('--------------------------------')

        # Step 7
        R_sum_qubits = [R[j] for j in range(n - 2 * i - 2, n, 1)]
        F_sum_qubits = [F[j] for j in range(0, 2 * i + 2, 1)]
        qs.append(control_add_sub_circuit(len(R_sum_qubits)), [z] + R_sum_qubits + F_sum_qubits)
        print(f'Part 2 Step 7 {i}')
        debug(R, F, z)
        print('--------------------------------')

def remainder_restoration(qs: QuantumSession, R: QuantumFloat, F: QuantumFloat, z: QuantumFloat, n: int):
    # Step 1
    qs.append(XGate().control(ctrl_state=0), [z, F[1]])
    print('Part 3 Step 1')
    debug(R, F, z)
    print('--------------------------------')
    # Step 2
    qs.cx(F[2], z)
    print('Part 3 Step 2')
    debug(R, F, z)
    print('--------------------------------')

    # Step 3
    qs.append(XGate().control(ctrl_state=0), [R[n-1], z])
    print('Part 3 Step 3')
    debug(R, F, z)
    print('--------------------------------')
    # Step 4
    qs.append(XGate().control(ctrl_state=0), [R[n-1], F[n//2+1]])
    print('Part 3 Step 4')
    debug(R, F, z)
    print('--------------------------------')

    # Step 5
    qs.x(z)
    print('Part 3 Step 5')
    debug(R, F, z)
    print('--------------------------------')
    # Step 6
    qs.append(control_add_circuit(n), [z] + R[:] + F[:])
    print('Part 3 Step 6')
    debug(R, F, z)
    print('--------------------------------')
    # Step 7
    qs.x(z)
    print('Part 3 Step 7')
    debug(R, F, z)
    print('--------------------------------')
    # Step 8
    for j in range(n//2 + 1, 2, -1):
        qs.swap(F[j], F[j-1])
        print(f'Part 3 Step 8 {j}')
        debug(R, F, z)
        print('--------------------------------')
    # Step 9
    qs.cx(F[2], z)
    print('Part 3 Step 9')
    debug(R, F, z)
    print('--------------------------------')

    

def calculate_square_root(a: int):
    # Should be amount of bits to represent a, taking into account sign bit, and the fact that n should be even
    n = math.ceil(math.log2(a + 1))

    if(n % 2 == 1):
        n += 1
    elif(a & (1 << (n - 1))):
        n += 2

    R = QuantumFloat(n, 0, name="R")
    F = QuantumFloat(n, 0, name="F")
    z = QuantumFloat(1, 0, name="z")

    R[:] = a
    F[:] = 1
    z[:] = 0

    qs = QuantumSession()
    # qs.append(initial_subtraction_circuit(n), R[:] + F[:] + z[:])
    # qs.append(conditional_addition_or_subtraction_circuit(n), R[:] + F[:] + z[:])
    # qs.append(remainder_restoration_circuit(n), R[:] + F[:] + z[:])
    print('Initial state')
    debug(R, F, z)
    print('--------------------------------')
    initial_subtraction(qs, R, F, z, n)
    conditional_addition_or_subtraction(qs, R, F, z, n)
    remainder_restoration(qs, R, F, z, n)

    remainder = list(R.get_measurement().keys())[0]
    root = list(F.get_measurement().keys())[0]
    root = int(root)

    root = root >> (n//2 - 1)

    return root, remainder


if __name__ == "__main__":
    test_cases = [i for i in range(8, 50)]
    test_cases = [8, 11, 12, 14, 15, 26, 32, 47, 48, 60, 76, 121, 125]
    test_cases = [26, 15, 48]
    for a in test_cases:
        calculated_root, calculated_remainder = calculate_square_root(a)
        root = int(math.sqrt(a))
        remainder = a - root**2
        if(calculated_root != root or calculated_remainder != remainder):
            print(f'\033[91mError for a = {a}\033[0m')
            print(f'Calculated root = {calculated_root}, Calculated remainder = {calculated_remainder}')
            print(f'Expected   root = {root}, Expected remainder = {remainder}')
        else:
            print(f'\033[92mSuccess for a = {a}\033[0m')