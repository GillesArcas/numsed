def isqrt(n):
    hi = n
    lo = 0
    mid = (hi + lo) // 2
    mid2 = mid * mid
    while lo < hi-1 and mid2 != n:
        if mid2 < n:
            lo = mid
        else:
            hi = mid
        mid = (hi + lo) // 2
        mid2 = mid * mid
    return mid
        

x = 5376587
x2 = x * x + 65486
print(x)
print(isqrt(x2))
