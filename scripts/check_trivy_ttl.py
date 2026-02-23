#!/usr/bin/env python3
import sys
import datetime
import re

def main():
    today = datetime.date.today()
    error_count = 0
    trivyignore_path = ".trivyignore"
    
    # Regex for 'exp:YYYY-MM-DD'
    ttl_pattern = re.compile(r"exp:(\d{4}-\d{2}-\d{2})")
    
    # Simple trackers for Risk and Reason (preceding comments)
    last_risk = ""
    last_reason = ""
    MIN_DESC_LEN = 15

    try:
        with open(trivyignore_path, "r") as f:
            for line_num, line in enumerate(f, 1):
                clean_line = line.strip()
                
                # Track Risk/Reason in comments
                if clean_line.startswith("# Risk:"):
                    last_risk = clean_line.replace("# Risk:", "").strip()
                elif clean_line.startswith("# Reason:"):
                    last_reason = clean_line.replace("# Reason:", "").strip()
                
                if not clean_line or clean_line.startswith("#"):
                    continue
                
                # We found a CVE entry
                match = ttl_pattern.search(clean_line)
                if match:
                    # 1. Check Expiry
                    expiry_date_str = match.group(1)
                    expiry_date = datetime.date.fromisoformat(expiry_date_str)
                    
                    if expiry_date < today:
                        print(f"ERROR: Entry '{clean_line}' on line {line_num} has expired (expiry was {expiry_date}).")
                        error_count += 1
                    
                    # 2. Check Description Quality (Audit Prevention)
                    if len(last_risk) < MIN_DESC_LEN:
                        print(f"ERROR: Entry '{clean_line}' on line {line_num} has insufficient 'Risk' description ({len(last_risk)} chars). Min: {MIN_DESC_LEN}.")
                        error_count += 1
                    if len(last_reason) < MIN_DESC_LEN:
                        print(f"ERROR: Entry '{clean_line}' on line {line_num} has insufficient 'Reason' description ({len(last_reason)} chars). Min: {MIN_DESC_LEN}.")
                        error_count += 1
                    
                    # Reset trackers for next CVE
                    last_risk = ""
                    last_reason = ""
                else:
                    print(f"WARNING: Entry '{clean_line}' on line {line_num} does not have an 'exp:YYYY-MM-DD' tag.")
    
    except FileNotFoundError:
        print(f"ERROR: {trivyignore_path} not found.")
        sys.exit(1)

    if error_count > 0:
        print(f"FAILED: {error_count} quality/policy errors found in {trivyignore_path}.")
        sys.exit(1)
    
    print(f"SUCCESS: All entries in {trivyignore_path} meet policy requirements.")
    sys.exit(0)

if __name__ == "__main__":
    main()
