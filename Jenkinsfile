pipeline {
    agent any

    parameters {

        choice(
            name: 'ENVIRONMENT',
            choices: ['DEV', 'UAT', 'PRODUCTION'],
            description: 'Select environment'
        )

        choice(
            name: 'ACTION',
            choices: ['DEPLOY', 'ROLLBACK'],
            description: 'Select action'
        )

        string(
            name: 'VERSION',
            defaultValue: '5.0',
            description: 'Application version'
        )

        choice(
            name: 'RUN_TESTS',
            choices: ['YES', 'NO'],
            description: 'Run validation tests'
        )

        choice(
            name: 'PRODUCTION_CONFIRM',
            choices: ['NO', 'YES'],
            description: 'Required for production deployment'
        )
    }

    stages {

        stage('Resolve Configuration') {
            steps {
                script {

                    if (params.ENVIRONMENT == 'DEV') {

                        env.BRANCH = 'develop'
                        env.APP = 'customer--dev--app'
                        env.DB = 'customer--dev--db'
                        env.NETWORK = 'customer--dev--net'
                        env.PORT = '8081'
                        env.IMAGE = 'customer-app-dev'

                    } else if (params.ENVIRONMENT == 'UAT') {

                        env.BRANCH = 'release'
                        env.APP = 'customer--uat--app'
                        env.DB = 'customer--uat--db'
                        env.NETWORK = 'customer--uat--net'
                        env.PORT = '8082'
                        env.IMAGE = 'customer-app-uat'

                    } else if (params.ENVIRONMENT == 'PRODUCTION') {

                        env.BRANCH = 'main'
                        env.APP = 'customer--prod--app'
                        env.DB = 'customer--prod--db'
                        env.NETWORK = 'customer--prod--net'
                        env.PORT = '8083'
                        env.IMAGE = 'customer-app-prod'

                    } else {
                        error "Invalid environment"
                    }

                    echo "============================================"
                    echo "RESOLVED DEPLOYMENT CONFIGURATION"
                    echo "============================================"
                    echo "Environment : ${params.ENVIRONMENT}"
                    echo "Branch      : ${env.BRANCH}"
                    echo "Application : ${env.APP}"
                    echo "Database    : ${env.DB}"
                    echo "Network     : ${env.NETWORK}"
                    echo "Host Port   : ${env.PORT}"
                    echo "Image       : ${env.IMAGE}"
                    echo "Version     : ${params.VERSION}"
                    echo "Action      : ${params.ACTION}"
                    echo "Run Tests   : ${params.RUN_TESTS}"
                    echo "============================================"
                }
            }
        }

        stage('Validate Parameters') {
            steps {
                script {

                    if (
                        params.ENVIRONMENT == 'PRODUCTION' &&
                        params.PRODUCTION_CONFIRM != 'YES'
                    ) {
                        error "Production deployment requires PRODUCTION_CONFIRM = YES"
                    }

                    if (
                        params.ACTION == 'ROLLBACK' &&
                        params.ENVIRONMENT != 'PRODUCTION'
                    ) {
                        error "ROLLBACK is allowed only for PRODUCTION"
                    }
                }
            }
        }

        stage('Checkout Correct Branch') {
            steps {
                script {

                    echo "Checking out branch: ${env.BRANCH}"

                    checkout([
                        $class: 'GitSCM',
                        branches: [[name: "*/${env.BRANCH}"]],
                        userRemoteConfigs: scm.userRemoteConfigs
                    ])
                }
            }
        }

        stage('Build Docker Image') {
            when {
                expression {
                    params.ACTION == 'DEPLOY'
                }
            }

            steps {
                bat """
                    docker build -t ${env.IMAGE}:${params.VERSION} .
                """
            }
        }

        stage('Validate Docker Image') {
            when {
                expression {
                    params.ACTION == 'DEPLOY'
                }
            }

            steps {
                bat """
                    docker image inspect ${env.IMAGE}:${params.VERSION}
                """
            }
        }

        stage('Deploy Application') {
            when {
                expression {
                    params.ACTION == 'DEPLOY'
                }
            }

            steps {
                script {

                    bat """
                        docker rm -f ${env.APP} 2>nul
                        exit /b 0
                    """

                    withCredentials([
                        usernamePassword(
                            credentialsId: 'customer-db-creds',
                            usernameVariable: 'CUSTOMER_DB_USER',
                            passwordVariable: 'CUSTOMER_DB_PASSWORD'
                        )
                    ]) {

                        bat """
                            docker run -d ^
                            --name ${env.APP} ^
                            --network ${env.NETWORK} ^
                            -p ${env.PORT}:8081 ^
                            -e APP_ENV=${params.ENVIRONMENT} ^
                            -e APP_VERSION=${params.VERSION} ^
                            -e DB_HOST=${env.DB} ^
                            -e DB_USER=%CUSTOMER_DB_USER% ^
                            -e DB_PASSWORD=%CUSTOMER_DB_PASSWORD% ^
                            -e DB_NAME=customerdb ^
                            ${env.IMAGE}:${params.VERSION}
                        """
                    }
                }
            }
        }

        stage('Application Container Check') {
            when {
                expression {
                    params.ACTION == 'DEPLOY'
                }
            }

            steps {
                bat """
                    docker inspect -f "{{.State.Running}}" ${env.APP}
                """
            }
        }

        stage('Database Container Check') {
            when {
                expression {
                    params.ACTION == 'DEPLOY'
                }
            }

            steps {
                bat """
                    docker inspect -f "{{.State.Running}}" ${env.DB}
                """
            }
        }

        stage('Network Validation') {
            when {
                expression {
                    params.ACTION == 'DEPLOY'
                }
            }

            steps {
                bat """
                    docker network inspect ${env.NETWORK}
                """
            }
        }

        stage('Health Check') {
            when {
                expression {
                    params.RUN_TESTS == 'YES' &&
                    params.ACTION == 'DEPLOY'
                }
            }

            steps {
                bat """
                    docker exec ${env.APP} python -c "import urllib.request; r=urllib.request.urlopen('http://localhost:8081/health'); print(r.read().decode())"
                """
            }
        }

        stage('Application Database Check') {
            when {
                expression {
                    params.RUN_TESTS == 'YES' &&
                    params.ACTION == 'DEPLOY'
                }
            }

            steps {
                bat """
                    docker exec ${env.APP} python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8081/db-test').read().decode())"
                """
            }
        }

        stage('Environment Version Validation') {
            when {
                expression {
                    params.RUN_TESTS == 'YES' &&
                    params.ACTION == 'DEPLOY'
                }
            }

            steps {
                bat """
                    docker exec ${env.APP} python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8081/health').read().decode())"
                """
            }
        }

        stage('Manual Rollback') {
            when {
                expression {
                    params.ACTION == 'ROLLBACK'
                }
            }

            steps {
                script {

                    if (params.ENVIRONMENT != 'PRODUCTION') {
                        error "Rollback is only supported for PRODUCTION"
                    }

                    echo "Restoring production version 5.0"

                    bat """
                        docker rm -f ${env.APP} 2>nul
                        exit /b 0
                    """

                    withCredentials([
                        usernamePassword(
                            credentialsId: 'customer-db-creds',
                            usernameVariable: 'CUSTOMER_DB_USER',
                            passwordVariable: 'CUSTOMER_DB_PASSWORD'
                        )
                    ]) {

                        bat """
                            docker run -d ^
                            --name ${env.APP} ^
                            --network ${env.NETWORK} ^
                            -p ${env.PORT}:8081 ^
                            -e APP_ENV=PRODUCTION ^
                            -e APP_VERSION=5.0 ^
                            -e DB_HOST=${wrong-db-host} ^
                            -e DB_USER=%CUSTOMER_DB_USER% ^
                            -e DB_PASSWORD=%CUSTOMER_DB_PASSWORD% ^
                            -e DB_NAME=customerdb ^
                            ${env.IMAGE}:5.0
                        """
                    }
                }
            }
        }

        stage('Final Validation') {
            steps {

                bat """
                    docker ps
                """

                bat """
                    docker network inspect ${env.NETWORK}
                """

                bat """
                    docker image inspect ${env.IMAGE}:${params.ACTION == 'ROLLBACK' ? '5.0' : params.VERSION}
                """

                bat """
                    docker volume ls
                """
            }
        }
    }

    post {

        success {
            echo "============================================"
            echo "DEPLOYMENT SUCCESS"
            echo "============================================"
            echo "Environment : ${params.ENVIRONMENT}"
            echo "Version     : ${params.ACTION == 'ROLLBACK' ? '5.0' : params.VERSION}"
            echo "Action      : ${params.ACTION}"
            echo "============================================"
        }

        failure {
            echo "============================================"
            echo "DEPLOYMENT FAILED"
            echo "============================================"
            echo "Environment : ${params.ENVIRONMENT}"
            echo "Version     : ${params.VERSION}"
            echo "Action      : ${params.ACTION}"
            echo "============================================"
        }
    }
}

