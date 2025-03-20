# Start with Ubuntu 22.04.5 LTS
FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Set environment variables
ENV XDG_RUNTIME_DIR=/tmp/runtime-dir
ENV DISPLAY=:99
ENV VK_INSTANCE_LAYERS=VK_LAYER_KHRONOS_validation
ENV VK_LAYER_SETTINGS_PATH=/etc/vulkan

# Install minimal dependencies needed for Vulkan CTS
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    python3 \
    python3-pip \
    cmake \
    ninja-build \
    pkg-config \
    xvfb \
    libgl-dev \
    libx11-dev \
    libglu1-mesa-dev \
    libvulkan-dev \
    vulkan-tools \
    vulkan-validationlayers \
    vulkan-validationlayers-dev \
    mesa-vulkan-drivers \
    mesa-common-dev \
    parallel \
    && rm -rf /var/lib/apt/lists/*

# Create vulkan configuration directory
RUN mkdir -p /etc/vulkan

# Copy validation layer settings
COPY vk_layer_settings.txt /etc/vulkan/

# Set working directory
WORKDIR /build

# Create results directory
RUN mkdir -p /build/results
