@Library('shared-lib-two')

//library identifier: 'jenkins-shared-library@master', retriever: modernSCM(
//    [$class: GitSCMSource,
//    remote: 'https-something',
//    credentialsId: 'some-credentials in jenkins'
//  ]
//)

def shouldExecuteOnBranch(branchName) {
    return BRANCH_NAME == branchName
}

def imageTag = "dreg.knust.edu.gh/neo/migrate-client:0.0.1"
pipeline {
    agent any

    stages {
        stage('build-and push docker-image'){
            when {
                expression {
                    shouldExecuteOnBranch("master")
                }
            }
            steps {
                script {
                    buildDockerImage "$imageTag"
                    dockerLogin ("knust-docker-registry", "https://dreg.knust.edu.gh")
                    pushDockerImage "$imageTag"
                }
            }
        }

        stage('deploy-app-to-test-server'){
            when{
                expression {
                    shouldExecuteOnBranch("master")
                }
            }
            steps {
                script {

                    def scriptCmd = "bash ./start-api.sh $imageTag"
                    def testServer = "ubuntu@10.40.1.98"
                    sshagent(['ubuntu']){
                        dockerLogin ("knust-docker-registry", "https://dreg.knust.edu.gh")
                        sh "scp start-api.sh ${testServer}:/home/ubuntu/"
                        sh "scp prod.yaml ${testServer}:/home/ubuntu/"
                        sh "ssh -o StrictHostKeyChecking=no ${testServer} ${scriptCmd}"
                    }
                }
            }
        }

    }
}