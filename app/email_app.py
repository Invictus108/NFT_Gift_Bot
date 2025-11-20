import requests
import base64
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition, ContentId
import os
from dotenv import load_dotenv

load_dotenv()

def send_template_email(to_email: str, image_url: str):
    """
    Sends a template email with an inline image.
    The image is downloaded, base64-encoded, and embedded via CID.
    """

    # Fetch the image
    try:
        img_request = requests.get(image_url, timeout=5)
        if img_request.status_code != 200:
            print("⚠️ Image URL is not reachable. Status:", img_request.status_code)
            return False
    except Exception as e:
        print("⚠️ Error fetching image:", e)
        return False

    # Encode image as base64
    encoded = base64.b64encode(img_request.content).decode()

    # Guess content type, default to image/png
    content_type = img_request.headers.get("Content-Type", "image/png")

    # HTML uses cid: to refer to the inline image
    html_content = """
    <div style="font-family: Arial; padding: 20px;">
        <h2>Your NFT Gift Awaits 🎁</h2>
        <p>Here's a preview of what you're receiving:</p>
        <img src="cid:nft_image" alt="Gift Image"
             style="width: 300px; border-radius: 8px; margin-top: 10px;">
        <p style="margin-top: 20px;">More details coming soon!</p>
    </div>
    """

    message = Mail(
        from_email="nftgiftbotnotifications@gmail.com",
        to_emails=to_email,
        subject="Your NFT Gift",
        html_content=html_content,
    )

    # Create inline attachment
    attachment = Attachment(
        file_content=FileContent(encoded),
        file_type=FileType(content_type),
        file_name=FileName("nft_image"),
        disposition=Disposition("inline"),
        content_id=ContentId("nft_image"),  # must match cid above
    )

    # Attach image
    message.attachment = attachment  # for single; or message.attachments = [attachment]

    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID"))
        response = sg.send(message)
        print("Email sent:", response.status_code)
        return True
    except Exception as e:
        print("⚠️ Failed to send email:", e)
        return False


if __name__ == "__main__":
    send_template_email(
        "jadencohen333@gmail.com",
        "https://uploads.coppermind.net/Worldsinger_by_Ari_Ibarra.jpg"
    )
