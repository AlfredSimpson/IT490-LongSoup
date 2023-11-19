# A little helping hand

For some reason, some things aren't working right in Ubuntu. For example, the clipboard or drag and drop.

We can fix some of our problems by creating scripts that run in systemd. 

## Clipboard/drag and drop
    To get the clipboard work, first, run the [clipboard.sh](../clipboard.sh) script. This will install clipboard initially. 
    Then, download or rewrite [constantclipboard.sh](../constantclipboard.sh). Place this somewhere convenient, give it executable permissions.
    Next, go to /etc/systemd/system. Create a file called constantclipboard.service.
    Modify the [constantclipboard.service](./constantclipboard.service) file with your information. 
    Once you've done that, run the following commands:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable constantclipboard.service
    sudo systemctl start constantclipboard.service
    ```
    This will start the service. You can check the status of the service by running:
    ```bash
    sudo systemctl status constantclipboard.service
    ```

    If you run into an issue where the service isn't starting - make sure the type is correct and that it is in a valid location with the correct permissions.