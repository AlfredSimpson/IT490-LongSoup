import psutil
import subprocess
import time
import logging
import json


logFile = "/home/alfred/Desktop/keephopping.json"
loggingFile = "/home/alfred/Desktop/keephopping-logging.log"
logging.basicConfig(filename=logFile, level=logging.DEBUG)


def keep_waiting(waitTime):
    start_time = time.time()
    while time.time() - start_time < waitTime:
        pass


file_paths = {
    "DBWorker.py": "/home/alfred/Desktop/IT490-LongSoup/DB/DBWorker.py",
    "DBSpotWorker.py": "/home/alfred/Desktop/IT490-LongSoup/DB/DBSpotWorker.py",
    # We can add more files or their paths here as needed.
}


# Function to check if a process is psrunning
def is_process_running(process_name):
    try:
        subprocess.check_output(["pgrep", "-f", "-i", process_name])
        return True
    except:
        print(
            f"Failed to find {process_name} as a running process.\n\nInitiating restart measures.\n"
        )
        return False


def main():
    while True:
        # Iterate over the files and their paths in the dictionary
        for filename, file_path in file_paths.items():
            if not is_process_running(filename):
                print(f"{filename} is not running. Checking RabbitMQ...")
                rabbitmq_running = is_process_running("rabbitmq-server")
                try:
                    if rabbitmq_running:
                        print(
                            f"RabbitMQ is running, but {filename} is not. Restarting RabbitMQ"
                        )
                        subprocess.Popen(["systemctl", "restart", "rabbitmq-server"])

                        # Check if RabbitMQ is able to be restarted, wait up to 25 seconds
                        wait_count = 0
                        while (not is_process_running("rabbitmq-server")) and (
                            wait_count <= 5
                        ):
                            wait_count += 1
                            time.sleep(5)

                        if not is_process_running("rabbitmq-server"):
                            logging.critical("RabbitMQ is not running. Exiting...")
                            message = "RabbitMQ failed to restart! Exiting loop"
                            log_date = time.strftime("%Y-%m-%d %H:%M:%S")
                            new_log = f"**Critical**\t[RMQ] - {log_date} - {message}\n"
                            with open(logFile, "a") as logFile:
                                logFile.write(new_log)
                            break
                        else:
                            print(f"RabbitMQ is running. Restarting {filename}")
                            subprocess.Popen(["python3", file_path])
                            message = f"{filename} experienced an error. Keephopping.py restarted it."
                            log_date = time.strftime("%Y-%m-%d %H:%M:%S")
                            new_log = f"[RMQ] - {log_date} - {message}\n"
                            with open(logFile, "a") as logFile:
                                logFile.write(new_log)
                except Exception as e:
                    pass

        # Sleep for a minute before the next check
        time.sleep(30)


if __name__ == "__main__":
    print(f"Starting keephopping.py")
    print(f"\nCritical Logging to {logFile}")
    print(f"\nDebug Logging to {loggingFile}")
    print(f"\n\tNote: No Data will be shown if all is running as planned.\n")
    print(f"\nPress Ctrl+C to exit")
    main()
