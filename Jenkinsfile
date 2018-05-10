pipeline {
  agent any
  stages {
    stage('setup) {
      steps {
        sh 'pip install virtualenv'
      }
    }
    stage('testing') {
      steps {
        sh '''PYENV_HOME=$WORKSPACE/.pyenv/
virtualenv --no-site-packages $PYENV_HOME
source $PYENV_HOME/bin/activate
pip install -U pytest
pip install -r requirements.txt
py.test . 
deactivate'''
      }
    }
    stage('sls deploy - test') {
      steps {
        sh 'sls deploy --stage test'
      }
    }
    stage('sls deploy - prod') {
      steps {
        sh 'sls deploy --stage prod'
      }
    }
  }
}