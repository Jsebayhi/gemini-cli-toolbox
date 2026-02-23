#!/usr/bin/env python3
import sys
import datetime
import re

def main():
    today = datetime.date.today()
    expired_count = 0
    trivyignore_path = ".trivyignore"
    
    # Regex for 'exp:YYYY-MM-DD'
    ttl_pattern = re.compile(r"exp:(\d{4}-\d{2}-\d{2})")
    
    try:
        with open(trivyignore_path, "r") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                
                match = ttl_pattern.search(line)
                if match:
                    expiry_date_str = match.group(1)
                    expiry_date = datetime.date.fromisoformat(expiry_date_str)
                    
                    if expiry_date < today:
                        print(f"ERROR: Entry '{line}' on line {line_num} has expired (expiry was {expiry_date}).")
                        expired_count += 1
                else:
                    # Optional: warn if an entry does not have a TTL?
                    # The ADR says "All suppressions MUST use the native 'exp:YYYY-MM-DD' syntax".
                    print(f"WARNING: Entry '{line}' on line {line_num} does not have an 'exp:YYYY-MM-DD' tag.")
    
    except FileNotFoundError:
        print(f"ERROR: {trivyignore_path} not found.")
        sys.exit(1)

    if expired_count > 0:
        print(f"FAILED: {expired_count} expired entries found in {trivyignore_path}.")
        sys.exit(1)
    
    print(f"SUCCESS: No expired entries found in {trivyignore_path}.")
    sys.exit(0)

if __name__ == "__main__":
    main()
