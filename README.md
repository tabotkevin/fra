# Feature Request App (fra) written in Python using Flask Framework

### Problem to Solve ####

Build a web application that allows the user to create "feature requests".

A "feature request" is a request for a new feature that will be added onto an existing piece of software. Assume that the user is an employee at IWS who would be entering this information after having some correspondence with the client that is requesting the feature. The necessary fields are:

	- Title: A short, descriptive name of the feature request.
	- Description: A long description of the feature request.
	- Client: A selection list of clients (use "Client A", "Client B", "Client C")
	- Client Priority: A numbered priority according to the client (1...n). Client Priority numbers should not repeat for the given client, so if a priority is set on a new feature as "1", then all other feature requests for that client should be reordered.
	- Target Date: The date that the client is hoping to have the feature.
	- Product Area: A selection list of product areas (use 'Policies', 'Billing', 'Claims', 'Reports')


### How do I get set up? ###

* Ubuntu dependencies
    - $ sudo apt-get install nginx supervisor python-pip python-virtualenv

* Environment Setup (Install virtualenv and pip)
    - Navigate to project folder and run the below command
	- $ virtualenv venv
	- $ source venv/bin/activate

* Install Dependencies
	- $ pip install -r requirement.txt

* Database configuration 
	- $ python manage.py db init 
	- $ python manage.py initdb 
	- $ python manage.py db migrate 
	- $ python manage.py db upgrade
	- $ python setup.py

* Start up local development server
	- $ python run.py

* To test
	- $ python test.py

* To deploy in production on Ubuntu Server
    - I used Gunicorn to deploy it on localhost using the command
    - $ gunicorn fra:app -b localhost:9000 --log-file log &
    - I used Supervisor to monitor Gunicorn process to make they are restarted in case of any problem
    - Create a supervisor file in /etc/supervisor/conf.d/ and configure it according with config below
        """
          [program:fra]
          directory=/home/ubuntu/fra
          command=/home/ubuntu/fra/venv/bin/gunicorn app:app -b localhost:9000
          autostart=true
          autorestart=true
          stderr_logfile=/var/log/fra/fra.err.log
          stdout_logfile=/var/log/fra/fra.out.log
        """
    - Enable Supervisor configuration
    - $ sudo supervisorctl reread
    - $ sudo service supervisor restart
	- Then used Nginx to serves as proxy to route all incoming requests to localhost:9000 where the server is listening
	- Create Nginx config file
	- $ sudo vim /etc/nginx/sites-available/iws
	- Nginx config is found below
		"""
	          server {
				    listen       80;
				    server_name  your_public_dnsname_here;

				    location / {
				    	include proxy_params;
				        proxy_pass http://127.0.0.1:9000;
				    }
				}
        """
    - sudo ln -s /etc/nginx/sites-available/iws /etc/nginx/sites-enabled
    - Restart Nginx web server
    - $ sudo nginx -t
    - $ sudo service nginx restart

* Application Structure
	- The application is devided into 3 main sections name, main, auth and admin sections
		- The auth section is ro handle authentication and account creation related tasks
		- The admin section is where authorised users can create, edit and delete Feature requests
		- The main section in this app doesn't really do anything, for now its just redircts users 
		  to the admin section. I made this section in anticipation that it can handle like the home page 
		  or any other pages that the app might need for public use, but there is none right now, so it just 
		  redirects to admin.

* Application Functionality
	- The auth section supports, login, user registration, account confirmation by email, password and email reset by email.
		- Account confirmation is done by users receiving an email with confirmation token
		- Password and email reset is done by users receiving an email with reset token
	- The app supports user roles and permisions and there are two types of users, Administrator and User (normal user)
		- The admin user can create other admin and normal user accounts, confirm and allow these user accounts, create, edit and delete feature requests and view all feature requests by all users.
			- User confirmation can be done by the registered user through email or manually by the admininistrator. A user whose account is not confirmed can not use the platform until their account is confirmed.
			- User accounts can only be allowed by the administrator. That means a user can create and confirm their accounts on their own, but until that account is allowed by the administrator the user can't use the platform.
			- Normal users whose accounts have been confirmed and allowed can only create, edit, delete and view only their feature requests.
			- Below are 2 test accounts for user and adminstrator
				- Email: admin@iws.com, password: password (default admin account confirmed and allowed)
				- Email: user@iws.com, password: password (default user account not confirmed and not allowed, you can try to login with this account and see how it behave without confirmation and not being allowed, then loggout and login with admin account to manually confirm without allowing the normal user account, then confirm and allow the user account each time login back in with the normal user account just to test this behaviour)
	- Feature requests can be created by both administrator and normal users
		- Administrators have the extra permision of creating, confirming and allowing other users and creating, editing, deleting and view all feature requests.
		- Normal users whose accounts have been confirmed and allowed can only create, edit, delete and view only their feature requests and do nothing else.
		- Feature requests have automatic priority adjustment according to application specifications.
	

### Who do I talk to? ###
* Repo owner or admin (Tabot Kevin | tabot.kevin@gmail.com)

