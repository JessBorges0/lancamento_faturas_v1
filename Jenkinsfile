pipeline {
    agent any
 
    stages {
    stage ("Setup Python Virtual Environment") {
        steps {
            bat 'python -m venv venv'
        }
    }
    stage ("Activate Python Virtual Environment") {
        steps {
            bat '%WORKSPACE%\\venv\\Scripts\\pip install -r requirements.txt'
        }
    }
    stage ("Sucessfully Installed Playwright") {
        steps {
            echo 'OK'
        }
    }
}
