from celery import shared_task


@shared_task(name='Sending simple mail to user')
def send_mail_to_user(
    recipient_email="test@test.com",
    message="If you receive this message contact Developer",
    subject="Password Reset"
):
    try:
        
        # Send email
        result = send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient_email], fail_silently=False)

        return {"success": "Email sent successfully!"}

    except Exception as e:
        return {"error": str(e)}
