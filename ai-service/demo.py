import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)

from demo import run_demo

if __name__ == "__main__":
    run_demo()
