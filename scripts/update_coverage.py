#!/usr/bin/env python3
import json
import os
import sys

# Paths to coverage files
BASH_COVERAGE_PATH = "coverage/bash/bats.e38fe61c8733e2cd/coverage.json"
PYTHON_COVERAGE_PATH = "coverage/python/coverage.json"

def load_bash_coverage():
    # Bash (kcov) output structure:
    # { "covered_lines": 545, "total_lines": 616, "percent_covered": "88.47" }
    # Note: The path might vary slightly based on kcov version/hash, so we search for it.
    base_dir = "coverage/bash"
    if not os.path.exists(base_dir):
        print(f"Warning: {base_dir} not found.")
        return 0, 0

    # Find the json file in subdirectories
    for root, dirs, files in os.walk(base_dir):
        if "coverage.json" in files:
            with open(os.path.join(root, "coverage.json"), 'r') as f:
                data = json.load(f)
                return int(data['covered_lines']), int(data['total_lines'])
    
    print("Warning: Bash coverage.json not found.")
    return 0, 0

def load_python_coverage():
    # Python (pytest-cov) output structure (summary object):
    # { "totals": { "covered_lines": 397, "num_statements": 431, "percent_covered": 92.11 } }
    if not os.path.exists(PYTHON_COVERAGE_PATH):
        print(f"Warning: {PYTHON_COVERAGE_PATH} not found.")
        return 0, 0

    with open(PYTHON_COVERAGE_PATH, 'r') as f:
        data = json.load(f)
        # pytest-cov json uses 'covered_lines' and 'num_statements' (or similar)
        # Structure varies by version, let's inspect typical output
        # Typically: data['totals']['covered_lines'] and data['totals']['num_statements']
        totals = data.get('totals', {})
        return int(totals.get('covered_lines', 0)), int(totals.get('num_statements', 0))

def get_color(coverage):
    if coverage >= 80:
        return "brightgreen"
    elif coverage >= 70:
        return "yellow"
    else:
        return "red"

def update_coverage_json(coverage):
    color = get_color(coverage)
    data = {
        "schemaVersion": 1,
        "label": "Coverage",
        "message": f"{coverage:.2f}%",
        "color": color
    }
    
    with open("coverage.json", "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Generated coverage.json with coverage: {coverage:.2f}% ({color})")
    
    if 'GITHUB_OUTPUT' in os.environ:
        with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
            print(f"coverage={coverage:.2f}", file=fh)

def main():
    print(">> Computing Global Coverage...")
    bash_covered, bash_total = load_bash_coverage()
    py_covered, py_total = load_python_coverage()

    total_covered = bash_covered + py_covered
    total_lines = bash_total + py_total

    if total_lines == 0:
        print("Error: No coverage data found.")
        sys.exit(1)

    global_coverage = (total_covered / total_lines) * 100
    print(f"Bash:   {bash_covered}/{bash_total}")
    print(f"Python: {py_covered}/{py_total}")
    print(f"Total:  {total_covered}/{total_lines} = {global_coverage:.2f}%")

    update_coverage_json(global_coverage)

if __name__ == "__main__":
    main()
