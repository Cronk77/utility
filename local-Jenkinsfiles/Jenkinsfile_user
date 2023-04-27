pipeline{
    agent any    
    tools{
        maven "Maven"
    }
    stages{
        stage('Checkout'){
            steps{
                checkout scm
            }
        }
        stage("Test"){
            steps{
                sh "mvn clean test"  
            }
        }
         stage('SonarQube Analysis') {
            steps{
                withSonarQubeEnv('aline-sonarqube-server') {
                    sh "mvn clean verify sonar:sonar -Dsonar.projectKey=User-Microservice-Root-Project"
                }
            }
        }
        stage('Quality Gate'){
            steps{
                waitForQualityGate abortPipeline: true
            }
        }
        stage("Build"){
            steps{
                sh "mvn -Dmaven.test.failure.ignore=true clean package"
            }
        }
    }
    post{
        always{
            archiveArtifacts artifacts: 'user-microservice/target/*.jar', onlyIfSuccessful: true
        }
    }
}