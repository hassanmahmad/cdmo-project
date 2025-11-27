import subprocess
import sys
from pathlib import Path

INSTANCES = [6, 8, 10]

if __name__ == '__main__':
    project_root = Path(__file__).parent
    
    print("=" * 50)
    print("RUNNING ALL EXPERIMENTS")
    print("=" * 50)
    
    # Run CP experiments
    print("\n>>> Running CP experiments...")
    subprocess.run([sys.executable, 'run_cp.py'], 
                   cwd=project_root / 'source' / 'CP')
    
    # Run SAT experiments
    print("\n>>> Running SMT experiments...")    
    for n in INSTANCES:
        print(f"    Instance n={n}...")
        subprocess.run([sys.executable, 'smt.py', str(n)], 
                       cwd=project_root / 'source' / 'SMT')
    
    # Run MIP experiments
    print("\n>>> Running MIP experiments...")
    for n in INSTANCES:
        print(f"    Instance n={n}...")
        subprocess.run([sys.executable, 'mip.py', str(n)], 
                       cwd=project_root / 'source' / 'MIP')
    
    # Validate all results
    print("\n" + "=" * 50)
    print("VALIDATING ALL RESULTS")
    print("=" * 50)
    
    print("\n>>> Checking CP solutions...")
    subprocess.run([sys.executable, 'solution_checker.py', 'res/CP'], 
                   cwd=project_root)
    
    print("\n>>> Checking SMT solutions...")
    subprocess.run([sys.executable, 'solution_checker.py', 'res/SMT'], 
                   cwd=project_root)
    
    print("\n>>> Checking MIP solutions...")
    subprocess.run([sys.executable, 'solution_checker.py', 'res/MIP'], 
                   cwd=project_root)
    
    print("\n" + "=" * 50)
    print("ALL EXPERIMENTS COMPLETE!")
    print("=" * 50)