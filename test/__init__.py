import sys
from pathlib import Path

# Get the path to the adjacent directory
adj_dir = Path(__file__).parent.parent / 'EVM_Sweeps'
print(adj_dir)
# sys.path.insert(0, str(adj_dir))        # Add it to sys.path
sys.path.append(str(adj_dir))           # Add it to sys.path
# sys.path.remove(str(adj_dir))         # Remove the path
