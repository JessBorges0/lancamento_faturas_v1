pipeline {
    agent any
    
    stages {
        stage('Setup Python Virtual Environment') {
            steps {
                bat 'python -m venv venv'
                bat '%WORKSPACE%\\venv\\Scripts\\pip install -r requirements.txt'
            }
        }
        stage('Successfully Installed Playwright') {
            steps {
                echo 'OK'
            }
        }
    }
}
