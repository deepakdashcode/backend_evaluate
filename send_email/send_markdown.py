import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import markdown
from dotenv import load_dotenv
import os

load_dotenv()
sender_email = os.getenv('EMAIL')
subject = "Quiz results"
def send_email_to_user(receiver_email: str, markdown_content: str):
    html_content = markdown.markdown(markdown_content)
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg.attach(MIMEText(markdown_content, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, "kvmx vxsf oikv pyox")
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

# markdown_content = "## Quiz Evaluation\n\n**Question 1: Capital of India [2]**\n\n**Marks: 2/2**\n\n**Comment:** Correct answer! \n\n**Question 2: Capital of Odisha [2]**\n\n**Marks: 1/2**\n\n**Comment:**  The correct answer is **Bhubaneswar**. While BBSR is a common abbreviation, it's important to use the full name for formal answers. \n\n**Question 3: Capital of Bihar [3]**\n\n**Marks: 3/3**\n\n**Comment:** Correct answer!\n\n**Total Marks: 6/7** \n\nOverall, you've done well on the quiz! You just need to be careful with abbreviations and ensure you use full names in formal answers. Keep up the good work! \n"


# Convert Markdown to HTML
# html_content = markdown.markdown(markdown_content)











