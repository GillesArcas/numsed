def play():
    print('You start. Make a guess ([1-4]{4}): ')
    guess = input()
    secret = 1234
    while guess != secret:
        n_bulls = 0
        n_cows = 0
        i = 0
        while i < 4:
            if digit(guess, i) == digit(secret, i):
                n_bulls += 1
            j = 0
            while j < 4:
                if j != i and digit(guess, i) == digit(secret, j):
                    n_cows += 1
                    break
                j += 1
            i += 1
        print('Bulls:')
        print(n_bulls)
        print('Cows:')
        print(n_cows)
        print('You start. Make a guess ([1-4]{4}): ')
        guess = input()
    print('You found')

        
def digit(num, index):
    return (num // 10 ** index) % 10
    
 
play()
