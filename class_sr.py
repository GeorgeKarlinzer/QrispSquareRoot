import math


def add(R: list[bool], F: list[bool], n: int):
    # parse boolean list to int
    R_int = int(''.join(str(int(x)) for x in R[::-1]), 2)
    F_int = int(''.join(str(int(x)) for x in F[::-1]), 2)

    # add
    result = R_int + F_int

    R = []
    for i in range(n):
        bit = result & 1
        R.append(bool(bit))
        result = result >> 1

    R.reverse()

def sub(R: list[bool], F: list[bool], n: int):
    # parse boolean list to int
    R_int = int(''.join(str(int(x)) for x in R), 2)
    F_int = int(''.join(str(int(x)) for x in F), 2)

    # subtract
    result = R_int - F_int

    R = []
    for i in range(n):
        bit = result & 1
        R.append(bool(bit))
        result = result >> 1

    R.reverse()

def initial_subtraction(R: list[bool], F: list[bool], z: bool, n):
    # Step 1
    R[n-2] = not R[n-2]

    # Step 2
    if R[n-2]:
        R[n-1] = not R[n-1]

    # Step 3
    if R[n-1]:
        F[1] = not F[1]

    # Step 4
    if not R[n-1]:
        z = not z

    # Step 5
    if not R[n-1]:
        F[2] = not F[2]

    # Step 6
    if z:
        R_sub = R[:4]
        F_sub = F[-4:]

        sub(R_sub, F_sub, 4)

        for i in range(4):
            R[i] = R_sub[i]
    else:
        R_add = R[:4]
        F_add = F[-4:]  

        add(R_add, F_add, 4)

        for i in range(4):
            R[i] = R_add[i]

def conditional_addition_or_subtraction(R: list[bool], F: list[bool], z: bool, n: int):
    for i in range(n//2-1, 1, -1):
        # Step 1
        if not z:
            F[1] = not F[1]

        # Step 2
        if F[2]:
            z = not z

        # Step 3
        if R[n-1]:
            F[1] = not F[1]

        # Step 4
        if not R[n-1]:
            z = not z

        # Step 5
        if not R[n-1]:
            F[i+1] = not F[i+1]

        # Step 6
        for j in range(i+1, 2, -1):
            F[j], F[j-1] = F[j-1], F[j]

        # Step 7
        if z:
            sub(R, F, n)
        else:
            add(R, F, n)

def remainder_restoration(R: list[bool], F: list[bool], z: bool, n: int):
    # Step 1
    if not z:
        F[1] = not F[1]

    # Step 2
    if F[2]:
        z = not z

    # Step 3
    if not R[n-1]:
        z = not z

    # Step 4
    if not R[n-1]:
        F[n//2+1] = not F[n//2+1]

    # Step 5
    z = not z

    # Step 6
    if not z:
        add(R, F, n)

    # Step 7
    z = not z

    # Step 8
    for j in range(n//2+1, 2, -1):
        F[j], F[j-1] = F[j-1], F[j]

    # Step 9
    if F[2]:
        z = not z


def calculate_square_root(a: int):
    n = math.ceil(math.log2(a + 1))

    if(n % 2 == 1):
        n += 1
    elif(a & (1 << (n - 1))):
        n += 2

    # Assign a to R as a collection of bools, with last bit in the collection being most significant bit
    R = []

    for i in range(n):
        R.append(bool(a & (1 << i)))

    # Assign F to be a collection of bools, with first bit in the collection being most significant bit
    F = [False] * n
    F[0] = True

    initial_subtraction(R, F, False, n)
    conditional_addition_or_subtraction(R, F, False, n)
    remainder_restoration(R, F, False, n)

    # take n // 2 bits from F starting from the third least significant bit
    root = int(''.join(str(int(x)) for x in F[2:n//2+2]), 2)
    return root


print(calculate_square_root(26))