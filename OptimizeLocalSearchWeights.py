# Script to run LocalSearchOptimizer
from LocalSearchOptimizer import *
import time

if __name__ == "__main__":
    l = LocalSearchOptimizer()
    # w = l.get_random_start()
    # print("Initial weights:", w)
    # s = l.get_random_successor(w)
    # print("Random successor:", s)
    # start = time.time()
    # e = l.evaluate(s)
    # print("Time elapsed:", (time.time() - start))
    # print("Evaluation result:", e)

    start = time.time()
    weights = l.get_weights()
    print("Time elapsed:", (time.time() - start))
    print("Final weights:", weights)
    # with open("optimized_weights.txt", "w") as f:
    #     f.write(str(weights))


