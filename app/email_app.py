import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_template_email(to_email: str, image_url: str):
    """
    Sends a placeholder template email with an image.
    Replace the template later when you're ready.
    """

    # Fetch the image to ensure it exists
    try:
        img_request = requests.get(image_url, timeout=5)
        if img_request.status_code != 200:
            print("⚠️ Image URL is not reachable.")
            return False
    except Exception as e:
        print("⚠️ Error fetching image:", e)
        return False

    # Placeholder HTML template
    html_content = f"""
    <div style="font-family: Arial; padding: 20px;">
        <h2>Your NFT Gift Awaits 🎁</h2>
        <p>Here's a preview of what you're receiving:</p>
        <img src="{image_url}" alt="Gift Image" style="width: 300px; border-radius: 8px; margin-top: 10px;">
        <p style="margin-top: 20px;">More details coming soon!</p>
    </div>
    """

    message = Mail(
        from_email="your-email@example.com",
        to_emails=to_email,
        subject="Your NFT Gift",
        html_content=html_content,
    )

    try:
        sg = SendGridAPIClient("YOUR_SENDGRID_API_KEY")
        response = sg.send(message)
        print("Email sent:", response.status_code)
        return True
    except Exception as e:
        print("⚠️ Failed to send email:", e)
        return False
