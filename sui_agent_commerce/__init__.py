# Allow running `python -m sui_agent_commerce.cli`
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent.cli import main

if __name__ == "__main__":
    main()
