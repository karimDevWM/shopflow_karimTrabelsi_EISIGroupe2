pipeline {
    agent any

    stages {
        stage('Install') {
            steps {
                sh '''
                    python3 --version || true
                    python --version || true

                    if ! command -v python3 >/dev/null 2>&1; then
                      apt-get update
                      apt-get install -y python3 python3-pip python3-venv
                    fi

                    python3 -m pip install --upgrade pip
                    python3 -m pip install -r requirements.txt
                '''
            }
        }

        stage('Lint') {
            steps {
                sh '''
                    python3 -m flake8 app tests --max-line-length=100 --exclude=__init__.py
                    python3 -m pylint app > pylint-report.txt || true
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                sh '''
                    python3 -m pytest tests/unit -v --junitxml=junit-unit.xml --no-cov
                '''
            }
            post {
                always {
                    junit 'junit-unit.xml'
                }
            }
        }

        stage('Integration Tests') {
            steps {
                sh '''
                    python3 -m pytest tests/integration -v --junitxml=junit-integration.xml --no-cov
                '''
            }
            post {
                always {
                    junit 'junit-integration.xml'
                }
            }
        }

        stage('Coverage') {
            steps {
                sh '''
                    python3 -m pytest tests --cov=app --cov-report=term-missing --cov-report=xml:coverage.xml --junitxml=junit-report.xml
                '''
            }
            post {
                always {
                    junit 'junit-report.xml'
                    archiveArtifacts artifacts: 'coverage.xml,pylint-report.txt,junit-*.xml', allowEmptyArchive: true
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline terminé'
        }
        success {
            echo 'Pipeline ShopFlow réussi'
        }
        failure {
            echo 'Pipeline ShopFlow échoué'
        }
    }
}