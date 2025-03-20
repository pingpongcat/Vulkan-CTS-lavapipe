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

# Configuration
RESULTS_DIR="/build/results"
DISPLAY_NUM=99
TEST_BINARY="./deqp-vk"

# Function to show usage
show_usage() {
    echo "Usage: $0 [-m|--modules <module_list>] [-s|--single-test <test_name>]"
    echo "  -m, --modules       Specify space-separated list of modules to test (e.g., 'api draw')"
    echo "  -s, --single-test   Run a single test case (e.g., 'dEQP-VK.info.device')"
    echo "  -h, --help          Show this help message"
    exit 1
}

# Clean up function
cleanup() {
    echo "Cleaning up..."
    if [ -f "/tmp/.X${DISPLAY_NUM}-lock" ]; then
        rm -f "/tmp/.X${DISPLAY_NUM}-lock"
    fi
    pkill -f "Xvfb :${DISPLAY_NUM}"
    exit
}

trap cleanup EXIT

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

# Ensure results directory exists
mkdir -p "$RESULTS_DIR"

# Clean previous results
echo "Cleaning previous test results..."
rm -f "$RESULTS_DIR"/*.txt
rm -f "$RESULTS_DIR"/*.qpa
rm -f "$RESULTS_DIR"/*.bin

# Clean up any existing X server
if [ -f "/tmp/.X${DISPLAY_NUM}-lock" ]; then
    rm -f "/tmp/.X${DISPLAY_NUM}-lock"
fi
pkill -f "Xvfb :${DISPLAY_NUM}" || true

# Start Xvfb
Xvfb :${DISPLAY_NUM} -screen 0 1280x1024x24 &
sleep 2  # Give Xvfb more time to start

cd /build/VK-GL-CTS/build/external/vulkancts/modules/vulkan

# Function to run tests for a module
run_tests() {
    local module="$1"
    
    echo "Testing module $module..."
    
    "$TEST_BINARY" \
        --deqp-log-images=disable \
        --deqp-log-shader-sources=disable \
        --deqp-log-flush=disable \
        --deqp-log-filename="$RESULTS_DIR/${module}.qpa" \
        --deqp-shadercache-filename="$RESULTS_DIR/shadercache_${module}.bin" \
        -n "dEQP-VK.${module}.*" \
        > "$RESULTS_DIR/${module}.txt" 2>&1
        
    echo "Completed testing module $module"
}

# Run single test if specified
if [ ! -z "$SINGLE_TEST" ]; then
    echo "Running single test: $SINGLE_TEST"
    "$TEST_BINARY" -n "$SINGLE_TEST" \
        --deqp-log-images=disable \
        --deqp-log-shader-sources=disable \
        > "$RESULTS_DIR/single_test.txt" 2>&1
    exit
fi

# Run tests for specified modules sequentially
for module in "${MODULES_TO_TEST[@]}"; do
    if [[ " ${all_modules[@]} " =~ " ${module} " ]]; then
        run_tests "$module"
    else
        echo "Warning: Unknown module '$module' - skipping"
    fi
done

echo "All tests completed successfully"
