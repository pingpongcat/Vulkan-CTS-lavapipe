#!/bin/bash

# Script to help with Jenkins setup for Vulkan CTS with Lavapipe
# This script checks for required plugins and provides instructions

echo "Checking for required Jenkins plugins..."

# Help text explaining how to use the script
cat << EOF
==========================================================
Vulkan CTS Lavapipe Jenkins Setup Helper
==========================================================

This script will help you set up Jenkins for running the Vulkan CTS
validation test pipeline. Before running the pipeline, ensure:

1. You have installed required Jenkins plugins:
   - Pipeline
   - Docker
   - Allure

2. You have Docker installed and usable by Jenkins

3. You have configured a Jenkins credential if you need to push Docker images
   to a private registry

==========================================================
EOF

# Check if jenkins-cli.jar is available
if [ ! -f "jenkins-cli.jar" ]; then
    echo "jenkins-cli.jar not found. You'll need to download it from your Jenkins server."
    echo "Visit: http://your-jenkins-server/jnlpJars/jenkins-cli.jar"
    echo "Run: wget http://your-jenkins-server/jnlpJars/jenkins-cli.jar"
fi

# Check if required commands exist
missing_commands=()
for cmd in docker python3 java; do
    if ! command -v $cmd &> /dev/null; then
        missing_commands+=($cmd)
    fi
done

if [ ${#missing_commands[@]} -gt 0 ]; then
    echo "WARNING: Some required commands are missing:"
    for cmd in "${missing_commands[@]}"; do
        echo "  - $cmd"
    done
    echo "Please install them before proceeding."
fi

# Check if Allure is installed
if ! command -v allure &> /dev/null; then
    echo "Allure CLI not found. While optional, it's useful for viewing reports locally."
    echo "Install with: pip install allure-commandline"
    echo "Or visit: https://docs.qameta.io/allure/#_installing_a_commandline"
fi

echo -e "\nSetup Instructions for Jenkins Pipeline:\n"

cat << EOF
1. Create a new Jenkins Pipeline job:
   - Go to Jenkins > New Item > Pipeline
   - Enter a name and click OK

2. Configure repository:
   - In Pipeline section, select "Pipeline script from SCM"
   - Select "Git" as SCM
   - Enter repository URL: https://github.com/your-username/Vulkan-CTS-lavapipe.git
   - Specify your branch (e.g., "main")

3. Configure Allure Reports:
   - In job configuration, scroll to "Post-build Actions"
   - Add "Allure Report" action
   - Set Results Path to "allure-results"

4. Configure build triggers as needed

5. Save the job configuration

6. Run the pipeline!

Note: The first run may take longer as it builds the Docker image.
EOF

# Create directories for Allure reports if they don't exist
mkdir -p "allure-results"

echo -e "\nScript directory structure is ready."
echo "You can now set up your Jenkins pipeline using the Jenkinsfile in this repository."