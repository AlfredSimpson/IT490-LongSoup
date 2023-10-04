# Steps taken to get rabbit to work on an test

Source information:
https://www.rabbitmq.com/tutorials/tutorial-one-php.html
https://www.digitalocean.com/community/tutorials/how-to-install-and-use-composer-on-ubuntu-20-04

1. Following this tutorial, I created composer.json with the same information. 
2. Install php-cli using:
   ```shell
   sudo apt install php-cli unzip``` 
3. Install curl
   1. ```shell
    sudo apt install curl
       ```
4. Install composer
   ```shell 
    cd ~
    curl -sS https://getcomposer.org/installer -o /tmp/composer-setup.php```
5. Verify install:
   ```shell
   HASH=`curl -sS https://composer.github.io/installer.sig`
   ```
6. echo hash
7. check hash
8. Execute php code
   1. ```php -r "if (hash_file('SHA384', '/tmp/composer-setup.php') === '$HASH') { echo 'Installer verified'; } else { echo 'Installer corrupt'; unlink('composer-setup.php'); } echo PHP_EOL;"```
      1. You should see Installer verified hopefully
9. install composer globally
   1.  ```sudo php /tmp/composer-setup.php --install-dir=/usr/local/bin --filename=composer```


Now that composer is installed...

in the directory we're working from:
1. ```shell
 composer.phar install```

