pipeline {
  agent any
  stages {
    stage('testing') {
      steps {
        sh '''#!/bin/bash

PYENV_HOME=$WORKSPACE/.pyenv/
virtualenv --no-site-packages $PYENV_HOME
source $PYENV_HOME/bin/activate
pip3 install -U pytest
pip3 install -r requirements.txt
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