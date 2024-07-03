pipeline {
    agent any
    stages {
        stage('Setup Python Virtual ENV') {
            steps {
                sh '''
                chmod u+x env.sh
                ./env.sh
                '''
            }
        }
        stage('Gunicorn Setup') {
            steps {
                sh '''
                chmod u+x gunicorn.sh
                ./gunicorn.sh
                '''
            }
        }
        stage('NGINX Setup') {
            steps {
                sh '''
                 chmod u+x nginx.sh
                ./nginx.sh
                '''
            }
        }
    }
}
