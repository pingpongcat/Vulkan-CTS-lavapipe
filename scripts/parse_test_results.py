#!/usr/bin/env python3

import argparse
import json
import os
import re
import glob
from datetime import datetime
from fnmatch import fnmatch

def parse_validation_errors(log_file):
    """Parse validation errors from test log files."""
    errors = []
    test_case = None
    
    with open(log_file, 'r', errors='replace') as f:
        content = f.read()
        
        # Extract the test case name from log file
        # Assume format like "Test case 'dEQP-VK.api.copy_and_blit.core.*'"
        match = re.search(r"Test case '(dEQP-VK\.[^']+)'", content)
        if match:
            test_case = match.group(1)
        
        # Extract validation errors/warnings
        # Example: "VUID-vkCmdBlitImage-srcImage-00233: Validation Error: [ VUID-vkCmdBlitImage-srcImage-00233 ]"
        validation_patterns = [
            r"(VUID-[^:]+): (Validation Error|Warning): \[ ([^\]]+) \][^$]*",
            r"(Undefined-[^:]+): (Validation Error|Warning): \[ ([^\]]+) \][^$]*"
        ]
        
        for pattern in validation_patterns:
            for match in re.finditer(pattern, content):
                error_id = match.group(1)
                severity = "ERROR" if "Error" in match.group(2) else "WARNING"
                message = match.group(0).strip()
                
                errors.append({
                    "test_case": test_case,
                    "error_id": error_id,
                    "severity": severity,
                    "message": message
                })
    
    return errors

def is_whitelisted(error, whitelist):
    """Check if an error is in the whitelist."""
    test_case = error.get("test_case", "")
    error_id = error.get("error_id", "")
    
    for entry in whitelist.get("whitelist", []):
        path_pattern = entry.get("path", "")
        message_pattern = entry.get("message", "")
        
        if fnmatch(test_case, path_pattern) and error_id.startswith(message_pattern):
            return True
    
    return False

def main():
    parser = argparse.ArgumentParser(description="Parse Vulkan validation errors from test logs")
    parser.add_argument("--results-dir", required=True, help="Directory containing test result files")
    parser.add_argument("--whitelist", required=True, help="Path to whitelist JSON file")
    parser.add_argument("--output-json", required=True, help="Path to output JSON file")
    
    args = parser.parse_args()
    
    # Load whitelist
    with open(args.whitelist, 'r') as f:
        whitelist = json.load(f)
    
    # Find all log files
    log_files = glob.glob(os.path.join(args.results_dir, "*.txt"))
    
    all_errors = []
    whitelisted_errors = []
    
    # Process each log file
    for log_file in log_files:
        errors = parse_validation_errors(log_file)
        
        for error in errors:
            if is_whitelisted(error, whitelist):
                error["whitelisted"] = True
                whitelisted_errors.append(error)
            else:
                error["whitelisted"] = False
                all_errors.append(error)
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(args.output_json), exist_ok=True)
    
    # Group errors by module
    grouped_errors = {}
    for error in all_errors:
        test_case = error.get("test_case", "unknown")
        parts = test_case.split('.')
        if len(parts) > 2:
            module = parts[1]  # dEQP-VK.{module}.xxx
        else:
            module = "unknown"
        
        if module not in grouped_errors:
            grouped_errors[module] = []
        
        grouped_errors[module].append(error)
    
    # Create summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_errors": len(all_errors),
        "total_whitelisted": len(whitelisted_errors),
        "errors_by_module": {module: len(errors) for module, errors in grouped_errors.items()},
        "errors_by_severity": {
            "ERROR": len([e for e in all_errors if e["severity"] == "ERROR"]),
            "WARNING": len([e for e in all_errors if e["severity"] == "WARNING"])
        },
        "modules": grouped_errors,
        "whitelisted": whitelisted_errors
    }
    
    # Write to JSON file
    with open(args.output_json, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Found {len(all_errors)} errors, {len(whitelisted_errors)} whitelisted")
    print(f"Results written to {args.output_json}")

if __name__ == "__main__":
    main()