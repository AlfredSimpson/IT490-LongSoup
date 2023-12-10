# SystemD

A core requirement of this project is to have a system that can be easily deployed and managed. SystemD is a great way to do this.

By using SystemD, we can easily manage our services and ensure that they are running. We can also easily start and stop them.

## What is SystemD?

SystemD is a system and service manager for Linux. It is a replacement for the init daemon. It provides a system and service manager that runs as PID 1 and starts the rest of the system. It provides aggressive parallelization capabilities, uses socket and D-Bus activation for starting services, offers on-demand starting of daemons, keeps track of processes using Linux control groups, supports snapshotting and restoring of the system state, maintains mount and automount points and implements an elaborate transactional dependency-based service control logic. It can work as a drop-in replacement for sysvinit.

## Why SystemD?

Because nobody wants to have to manually do everything.

## How to create services for systemd

To create a service for systemd, you need to create a service file. This file will contain the information that systemd needs to run your service. It must have three main parts, wrapped in square brackets. These parts are:
- Unit
- Service
- Install

For more information, go to [Free Desktop's site](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html)

### Unit

The unit section is where you define the service. It could contain the following:
- Description
- Wants
- After
- Requires
- PartOf

### Service

The service section is where you define the service. It could contain the following:
- Type
  - This is the type of service. It could be simple, forking, oneshot, dbus, notify, idle, or a combination of these.
  - Simple is the default. Use this when the process is the main process of the service.
  - Forking is used when the process forks a child process. This is used when the process is not the main process of the service.
  - Oneshot is used when the process is expected to exit after a single run.
  - Dbus is used when the process is a D-Bus service.
  - Notify is used when the process signals readiness to systemd.
  - Idle is used when the process is not ready to run until all jobs are dispatched.
  - Combination is used when the process is a combination of the above.
- ExecStart
  - This is the command to start the service.
  - This is required.
  - This can be a path to a script.
  - Use the full path!
- ExecStop
  - ExecStop is the command to stop the service and how we handle it.
- ExecReload
  - ExecReload is the command to reload the service and how we handle it.
  - This is used when the service supports reloading.
  - This is not used by default.
- Restart
  - Restart is used to define when the service should be restarted. Options are no, on-success, on-failure, on-abnormal, on-abort, on-watchdog, on-disconnect, on-panic, or always.
- RestartSec
  - RestartSec is used to define the time to sleep before restarting the service.
  - This is used when the service is restarted.
  - This is not used by default.
- User
  - User is used to define the user to run the service as. This is used when the service is started.
  - This is not used by default, but is a good practice to set it because it is more secure.
- Group
  - Group is used to define the group to run the service as. This is used when the service is started.
  - This is not used by default, but is a good practice to set it because it is more secure.
- WorkingDirectory
  - WorkingDirectory is used to define the working directory for the service.
  - For example, if you have a script that you want to run, you would put the path to the script here.
  - Use the full absolute path!
  - This is not used by default.
- Environment
  - Environment is used to define the environment variables for the service. It is not used by default.
  - For example, if your script needs to know the path to something, you would put it here.
  - Set environment variables for executed processes using the Environment directive.
  - Example: Environment="FOO=bar"
- EnvironmentFile
  - EnvironmentFile is used to define the environment variables for the service. It is not used by default.
  - This is the file that contains the environment variables.
  - Similar to Environment=, but this will read the environment variables from a file.
  - The text file should contain new-line-separated variable assignments.
  - Example: EnvironmentFile=/etc/conf.d/foo
- StandardInput
  - This controls where file descriptor 0 (stdin) of the executed processes is connected to. Takes one of null, tty, tty-force, tty-fail, socket, socket-force, socket-fail, path, path-force, path-fail, or inherit.
  - This is not used by default.
- StandardOutput
  - Similar to StandardInput, but for file descriptor 1 (stdout).
- StandardError
  - Controls where file descriptor 2 (stderr) of the executed processes is connected to. Takes one of null, tty, tty-force, tty-fail, socket, socket-force, socket-fail, path, path-force, path-fail, or inherit.
- SyslogIdentifier
  - Sets the process name to prefix log lines sent to the logging system.

### Install

If you've guessed that this is the section where you define how to install the service, you're right! This section is used to define how to install the service. It could contain the following:

- WantedBy
  - WantedBy is used to define the target that the service should be started under.
  - This is not used by default.
  - Example: WantedBy=multi-user.target
    - This is used when the service should be started under a multi-user target.
  - Example: WantedBy=graphical.target 
    - This is used when the service should be started under a graphical target.
- RequiredBy
    - RequiredBy is used to define the target that the service should be started under.
    - This is not used by default.
    - Example: RequiredBy=multi-user.target
        - This is used when the service should be started under a multi-user target.
    - Example: RequiredBy=graphical.target 
        - This is used when the service should be started under a graphical target.