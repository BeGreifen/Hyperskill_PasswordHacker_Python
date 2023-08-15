from time import time

def catalan(n):
    if n <= 1:
        return 1
    res = 0
    for i in range(n):
        res += catalan(i) * catalan(n-i-1)
    return res

# start the timer
for i in range(16):
    catalan(i)
# end timer and save the message