#!/usr/bin/env groovy

library 'jenkins-mbdev-pl-libs'

pipeline {

  options {
    ansiColor('xterm')
  }

  environment {
    PYTHON_PACKAGE = 'version-query'
  }

  agent {
    dockerfile {
      additionalBuildArgs '--build-arg USER_ID=${USER_ID} --build-arg GROUP_ID=${GROUP_ID}' \
        + ' --build-arg AUX_GROUP_IDS="${AUX_GROUP_IDS}" --build-arg TIMEZONE=${TIMEZONE}'
      label 'docker'
    }
  }

  stages {

    stage('Lint') {
      environment {
        PYTHON_MODULES = "${env.PYTHON_PACKAGE.replace('-', '_')} test *.py"
      }
      steps {
        sh """#!/usr/bin/env bash
          set -Eeux
          python3 -m pylint ${PYTHON_MODULES} |& tee pylint.log
          echo "\${PIPESTATUS[0]}" | tee pylint_status.log
          python3 -m mypy ${PYTHON_MODULES} |& tee mypy.log
          echo "\${PIPESTATUS[0]}" | tee mypy_status.log
          python3 -m flake518 ${PYTHON_MODULES} |& tee flake518.log
          echo "\${PIPESTATUS[0]}" | tee flake518_status.log
          python3 -m pydocstyle ${PYTHON_MODULES} |& tee pydocstyle.log
          echo "\${PIPESTATUS[0]}" | tee pydocstyle_status.log
        """
      }
    }

    stage('Test') {
      steps {
        sh '''#!/usr/bin/env bash
          set -Eeuxo pipefail
          python3 -m coverage run --branch --source . -m unittest -v
        '''
      }
    }

    stage('Coverage') {
      steps {
        sh '''#!/usr/bin/env bash
          set -Eeux
          python3 -m coverage report --show-missing |& tee coverage.log
          echo "${PIPESTATUS[0]}" | tee coverage_status.log
        '''
        script {
          defaultHandlers.afterPythonBuild()
        }
      }
    }

    stage('Codecov') {
      environment {
        CODECOV_TOKEN = credentials('codecov-token-mbdevpl-version-query')
      }
      steps {
        sh '''#!/usr/bin/env bash
          set -Eeuxo pipefail
          python3 -m codecov --token ${CODECOV_TOKEN}
        '''
      }
    }

    stage('Upload') {
      when {
        anyOf {
          branch 'main'
          buildingTag()
        }
      }
      environment {
        VERSION = sh(script: 'python3 -m version_query --predict .', returnStdout: true).trim()
        PYPI_AUTH = credentials('mbdev-pypi-auth')
        TWINE_USERNAME = "${PYPI_AUTH_USR}"
        TWINE_PASSWORD = "${PYPI_AUTH_PSW}"
        TWINE_REPOSITORY_URL = credentials('mbdev-pypi-public-url')
      }
      steps {
        sh """#!/usr/bin/env bash
          set -Eeuxo pipefail
          python3 -m twine upload \
            dist/${PYTHON_PACKAGE.replace('-', '_')}-${VERSION}-py3-none-any.whl \
            dist/${PYTHON_PACKAGE}-${VERSION}.tar.gz \
            dist/${PYTHON_PACKAGE}-${VERSION}.zip
        """
      }
    }

    stage('Release') {
      when {
        buildingTag()
      }
      environment {
        VERSION = sh(script: 'python3 -m version_query .', returnStdout: true).trim()
      }
      steps {
        script {
          githubUtils.createRelease([
            "dist/${PYTHON_PACKAGE.replace('-', '_')}-${VERSION}-py3-none-any.whl",
            "dist/${PYTHON_PACKAGE}-${VERSION}.tar.gz",
            "dist/${PYTHON_PACKAGE}-${VERSION}.zip"
            ])
        }
      }
    }

  }

  post {
    unsuccessful {
      script {
        defaultHandlers.afterBuildFailed()
      }
    }
    regression {
      script {
        defaultHandlers.afterBuildBroken()
      }
    }
    fixed {
      script {
        defaultHandlers.afterBuildFixed()
      }
    }
  }

}
