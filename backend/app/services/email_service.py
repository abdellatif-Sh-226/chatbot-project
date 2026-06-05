import smtplib
from email.mime.text import MIMEText
from typing import List


class EmailService:
    def __init__(self, smtp_host: str = "", smtp_port: int = 587, smtp_user: str = "", smtp_pass: str = "", from_email: str = "library@smartlib.com"):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_pass = smtp_pass
        self.from_email = from_email

    def send_email(self, to_email: str, subject: str, body: str):
        if not self.smtp_host:
            print(f"[EmailService] SMTP not configured. Would send: {subject} -> {to_email}")
            return
        msg = MIMEText(body, "plain")
        msg["Subject"] = subject
        msg["From"] = self.from_email
        msg["To"] = to_email
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.sendmail(self.from_email, [to_email], msg.as_string())
        except Exception as e:
            print(f"[EmailService] Failed to send email: {e}")

    def notify_due_soon(self, to_email: str, book_title: str, due_date: str):
        self.send_email(to_email, "Book Due Soon", f"Dear user,\n\n'{book_title}' is due on {due_date}. Please return it on time to avoid penalties.\n\n- SmartLib")

    def notify_overdue(self, to_email: str, book_title: str, penalty: float):
        self.send_email(to_email, "Book Overdue", f"Dear user,\n\n'{book_title}' is overdue. Penalty: ${penalty:.2f}. Please return it as soon as possible.\n\n- SmartLib")

    def notify_reservation_confirmed(self, to_email: str, book_title: str):
        self.send_email(to_email, "Reservation Confirmed", f"Dear user,\n\nYour reservation for '{book_title}' has been confirmed.\n\n- SmartLib")
