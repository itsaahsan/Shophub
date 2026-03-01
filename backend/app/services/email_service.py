"""SMTP email service for order confirmations."""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings


def send_order_confirmation(email: str, order: dict) -> None:
    """Send an order confirmation email."""
    if not settings.SMTP_HOST:
        print(f"SMTP not configured. Skipping confirmation email to {email}")
        return

    msg = MIMEMultipart()
    msg["From"] = settings.SMTP_USER
    msg["To"] = email
    msg["Subject"] = f"shophub Order Confirmation - #{order['id']}"

    body = f"""
    <h1>Thank you for your order!</h1>
    <p>Order ID: {order['id']}</p>
    <p>Total: ${order['total']:.2f}</p>
    <p>Status: {order['status'].title()}</p>
    <br/>
    <p>We'll notify you when your order ships.</p>
    """
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"Failed to send email: {e}")
