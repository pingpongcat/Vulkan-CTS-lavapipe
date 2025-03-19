#!/usr/bin/env python3

import argparse
import json
import os
from datetime import datetime
import uuid

def create_allure_test_result(test_case, error, status="failed"):
    """Create an Allure test result JSON file."""
    result = {
        "name": test_case,
        "status": status,
        "stage": "finished",
        "steps": [],
        "parameters": [],
        "start": datetime.now().timestamp() * 1000,
        "stop": datetime.now().timestamp() * 1000,
        "uuid": str(uuid.uuid4()),
        "historyId": test_case,
        "fullName": test_case,
        "labels": [
            {
                "name": "severity",
                "value": error.get("severity", "normal").lower()
            },
            {
                "name": "module",
                "value": test_case.split('.')[1] if len(test_case.split('.')) > 1 else "unknown"
            }
        ]
    }
    
    # Add failure details
    if status == "failed":
        result["statusDetails"] = {
            "message": error.get("error_id", "Unknown error"),
            "trace": error.get("message", "No message")
        }
    
    return result

def create_allure_category(name, matched_statuses=None):
    """Create an Allure category JSON file."""
    if matched_statuses is None:
        matched_statuses = ["failed"]
        
    return {
        "name": name,
        "matchedStatuses": matched_statuses
    }

def main():
    parser = argparse.ArgumentParser(description="Generate Allure reports from validation results")
    parser.add_argument("--input-json", required=True, help="Path to validation results JSON file")
    parser.add_argument("--output-dir", required=True, help="Directory to output Allure report files")
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load validation results
    with open(args.input_json, 'r') as f:
        results = json.load(f)
    
    # Create module categories
    categories = []
    for module in results.get("errors_by_module", {}).keys():
        categories.append(create_allure_category(module))
    
    # Add severity categories
    categories.append(create_allure_category("ERROR"))
    categories.append(create_allure_category("WARNING"))
    
    # Write categories.json
    with open(os.path.join(args.output_dir, "categories.json"), 'w') as f:
        json.dump(categories, f, indent=2)
    
    # Create environment.properties
    with open(os.path.join(args.output_dir, "environment.properties"), 'w') as f:
        f.write(f"Report.Date={datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total.Errors={results.get('total_errors', 0)}\n")
        f.write(f"Total.Whitelisted={results.get('total_whitelisted', 0)}\n")
    
    # Generate test result files
    test_count = 0
    
    # Process non-whitelisted errors
    for module, errors in results.get("modules", {}).items():
        for error in errors:
            test_case = error.get("test_case", f"unknown-{test_count}")
            test_result = create_allure_test_result(test_case, error, "failed")
            
            # Write test result
            with open(os.path.join(args.output_dir, f"{uuid.uuid4()}-result.json"), 'w') as f:
                json.dump(test_result, f, indent=2)
            
            test_count += 1
    
    # Process whitelisted errors (mark as skipped)
    for error in results.get("whitelisted", []):
        test_case = error.get("test_case", f"whitelisted-{test_count}")
        test_result = create_allure_test_result(test_case, error, "skipped")
        
        # Add whitelisted annotation
        test_result["labels"].append({
            "name": "tag",
            "value": "whitelisted"
        })
        
        # Write test result
        with open(os.path.join(args.output_dir, f"{uuid.uuid4()}-result.json"), 'w') as f:
            json.dump(test_result, f, indent=2)
        
        test_count += 1
    
    # Create summary widget data
    summary = {
        "reportName": "Vulkan CTS Validation Report",
        "statistics": {
            "total": test_count,
            "failed": results.get("total_errors", 0),
            "skipped": results.get("total_whitelisted", 0),
            "passed": 0
        },
        "modules": {
            module: {"failed": count, "total": count} 
            for module, count in results.get("errors_by_module", {}).items()
        }
    }
    
    # Write widgets data
    with open(os.path.join(args.output_dir, "widgets.json"), 'w') as f:
        json.dump({"summary": summary}, f, indent=2)
    
    print(f"Generated Allure reports in {args.output_dir}")
    print(f"Total test cases: {test_count}")

if __name__ == "__main__":
    main()