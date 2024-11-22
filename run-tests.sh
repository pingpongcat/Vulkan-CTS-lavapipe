#!/bin/bash

# Default modules list
all_modules=("api" "binding_model" "clipping" "compute" "conditional_descriptor_indexing" \
"conditional_rendering" "depth" "device_group" "dgc" "draw" "drm_format_modifiers" \
"dynamic_rendering" "dynamic_state" "fragment_operations" "fragment_shader_interlock" \
"fragment_shading_barycentric" "fragment_shading_rate" "geometry" "glsl" "graphicsfuzz" \
"image" "imageless_framebuffer" "info" "memory" "memory_model" "mesh_shader" "multiview" \
"pipeline" "protected_memory" "query_pool" "rasterization" "ray_query" "ray_tracing_pipeline" \
"reconvergence" "renderpass" "renderpass2" "robustness" "shader_object" "sparse_resources" \
"spirv_assembly" "ssbo" "subgroups" "synchronization" "synchronization2" "tessellation" \
"texture" "transform_feedback" "ubo" "video" "wsi" "ycbcr")

# Function to show usage
show_usage() {
    echo "Usage: $0 [-m|--modules <module_list>] [-s|--single-test <test_name>]"
    echo "  -m, --modules       Specify space-separated list of modules to test (e.g., 'api draw')"
    echo "  -s, --single-test   Run a single test case (e.g., 'dEQP-VK.info.device')"
    echo "  -h, --help         Show this help message"
    exit 1
}

# Parse command line arguments
MODULES_TO_TEST=()
SINGLE_TEST=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--modules)
            read -ra MODULES_TO_TEST <<< "$2"
            shift 2
            ;;
        -s|--single-test)
            SINGLE_TEST="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            ;;
    esac
done

# If no modules specified and no single test, use all modules
if [ -z "$SINGLE_TEST" ] && [ ${#MODULES_TO_TEST[@]} -eq 0 ]; then
    MODULES_TO_TEST=("${all_modules[@]}")
fi

# Start Xvfb
Xvfb :99 -screen 0 1280x1024x24 &
sleep 1  # Give Xvfb a moment to start

cd /build/VK-GL-CTS/build/external/vulkancts/modules/vulkan

# Run single test if specified
if [ ! -z "$SINGLE_TEST" ]; then
    echo "Running single test: $SINGLE_TEST"
    ./deqp-vk -n "$SINGLE_TEST" \
              --deqp-log-images=disable \
              --deqp-log-shader-sources=disable \
              > "/build/results/single_test.txt" 2>&1
    exit
fi

# Run tests for specified modules
for module in "${MODULES_TO_TEST[@]}"; do
    if [[ " ${all_modules[@]} " =~ " ${module} " ]]; then
        echo "Testing module: $module"
        ./deqp-vk -n "dEQP-VK.$module.*" \
                  --deqp-log-images=disable \
                  --deqp-log-shader-sources=disable \
                  > "/build/results/lava_${module}.txt" 2>&1 || true
    else
        echo "Warning: Unknown module '$module' - skipping"
    fi
done
EOL
