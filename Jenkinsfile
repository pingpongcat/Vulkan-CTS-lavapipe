pipeline {
    agent any
    
    options {
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 3, unit: 'HOURS')
    }
    
    environment {
        DOCKER_IMAGE = 'vulkan-cts-lavapipe'
        DOCKER_TAG = "${env.BUILD_NUMBER}"
    }
    
    stages {
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .'
            }
        }
        
        stage('Run Tests in Parallel') {
            steps {
                script {
                    def modules = ['api', 'binding_model', 'clipping', 'compute', 'conditional_descriptor_indexing',
                                 'conditional_rendering', 'depth', 'device_group', 'dgc', 'draw', 'drm_format_modifiers',
                                 'dynamic_rendering', 'dynamic_state', 'fragment_operations', 'fragment_shader_interlock',
                                 'fragment_shading_barycentric', 'fragment_shading_rate', 'geometry', 'glsl', 'graphicsfuzz',
                                 'image', 'imageless_framebuffer', 'info', 'memory', 'memory_model', 'mesh_shader', 'multiview',
                                 'pipeline', 'protected_memory', 'query_pool', 'rasterization', 'ray_query', 'ray_tracing_pipeline',
                                 'reconvergence', 'renderpass', 'renderpass2', 'robustness', 'shader_object', 'sparse_resources',
                                 'spirv_assembly', 'ssbo', 'subgroups', 'synchronization', 'synchronization2', 'tessellation',
                                 'texture', 'transform_feedback', 'ubo', 'video', 'wsi', 'ycbcr']
                    
                    // Create a directory to store test results
                    sh 'mkdir -p test-results'
                    
                    // Run each module test in parallel
                    def parallelSteps = modules.collectEntries { module ->
                        ["${module}" : {
                            sh """
                            docker run --rm \
                                -v \${WORKSPACE}/test-results:/build/results \
                                \${DOCKER_IMAGE}:\${DOCKER_TAG} \
                                /build/run-tests.sh -m ${module}
                            """
                        }]
                    }
                    
                    parallel parallelSteps
                }
            }
        }
        
        stage('Process Results') {
            steps {
                sh 'python3 scripts/parse_test_results.py --results-dir test-results --whitelist vk-vvl-whitelist.json --output-json allure-results/validation-results.json'
                sh 'python3 scripts/generate_allure_reports.py --input-json allure-results/validation-results.json --output-dir allure-results'
            }
        }
        
        stage('Publish Reports') {
            steps {
                allure([
                    includeProperties: false,
                    jdk: '',
                    properties: [],
                    reportBuildPolicy: 'ALWAYS',
                    results: [[path: 'allure-results']]
                ])
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
    }
}