from celery import shared_task, chain
from celery import current_app
from datetime import timedelta
from django.conf import settings
from django.utils.timezone import now
from django.core.mail import send_mail, mail_admins
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Assignment, EmailLog, Abstract

@shared_task
def send_reminder_email(assignment_id, message_type):
    """
    Send a reminder email to the reviewer based on the message type.
    """
    try:
        assignment = Assignment.objects.get(id=assignment_id)
        if assignment.is_completed:
            print(f"Skipping reminder for Assignment {assignment_id}, review already completed.")
            return

        reviewer = assignment.reviewer
        abstract = assignment.abstract

        # Define email subjects and templates
        if message_type == '3_days_reminder':
            subject = "Reminder: 4 days left to review your assigned abstract"
            template = 'emails/3_days_reminder.html'
        elif message_type == '1_day_reminder':
            subject = "Reminder: 1 day left to review your assigned abstract"
            template = 'emails/1_day_reminder.html'
        elif message_type == 'overdue_reminder':
            subject = "Urgent: Review submission overdue!"
            template = 'emails/overdue_reminder.html'
        else:
            return

        # Render email content
        html_message = render_to_string(template, {'abstract': abstract, 'reviewer': reviewer})
        plain_message = strip_tags(html_message)

        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[reviewer.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Assignment.DoesNotExist:
        print(f"Assignment {assignment_id} not found.")


#reminder function
def schedule_reminders(assignment):
    """
    Schedule reminders to reviewers at specific intervals.
    """
    assignment_date = assignment.assigned_at

    # Schedule 3-day reminder
    task_3_days = send_reminder_email.apply_async(
        args=[assignment.id, '3_days_reminder'], eta=assignment_date + timedelta(days=3)
    )
    assignment.task_3_days_id = task_3_days.id

    # Schedule 1-day reminder
    task_1_day = send_reminder_email.apply_async(
        args=[assignment.id, '1_day_reminder'], eta=assignment_date + timedelta(days=6)
    )
    assignment.task_1_day_id = task_1_day.id

    # Schedule overdue reminders daily after 7 days
    overdue_tasks = []
    for day in range(7, 15):
        task = send_reminder_email.apply_async(
            args=[assignment.id, 'overdue_reminder'], eta=assignment_date + timedelta(days=day)
        )
        overdue_tasks.append(task.id)

    assignment.overdue_task_ids = overdue_tasks
    assignment.save()



#cancel reminder
def cancel_reminders(assignment):
    """
    Cancel scheduled reminder tasks when the review is submitted.
    """
    if assignment.task_3_days_id:
        current_app.control.revoke(assignment.task_3_days_id, terminate=True)
    if assignment.task_1_day_id:
        current_app.control.revoke(assignment.task_1_day_id, terminate=True)
    for task_id in assignment.overdue_task_ids:
        current_app.control.revoke(task_id, terminate=True)

    # Clear task IDs
    assignment.task_3_days_id = None
    assignment.task_1_day_id = None
    assignment.overdue_task_ids = []
    assignment.save()


@shared_task
def send_email_task(email_type, subject, recipient, template_name, context, is_admin=False):
    """
    Celery task to send emails and log them.
    """
    abstract = Abstract.object.all()
    html_message = render_to_string(template_name, context)
    plain_message = strip_tags(html_message)

    if is_admin:
        mail_admins(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            fail_silently=False,
        )
    else:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            html_message=html_message,
            fail_silently=False,
        )

    # Log the email
    EmailLog.objects.create(
        recipient=recipient,
        subject=subject,
        plain_message=plain_message,
        html_message=html_message,
        abstract=abstract.abstract_title,
    )


