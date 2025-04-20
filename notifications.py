import os
import logging

# Email notifications
def send_email_notification(to_email, subject, content):
    """
    Send email notification using SendGrid
    """
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content

    try:
        # Get API key from environment
        sendgrid_key = os.environ.get('SENDGRID_API_KEY')
        if not sendgrid_key:
            logging.warning("SENDGRID_API_KEY not found. Email notification not sent.")
            return False
        
        message = Mail(
            from_email=Email("noreply@phulkaricorner.com"),
            to_emails=To(to_email),
            subject=subject
        )
        
        # Set content based on format
        if "<html>" in content:
            message.content = Content("text/html", content)
        else:
            message.content = Content("text/plain", content)
            
        # Send the email
        sg = SendGridAPIClient(sendgrid_key)
        response = sg.send(message)
        
        # Check response
        if response.status_code >= 200 and response.status_code < 300:
            logging.info(f"Email notification sent to {to_email}")
            return True
        else:
            logging.error(f"Failed to send email. Status code: {response.status_code}")
            return False
    except Exception as e:
        logging.error(f"Error sending email notification: {str(e)}")
        return False


# SMS notifications
def send_sms_notification(to_phone, message):
    """
    Send SMS notification using Twilio
    """
    from twilio.rest import Client
    
    try:
        # Get Twilio credentials from environment
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        from_phone = os.environ.get('TWILIO_PHONE_NUMBER')
        
        if not (account_sid and auth_token and from_phone):
            logging.warning("Twilio credentials not found. SMS notification not sent.")
            return False
        
        # Initialize Twilio client
        client = Client(account_sid, auth_token)
        
        # Send the SMS
        sms = client.messages.create(
            body=message,
            from_=from_phone,
            to=to_phone
        )
        
        logging.info(f"SMS notification sent to {to_phone}, SID: {sms.sid}")
        return True
    except Exception as e:
        logging.error(f"Error sending SMS notification: {str(e)}")
        return False


# Push notifications for order status updates
def send_order_status_notification(order_id, status, customer_name, customer_email, customer_phone=None):
    """
    Send notifications when order status changes
    """
    # Email notification
    subject = f"Order #{order_id} Status Update"
    email_content = f"""
    <html>
    <body>
        <h2>Order Status Update</h2>
        <p>Hello {customer_name},</p>
        <p>Your order #{order_id} status has been updated to: <strong>{status}</strong></p>
        <p>You can check your order details by logging into your account.</p>
        <p>Thank you for shopping with Phulkari Corner!</p>
    </body>
    </html>
    """
    
    # Send email notification
    email_sent = send_email_notification(customer_email, subject, email_content)
    
    # SMS notification if phone number provided
    sms_sent = False
    if customer_phone:
        sms_message = f"Phulkari Corner: Your order #{order_id} status has been updated to {status}. Thank you for shopping with us!"
        sms_sent = send_sms_notification(customer_phone, sms_message)
    
    return email_sent, sms_sent


# Delivery tracking notification
def send_tracking_update(order_id, tracking_number, carrier, status, customer_name, customer_email, customer_phone=None):
    """
    Send delivery tracking updates
    """
    # Email notification
    subject = f"Tracking Update for Order #{order_id}"
    email_content = f"""
    <html>
    <body>
        <h2>Delivery Tracking Update</h2>
        <p>Hello {customer_name},</p>
        <p>We have an update on your order #{order_id}:</p>
        <p><strong>Status:</strong> {status}</p>
        <p><strong>Tracking Number:</strong> {tracking_number}</p>
        <p><strong>Carrier:</strong> {carrier}</p>
        <p>You can track your package using the tracking number above on the carrier's website.</p>
        <p>Thank you for shopping with Phulkari Corner!</p>
    </body>
    </html>
    """
    
    # Send email notification
    email_sent = send_email_notification(customer_email, subject, email_content)
    
    # SMS notification if phone number provided
    sms_sent = False
    if customer_phone:
        sms_message = f"Phulkari Corner: Your order #{order_id} is now {status}. Track with {carrier} using tracking #{tracking_number}."
        sms_sent = send_sms_notification(customer_phone, sms_message)
    
    return email_sent, sms_sent