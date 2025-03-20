pipeline {
    agent any
    
    parameters {
        string(name: 'TEST_GROUP', defaultValue: 'dEQP-VK.info.*', description: 'Vulkan CTS test group to run')
        booleanParam(name: 'GENERATE_REPORT', defaultValue: true, description: 'Generate test report after running')
    }
    
    stages {
        stage('Checkout CI') {
            agent {
                docker { 
                    image 'ubuntu:22.04'
                    args '-v /var/run/docker.sock:/var/run/docker.sock -u root'
                }
            }
            steps {
                sh '''
                apt-get update && apt-get install -y git
                rm -rf ci || true
                git clone https://github.com/pingpongcat/Vulkan-CTS-lavapipe.git ci
                '''
                stash includes: 'ci/**', name: 'ci-repo'
            }
        }
        
        stage('Build Docker Image') {
            steps {
                unstash 'ci-repo'
                sh '''
                cd ci
                docker build -t vulkan-cts-runner .
                '''
            }
        }
        
        stage('Checkout Vulkan CTS') {
            agent {
                docker { 
                    image 'vulkan-cts-runner'
                }
            }
            steps {
                sh '''
                cd /build
                rm -rf VK-GL-CTS || true
                git clone https://github.com/pingpongcat/VK-GL-CTS.git
                cd VK-GL-CTS
                python3 external/fetch_sources.py
                mkdir -p build
                cd build
                cmake -G Ninja -DCMAKE_BUILD_TYPE=Release -DDEQP_TARGET=default ..
                ninja -j$(nproc) deqp-vk
                '''
            }
        }
        
        stage('Run Tests') {
            agent {
                docker { 
                    image 'vulkan-cts-runner'
                }
            }
            steps {
                sh '''
                cd /build/VK-GL-CTS/build/external/vulkancts/modules/vulkan
                mkdir -p /build/results
                ./deqp-vk -n ${TEST_GROUP} --deqp-log-images=disable --deqp-log-shader-sources=disable > /build/results/test_output.txt 2>&1
                '''
                sh 'cat /build/results/test_output.txt'
                stash includes: '/build/results/**', name: 'test-results'
            }
        }
        
        // stage('Parse Results') {
        //     when {
        //         expression { return params.GENERATE_REPORT }
        //     }
        //     agent {
        //         docker { 
        //             image 'vulkan-cts-runner'
        //         }
        //     }
        //     steps {
        //         unstash 'ci-repo'
        //         unstash 'test-results'
        //         sh '''
        //         cd /build
        //         python3 ci/scripts/parse_test_results.py --results-dir=/build/results --whitelist=ci/vk-vvl-whitelist.json --output-json=/build/results/parsed_results.json
        //         '''
        //         archiveArtifacts artifacts: '/build/results/**', fingerprint: true
        //     }
        // }
    }
    
    post {
        always {
            cleanWs()
        }
    }
}
