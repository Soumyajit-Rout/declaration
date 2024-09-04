pipeline {
    agent any
    environment {
        SONARQUBE_TOKEN = credentials('sonarqube')
    }

    stages {
        stage('Setup Python Virtual ENV') {
            steps {
                script {
                    def setupLog = sh(script: '''
                    chmod u+x env.sh
                    ./env.sh 2>&1
                    ''', returnStdout: true).trim()
                    echo setupLog
                    currentBuild.description = (currentBuild.description ?: "") + "\n" + setupLog
                }
            }
        }
        stage('Gunicorn Setup') {
            steps {
                script {
                    def gunicornLog = sh(script: '''
                    chmod u+x gunicorn.sh
                    ./gunicorn.sh 2>&1
                    ''', returnStdout: true).trim()
                    echo gunicornLog
                    currentBuild.description = currentBuild.description + "\n" + gunicornLog
                }
            }
        }
        stage('NGINX Setup') {
            steps {
                script {
                    def nginxLog = sh(script: '''
                    chmod u+x nginx.sh
                    ./nginx.sh 2>&1
                    ''', returnStdout: true).trim()
                    echo nginxLog
                    currentBuild.description = currentBuild.description + "\n" + nginxLog
                }
            }
        }
        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'SonarQube Scanner'
                    withSonarQubeEnv('SonarQube Server') {
                        sh(script: """
                        ${scannerHome}/bin/sonar-scanner -Dsonar.projectKey=declaration-dev-server \
                        -Dsonar.sources=. -Dsonar.host.url=http://54.147.128.77:9000 -Dsonar.login=${SONARQUBE_TOKEN} 2>&1
                        """)
                        // SonarQube logs are not appended to currentBuild.description
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
                def pipelineStatus = currentBuild.result ?: 'SUCCESS'
                def bannerColor = pipelineStatus.toUpperCase() == 'SUCCESS' ? 'green' : 'red'

                // Capture the final log output from currentBuild.description excluding SonarQube logs
                def finalLog = currentBuild.description ?: "No logs available."

                // Email body with styled log
                def body = """
                    <html>
                        <body>
                            <div style="border: 4px solid ${bannerColor}; padding: 10px;">
                                <h2>${jobName} - Build ${buildNumber}</h2>
                                <div style="background-color: ${bannerColor}; padding: 10px;">
                                    <h3 style="color: white;">Pipeline Status: ${pipelineStatus.toUpperCase()}</h3>
                                </div>
                                <p>Please find the build log details below:</p>
                                <pre style="background-color: black; color: white; padding: 10px; border-radius: 5px; font-family: 'Courier New', Courier, monospace; font-size: 14px;">${finalLog}</pre>
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
                    mimeType: 'text/html'
                )
            }
        }
    }
}
