import smtplib, os, json
from email.message import EmailMessage

SMTP_HOST = os.environ["SMTP_HOST"]
SMTP_PORT = 587
SMTP_EMAIL_ADDRESS = os.environ["SMTP_EMAIL_ADDRESS"]
SMTP_EMAIL_PASSWORD = os.environ["SMTP_EMAIL_PASSWORD"]
GATEWAY_DOWNLOAD_URL = os.environ["GATEWAY_DOWNLOAD_URL"]

def notify(message):
    try:
        message = json.loads(message)
        audio_id = message["audio_id"]
        receiver_address = message["username"]
        full_download_url = f"{GATEWAY_DOWNLOAD_URL}?file_id={audio_id}"

        msg = EmailMessage()
        msg.set_content(f"audio with file_id {audio_id} is now ready at {full_download_url}")
        msg["Subject"] = "Video to Audio Conversion"
        msg["From"] = SMTP_EMAIL_ADDRESS
        msg["TO"] = receiver_address

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as session:
            session.starttls()
            session.login(SMTP_EMAIL_ADDRESS, SMTP_EMAIL_PASSWORD)
            session.send_message(msg, SMTP_EMAIL_ADDRESS, receiver_address)

    except Exception as err:
        return err
