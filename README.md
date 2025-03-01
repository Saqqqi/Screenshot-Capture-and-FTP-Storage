# Screenshot Capture and FTP Storage

A Python-based tool to automatically capture screenshots of an employee's system and upload them to an FTP server. This tool is designed for remote work monitoring and productivity tracking.

---

## Features
- Automatically captures screenshots at regular intervals.
- Uploads screenshots to a specified FTP server.
- Pauses screenshot capture when the system is locked or inactive.
- Configurable FTP credentials and storage directory.
- Lightweight and easy to integrate.

---

## How It Works
1. The tool captures screenshots of the active screen at predefined intervals.
2. Screenshots are saved locally and then uploaded to the specified FTP server.
3. If the system is locked or inactive, screenshot capture is paused to avoid unnecessary storage usage.
4. The tool resumes capturing screenshots when the system becomes active again.

---

## Configuration
Before running the script, update the following FTP credentials in the `config.py` file:

```python
ftp_host = "your_ftp_host_ip"  # Replace with your FTP server IP
ftp_user = "your_ftp_username"  # Replace with your FTP username
ftp_password = "your_ftp_password"  # Replace with your FTP password
ftp_base_directory = "/screenshots/"  # Replace with your desired FTP directory
