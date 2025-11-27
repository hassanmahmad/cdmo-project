import subprocess
import sys
from pathlib import Path

INSTANCES = [6, 8, 10]

def run_command(cmd, cwd):
    """Run command and stream output in real-time"""
    process = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    for line in process.stdout:
        print(line, end='', flush=True)
    process.wait()

if __name__ == '__main__':
    project_root = Path(__file__).parent
    
    print("=" * 50, flush=True)
    print("RUNNING ALL EXPERIMENTS", flush=True)
    print("=" * 50, flush=True)
    
    # Run CP experiments
    print("\n>>> Running CP experiments...", flush=True)
    run_command([sys.executable, 'run_cp.py'], 
                cwd=project_root / 'source' / 'CP')
    
    # Run SMT experiments
    print("\n>>> Running SMT experiments...", flush=True)
    for n in INSTANCES:
        print(f"    Instance n={n}...", flush=True)
        run_command([sys.executable, 'smt.py', str(n)], 
                    cwd=project_root / 'source' / 'SMT')
    
    # Run MIP experiments
    print("\n>>> Running MIP experiments...", flush=True)
    for n in INSTANCES:
        print(f"    Instance n={n}...", flush=True)
        run_command([sys.executable, 'mip.py', str(n)], 
                    cwd=project_root / 'source' / 'MIP')
    
    # Validate all results
    print("\n" + "=" * 50, flush=True)
    print("VALIDATING ALL RESULTS", flush=True)
    print("=" * 50, flush=True)
    
    print("\n>>> Checking CP solutions...", flush=True)
    run_command([sys.executable, 'solution_checker.py', 'res/CP'], 
                cwd=project_root)
    
    print("\n>>> Checking SMT solutions...", flush=True)
    run_command([sys.executable, 'solution_checker.py', 'res/SMT'], 
                cwd=project_root)
    
    print("\n>>> Checking MIP solutions...", flush=True)
    run_command([sys.executable, 'solution_checker.py', 'res/MIP'], 
                cwd=project_root)
    
    print("\n" + "=" * 50, flush=True)
    print("ALL EXPERIMENTS COMPLETE!", flush=True)
    print("=" * 50, flush=True)