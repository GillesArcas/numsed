# Collatz 3n+1 problem
# Here, compute the first integer needing more than a given number of
# iterations to reach 1.

a = 100
i = 1
n = 0

while n < a:
    i += 1
    j = i
    n = 0

    while j != 1:
        x = j // 2

        if j == x * 2:
            j = x
        else:
            j = j * 3 + 1

        n += 1

    print(i)
    print(n)
