pipeline {
  agent any
  stages {
    stage('testing') {
      steps {
        sh '''#!/bin/bash

PYENV_HOME=$WORKSPACE/.pyenv/
virtualenv -p python3 --no-site-packages $PYENV_HOME
source $PYENV_HOME/bin/activate
pip install -U pytest
pip install -r requirements.txt
py.test . 
deactivate'''
        sh 'rm -rdf $WORKSPACE/.pyenv'
      }
    }
    stage('sls deploy - test') {
      steps {
        sh '''npm install serverless-domain-manager
npm install serverless-python-requirements
sls deploy --stage test'''
        echo 'test deployment succeded'
      }
    }
    stage('sls deploy - prod') {
      steps {
        sh 'sls deploy --stage prod'
      }
    }
  }
}