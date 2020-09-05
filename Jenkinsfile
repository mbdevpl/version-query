pipeline {
  agent none
  stages {
    stage('Test') {
      agent { label 'x86_64 && gpu && pgi' }
      steps {
        sh "python3 -m coverage run --branch --source . -m unittest -v"
      }
    }
  }
}
