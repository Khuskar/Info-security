from datetime import datetime
import os
log_path = "/Users/mac/Desktop/Info-security/lab7/email_log.txt"
with open(log_path, "a") as f:
    f.write(f"Email sent to server owner at {datetime.now()}\n")
