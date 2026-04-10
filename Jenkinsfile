pipeline {
    agent {
        docker {
            image 'python:3.11-slim'
            args '--user root'
        }
    }

    stages {
        stage('Install') {
            steps {
                sh '''
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Lint') {
            steps {
                sh '''
                    flake8 app tests --max-line-length=100 --exclude=__init__.py
                    pylint app > pylint-report.txt || true
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                sh '''
                    pytest tests/unit -v --junitxml=junit-unit.xml --no-cov
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
                    pytest tests/integration -v --junitxml=junit-integration.xml --no-cov
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
                    pytest tests --cov=app --cov-report=term-missing --cov-report=xml:coverage.xml --junitxml=junit-report.xml
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
        always { echo 'Pipeline terminé' }
        success { echo 'Pipeline ShopFlow réussi' }
        failure { echo 'Pipeline ShopFlow échoué' }
    }
}