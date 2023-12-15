import psutil
import subprocess
import time
import logging
import json


logFile_path = "/home/alfred/Desktop/keephopping.log"
loggingFile = "/home/alfred/Desktop/keephopping_and_logging.log"
logging.basicConfig(filename=loggingFile, level=logging.DEBUG)

CRIT = "CRITICAL"
LOW = "LOW"
INFO = "INFO"


def keep_waiting(waitTime):
    """# keep_waiting
    Waits for a specified amount of time. This is used to give processes time to start up before we check if they are running.
    Args:
        waitTime (int): time in seconds to wait.
    """
    start_time = time.time()
    while time.time() - start_time < waitTime:
        pass


# ! Commenting out for now, but if we reinstitute json logging, this is a good step. I couldn't get the correct format down.
# def initializeLog(file):
#     """# initializeLog
#     This is just to initialize the log file. It will be called whenever this starts - so it will rewrite the logfile... but that's fine for our project.
#     It takes one parameter, the path to the log file.

#     Args:
#         file (str): Path to the log file
#     """
#     initial_log = {
#         "logs": {
#             "INFO": [],
#             "LOW": [],
#             "MEDIUM": [],
#             "CRITICAL": [],
#         }
#     }
#     with open(file, "w") as log_file:
#         json.dump(initial_log, log_file)


def writeLog(msg, file, criticality):
    """# writeLog
    Takes in msg, file, criticality
    Writes to a log file with the current date and time, the message passed to the function, and the criticality of the message.

    Args:
        msg (str): What happened
        file (str): The path to the log file - a string
        criticality (str): Low/Critical, etc.
    """
    log_date = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{criticality} - {log_date} - {msg}"

    with open(file, "a") as log_file:
        log_file.write(log_entry)


file_paths = {
    "DBWorker.py": "/home/alfred/Desktop/IT490-LongSoup/DB/DBWorker.py",
    "DBSpotWorker.py": "/home/alfred/Desktop/IT490-LongSoup/DB/DBSpotWorker.py",
    # We can add more files or their paths here as needed.
}


def verify(process):
    try:
        subprocess.check_output(["pgrep", "-f", "-i", process])
        # print(f"\nVerification check successful: {process} is running.\n")
        return True
    except:
        msg = f"Failed to find {process} as a running process.\nInitiating restart measures.\n"
        print(msg)
        writeLog(msg, logFile_path, LOW)
        return False


def keepRunning():
    while True:
        for filename, file_path in file_paths.items():
            if not verify(filename):
                print(
                    f"\n[ALERT]\t{filename} is not running. First we will attempt to reboot the files - then we will reboot RabbitMQ...\n"
                )
                subprocess.Popen(["python3", file_path])
                keep_waiting(5)
                # Check if it's running, if it is, great, move on to the next file.
                if verify(filename):
                    print(f"{filename} is running. Continuing to next file\n")
                    continue
                else:
                    # If it's not, see if rabbitmq is working.
                    rabbitmq_running = verify("rabbit")
                try:
                    # If rabbitmq is running but we can't start the file, something might be blocking it. Restart RabbitMQ
                    if rabbitmq_running:
                        print(
                            f"RabbitMQ is running, but {filename} is not. Restarting RabbitMQ"
                        )
                        subprocess.Popen(["systemctl", "restart", "rabbitmq-server"])

                        # Check if RabbitMQ is able to be restarted, wait up to 25 seconds
                        wait_count = 0
                        while (not verify("rabbit")) and (wait_count <= 5):
                            wait_count += 1
                            time.sleep(5)
                        # If rabbitmq is still not running, exit the loop - This is a critical failure.
                        if not verify("rabbit"):
                            msg = f"RabbitMQ failed to restart. Exiting keephopping.py"
                            logging.debug(msg)
                            print(msg)
                            writeLog(msg, logFile_path, CRIT)
                            break
                        # Otherwise, if we could get rabbitMQ up, let's restart all dependent files before starting again.
                        else:
                            print(
                                f"RabbitMQ is running. Restarting all files dependent on RabbitMQ\n"
                            )
                            bootUp()
                except Exception as e:
                    logging.debug(f"Exception: {e}")
                    pass
        # Sleep for 45 seconds before the next check
        time.sleep(45)


def bootUp():
    # Ensure that rabbitMQ is running
    msg = f"Booting or rebooting keepHopping.py\n"
    print(msg)
    rabbitmq_running = verify("rabbit")

    # If rabbitmq is not running, start it
    if not rabbitmq_running:
        # Start RabbitMQ, wait up to 30 seconds
        print(f"\nRabbitMQ is not running at bootUp. Starting RabbitMQ\n")
        subprocess.Popen(["systemctl", "start", "rabbitmq-server"])

        # Give RabbitMQ time to start - It can be slow...
        print(f"\nWaiting 30 seconds for RabbitMQ to start...\n")
        time.sleep(30)
        print(f"\nDone waiting for RabbitMQ to start...\n")

        # If rabbitmq still isn't up, something might be wrong.
        if not verify("rabbit"):
            logging.critical("\n\nRabbitMQ failed to start.\n\n\tExiting...\n")
            writeLog(
                "RabbitMQ failed to start. Exiting keephopping.py", logFile_path, CRIT
            )
            # Attempt to restart rabbit on our way out
            subprocess.Popen(["systemctl", "restart", "rabbitmq-server"])
            exit(1)
        else:
            # If RabbitMQ is running, recursively call bootUp. it will verify rabbit again, which should pass. From there, for all files in the dictionary, it will boot them.
            bootUp()
    # If RabbitMQ was already running, we can continue...
    else:
        print(f"RabbitMQ is running. Checking on other files\n")
        for filename, file_path in file_paths.items():
            # First see if it's running - no sense respawning it if it is.
            if verify(filename):
                print(f"{filename} is running. Continuing to next file.")
                continue
            else:
                print(f"{filename} is not running. Starting it now...\n")

                writeLog(
                    f"{filename} is not running. Starting it now...", logFile_path, LOW
                )
                # Attempt to start the file
                subprocess.Popen(["python3", file_path])
                # Give it time to start - just in case.
                keep_waiting(10)
                # Check if it's running
                if verify(filename):
                    print(f"{filename} is running. Continuing...\n")
                # If it's not running, something is wrong.
                else:
                    logging.critical(f"{filename} failed to start. Exiting...\n\n\n")
                    writeLog(
                        "Failed to start. Exiting keephopping.py", logFile_path, CRIT
                    )
                    exit(1)


def main():
    bootUp()
    keepRunning()


if __name__ == "__main__":
    print(f"Starting keephopping.py")
    print(f"\nInfo & Critical Logging to {logFile_path}")
    print(f"\nDebug Logging to {loggingFile}")
    print(
        f"\n\tNote: We will attempt to first boot all files.\nAfter that, if all is running smoothly, we will see no output.\n"
    )
    print(f"\nPress Ctrl+C to exit")
    main()
