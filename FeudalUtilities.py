import os, random, time

# Needed to ensure separate seeding of processes (see below link) as otherwise
# all simulations would be the same
# https://stackoverflow.com/questions/9209078/using-python-multiprocessing-with-different-random-seed-for-each-process
# Credit to Professor Weiss (previous semester - Parallel Programming) for the
# idea of getting a good seed via multiplying the current system time by the
# process id
def parallel_seed():
    pid = os.getpid()
    seed = pid * int(time.time())
    #print("Process", pid, "seed:", seed)
    random.seed(seed)
    #print(random.randrange(2048))
