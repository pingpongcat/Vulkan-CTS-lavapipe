# Vulkan-CTS-lavapipe

Docker environment for running Vulkan Conformance Test Suite (CTS) with LavaPipe software renderer.

## Prerequisites

- Docker installed on your system
- Git
- ~10GB of free disk space

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

4. Run tests with multiple parallel jobs:
```bash
/build/run-tests.sh --modules "api" --jobs 4
```

Test results will be stored in the `results` directory with filenames like `lava_api.txt`.

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