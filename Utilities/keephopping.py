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


# Function to check if a process is running
def is_process_running(process_name):
    for proc in psutil.process_iter(attrs=["name"]):
        if process_name.lower() == proc.info["name"].lower():
            return True
        # logging.info("Process %s is not running", process_name)
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
    print(f"\nPress Ctrl+C to exit")
    main()


# while True:
#     # Check for DBWorker.py to be running
#     if not is_process_running("DBWorker.py"):
#         print("DBWorker.py is not running. Checking RabbitMQ...")
#         rabbitmq_running = is_process_running("rabbitmq-server")
#         try:
#             # If RabbitMQ is running, attempt to restart it. Wait 20-25 seconds for it to restart. If it fails, break the loop and exit. If it doesn't, restart the file.
#             if rabbitmq_running:
#                 print(
#                     "RabbitMQ is running, but DBWorker.py is not. Restarting RabbitMQ"
#                 )
#                 subprocess.Popen(["systemctl", "restart", "rabbitmq-server"])

#                 # check to see if rabbitMQ is able to be restarted. Give it 20 seconds, checking every 5 seconds
#                 waitCount = 4
#                 while (is_process_running("rabbitmq-server") == False) or (
#                     waitCount <= 4
#                 ):
#                     waitCount += 1
#                     keep_waiting(5)
#                 if is_process_running("rabbitmq-server") == False:
#                     logging.critical("RabbitMQ is not running. Exiting...")
#                     message = "RabbitMQ failed to restart! Exiting loop"
#                     logDate = time.strftime("%Y-%m-%d %H:%M:%S")
#                     newlog = f"**Critical**\t[RMQ] - {logDate} - {message}-{e}\n"
#                     with open(logFile, "a") as logFile:
#                         logFile.write(newlog)
#                     break
#                 else:
#                     print("RabbitMQ is running. Restarting DBWorker.py")
#                     subprocess.Popen(
#                         [
#                             "python3",
#                             "/home/alfred/Desktop/IT490-LongSoup/DB/DBWorker.py",
#                         ]
#                     )
#                     message = (
#                         "DBWorker.py experienced an error. Keephopping.py restarted it."
#                     )
#                     logDate = time.strftime("%Y-%m-%d %H:%M:%S")
#                     newlog = f"[RMQ] - {logDate} - {message}-{e}\n"
#                     with open(logFile, "a") as logFile:
#                         logFile.write(newlog)
#         except Exception as e:
#             pass


# while True:
#     # Check if DBWorker.py is running
#     if not is_process_running("DBWorker.py"):
#         print("DBWorker.py is not running. Checking RabbitMQ...")
#         rabbitmq_running = is_process_running("rabbitmq-server")
#         try:
#             if rabbitmq_running:
#                 subprocess.Popen(
#                     ["python3", "/home/alfred/Desktop/IT490-LongSoup/DB/DBWorker.py"]
#                 )
#                 message = "DBWorker.py experienced an error. Keephopping.py restarted it."
#                 logDate = time.strftime("%Y-%m-%d %H:%M:%S")
#                 newlog = f"[RMQ] - {logDate} - {message}-{e}\n"
#                 with open(logFile, "a") as logFile:
#                     logFile.write(newlog)
#         except Exception as e:
#             message = "Error restarting DBWorker.py"
#             logDate = time.strftime("%Y-%m-%d %H:%M:%S")
#             newlog = f"****[CRITICAL]****\t[RMQ] - {logDate} - {message}-{e}\n"
#             with open(logFile, "a") as logFile:
#                 logFile.write(newlog)

#         time.sleep(2)

#     # Check if DBSpotWorker.py is running
#     if not is_process_running("DBSpotWorker.py"):
#         print("DBSpotWorker.py is not running. Restarting...")
#         try:
#             subprocess.Popen(
#                 ["python3", "/home/alfred/Desktop/IT490-LongSoup/DB/DBSpotWorker.py"]
#             )
#             message = (
#                 "DBSpotWorker.py experienced an error. Keephopping.py restarted it."
#             )
#             logDate = time.strftime("%Y-%m-%d %H:%M:%S")
#             newlog = f"[RMQ] - {logDate} - {message}-{e}\n"
#             with open(logFile, "a") as logFile:
#                 logFile.write(newlog)
#         except Exception as e:
#             message = "Error restarting DBSpotWorker.py"
#             logDate = time.strftime("%Y-%m-%d %H:%M:%S")
#             newlog = f"****[CRITICAL]****\t[RMQ] - {logDate} - {message}-{e}\n"
#             with open(logFile, "a") as logFile:
#                 logFile.write(newlog)
#         time.sleep(2)

#     # Sleep for a minute before the next check
#     time.sleep(60)
