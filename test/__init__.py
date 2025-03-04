import sys
from pathlib import Path

# Get the path to the adjacent directory
adjacent_dir = Path(__file__).parent.parent / 'EVM_Sweeps'
sys.path.insert(0, str(adjacent_dir))       # Add it to sys.path
# sys.path.remove(str(adjacent_dir))        # Remove the path
