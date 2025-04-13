from qrisp import QuantumFloat, QuantumCircuit, QuantumSession
import math

def peres_gate():
    qc = QuantumCircuit(3)
    qc.ccx(0, 1, 2)
    qc.cx(0, 1)
    return qc.to_gate(name="peres")

def add_circuit(n):
    qc = QuantumCircuit(2 * n + 1)
    A = [i for i in range(0, n + 1, 1)]
    B = [i for i in range(n + 1, 2 * n + 1, 1)]
    
    # Step 1
    for i in range(1, n, 1):
        qc.cx(A[i], B[i])
        
    # Step 2
    for i in range(n-1, 0, -1):
        qc.cx(A[i], A[i+1])

    # Step 3
    for i in range(0, n-1, 1):
        qc.ccx(A[i], B[i], A[i+1])

    # Step 4
    for i in range(n-1, -1, -1):
        qc.append(peres_gate(), [A[i], B[i], A[i+1]])

    # Step 5
    for i in range(1, n-1, 1):
        qc.cx(A[i], A[i+1])

    # Step 6
    for i in range(1, n, 1):
        qc.cx(A[i], B[i])

    return qc.to_gate()

def add_circuit_wo_overflow(n):
    qc = QuantumCircuit(2 * n)
    A = [i for i in range(0, n, 1)]
    B = [i for i in range(n, 2 * n, 1)]
    
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

    return qc.to_gate()

def sub_circuit(n):
    qc = QuantumCircuit(2 * n + 1)
    A = [i for i in range(0, n + 1, 1)]
    B = [i for i in range(n + 1, 2 * n + 1, 1)]

    for i in A[:-1]:
        qc.x(i)

    qc.append(add_circuit(n), A + B)

    for i in A[:-1]:
        qc.x(i)

    for i in B:
        qc.x(i)

    return qc.to_gate()

def sub_circuit_wo_overflow(n):
    qc = QuantumCircuit(2 * n)
    A = [i for i in range(0, n, 1)]
    B = [i for i in range(n, 2 * n, 1)]

    for i in A:
        qc.x(i)
    
    qc.append(add_circuit_wo_overflow(n), A + B)

    for i in A:
        qc.x(i)

    for i in B:
        qc.x(i)

    return qc.to_gate()

def apply_add(a: int, b: int):
    n = math.ceil(math.log2(max(a, b) + 1))
    A = QuantumFloat(n+1, 0, name="A")
    B = QuantumFloat(n, 0, name="B")

    A[:] = a
    B[:] = b
    
    qs = QuantumSession()
    qs.append(add_circuit(n), A[:] + B[:])

    B_value = list(B.get_measurement().keys())[0]
    A_value = list(A.get_measurement().keys())[0]
    A_msb = A_value & (1 << (n))
    B_value = B_value | A_msb

    print(f'Result: {B_value}')
    print(f'Should be: {a + b}')

def apply_add_wo_overflow(a: int, b: int):
    n = math.ceil(math.log2(max(a, b) + 1))
    A = QuantumFloat(n, 0, name="A")
    B = QuantumFloat(n, 0, name="B")

    A[:] = a
    B[:] = b
    
    qs = QuantumSession()
    qs.append(add_circuit_wo_overflow(n), A[:] + B[:])

    B_value = list(B.get_measurement().keys())[0]

    print(f'Result: {B_value}')

def apply_sub(a: int, b: int):
    n = math.ceil(math.log2(max(a, b) + 1))
    A = QuantumFloat(n+1, 0, name="A")
    B = QuantumFloat(n, 0, name="B")

    A[:] = a
    B[:] = b
    
    qs = QuantumSession()
    qs.append(sub_circuit(n), A[:] + B[:])

    B_value = list(B.get_measurement().keys())[0]
    A_value = list(A.get_measurement().keys())[0]
    A_msb = A_value & (1 << (n))
    B_value = B_value | A_msb

    if(a < b):
        B_value =  B_value - 2**(n+1)
    print(f'Result: {B_value}')
    print(f'Should be: {a - b}')

def apply_sub_wo_overflow(a: int, b: int):
    n = math.ceil(math.log2(max(a, b) + 1))
    A = QuantumFloat(n, 0, name="A")
    B = QuantumFloat(n, 0, name="B")

    A[:] = a
    B[:] = b

    qs = QuantumSession()
    qs.append(sub_circuit_wo_overflow(n), A[:] + B[:])

    B_value = list(B.get_measurement().keys())[0]
    print(f'Result: {B_value}')

if __name__ == "__main__":
    apply_add_wo_overflow(255, 255)