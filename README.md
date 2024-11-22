# Vulkan-CTS-lavapipe

Docker environment for running Vulkan Conformance Test Suite (CTS) with LavaPipe software renderer, including Jenkins automation for parallel testing and validation error reporting.

## Prerequisites

- Docker installed on your system
- Git
- ~10GB of free disk space
- For automation: Jenkins server with Docker support and Allure plugin

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/pingpongcat/Vulkan-CTS-lavapipe.git
cd Vulkan-CTS-lavapipe
```

2. Build the Docker image:
```bash
docker build -t vulkan-cts .
```

3. Create a directory for test results:
```bash
mkdir -p results
```

4. Run the container:
```bash
docker run -it --name vulkan-test -v $(pwd)/results:/build/results vulkan-cts
```

## Running Tests

Once inside the container, you can run tests using various options:

1. Run a specific module:
```bash
/build/run-tests.sh --modules "api"
```

2. Run multiple modules:
```bash
/build/run-tests.sh --modules "api draw memory"
```

3. Run a single test:
```bash
/build/run-tests.sh --single-test "dEQP-VK.api.info.device"
```

4. Run in parallel:
```bash
/build/run-tests.sh --modules "api" --parallel 8
```

Test results will be stored in the `results` directory with filenames like `api_0.txt`.

## Jenkins Automation

This repository includes a complete Jenkins pipeline setup for automating:
- Building the Docker image
- Running all test modules in parallel
- Collecting and parsing validation errors
- Generating reports using the Allure plugin
- Filtering whitelisted validation errors

### Jenkins Setup Requirements

- Jenkins server with Docker support
- Jenkins plugins:
  - [Pipeline](https://plugins.jenkins.io/workflow-aggregator/)
  - [Docker](https://plugins.jenkins.io/docker-workflow/)
  - [Allure](https://plugins.jenkins.io/allure-jenkins-plugin/)

### Configuring the Pipeline

1. Create a new Jenkins Pipeline job
2. Set the pipeline to use SCM and point to this repository
3. Configure the pipeline to use the Jenkinsfile in the repository root

### Validation Error Whitelist

The `vk-vvl-whitelist.json` file defines patterns for test cases and validation errors that should be ignored in reports. The format is:

```json
{
  "path": "dEQP-VK.dynamic_rendering.*.unused_attachments.*",
  "message": "Undefined-Value-ShaderInputNotProduced-DynamicRendering",
  "description": "Warning about attachments not being written in FS, however, this behavior is intentional."
}
```

### Report Generation

The scripts in the `scripts/` directory process test results and generate Allure-compatible reports:

```bash
# Parse test results
python3 scripts/parse_test_results.py \
  --results-dir results \
  --whitelist vk-vvl-whitelist.json \
  --output-json allure-results/validation-results.json

# Generate Allure reports
python3 scripts/generate_allure_reports.py \
  --input-json allure-results/validation-results.json \
  --output-dir allure-results
```

## Available Test Modules

- api
- binding_model
- clipping
- compute
- conditional_descriptor_indexing
- conditional_rendering
- depth
- device_group
- dgc
- draw
- drm_format_modifiers
- dynamic_rendering
- dynamic_state
- fragment_operations
- fragment_shader_interlock
- fragment_shading_barycentric
- fragment_shading_rate
- geometry
- glsl
- graphicsfuzz
- image
- imageless_framebuffer
- info
- memory
- memory_model
- mesh_shader
- multiview
- pipeline
- protected_memory
- query_pool
- rasterization
- ray_query
- ray_tracing_pipeline
- reconvergence
- renderpass
- renderpass2
- robustness
- shader_object
- sparse_resources
- spirv_assembly
- ssbo
- subgroups
- synchronization
- synchronization2
- tessellation
- texture
- transform_feedback
- ubo
- video
- wsi
- ycbcr

## Notes

- Tests are run with Vulkan Validation Layers enabled
- The environment uses LavaPipe software renderer
- Test results are stored in the mounted results directory
- Each test run creates a new log file, overwriting any previous results for the same module
- The validation error whitelist can be customized to ignore expected validation issues

## Cleaning Up

To remove the container and image:
```bash
# Remove container
docker rm vulkan-test

# Remove image
docker rmi vulkan-cts

# Remove all unused Docker resources
docker system prune
```