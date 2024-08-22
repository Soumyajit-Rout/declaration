
pipeline {
    agent any
    environment {
        SONARQUBE_TOKEN = credentials('sonarqube')
    }
    stages {
        stage('Setup Python Virtual ENV') {
            steps {
                script {
                    sh '''
                    chmod u+x env.sh
                    ./env.sh >> build-output.log 2>&1
                    cat build-output.log
                    '''
                }
            }
        }
        stage('Gunicorn Setup') {
            steps {
                script {
                    sh '''
                    chmod u+x gunicorn.sh
                    ./gunicorn.sh >> build-output.log 2>&1
                    cat build-output.log
                    '''
                }
            }
        }
        stage('NGINX Setup') {
            steps {
                script {
                    sh '''
                    chmod u+x nginx.sh
                    ./nginx.sh >> build-output.log 2>&1
                    cat build-output.log
                    '''
                }
            }
        }
        stage('Verify Log File') {
            steps {
                script {
                    sh 'ls -l build-output.log'
                    sh 'cat build-output.log'
                }
            }
        }
        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'SonarQube Scanner' // Adjust to the name of your SonarQube Scanner installation
                    withSonarQubeEnv('SonarQube Server') { // Adjust to the name of your SonarQube server configuration
                        sh "${scannerHome}/bin/sonar-scanner -Dsonar.projectKey=declaration-dev-server -Dsonar.sources=. -Dsonar.host.url=http://54.147.128.77:9000 -Dsonar.login=${SONARQUBE_TOKEN}"
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                def jobName = env.JOB_NAME
                def buildNumber = env.BUILD_NUMBER
                def pipelineStatus = currentBuild.result ?: 'UNKNOWN'
                def bannerColor = pipelineStatus.toUpperCase() == 'SUCCESS' ? 'green' : 'red'

                // Email body
                def body = """
                    <html>
                        <body>
                            <div style="border: 4px solid ${bannerColor}; padding: 10px;">
                                <h2>${jobName} - Build ${buildNumber}</h2>
                                <div style="background-color: ${bannerColor}; padding: 10px;">
                                    <h3 style="color: white;">Pipeline Status: ${pipelineStatus.toUpperCase()}</h3>
                                </div>
                                <p>Please find the build console output attached.</p>
                            </div>
                        </body>
                    </html>
                """

                emailext(
                    subject: "${jobName} - Build ${buildNumber} - ${pipelineStatus.toUpperCase()}",
                    body: body,
                    to: 'sreejesh@finloge.com,soumyarout567@gmail.com',
                    from: 'soumyajit.rout@finloge.com',
                    replyTo: 'soumyajit.rout@finloge.com',
                    attachmentsPattern: 'build-output.log',
                    mimeType: 'text/html'
                )
            }
        }
    }
}
