pipeline {
    agent any

    stages {
        stage('Install') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    python -m pip install --upgrade pip
                    python -m pip install -r requirements.txt
                '''
            }
        }

        stage('Lint') {
            steps {
                sh '''
                    . .venv/bin/activate
                    python3 -m flake8 app tests --max-line-length=100 --exclude=__init__.py
                    python3 -m pylint app > pylint-report.txt || true
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                sh '''
                    . .venv/bin/activate
                    python -m pytest tests/unit -v --junitxml=junit-unit.xml --no-cov
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
                    . .venv/bin/activate
                    python -m pytest tests/integration -v --junitxml=junit-integration.xml --no-cov
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
                    . .venv/bin/activate
                    python -m pytest tests --cov=app --cov-report=term-missing --cov-report=xml:coverage.xml --junitxml=junit-report.xml
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