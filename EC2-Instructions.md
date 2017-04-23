# Launching an EC2 Instance for Prefer

## Launch the Instance

Launch a regular EC2 Ubuntu instance and make sure that the security group includes HTTP on port 80 open to the public.

## Install Basic Requirements

Run the following commands, this will allow for the use of pip installs and will also install PostgreSQL and Tmux on the server.

`sudo apt-get install update`
`sudo apt-get install apache2`
`sudo apt-get install libapache2-mod-wsgi`
`sudo apt-get install python-pip`

## Clone the Repo and Install the Required Packages

[Check if git is installed (run `git`), if not run `sudo yum install git`]

First clone the repo:

`git clone https://github.com/spencersmith6/prefer.git`

Enter your username and password.

Then `cd` into the repo and install the required Python packages:

`sudo pip install -r requirements.txt`

Now we need to copy over those super secret credentials files.

`sudo nano db_admin/creds.json`

and copy/paste or type in the credentials.

## Launch the App

Now that the EC2 instance is running and all the packages are installed, we can launch our app!

First run `tmux` so the app doesn't close when we disconnect from our ssh instance. Now run:

`python main.py`

You should get a message saying: `* Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)`, this means it's working!

Now from you're browser go to <the EC2 DNS>:5000 and make sure everything is A-Okay!

Now, hit `cntrl-b d` to disconnect from the tmux session and you're good to go.

Happy swiping.


