from time import time


def catalan(n):
    if n <= 1:
        return 1
    res = 0
    for i in range(n):
        res += catalan(i) * catalan(n-i-1)
    return res


start = time()
# start the timer
for int_run in range(16):
    catalan(int_run)
# end timer and save the message
ans = time() - start
message = f'It took {ans} seconds!'
