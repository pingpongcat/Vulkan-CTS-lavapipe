import re
import json
import sys
from collections import defaultdict
from datetime import datetime

def parse_vulkan_log(log_file_path):
    """
    Parse a Vulkan CTS log file and generate Allure-compatible JSON output.
    """
    with open(log_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract test cases and their results
    test_pattern = r'Test case \'([\w\.-]+)\'\.\.(?:\s+(.+?)(?=\s+Test case|\s+DONE!|$))'
    test_matches = re.findall(test_pattern, content, re.DOTALL)
    
    # Pattern to extract error IDs from error messages
    error_pattern = r'(VUID-[a-zA-Z0-9_-]+)(?:\(ERROR / SPEC\))?: msgNum: .+? - Validation Error:'
    
    # Statistics
    total_tests = len(test_matches)
    tests_with_errors = []
    error_counts = defaultdict(int)
    total_errors = 0
    
    # Process each test case
    test_results = []
    for test_name, test_output in test_matches:
        errors = re.findall(error_pattern, test_output)
        
        # If there are errors in this test
        if errors:
            tests_with_errors.append(test_name)
            total_errors += len(errors)
            
            # Count each type of error
            for error_id in errors:
                error_counts[error_id] += 1
            
            # Extract specific error details for each error
            error_details = []
            for error_id in set(errors):  # Use set to avoid duplicates
                count = errors.count(error_id)
                # Try to extract the error message
                msg_pattern = f"{error_id}(?:\\(ERROR / SPEC\\))?: msgNum: .+? - Validation Error:[^\\n]+(.*?)(?=\\n\\s+The Vulkan spec states:|$)"
                msg_matches = re.findall(msg_pattern, test_output, re.DOTALL)
                error_message = msg_matches[0].strip() if msg_matches else "No detailed message available"
                
                error_details.append({
                    "error_id": error_id,
                    "count": count,
                    "message": error_message
                })
            
            # Create a test result with error information
            test_results.append({
                "name": test_name,
                "status": "passed" if "Pass" in test_output else "failed",
                "has_errors": True,
                "error_count": len(errors),
                "errors": error_details
            })
        else:
            # Test without errors
            test_results.append({
                "name": test_name,
                "status": "passed" if "Pass" in test_output else (
                    "skipped" if "NotSupported" in test_output else "failed"),
                "has_errors": False,
                "error_count": 0,
                "errors": []
            })
    
    # Extract summary statistics
    summary_pattern = r'Test run totals:\s+Passed:\s+(\d+)/(\d+) \([\d\.]+%\)\s+Failed:\s+(\d+)/(\d+) \([\d\.]+%\)\s+Not supported:\s+(\d+)/(\d+) \([\d\.]+%\)'
    summary_match = re.search(summary_pattern, content)
    
    summary = {}
    if summary_match:
        summary = {
            "passed": int(summary_match.group(1)),
            "total": int(summary_match.group(2)),
            "failed": int(summary_match.group(3)),
            "not_supported": int(summary_match.group(5))
        }
    
    # Create the final JSON structure
    result = {
        "timestamp": datetime.now().isoformat(),
        "summary": summary,
        "statistics": {
            "total_tests": total_tests,
            "tests_with_errors": len(tests_with_errors),
            "total_errors": total_errors,
            "error_types": len(error_counts)
        },
        "error_counts": [{"id": error_id, "count": count} for error_id, count in error_counts.items()],
        "tests": test_results
    }
    
    return result

def generate_allure_json(parsed_data, output_dir):
    """
    Generate Allure-compatible JSON files from the parsed data
    """
    import os
    import uuid
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Write each test as a separate Allure result file
    for test in parsed_data["tests"]:
        # Generate a unique UUID for the test result file
        test_uuid = str(uuid.uuid4())
        
        allure_test = {
            "uuid": test_uuid,
            "name": test["name"],
            "status": test["status"],
            "stage": "finished",
            "steps": [],
            "attachments": [],
            "parameters": [],
            "start": 1000000,
            "stop": 1000001,
            "labels": [
                {
                    "name": "suite",
                    "value": "VulkanCTS"
                },
                {
                    "name": "framework",
                    "value": "Vulkan CTS"
                },
                {
                    "name": "testClass",
                    "value": test["name"].split('.')[0] if '.' in test["name"] else "VulkanCTS"
                }
            ]
        }
        
        # Add failure details if the test has errors
        if test["has_errors"]:
            error_messages = []
            for error in test["errors"]:
                error_messages.append(f"{error['error_id']} (occurred {error['count']} times): {error['message']}")
                
                # Add steps for each error
                allure_test["steps"].append({
                    "name": f"Validation Error: {error['error_id']}",
                    "status": "failed",
                    "stage": "finished",
                    "steps": [],
                    "attachments": [],
                    "parameters": [
                        {
                            "name": "count",
                            "value": str(error["count"])
                        },
                        {
                            "name": "message",
                            "value": error["message"]
                        }
                    ]
                })
            
            # Add statusDetails for failed tests
            allure_test["statusDetails"] = {
                "known": False,
                "muted": False,
                "flaky": False,
                "message": f"Test contains {test['error_count']} validation errors",
                "trace": "\n".join(error_messages)
            }
        
        # Write the test result to a JSON file
        result_file = os.path.join(output_dir, f"{test_uuid}-result.json")
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(allure_test, f, indent=2)
    
    # Also write a summary file with statistics
    summary_file = os.path.join(output_dir, "summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        summary_data = {
            "summary": parsed_data["summary"],
            "statistics": parsed_data["statistics"],
            "error_counts": parsed_data["error_counts"]
        }
        json.dump(summary_data, f, indent=2)
        
    print(f"Generated {len(parsed_data['tests'])} Allure result files in {output_dir}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python vulkan_log_parser.py <log_file_path> [output_directory]")
        sys.exit(1)
    
    log_file_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "allure-results"
    
    parsed_data = parse_vulkan_log(log_file_path)
    generate_allure_json(parsed_data, output_dir)
    
    print(f"Parsing complete. Results written to {output_dir}")
    print(f"Total tests: {parsed_data['statistics']['total_tests']}")
    print(f"Tests with errors: {parsed_data['statistics']['tests_with_errors']}")
    print(f"Total errors: {parsed_data['statistics']['total_errors']}")
    print(f"Error types: {parsed_data['statistics']['error_types']}")
    print(f"\nTo generate the Allure report, run:")
    print(f"  allure generate {output_dir} -o allure-report")
    print(f"  allure open allure-report")

if __name__ == "__main__":
    main()
