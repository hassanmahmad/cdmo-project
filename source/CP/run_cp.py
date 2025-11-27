import subprocess
import json
import time
import os
import sys
from pathlib import Path

# Configuration
INSTANCES = [6, 8, 10]
TIMEOUT = 300

EXPERIMENTS = [
    ('gecode', 'cp.mzn', 'gecode_default'),
    ('gecode', 'cp_fail_first.mzn', 'gecode_fail_first'),
    ('gecode', 'cp_dom_w_deg.mzn', 'gecode_dom_w_deg'),
    ('chuffed', 'cp.mzn', 'chuffed_default'),
]

def find_minizinc():
    # Find MiniZinc executable for docker and local
    
    # for docker
    try:
        result = subprocess.run(['minizinc', '--version'], 
                              capture_output=True, timeout=5)
        if result.returncode == 0:
            return 'minizinc'
    except:
        pass
    
    # for windows
    windows_paths = [
        r'C:\Program Files\MiniZinc\minizinc.exe',
        r'C:\Program Files (x86)\MiniZinc\minizinc.exe',
    ]
    
    for path in windows_paths:
        if os.path.exists(path):
            return path
    
    return None

def parse_output(output):
    # Parse MiniZinc output
    schedule = []
    for line in output.split('\n'):
        if line.startswith('Week ') and ':' in line:
            parts = line.split(':')
            if len(parts) >= 2:
                games_str = parts[1].strip()
                games = []
                for game in games_str.split('    '):
                    if 'vs' in game:
                        teams = game.strip().split(' vs ')
                        if len(teams) == 2:
                            games.append([int(teams[0]), int(teams[1])])
                if games:
                    schedule.append(games)
    
    if not schedule:
        return []
    
    num_periods = len(schedule[0])
    flipped = []
    for p in range(num_periods):
        flipped.append([schedule[w][p] for w in range(len(schedule))])
    
    return flipped

def run_model(n, solver, model_file, timeout=TIMEOUT):
    # Run MiniZinc model and return results
    script_dir = Path(__file__).parent
    model_path = script_dir / model_file
    
    if not model_path.exists():
        print(f"ERROR: {model_file} not found!")
        return {'time': 300, 'optimal': False, 'obj': None, 'sol': []}
    
    minizinc = find_minizinc()
    if not minizinc:
        print("ERROR: MiniZinc not found!")
        return {'time': 300, 'optimal': False, 'obj': None, 'sol': []}
    
    cmd = [minizinc, '--solver', solver, '--time-limit', str(timeout * 1000), '-D', f'n={n}', str(model_path)]
    
    start = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 10)
        elapsed = time.time() - start
        
        schedule = parse_output(result.stdout)
        
        if schedule:
            return {'time': int(elapsed), 'optimal': True, 'obj': None, 'sol': schedule}
        else:
            return {'time': 300, 'optimal': False, 'obj': None, 'sol': []}
    except:
        return {'time': 300, 'optimal': False, 'obj': None, 'sol': []}

def main():
    script_dir = Path(__file__).parent
    output_dir = (script_dir / '..' / '..' / 'res' / 'CP').resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("CP EXPERIMENTS")
    print("=" * 70)
    
    total = len(INSTANCES) * len(EXPERIMENTS)
    current = 0
    
    for n in INSTANCES:
        print(f"\nInstance n={n}")
        print("-" * 70)
        
        results = {}
        
        for solver, model_file, approach_name in EXPERIMENTS:
            current += 1
            print(f"[{current}/{total}] {approach_name}...", end=' ', flush=True)
            
            result = run_model(n, solver, model_file)
            
            if result['optimal']:
                print(f"{result['time']}s")
            else:
                print("Failed")
            
            results[approach_name] = result
        
        output_file = output_dir / f'{n}.json'
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Saved: {output_file}")
    
    print("\n" + "=" * 70)
    print("CP COMPLETE - Validate with: python check_solution.py res/CP")
    print("=" * 70)

if __name__ == '__main__':
    main()