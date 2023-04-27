This README is to have useful information on how to run Aline-Financial microservices

Changes needed in microservices codebase:

    In aline-underwriter-microservice:
    main/.../controller/applicationController.java
    change :
            ApplyResponse applyResponse = service.applyAndSendEmail(request);
    to:
            ApplyResponse applyResponse = service.apply(request);

    under each micro service, you need to populate Core subfolder:
    git submodule init
    git submodule update

    in UserConfirmationService.java under aline-user-microservice/user-microservice/.../service/
    under sendMemberUserConfirmationEmail function comment out this line
    //emailService.sendHtmlEmail(subject, template, email, variables);
    System.out.println("Token for " + username + ": " + token);

    under aline-card-microservice:
    go under application.yaml and change initilization to 'never'


    under aline-underwriter-microservice:
    go under service/CardService.java
        comment out this line:
                //emailService.sendHtmlEmail("Credit card successfully issued", templateName, applicant.getEmail(), variables);

    under aline-bank-microservices
        add application.yaml under src/../resources
        in yapplication.yaml change microservice name to "bank-microservice"

    under aline-card-microservice
	under src/.../controller/CardController.java
		comment out:
		line 40: 
			//cardEmailService.sendCard(card, request.isReplacement());

Useful commands to get Microservices up and running:

    stop docker running mysql:
        sudo docker stop mysql

    start docker engine:
        sudo service docker start

    running mysql docker container in linux enviroment:
        docker container run --rm --detach --publish 3306:3306 --name mysql --env MYSQL_ROOT_PASSWORD=secret --env MYSQL_DATABASE=aline mysql

    within subfolder(user-microservice)
        APP_PORT=8177 ENCRYPT_SECRET_KEY=12345678901234567890123456789012 JWT_SECRET_KEY=12345678901234567890123456789012 DB_USERNAME="root" DB_PASSWORD="secret" DB_HOST="localhost" DB_PORT=3306 DB_NAME="aline" mvn spring-boot:run

    within subfolder(underwriter-microservice)
        APP_PORT=8170 ENCRYPT_SECRET_KEY=12345678901234567890123456789012 JWT_SECRET_KEY=12345678901234567890123456789012 DB_USERNAME="root" DB_PASSWORD="secret" DB_HOST="localhost" DB_PORT=3306 DB_NAME="aline" mvn spring-boot:run

    within subfolder(bank-microservice)
        APP_PORT=8172 ENCRYPT_SECRET_KEY=12345678901234567890123456789012 JWT_SECRET_KEY=12345678901234567890123456789012 DB_USERNAME="root" DB_PASSWORD="secret" DB_HOST="localhost" DB_PORT=3306 DB_NAME="aline" mvn spring-boot:run

    within subfolder(card-microservice)
        APP_PORT=8174 ENCRYPT_SECRET_KEY=12345678901234567890123456789012 JWT_SECRET_KEY=12345678901234567890123456789012 DB_USERNAME="root" DB_PASSWORD="secret" DB_HOST="localhost" DB_PORT=3306 DB_NAME="aline" mvn spring-boot:run

    within subfolder(account-microservice)
        APP_PORT=8176 ENCRYPT_SECRET_KEY=12345678901234567890123456789012 JWT_SECRET_KEY=12345678901234567890123456789012 DB_USERNAME="root" DB_PASSWORD="secret" DB_HOST="localhost" DB_PORT=3306 DB_NAME="aline" mvn spring-boot:run


    kill all programs running on ports:
        fuser -k 8177/tcp 8170/tcp 8172/tcp 8174/tcp 8176/tcp

    Process of running program with rest of set up complete:
        start mysql docker
        mvn clean install  on underwriter user banks: success
        run underwriter: break
        mvn clean install core underwriter: success
        run underwriter:success
        run user: success
        run bank: success

    h2-console ui:
        http://localhost:8172/h2-console
        Saved Settings: Generic MySQL
        Setting Name: Generic MYSQL
        Driver Class: com.mysql.jdbc.Driver
        JDBC URL: jdbc:mysql://localhost:3306/aline
        User Name: root
        password: secret

    sql commands:
        show tables;
        select * from applicant;
        select * from application;
        select * from user;
        select * from bank;
        select * from branch;

    Pytest:
        within gen_data:
            pytest -v

    pylint:
        pylint gen_applicant.py

        pylint applications.py

        pylint user.py

        pylint bank_branch.py

        pylint card.py

        pylint account.py

Containerizing building INDIVIDUAL services pre-compose:

	***To run individual containers uncomment out the block in each dockerfile
    
	underwriter:
		sudo docker build -t underwriter --build-arg APP_PORT=8170 --build-arg ENCRYPT_SECRET_KEY=12345678901234567890123456789012 --build-arg JWT_SECRET_KEY=12345678901234567890123456789012 --build-arg DB_USERNAME="admin" --build-arg DB_PASSWORD="password123" --build-arg DB_HOST="aline-db.clxfaquthjyh.us-east-1.rds.amazonaws.com" --build-arg DB_PORT=3306 --build-arg DB_NAME="aline" .
		sudo docker run -p 8170:8170 underwriter

	user:
		sudo docker build -t user --build-arg APP_PORT=8177 --build-arg ENCRYPT_SECRET_KEY=12345678901234567890123456789012 --build-arg JWT_SECRET_KEY=12345678901234567890123456789012 --build-arg DB_USERNAME="admin" --build-arg DB_PASSWORD="password123" --build-arg DB_HOST="aline-db.clxfaquthjyh.us-east-1.rds.amazonaws.com" --build-arg DB_PORT=3306 --build-arg DB_NAME="aline" .
		sudo docker run -p 8177:8177 user

	transaction:
		sudo docker build -t transaction --build-arg APP_PORT=8178 --build-arg ENCRYPT_SECRET_KEY=12345678901234567890123456789012 --build-arg JWT_SECRET_KEY=12345678901234567890123456789012 --build-arg DB_USERNAME="admin" --build-arg DB_PASSWORD="password123" --build-arg DB_HOST="aline-db.clxfaquthjyh.us-east-1.rds.amazonaws.com" --build-arg DB_PORT=3306 --build-arg DB_NAME="aline" .
		sudo docker run -p 8178:8178 transaction

	card:
		sudo docker build -t card --build-arg APP_PORT=8174 --build-arg ENCRYPT_SECRET_KEY=12345678901234567890123456789012 --build-arg JWT_SECRET_KEY=12345678901234567890123456789012 --build-arg DB_USERNAME="admin" --build-arg DB_PASSWORD="password123" --build-arg DB_HOST="aline-db.clxfaquthjyh.us-east-1.rds.amazonaws.com" --build-arg DB_PORT=3306 --build-arg DB_NAME="aline" .
		sudo docker run -p 8174:8174 card

	bank:
		sudo docker build -t bank --build-arg APP_PORT=8172 --build-arg ENCRYPT_SECRET_KEY=12345678901234567890123456789012 --build-arg JWT_SECRET_KEY=12345678901234567890123456789012 --build-arg DB_USERNAME="admin" --build-arg DB_PASSWORD="password123" --build-arg DB_HOST="aline-db.clxfaquthjyh.us-east-1.rds.amazonaws.com" --build-arg DB_PORT=3306 --build-arg DB_NAME="aline" .
		sudo docker run -p 8172:8172 bank

	account:
		sudo docker build -t account --build-arg APP_PORT=8176 --build-arg ENCRYPT_SECRET_KEY=12345678901234567890123456789012 --build-arg JWT_SECRET_KEY=12345678901234567890123456789012 --build-arg DB_USERNAME="admin" --build-arg DB_PASSWORD="password123" --build-arg DB_HOST="aline-db.clxfaquthjyh.us-east-1.rds.amazonaws.com" --build-arg DB_PORT=3306 --build-arg DB_NAME="aline" .
		sudo docker run -p 8176:8176 account

Docker compose:

	***Comment out the Block in each Dockerfile to user docker compose

	to run all aline containers use this command:
		sudo docker compose up

	to stop all the containers and remove them use this command:
		sudo docker compose down

Code Bugs found:

    in banks microservice:
        when creating a bank then multiple branches, the microservice overwrites the last branch created in the
        DB, so there can only be one branch per bank

    in users microservice:
        when registering a user, it requires a token which can be gotten through an email sent,
        but my gen_user module prints it out to the console to be manually placed. This isnt a Bug
        for production but requires tedious work to register works in dev enviroment

    in card microservice:
        when creating a credit card, the information sent back from the post request  on the application
        doesn't give the nessasary information to activate the cards, and this is needed for transactions
        my gen_card script asks for it manually. The other option would be to pull the information from the 
        db, but this is forbidden as directed by the project manager. Also in dev enviroments, its uncommon 
        to have access to the database keys directly. 

    in account microservice: 
        when hitting the /members/{memberId}/accounts, it should return all accounts from that user by 
        memberid, but instead only gives the last created account created for that memberid. In order to
        do transactions properly, by getting each account and their balance, in order to make transactions
        there isnt another endpoint that provides the balance of each account.

    in card microservice:
        When i try to acctivate 2 cards per member, it rejects it, therefore a member may have a Checking
        account and a Credit Card account but may not activate a card for both
