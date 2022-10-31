# OneTeam
OneTeam - digital sales assistant


Installation:

# must have git installed

[Install Git](https://github.com/git-guides/install-git)


# Must have docker and docker compose installed.
[Install Docker Desktop](https://www.docker.com/products/docker-desktop)

Works well with docker-desktop for macbook

```
% git clone https://github.com/xod442/oneteam.git
% chmod 766 oneteam-v1
% cd oneteam
oneteam%  docker-compose up -d
```

# Before you get started
Verify you have set the oneteam directory to 766. If you do not verify this, when you backup your database it will not work.
it will never tell you either. When you dump the database make sure you have a 'oneteam_data.txt' file in the oneteam-v1 folder.
If you wipe your database without a valid 'oneteam_data.txt' file saved in the oneteam directory, you will be back to square zero.

You have been warned. :-)


# Open browser
Use: localhost:5001


# Create user credentials
The first time you login with your code, oneteam will present a credential page.
Enter your username, and password. oneteam will redirect to a page to enter your credentials. It will be saved to system.

These will be your access credentials. You will be asked to login with them.
This is not a multiuser system...yet.
If you want to change your password, call me :-)

# Inside the app, create companies.
Just add a list of anything here, I use companies I work with.
For personal action items, I just add the word personal to the company tab.

This app is basically worthless unless you add companies.
