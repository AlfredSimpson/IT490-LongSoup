# Hot Standby

We were required to create a hot standby server for each of our production machines. We did this by first creating our initial production servers, and then cloning them in VirtualBox once they were configured. After that, we installed Keepalived on each of the machines - production and the standby machines. Finally, we configured them to work together.


## Keepalived Configuration

We first installed Keepalived on each of the machines by running:

```bash
sudo apt-get install keepalived
```

Each server had to be configured with it's own conf file. In this directory you'll find them labled as primary_keepalived.conf or secondary_keepalived.conf. However, we did configure these on the machines themsleves as simply keepalived.conf.


This is an example of keepalived.conf, with the most important parts noted:

```bash

# global_defs sets the router_id, specific to this machine, and enable_script_security enables script security
global_defs {
  router_id back_prod_standby
  enable_script_security
}

# vrrp_script is the script that will be run to check if the machine is alive. interval is how often it will be run, and weight is how important it is
vrrp_script chk_heartbeat {
  script "/etc/keepalived/check_heartbeat.sh"
  interval 2
  weight 2
}

# vrrp_instance is the instance of keepalived that will be run. state is the state of the machine, interface is the interface that will be used, virtual_router_id is the id of the router, priority is the priority of the machine, advert_int is the interval at which the machine will advertise itself, authentication is the authentication type and password, and virtual_ipaddress is the ip address that will be used
# Out of all of this, state should be MASTER or BACKUP - though I wish they used different language for that.
# interface can be found using ip a or ifconfig. In our vms it showed as enp0s3.
# virtual_router_id should be unique for each pair - so 51 was the same on both the primary and secondary for prod_back. 
# Priority - the higher the number, the more likely it is to be the master. So the primary should have a higher number than the secondary.
# advert_int - how often the machine will advertise itself. This should be the same on both machines.
# authentication - use auth_type PASS so it looks for a password. It can only be 8 characters long apparently. We shared the password across the machines so they could communicate.
# virtual_ipaddress - this tripped us up a bit at first. It is not the IP of either machine - but rather the IP they'll both use. So set it to one that is not currently and will not be in use by any other machine on your subnet.
# track_script was defined above, but this told it which to use.
vrrp_instance VI_1 {
  state BACKUP
  interface enp0s3
  virtual_router_id 51
  priority 100
  advert_int 1
  authentication {
    auth_type PASS
    auth_pass njit490
  }
  virtual_ipaddress {
    192.168.68.89
  }
  track_script {
    chk_heartbeat
  }
}
```

After it's all running - you can check by sshing into the "new" ip address and running ip a. You should see the virtual ip address listed there. If you run ip a on the other machine, you should not see it listed. If you run ip a on the machine that is currently the master, you should see the virtual ip address listed there as well.