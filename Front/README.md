# Front End Server


This is the Front End server. This handles the user interface and user interaction.


## Languages and frameworks used:
- HTML
- CSS
- JavaScript
- Node.js
- PHP
- RabbitMQ (slightly)



## Set up apache

After apache is installed, we'll need to make sure our files are in the write directory and that apache is accessing them.

First, let's make sure apache is running & that necessary packages are installed:

```bash

sudo systemctl status apache2
sudo apt install php libapache2-mod-php
sudo apt install php-cli
sudo apt install php-cgi
sudo apt install php-mysql
sudo apt install php-pgsql # For postgres
```

If it's not running, start it:

```bash

sudo systemctl start apache2

```

Next, let's go to the apache directory and modify the sites-available. Copy the existing default into a new name (I used cgs).

```bash

cd /etc/apache2/sites-available
sudo cp 000-default.conf cgs.conf

```

This makes a copy of the default as cgs.conf. Now we should edit the cgs.conf to have our info in it:

```bash

sudo vim cgs.conf

```

Inside the file, we'll need to change the DocumentRoot to the directory where our files are. In my case, it's /var/www/cgs. We'll also need to change the ServerName to the IP address of the server. Our front end server is 192.168.1.13 - but I chose commongrounds.localhost. It was available so why not. The file should look like this:

```bash

<VirtualHost *:80>

    ServerAdmin nicc-group@njit.edu
    DocumentRoot /var/www/cgs/
    ServerName  commongrounds.localhost

    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined

</VirtualHost>

```

With our virtualhost set up in apache we now need to enable it.


```bash

sudo a2ensite cgs.conf

```

We'll get a response saying to reload it, so we should


```bash

sudo systemctl reload apache2
sudo systemctl restart apache2
```

You could also use service instead of systemctl. From here we can access the website by going to commongrounds.localhost OR to the IP address of the server. If you want to use the IP address, you'll need to add it to your hosts file. On linux, this is /etc/hosts. 

