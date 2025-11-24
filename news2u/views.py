from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import permission_required
from .models import CustomUser, Publisher, Editor, Journalist, Reader
from .models import Article, Newsletter, AdminApproval, ResetToken
from .models import ArticleSerializer
from .models import JournalistSerializer, PublisherSerializer
from .forms import PublisherRegistrationForm, EditorRegistrationForm
from .forms import JournalistRegistrationForm, ReaderRegistrationForm
from .forms import SelectEditorForm
from .forms import SubmitToPublisherForm, SubscriptionForm
from .forms import ArticleForm, NewsletterForm, LoginFormSerializer
from django.core.mail import send_mass_mail
from django.conf import settings
import secrets
from django.contrib.auth.models import Group
from datetime import datetime, timedelta
from hashlib import sha1
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


# Helper functions to check user roles
def is_journalist(user):
    try:
        return user.customuser.role == 'journalist'
    except CustomUser.DoesNotExist:
        return False


def is_editor(user):
    try:
        return user.customuser.role == 'editor'
    except CustomUser.DoesNotExist:
        return False


def is_publisher(user):
    try:
        return user.customuser.role == 'publisher'
    except CustomUser.DoesNotExist:
        return False


def is_reader(user):
    try:
        return user.customuser.role == 'reader'
    except CustomUser.DoesNotExist:
        return False


# View for home page
def home(request):
    # Display latest 6 articles
    articles = Article.objects.filter(
        status__in=['published_independent', 'published_publisher']
        ).order_by('-published_at')[:9]

    return render(request, 'news2u/home.html', {'articles': articles})


# ============================================================
# REGISTRATION & APPROVAL
# ============================================================


# User Registration for the Publisher role
def register(request):
    return render(request, 'news2u/register.html')


def register_publisher(request):
    if request.method == 'POST':
        form = PublisherRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    new_user = form.save(commit=False)
                    # Until approval is granted
                    new_user.is_active = False
                    new_user.save()

                    # Create CustomUser profile with role
                    custom_user = CustomUser.objects.create(
                        user=new_user,
                        role='publisher',
                        is_approved=False
                    )

                    # Create AdminApproval record
                    AdminApproval.objects.create(
                        user=custom_user,
                        role='publisher',
                        is_approved=False
                    )

                    # Add to Publisher group
                    publisher_group = Group.objects.get(
                        name='Publisher')
                    new_user.groups.add(publisher_group)

                    # Create Publisher profile
                    Publisher.objects.create(
                        user=new_user,
                        publisher_name=form.cleaned_data[
                            'publisher_name'],
                        publisher_description=form.cleaned_data[
                            'publisher_description'],
                        publisher_logo=form.cleaned_data.get(
                            'publisher_logo')
                    )

                    messages.success(
                        request,
                        'Registration successful! An admin '
                        'will review your account in the '
                        'next 24-48 hours.'
                        )
                    return redirect('registration_pending')

            except Exception as e:
                messages.error(
                    request, f'Registration failed: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PublisherRegistrationForm()

    return render(request,
                  'news2u/register_publisher.html', {'form': form})


# User Registration for the Editor role
def register_editor(request):
    if request.method == 'POST':
        form = EditorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    new_user = form.save(commit=False)
                    # Until approval is granted
                    new_user.is_active = False
                    new_user.save()

                # Create CustomUser profile with role
                custom_user = CustomUser.objects.create(
                    user=new_user,
                    role='editor',
                    is_approved=False
                )

                # Create AdminApproval record
                AdminApproval.objects.create(
                    user=custom_user,
                    role='editor',
                    is_approved=False
                )

                # Add to Editor group
                editor_group = Group.objects.get(name='Editor')
                new_user.groups.add(editor_group)

                Editor.objects.create(
                    user=new_user,
                    editor_name=form.cleaned_data['editor_name'],
                    editor_interests=form.cleaned_data['editor_interests'],
                    editor_bio=form.cleaned_data['editor_bio'],
                    editor_photo=form.cleaned_data.get('editor_photo')
                )

                messages.success(
                    request,
                    'Registration successful! An admin will '
                    'review your account in the next '
                    '24-48 hours.'
                )
                return redirect('registration_pending')

            except Exception as e:
                messages.error(
                    request, f'Registration failed: {str(e)}')

    else:
        form = EditorRegistrationForm()

    return render(request,
                  'news2u/register_editor.html', {'form': form})


# User Registration for the Journalist role
def register_journalist(request):
    if request.method == 'POST':
        form = JournalistRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    new_user = form.save(commit=False)
                    # Until approval is granted
                    new_user.is_active = False
                    new_user.save()

                # Create CustomUser profile with role
                custom_user = CustomUser.objects.create(
                    user=new_user,
                    role='journalist',
                    is_approved=False
                )

                # Create AdminApproval record
                AdminApproval.objects.create(
                    user=custom_user,
                    role='journalist',
                    is_approved=False
                )

                # Add to Journalist group
                journalist_group = Group.objects.get(name='Journalist')
                new_user.groups.add(journalist_group)

                Journalist.objects.create(
                    user=new_user,
                    journalist_name=form.cleaned_data['journalist_name'],
                    journalist_bio=form.cleaned_data['journalist_bio'],
                    journalist_photo=form.cleaned_data.get(
                        'journalist_photo')
                    )

                messages.success(
                    request,
                    'Registration successful! An admin will review your'
                    ' account in the next 24-48 hours.'
                    )
                return redirect('registration_pending')

            except Exception as e:
                messages.error(
                    request, f'Registration failed: {str(e)}')

    else:
        form = JournalistRegistrationForm()

    return render(request,
                  'news2u/register_journalist.html', {'form': form})


# User registration for the Reader role
def register_reader(request):
    """ Handle Reader user registration. Readers are immediately
    active"""

    if request.method == 'POST':
        form = ReaderRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    new_user = form.save(commit=False)
                    # Readers are immediately active
                    new_user.is_active = True
                    new_user.email = form.cleaned_data.get('email')
                    new_user.save()

                # Create CustomUser profile with role
                custom_user = CustomUser.objects.create(
                    user=new_user,
                    role='reader',
                    email=new_user.email,
                    is_approved=True
                )

                # Add to Reader group
                reader_group = Group.objects.get(name='Reader')
                new_user.groups.add(reader_group)

                Reader.objects.create(
                    user=new_user,
                    reader_name=form.cleaned_data['reader_name'],
                    reader_interests=form.cleaned_data['reader_interests'],
                    reader_photo=form.cleaned_data.get('reader_photo')
                    )

                messages.success(
                    request,
                    'Registration successful! You can now '
                    'log in and start reading articles.'
                    )
                return redirect('login')

            except Exception as e:
                messages.error(
                    request, f'Registration failed: {str(e)}')

    else:
        form = ReaderRegistrationForm()

    return render(
        request,
        'news2u/register_reader.html',
        {'form': form})


def registration_pending(request):
    return render(request, 'news2u/registration_pending.html')


# View the pending registrations (admin only)
@login_required
@user_passes_test(lambda u: u.is_superuser)
def view_pending_registration(request):
    if request.method == 'GET':
        return render(request, 'news2u/registration_pending.html')


# ============================================================
# # USER AUTHENTICATION (LOGIN, LOGOUT, PASSWORD RESET)
# ============================================================

# User Login
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request,
                                username=username,
                                password=password)

            if user is not None:
                login(request, user)

                if is_publisher(user):
                    return redirect('publisher_dashboard')
                elif is_editor(user):
                    return redirect('editor_dashboard')
                elif is_journalist(user):
                    return redirect('journalist_dashboard')
                elif is_reader(user):
                    return redirect('reader_dashboard')
                else:
                    return redirect('home')
    else:
        form = AuthenticationForm()

    return render(request, 'news2u/login.html', {'form': form})


# User Logout
def user_logout(request):
    if request.user.is_authenticated:  # Better check than is not None
        # Clear pending messages
        storage = messages.get_messages(request)
        storage.used = True

        logout(request)
        messages.success(request, 'You have been logged out successfully.')

    return redirect('login')


# Reset Password
def generate_reset_url(user):
    domain = "http://127.0.0.1:8000/"
    app_name = "news2u"
    url = f"{domain}{app_name}/reset_password/"
    token = str(secrets.token_urlsafe(16))
    expiry_date = timezone.now() + timedelta(minutes=5)
    reset_token = ResetToken.objects.create(
        user=user,
        token=sha1(token.encode()).hexdigest(),
        expiry_date=expiry_date
        )
    url += f"{token}/"
    return url


# Build an email to send email to user with reset link
def build_email(user, reset_url):
    subject = "Password Reset"
    user_email = user.email
    domain_email = "example@domain.com"
    body = (
        f"Hi {user.username},\nHere is your link to reset your"
        f"password: {reset_url}"
    )
    email = EmailMessage(subject, body, domain_email, [user_email])
    return email


# Take user to the forgot password page
def forgot_password(request):
    return render(request, 'news2u/forgot_password.html')


# Send password reset link to user's email
def send_password_reset(request):
    user_email = request.POST.get('email')
    user = User.objects.get(email=user_email)
    url = generate_reset_url(user)
    email = build_email(user, url)
    email.send()

    messages.success(
        request, 'Password reset link has been sent to '
        'your email.')
    return redirect(reverse('login'))


# Password Reset Confirmation
def reset_password(request, token):
    hashed_token = sha1(token.encode()).hexdigest()
    reset_token = get_object_or_404(ResetToken, token=hashed_token)

    try:
        if reset_token.expiry_date < timezone.now():
            return render(
                request,
                'news2u/reset_password.html',
                {'error': 'Token has expired'}
                )

        if request.method == 'POST':
            new_password = request.POST['new_password']
            password_confirm = request.POST.get('password_confirm')

            if new_password == password_confirm:
                reset_token.user.set_password(new_password)
                reset_token.user.save()
                reset_token.delete()
                messages.success(
                    request, 'Password has been reset successfully.')
                return redirect(reverse('login'))

            else:
                return render(
                    request,
                    'news2u/reset_password.html',
                    {'error': 'Passwords do not match'}
                    )
        return render(request, 'news2u/reset_password.html')

    except ResetToken.DoesNotExist:
        return render(request, 'news2u/reset_password.html',
                      {'error': 'Invalid token'})


# ============================================================
# EMAIL NOTIFICATIONS (WHEN EDITOR APPROVES ARTICLE/NEWSLETTER)
# ============================================================

def send_article_email(article):
    """ Send email to subscribers when article is approved """

    print("=== SEND ARTICLE EMAIL PRINT TO CONSOLE ===")
    print(f"Article: {article.article_title}")
    print(f"Status: {article.status}")
    print(f"Journalist: {article.journalist.journalist_name}")
    print(f"Publisher: {article.publisher}")

    # For articles ready to publish or published independently -
    # send to journalist subscribers
    if article.status == 'ready_to_publish':
        subscribed_readers = CustomUser.objects.filter(
            role='reader',
            subscribed_journalists=article.journalist
        )
        print("Checking journalist subscribers...")

    # For articles published via publisher -
    # send to publisher subscribers
    elif article.status == 'ready_to_publish':
        subscribed_readers = CustomUser.objects.filter(
            role='reader',
            subscribed_publishers=article.publisher
        )
        print("Checking publisher subscribers...")

    else:
        print(f"Status {article.status} doesn't match - not sending")
        return

    print(f"Subscribers found: {subscribed_readers.count()}")
    for reader in subscribed_readers:
        email = reader.user.email
        if email:
            print(f"  - {reader.user.username}: {email}")

    # If there are NO subscribers
    if not subscribed_readers.exists():
        print("No subscribers - exiting")
        return

    # Prepare email
    subject = f"New Article: {article.article_title}"
    message = f"""
    A new article by {article.journalist.journalist_name} \
        has just been released!

Title: {article.article_title}

{article.article_content[:200]}...

Read the full article on News2U.
    """

    sent_count = 0
    for reader in subscribed_readers:
        email = reader.user.email
        if email:
            print(f"Sending email to: {email}")
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [reader.email],
                    fail_silently=False  # Show errors!
                )
                sent_count += 1
                print("Sent!")
            except Exception as e:
                print(f"Error: {e}")

    print(f"Total emails sent: {sent_count}")


# Send newsletter email (Only Publisher & Journalist can send)
def send_newsletter_email(newsletter):
    """ Send newsletter to subscribers via email and after approval
      by editor.
      """

    # For newsletter published independently by journalists

    print("=== SEND NEWSLETTER EMAIL DEBUG ===")
    print(f"Newsletter: {newsletter.newsletter_title}")
    print(f"Status: {newsletter.status}")
    print(f"Journalist: {newsletter.journalist}")
    print(f"Publisher: {newsletter.publisher}")

    # For newsletter published independently by journalists
    if newsletter.status == 'ready_to_publish':
        print("Newsletter is independent")
        subscribed_readers = CustomUser.objects.filter(
            role='reader',
            subscribed_journalists=newsletter.journalist
        )
        print(f"Subscribers found: {subscribed_readers.count()}")

    # For newsletters published via publisher
    elif newsletter.status == 'published_newsletter_by_publisher':
        print("Newsletter is via publisher")
        subscribed_readers = CustomUser.objects.filter(
            role='reader',
            subscribed_publishers=newsletter.publisher
        )
        print(f"Subscribers found: {subscribed_readers.count()}")
    else:
        print(f"Newsletter status ' "
              f"{newsletter.status}' doesn't match - exiting")
        return

    # If there are NO subscribers
    if not subscribed_readers.exists():
        return

    # Prepare email
    subject = f"New Newsletter: {newsletter.newsletter_title}"

    # Build articles section with previews
    articles_text = ""
    if newsletter.articles.exists():
        articles_text = "\n\n--- Featured Articles ---\n\n"
        for article in newsletter.articles.all():
            articles_text += f"{article.article_title}\n"
            articles_text += f"By {article.journalist.journalist_name}\n"
            articles_text += f"{article.article_content[:100]}...\n\n"

    message = f"""
    A new newsletter by {newsletter.journalist.journalist_name} has
    just been released.

    {newsletter.newsletter_title}
    {'-' * 50}

    {newsletter.newsletter_content[:200]}...
    {articles_text}

    Visit News2U to read the full newsletter and articles.
    """

    # Create email list
    emails = []
    for reader in subscribed_readers:
        if reader.email:  # Check if they have an email
            emails.append((
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [reader.email]
            ))

    if emails:
        send_mass_mail(emails, fail_silently=True)


# ============================================================
# DASHBOARDS
# ============================================================

# Publisher Dashboard
@login_required
@user_passes_test(is_publisher)
def publisher_dashboard(request):
    """ Show publisher dashboard with stats on published content """

    try:
        publisher = Publisher.objects.get(user=request.user)
    except Publisher.DoesNotExist:
        messages.error(request, "Publisher profile not found.")
        return redirect('home')

    # Show statistics for the dashboard
    total_published_articles = Article.objects.filter(
        publisher=publisher,
        status='published_publisher').count()
    total_newsletters = Newsletter.objects.filter(
        publisher=publisher,
        status='published_newsletter_by_publisher').count()
    total_journalists = publisher.journalists.count()
    total_editors = publisher.editors.count()
    total_subscribers = publisher.reader_subscribers.count()
    total_requests = Article.objects.filter(
        publisher=publisher,
        status='in_review_publisher').count()
    total_draft_newsletters = Newsletter.objects.filter(
        publisher=publisher,
        status='draft').count()

    return render(request, 'news2u/publisher_dashboard.html', {
        'total_published_articles': total_published_articles,
        'total_newsletters': total_newsletters,
        'total_journalists': total_journalists,
        'total_editors': total_editors,
        'total_subscribers': total_subscribers,
        'total_requests': total_requests,
        'total_draft_newsletters': total_draft_newsletters
    })


# Editor Dashboard
@login_required
@user_passes_test(is_editor)
def editor_dashboard(request):
    try:
        editor = Editor.objects.get(user=request.user)
    except Editor.DoesNotExist:
        messages.error(request, "Editor profile not found.")
        return redirect('home')

    # Show statistics for the dashboard
    total_articles = Article.objects.filter(
        editor=editor,
        status__in=['published_independent', 'published_publisher']).count()
    total_newsletters = Newsletter.objects.filter(
        status__in=['ready_to_publish',
                    'published_newsletter',
                    'published_newsletter_by_publisher'],
        editor=editor).count()
    total_journalists = editor.journalists.count()
    total_publishers = editor.publishers.count()
    edit_requests = Article.objects.filter(
        editor=editor,
        status='awaiting_editor').count() + Newsletter.objects.filter(
        editor=editor,
        status='awaiting_editor').count()
    accepted_requests = Article.objects.filter(
        editor=editor,
        status='ready_to_publish').count()
    declined_requests = Article.objects.filter(
        editor=editor,
        status='revise').count()
    accepted_newsletters = Newsletter.objects.filter(
        editor=editor,
        status='ready_to_publish').count()

    return render(request, 'news2u/editor_dashboard.html', {
        'total_articles': total_articles,
        'total_newsletters': total_newsletters,
        'total_journalists': total_journalists,
        'total_publishers': total_publishers,
        'edit_requests': edit_requests,
        'accepted_requests': accepted_requests,
        'declined_requests': declined_requests,
        'accepted_newsletters': accepted_newsletters
    })


# Journalist Dashboard
@login_required
@user_passes_test(is_journalist)
def journalist_dashboard(request):
    try:
        journalist = Journalist.objects.get(user=request.user)
    except Journalist.DoesNotExist:
        messages.error(request, "Journalist profile not found.")
        return redirect('home')

    # Show statistics for the dashboard
    total_newsletters = Newsletter.objects.filter(
        journalist=journalist).count()
    total_editors = journalist.editors.count()
    total_publishers = journalist.publishers.count()
    total_subscribers = CustomUser.objects.filter(
        role='reader',
        subscribed_journalists=journalist
    ).count()

    # Get counts
    draft_articles_count = Article.objects.filter(
        journalist=journalist,
        status__in=['draft', 'revise']).count()

    submitted_articles_count = Article.objects.filter(
        journalist=journalist, status='awaiting_editor').count()

    published_articles_count = Article.objects.filter(
        journalist=journalist,
        status__in=['published_independent',
                    'published_publisher']).count()

    submitted_to_publisher_count = Article.objects.filter(
        journalist=journalist, status='in_review_publisher').count()

    submitted_newsletters_count = Newsletter.objects.filter(
        journalist=journalist, status='awaiting_editor').count()

    published_newsletters_count = Newsletter.objects.filter(
        journalist=journalist,
        status='published_newsletter').count()

    draft_newsletters_count = Newsletter.objects.filter(
        journalist=journalist, status='draft').count()

    accepted_articles = Article.objects.filter(
        journalist=journalist, status='ready_to_publish').count()

    accepted_newsletters = Newsletter.objects.filter(
        journalist=journalist, status='ready_to_publish').count()

    return render(request, 'news2u/journalist_dashboard.html', {
        # Show statistics
        'total_newsletters': total_newsletters,
        'total_editors': total_editors,
        'total_publishers': total_publishers,
        'total_subscribers': total_subscribers,
        # Show counts
        'journalist': journalist,
        'draft_articles_count': draft_articles_count,
        'submitted_articles_count': submitted_articles_count,
        'published_articles_count': published_articles_count,
        'draft_newsletters_count': draft_newsletters_count,
        'accepted_articles': accepted_articles,
        'submitted_newsletters_count': submitted_newsletters_count,
        'published_newsletters_count': published_newsletters_count,
        'submitted_to_publisher_count': submitted_to_publisher_count,
        'accepted_newsletters': accepted_newsletters,
    })


# Reader Dashboard
@login_required
@user_passes_test(is_reader)
@permission_required('news2u.view_article', raise_exception=True)
def reader_dashboard(request):
    """ Show reader dashboard with stats on subscribed content """
    try:
        reader = Reader.objects.get(user=request.user)
        customuser = request.user.customuser
    except Reader.DoesNotExist:
        messages.error(request, "Reader profile not found.")
        return redirect('home')
    except CustomUser.DoesNotExist:
        messages.error(request, "User profile not found.")
        return redirect('home')

    # Articles from subscribed journalists and publishers
    total_articles = Article.objects.filter(
        journalist__in=customuser.subscribed_journalists.all(),
        is_approved=True
        ).count() + Article.objects.filter(
            publisher__in=customuser.subscribed_publishers.all(),
            is_approved=True
            ).count()

    # Newsletters from subscribed journalists and publishers
    total_newsletters = Newsletter.objects.filter(
        journalist__in=customuser.subscribed_journalists.all(),
        is_approved=True
        ).count() + Newsletter.objects.filter(
            publisher__in=customuser.subscribed_publishers.all(),
            is_approved=True
            ).count()

    context = {
        'reader': reader,  # Now it's used!
        'customuser': customuser,
        }

    # Subscription counts
    total_journalists = customuser.subscribed_journalists.count()
    total_publishers = customuser.subscribed_publishers.count()

    return render(request, 'news2u/reader_dashboard.html', {
        'total_articles': total_articles,
        'total_newsletters': total_newsletters,
        'total_journalists': total_journalists,
        'total_publishers': total_publishers,
        'context': context,
    })


# ============================================================
# SHARED VIEWS FOR PUBLISHED CONTENT
# ============================================================

# View Published Articles based on user role
@login_required
@user_passes_test(lambda u:
                  is_journalist(u) or
                  is_editor(u) or
                  is_publisher(u) or
                  is_reader(u))
@permission_required(
    'news2u.view_article', raise_exception=True)
def my_published_articles(request):
    """Show published articles based on user role"""

    user = request.user

    if is_journalist(user):
        journalist = Journalist.objects.get(user=user)
        articles = Article.objects.filter(
            journalist=journalist,
            status__in=['published_independent', 'published_publisher'],
        )
        role_label = "Your Published Articles"

    elif is_editor(user):
        editor = Editor.objects.get(user=user)
        articles = Article.objects.filter(
            editor=editor,
            status__in=['published_independent', 'published_publisher'],
            is_approved=True
        )
        role_label = "Articles You Approved"

    elif is_publisher(user):
        publisher = Publisher.objects.get(user=user)
        articles = Article.objects.filter(
            publisher=publisher,
            status='published_publisher',
            is_approved=True
        )
        role_label = "Published Articles from Your Publication House"

    elif is_reader(user):
        custom_user = user.customuser
        articles = Article.objects.filter(
            journalist__in=custom_user.subscribed_journalists.all(),
            status__in=['published_independent', 'published_publisher']
        ) | Article.objects.filter(
            publisher__in=custom_user.subscribed_publishers.all(),
            status='published_publisher'
        )
        role_label = "Articles from Your Subscriptions"

    else:
        articles = Article.objects.none()
        role_label = "No Articles to Read yet. Are you subscribed?"

    return render(request, 'news2u/my_published_articles.html', {
        'articles': articles,
        'role_label': role_label,
        'is_reader': is_reader(request.user),
        'is_journalist': is_journalist(request.user),
        'is_editor': is_editor(request.user),
        'is_publisher': is_publisher(request.user),
    })


# View Published Newsletters based on user role
@login_required
@user_passes_test(lambda u:
                  is_journalist(u) or
                  is_editor(u) or
                  is_publisher(u) or
                  is_reader(u))
@permission_required(
    'news2u.view_newsletter', raise_exception=True)
def my_published_newsletters(request):
    """Show published newsletters based on user role"""

    user = request.user

    if is_journalist(user):
        journalist = Journalist.objects.get(user=user)
        newsletters = Newsletter.objects.filter(
            journalist=journalist,
            status='published_newsletter'
        ).order_by('-published_at')
        role_label = "Your Published Newsletters"

    elif is_editor(user):
        editor = Editor.objects.get(user=user)
        newsletters = Newsletter.objects.filter(
            editor=editor,
            is_approved=True,
        ).order_by('-published_at')
        role_label = "Newsletters You Approved"

    elif is_publisher(user):
        publisher = Publisher.objects.get(user=user)
        newsletters = Newsletter.objects.filter(
            publisher=publisher,
            status='published_newsletter_by_publisher'
        ).order_by('-published_at')
        role_label = "Published Newsletters from Your Publication House"

    elif is_reader(user):
        custom_user = user.customuser
        newsletters = Newsletter.objects.filter(
            journalist__in=custom_user.subscribed_journalists.all(),
            is_approved=True
        ) | Newsletter.objects.filter(
            publisher__in=custom_user.subscribed_publishers.all(),
            status__in=['published_newsletter',
                        'published_newsletter_by_publisher']
        )
        newsletters = newsletters.order_by('-published_at')
        role_label = "Newsletters from Your Subscriptions"

    else:
        newsletters = Newsletter.objects.none()
        role_label = "No Newsletters"

    return render(request, 'news2u/my_published_newsletters.html', {
        'newsletters': newsletters,
        'role_label': role_label,
        'is_journalist': is_journalist(user),
        'is_editor': is_editor(user),
        'is_publisher': is_publisher(user),
        'is_reader': is_reader(user),
    })


# ============================================================
# JOURNALIST FUNCTIONS
# ============================================================

# Create Article
@login_required
@user_passes_test(is_journalist)
@permission_required('news2u.add_article', raise_exception=True)
def create_article(request):
    """ Journalist is the only user that can create an article.
    - Can publish independently
    - Can submit and publish via publisher
    - All articles need to be edited by an editor and approved
    before publication
    """

    # Clear old messages
    storage = messages.get_messages(request)
    for _ in storage:
        pass

    try:
        journalist = Journalist.objects.get(user=request.user)
    except Journalist.DoesNotExist:
        messages.error(request, "Journalist profile not found.")
        return redirect('home')

    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.journalist = journalist
            article.status = 'draft'
            article.save()

            messages.success(request, 'Article created!')
            return redirect('article_detail', article_id=article.id)
    else:
        form = ArticleForm()

    return render(request, 'news2u/create_article.html', {'form': form})


# View Article Details
@login_required
@user_passes_test(is_journalist)
@permission_required('news2u.view_article', raise_exception=True)
def article_detail(request, article_id):
    """ View article details """

    try:
        journalist = Journalist.objects.get(user=request.user)
        article = Article.objects.get(
            id=article_id,
            journalist=journalist)
    except (Journalist.DoesNotExist, Article.DoesNotExist):
        messages.error(request, "Article not found.")
        return redirect('journalist_dashboard')

    return render(request, 'news2u/article_detail.html',
                  {'article': article})


# Edit Article by Journalist or Editor
@login_required
@user_passes_test(lambda u: is_journalist(u) or is_editor(u))
@permission_required('news2u.change_article', raise_exception=True)
def edit_article(request, article_id):
    """ Journalists or Editors can edit articles:
    - Journalists can edit draft articles
    - Editors can edit articles awaiting their review"""

    user = request.user
    article = None

    # Fetch the article based on user role
    # Journalists can edit their own draft articles
    # Editors can edit articles assigned to them awaiting review

    try:
        if is_journalist(user):
            journalist = Journalist.objects.get(user=request.user)
            article = Article.objects.get(
                id=article_id,
                journalist=journalist,
                status__in=['draft', 'revise']
                )

        elif is_editor(user):
            editor = Editor.objects.get(user=request.user)
            article = Article.objects.get(
                id=article_id,
                editor=editor,
                status='awaiting_editor'
                )

        else:
            messages.error(request, "Access denied.")
            return redirect('home')

    except (Journalist.DoesNotExist,
            Editor.DoesNotExist,
            Article.DoesNotExist):

        messages.error(request, "Article not found.")
        if is_journalist(user):
            return redirect('journalist_dashboard')
        else:
            return redirect('editor_dashboard')

    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, 'Article Updated!')
            if is_journalist(user):
                return redirect('article_detail', article_id=article.id)
            if is_editor(user):
                return redirect('view_requests')
            else:
                return redirect('home')
    else:
        form = ArticleForm(instance=article)

    return render(request, 'news2u/edit_article.html',
                  {'form': form,
                   'article': article,
                   is_journalist: is_journalist(user),
                   is_editor: is_editor(user)
                   })


# Select Editor for Article
@login_required
@user_passes_test(is_journalist)
def select_editor(request, article_id):
    """ All articles require approval by an editor """

    user = request.user
    article = None
    journalist = None
    publisher = None

    # Fetch the article based on user role
    # Journalists can select editor for their own draft articles

    try:
        if is_journalist(user):
            journalist = Journalist.objects.get(user=request.user)
            article = Article.objects.get(
                id=article_id,
                journalist=journalist,
                status__in=['draft', 'revise']
                )

        elif is_publisher(user):
            publisher = Publisher.objects.get(user=request.user)
            article = Article.objects.get(
                id=article_id,
                publisher=publisher,
                status='draft'
                )

        else:
            messages.error(request, "Access denied.")
            return redirect('home')

    except (Journalist.DoesNotExist,
            Publisher.DoesNotExist,
            Article.DoesNotExist):
        messages.error(request, "Publication not found.")

        if is_journalist(request.user):
            return redirect('journalist_dashboard')
        else:
            return redirect('publisher_dashboard')

    if request.method == 'POST':
        form = SelectEditorForm(request.POST)
        if form.is_valid():
            article.editor = form.cleaned_data['editor']
            article.status = 'awaiting_editor'
            article.submitted_at = datetime.now()
            article.save()

            messages.success(request,
                             f'Article sent to '
                             f'{article.editor.editor_name} for review.')
            return redirect('article_submit_success')
    else:
        form = SelectEditorForm()

    return render(request, 'news2u/select_editor.html', {
        'form': form,
        'article': article,
        'editor': article.editor
    })


# Select Editor for Newsletter
@login_required
@user_passes_test(lambda u: is_journalist(u) or is_publisher(u))
def select_editor_newsletter(request, newsletter_id):
    """ All newsletters require approval by an editor """

    user = request.user
    newsletter = None
    journalist = None
    publisher = None

    # Fetch the article based on user role
    # Journalists and publishers can select an editor for their own
    # draft newsletters

    try:
        if is_journalist(user):
            journalist = Journalist.objects.get(user=request.user)
            newsletter = Newsletter.objects.get(
                id=newsletter_id,
                journalist=journalist,
                status='draft'
                )

        elif is_publisher(user):
            publisher = Publisher.objects.get(user=request.user)
            newsletter = Newsletter.objects.get(
                id=newsletter_id,
                publisher=publisher,
                status='draft'
                )

        else:
            messages.error(request, "Access denied.")
            return redirect('home')

    except (Journalist.DoesNotExist,
            Publisher.DoesNotExist,
            Newsletter.DoesNotExist):
        messages.error(request, "Publication not found.")

        if is_journalist(request.user):
            return redirect('journalist_dashboard')
        else:
            return redirect('publisher_dashboard')

    if request.method == 'POST':
        form = SelectEditorForm(request.POST)
        if form.is_valid():
            newsletter.editor = form.cleaned_data['editor']
            newsletter.status = 'awaiting_editor'
            newsletter.submitted_at = datetime.now()
            newsletter.save()

            messages.success(request,
                             f'Newsletter sent to'
                             f'{newsletter.editor.editor_name} for review.')
            return redirect('newsletter_submit_success')
    else:
        form = SelectEditorForm()

    return render(request, 'news2u/select_editor_newsletter.html', {
        'form': form,
        'newsletter': newsletter,
        'editor': newsletter.editor,
        is_journalist: is_journalist(user),
        is_publisher: is_publisher(user)
    })


# Newsletter submit success
@login_required
@user_passes_test(lambda u: is_journalist(u) or is_publisher(u))
def newsletter_submit_success(request):
    return render(request, 'news2u/newsletter_submit_success.html')


# Journalist publish independently (after approval by editor)
@login_required
@user_passes_test(is_journalist)
def publish_independent(request, article_id):
    """ Journalist can publish article independently."""

    try:
        journalist = Journalist.objects.get(user=request.user)
        article = Article.objects.get(
            id=article_id,
            journalist=journalist,
            status='ready_to_publish')
    except (Journalist.DoesNotExist, Article.DoesNotExist):
        messages.error(request, "Article not found.")
        return redirect('journalist_dashboard')

    if request.method == 'POST':
        article.status = 'published_independent'
        article.published_at = datetime.now()
        article.publisher = None  # No publisher for independent
        article.save()

        messages.success(request, 'Article published independently!')
        return redirect('journalist_dashboard')

    return render(
        request,
        'news2u/publish_independent.html',
        {'article': article}
        )


# View Published Article
@login_required
@user_passes_test(lambda u: is_journalist(u) or
                  is_editor(u) or
                  is_publisher(u) or
                  is_reader(u))
@permission_required('news2u.view_article', raise_exception=True)
def view_published_article(request, article_id):
    """Show published articles for journalist"""

    try:
        article = Article.objects.get(
            id=article_id,
            status__in=['published_independent', 'published_publisher']
        )

    except Article.DoesNotExist:
        messages.error(request, "Article not found.")
        return redirect('home')

    return render(request, 'news2u/view_published_article.html', {
        'article': article
    })


# View Submitted Articles to Editor
@login_required
@user_passes_test(is_journalist)
@permission_required('news2u.view_article', raise_exception=True)
def view_submitted_articles(request):
    """Show submitted articles for journalist"""

    try:
        journalist = Journalist.objects.get(user=request.user)
        articles = Article.objects.filter(
            journalist=journalist,
            status__in=['awaiting_editor', 'in_review_publisher']
        ).order_by('-submitted_at')
    except Journalist.DoesNotExist:
        messages.error(request, "Journalist profile not found.")
        return redirect('home')

    return render(request, 'news2u/view_submitted_articles.html', {
        'articles': articles
    })


# Journalist submit to publisher (after approval by editor)
@login_required
@user_passes_test(is_journalist)
def submit_to_publisher(request, article_id):
    """ Journalist can submit article to a publisher for publication."""

    try:
        journalist = Journalist.objects.get(user=request.user)
        article = Article.objects.get(id=article_id,
                                      journalist=journalist,
                                      status='ready_to_publish')
    except (Journalist.DoesNotExist, Article.DoesNotExist):
        messages.error(request, "Article not found.")
        return redirect('journalist_dashboard')

    if request.method == 'POST':
        form = SubmitToPublisherForm(request.POST)
        if form.is_valid():
            article.publisher = form.cleaned_data['publisher']
            article.status = 'in_review_publisher'
            article.published_at = datetime.now()
            article.save()

            messages.success(request,
                             f'Article submitted to '
                             f'{article.publisher.publisher_name}'
                             f' for publication!')
            return redirect('journalist_dashboard')
    else:
        form = SubmitToPublisherForm()

    return render(request, 'news2u/submit_to_publisher.html', {
        'form': form,
        'article': article
    })


# Article published by Publication House
@login_required
@user_passes_test(is_publisher)
def published_by_publisher(request, article_id):
    """ Publisher can publish articles assigned to them."""

    try:
        publisher = Publisher.objects.get(user=request.user)
        article = Article.objects.get(
            id=article_id,
            publisher=publisher,
            status='ready_to_publish')
    except (Publisher.DoesNotExist, Article.DoesNotExist):
        messages.error(request, "Article not found.")
        return redirect('publish_success')

    if request.method == 'POST':
        article.status = 'published_publisher'
        article.published_at = datetime.now()
        article.save()

        messages.success(request,
                         f'Article "{article.article_title}" published!')
        return redirect('publisher_dashboard')

    return render(
        request,
        'news2u/published_by_publisher.html',
        {'article': article}
        )


# Publish Success Message
@login_required
@user_passes_test(lambda u: is_journalist(u) or is_publisher(u))
def publish_success(request):
    return render(request, 'news2u/publish_success.html')


# Newsletter published independently by Journalist
@login_required
@user_passes_test(is_journalist)
def publish_newsletter(request, newsletter_id):
    """ Journalist can publish newsletter independently."""

    try:
        journalist = Journalist.objects.get(user=request.user)
        newsletter = Newsletter.objects.get(
            id=newsletter_id,
            journalist=journalist,
            status='ready_to_publish')
    except (Journalist.DoesNotExist, Newsletter.DoesNotExist):
        messages.error(request, "Newsletter not found.")
        return redirect('journalist_dashboard')

    if request.method == 'POST':
        newsletter.status = 'published_newsletter'
        newsletter.published_at = datetime.now()
        newsletter.publisher = None  # No publisher for independent
        newsletter.save()

        messages.success(request, 'Newsletter published independently!')
        return redirect('journalist_dashboard')

    return render(
        request,
        'news2u/publish_newsletter.html',
        {'newsletter': newsletter}
        )


# Newsletter published by Publication House
@login_required
@user_passes_test(is_publisher)
def publish_newsletter_by_publisher(request, newsletter_id):
    """ Publisher can publish newsletters assigned to them."""
    try:
        publisher = Publisher.objects.get(user=request.user)
        newsletter = Newsletter.objects.get(
            id=newsletter_id,
            publisher=publisher,
            status='ready_to_publish')
    except (Publisher.DoesNotExist, Newsletter.DoesNotExist):
        messages.error(request, "Newsletter not found.")
        return redirect('publish_success')

    if request.method == 'POST':
        newsletter.status = 'published_newsletter_by_publisher'
        newsletter.published_at = datetime.now()
        newsletter.save()

        # Send email to subscribers
        send_newsletter_email(newsletter)

        messages.success(
            request,
            f'Newsletter "{newsletter.newsletter_title}" published!')
        return redirect('publisher_dashboard')

    return render(
        request,
        'news2u/publish_newsletter_by_publisher.html',
        {'newsletter': newsletter}
        )


@login_required
@user_passes_test(lambda u: is_journalist(u) or is_editor(u))
def view_published_newsletter(request, newsletter_id):
    """Show published newsletters for journalist"""

    try:
        newsletter = Newsletter.objects.get(
            id=newsletter_id,
            status__in=['published_newsletter',
                        'published_newsletter_by_publisher']
        )

    except Newsletter.DoesNotExist:
        messages.error(request, "Newsletter not found.")
        return redirect('home')

    return render(request, 'news2u/view_published_newsletter.html', {
        'newsletter': newsletter
    })


# View Draft Articles
@login_required
@user_passes_test(lambda u: is_journalist(u) or is_editor(u))
@permission_required('news2u.view_article', raise_exception=True)
def draft_articles(request):
    """Show draft articles for journalist OR editor"""

    if is_journalist(request.user):
        try:
            journalist = Journalist.objects.get(user=request.user)
            articles = Article.objects.filter(
                journalist=journalist,
                status__in=['draft', 'revise']
            ).order_by('-submitted_at')
        except Journalist.DoesNotExist:
            messages.error(request, "Journalist profile not found.")
            return redirect('home')

    elif is_editor(request.user):
        try:
            editor = Editor.objects.get(user=request.user)
            # Editor sees articles that need revision
            articles = Article.objects.filter(
                editor=editor,
                status='revise'
            ).order_by('-submitted_at')
        except Editor.DoesNotExist:
            messages.error(request, "Editor profile not found.")
            return redirect('home')

    else:
        messages.error(request, "Access denied.")
        return redirect('home')

    return render(request, 'news2u/draft_articles.html', {
        'articles': articles,
        'is_editor': is_editor(request.user),
        'is_journalist': is_journalist(request.user),
    })


# Success page after article submission
@login_required
@user_passes_test(is_journalist)
def article_submit_success(request):
    return render(request, 'news2u/article_submit_success.html')


# ============================================================
# -- EDITOR FUNCTIONS -- ##
# ============================================================

# Review Article
@login_required
@user_passes_test(is_editor)
def review_article(request, article_id):
    """ Editor is the only role that can approve articles.
    Editor can:
    - view
    - update
    - delete
    """

    try:
        editor = Editor.objects.get(user=request.user)
        article = Article.objects.get(
            id=article_id,
            editor=editor,
            status='awaiting_editor')
    except (Editor.DoesNotExist, Article.DoesNotExist):
        messages.error(request, "Article not found.")
        return redirect('view_requests')

    if request.method == 'POST':
        action = request.POST.get('action')
        editor_comments = request.POST.get('editor_comments', '')

        if action == 'approve':
            article.status = 'ready_to_publish'
            article.is_approved = False
            article.editor = None
            article.editor_comments = editor_comments
            article.save()
            messages.success(
                request,
                'Article approved! '
                'Journalist can now publish.')

        elif action == 'edit':
            article.status = 'in_review'
            article.editor_comments = editor_comments
            article.save()
            messages.info(
                request,
                'Article edited by editor.')

        elif action == 'revise':
            article.status = 'revise'
            article.editor_comments = editor_comments
            article.save()
            messages.info(
                request,
                'Article sent back to journalist '
                'for revisions.')

        return redirect('view_requests')

    return render(request, 'news2u/review_article.html', {
        'article': article})


# Accept/Approve Article
@login_required
@user_passes_test(is_editor)
@permission_required('news2u.change_article', raise_exception=True)
def accept_article(request, article_id):
    """ Editor can approve articles assigned to them."""

    try:
        editor = Editor.objects.get(user=request.user)
        article = Article.objects.get(
            id=article_id,
            editor=editor,
            status='awaiting_editor')
    except (Editor.DoesNotExist, Article.DoesNotExist):
        messages.error(request, "Article not found.")
        return redirect('view_requests')

    if request.method == 'POST':
        action = request.POST.get('action')
        editor_comments = request.POST.get('editor_comments', '')

        if action == 'approve':
            article.status = 'ready_to_publish'
            article.is_approved = True
            article.editor_comments = editor_comments
            article.save()

            # Send email to subscribers
            send_article_email(article)

            messages.success(request,
                             f'Article "{article.article_title}"'
                             f'approved!')
            return redirect('view_requests')

        elif action == 'edit':
            article.status = 'draft'
            article.editor_comments = editor_comments
            article.save()

    return render(
        request,
        'news2u/accept_article.html',
        {'article': article}
        )


# View Accepted Articles
@login_required
@user_passes_test(lambda u: is_editor(u) or is_journalist(u))
@permission_required('news2u.view_article', raise_exception=True)
def view_accepted_articles(request):
    """Show accepted articles journalist"""

    user = request.user

    try:
        if is_editor(user):
            editor = Editor.objects.get(user=request.user)
            articles = Article.objects.filter(
                editor=editor,
                status='ready_to_publish'
            ).order_by('-submitted_at')

            accepted_articles = Article.objects.filter(
                editor=editor,
                status='ready_to_publish').count()

        elif is_journalist(user):
            journalist = Journalist.objects.get(user=request.user)
            articles = Article.objects.filter(
                journalist=journalist,
                status='ready_to_publish'
            ).order_by('-submitted_at')

            accepted_articles = Article.objects.filter(
                journalist=journalist,
                status='ready_to_publish').count()

    except (Editor.DoesNotExist, Journalist.DoesNotExist):
        messages.error(request,
                       "Editor or Journalist profile not found.")
        return redirect('home')

    return render(request, 'news2u/view_accepted_articles.html', {
        'articles': articles,
        'accepted_articles': accepted_articles,
        'is_editor': is_editor(user),
        'is_journalist': is_journalist(user)
    })


# Decline/Reject Article
@login_required
@user_passes_test(is_editor)
def decline_article(request, article_id):
    try:
        editor = Editor.objects.get(user=request.user)
        article = Article.objects.get(
            id=article_id,
            editor=editor,
            status='awaiting_editor')

        if request.method == 'POST':
            article.status = 'revise'
            article.is_approved = False
            article.save()
            messages.success(request,
                             f'Article "{article.article_title}" '
                             f'to be revised.')
            return redirect('view_requests')
    except (Editor.DoesNotExist, Article.DoesNotExist):
        messages.error(request, "Article not found.")
        return redirect('view_requests')


# Editor approved article
@login_required
@user_passes_test(is_journalist)
def article_approved(request, article_id):
    """ Journalist can opt to publish independently or via
    a publication house.
    """

    try:
        journalist = Journalist.objects.get(user=request.user)
        article = Article.objects.get(
            id=article_id,
            journalist=journalist,
            status='ready_to_publish')
    except (Journalist.DoesNotExist, Article.DoesNotExist):
        messages.error(request,
                       "Article not found or not ready to publish.")
        return redirect('journalist_dashboard')

    return render(request,
                  'news2u/article_approved.html', {'article': article})


# View Edited Article
@login_required
@user_passes_test(lambda u:
                  is_journalist(u) or
                  is_editor(u) or
                  is_publisher(u))
@permission_required('news2u.view_article', raise_exception=True)
def view_edited_article(request, article_id):
    """ Journalist, Publisher or Editor can view article details."""

    user = request.user

    try:
        if is_journalist(user):
            journalist = Journalist.objects.get(user=user)
            article = Article.objects.get(
                id=article_id,
                journalist=journalist
                )
        elif is_editor(user):
            editor = Editor.objects.get(user=user)
            article = Article.objects.get(
                id=article_id,
                editor=editor
                )

        elif is_publisher(user):
            publisher = Publisher.objects.get(user=user)
            article = Article.objects.get(
                id=article_id,
                publisher=publisher
                )
        else:
            messages.error(request, "Access denied.")
            return redirect('home')

    except (Journalist.DoesNotExist,
            Editor.DoesNotExist,
            Article.DoesNotExist):
        messages.error(request, "Article not found.")
        return redirect('home')

    return render(request, 'news2u/view_edited_article.html',
                  {'article': article,
                   'is_journalist': is_journalist(user),
                   'is_editor': is_editor(user),
                   'is_publisher': is_publisher(user),
                   'editor_comments': article.editor_comments
                   })


# Delete Article
@login_required
@user_passes_test(lambda u: is_journalist(u) or is_editor(u))
@permission_required('news2u.delete_article', raise_exception=True)
def delete_article(request, article_id):
    """ Journalist or Editor can delete draft articles."""

    user = request.user

    try:
        if is_journalist(user):
            journalist = Journalist.objects.get(user=user)
            article = Article.objects.get(
                id=article_id,
                journalist=journalist,
                status__in=['draft', 'awaiting_editor']
                )
        elif is_editor(user):
            editor = Editor.objects.get(user=user)
            article = Article.objects.get(
                id=article_id,
                editor=editor,
                status__in=['draft', 'awaiting_editor', 'in_review']
                )
        else:
            messages.error(request, "Access denied.")
            return redirect('view_submitted_articles')

    except (Journalist.DoesNotExist,
            Editor.DoesNotExist,
            Article.DoesNotExist):
        messages.error(request, "Article not found.")
        return redirect('view_submitted_articles')

    if request.method == 'POST':
        article.delete()
        messages.success(request, 'Draft article deleted!')
        return redirect('view_submitted_articles')

    return render(request, 'news2u/delete_article.html',
                  {'article': article})


# Create Newsletter
@login_required
@user_passes_test(is_journalist)
@permission_required('news2u.add_newsletter', raise_exception=True)
def create_newsletter(request):
    """ Journalist is the only user that can create an article.
    - Can publish independently
    - Can submit and publish via publisher
    - All articles need to be edited by an editor and approved
    before publication
    """

    user = request.user
    journalist = None
    publisher = None

    try:
        if is_journalist(user):
            journalist = Journalist.objects.get(user=request.user)
        elif is_publisher(user):
            publisher = Publisher.objects.get(user=request.user)
        else:
            messages.error(request, "Access denied.")
            return redirect('home')

    except Journalist.DoesNotExist:
        messages.error(request, "Journalist profile not found.")
        return redirect('home')

    # Get only published articles by journalist or publisher
    published_articles = Article.objects.filter(
        journalist=journalist,
        status__in=['published_independent', 'published_publisher']
    )

    if request.method == 'POST':
        if journalist:
            form = NewsletterForm(request.POST,
                                  request.FILES,
                                  journalist=journalist)
        elif publisher:
            form = NewsletterForm(request.POST,
                                  request.FILES,
                                  publisher=publisher)
        form = NewsletterForm(request.POST,
                              request.FILES,
                              journalist=journalist)

        if form.is_valid():
            newsletter = form.save(commit=False)

            if journalist:
                newsletter.journalist = journalist
                newsletter.publisher = None
            elif publisher:
                newsletter.publisher = publisher
                newsletter.journalist = None

            newsletter.status = 'draft' or 'revise'
            newsletter.save()
            form.save_m2m()

            messages.success(request, 'Newsletter created!')
            return redirect('newsletter_detail',
                            newsletter_id=newsletter.id)
    else:
        if journalist:
            form = NewsletterForm(journalist=journalist)
        else:
            form = NewsletterForm(publisher=publisher)

    return render(request, 'news2u/create_newsletter.html',
                  {'form': form,
                   'is_journalist': is_journalist(user),
                   'is_publisher': is_publisher(user),
                   'published_articles': published_articles
                   })


# Delete Newsletter
@login_required
@user_passes_test(lambda u: is_journalist(u) or is_editor(u))
@permission_required('news2u.delete_newsletter', raise_exception=True)
def delete_newsletter(request, newsletter_id):
    """ Journalist or Editor can delete draft newsletters."""

    user = request.user

    try:
        if is_journalist(user):
            journalist = Journalist.objects.get(user=user)
            newsletter = Newsletter.objects.get(
                id=newsletter_id,
                journalist=journalist,
                status='draft'
                )
        elif is_editor(user):
            editor = Editor.objects.get(user=user)
            newsletter = Newsletter.objects.get(
                id=newsletter_id,
                editor=editor,
                status='draft'
                )
        else:
            messages.error(request, "Access denied.")
            return redirect('draft_newsletters')

    except (Journalist.DoesNotExist,
            Editor.DoesNotExist,
            Newsletter.DoesNotExist):
        messages.error(request, "Newsletter not found.")
        return redirect('draft_newsletters')

    if request.method == 'POST':
        newsletter.delete()
        messages.success(request, 'Draft newsletter deleted!')
        return redirect('draft_newsletters')

    return render(request, 'news2u/delete_newsletter.html',
                  {'newsletter': newsletter})


# View Edited Newsletter
@login_required
@user_passes_test(lambda u:
                  is_journalist(u) or
                  is_editor(u) or
                  is_publisher(u))
@permission_required('news2u.view_newsletter', raise_exception=True)
def view_edited_newsletter(request, newsletter_id):
    """ Journalist, Publisher or Editor can view newsletter details."""

    user = request.user

    try:
        if is_journalist(user):
            journalist = Journalist.objects.get(user=user)
            newsletter = Newsletter.objects.get(
                id=newsletter_id,
                journalist=journalist
                )
        elif is_editor(user):
            editor = Editor.objects.get(user=user)
            newsletter = Newsletter.objects.get(
                id=newsletter_id,
                editor=editor
                )

        elif is_publisher(user):
            publisher = Publisher.objects.get(user=user)
            newsletter = Newsletter.objects.get(
                id=newsletter_id,
                publisher=publisher
                )
        else:
            messages.error(request, "Access denied.")
            return redirect('home')

    except (Journalist.DoesNotExist,
            Editor.DoesNotExist,
            Newsletter.DoesNotExist):
        messages.error(request, "Newsletter not found.")
        return redirect('home')

    return render(request, 'news2u/view_edited_newsletter.html',
                  {'newsletter': newsletter,
                   'is_journalist': is_journalist(user),
                   'is_editor': is_editor(user),
                   'is_publisher': is_publisher(user),
                   })


# Review |Newsletter
@login_required
@user_passes_test(is_editor)
def review_newsletter(request, newsletter_id):
    """ Editor is the only role that can approve newsletters.
    Editor can:
    - view
    - update
    - delete
    """

    try:
        editor = Editor.objects.get(user=request.user)
        newsletter = Newsletter.objects.get(
            id=newsletter_id,
            editor=editor,
            status='awaiting_editor')

    except (Editor.DoesNotExist, Newsletter.DoesNotExist):
        messages.error(request, "Newsletter not found.")
        return redirect('view_requests')

    if request.method == 'POST':
        action = request.POST.get('action')
        editor_comments = request.POST.get('editor_comments', '')

        if action == 'approve':
            newsletter.status = 'ready_to_publish'
            newsletter.is_approved = False
            newsletter.editor = None
            newsletter.editor_comments = editor_comments
            newsletter.save()
            messages.success(
                request,
                'Newsletter approved! '
                'Journalist can now publish.')

        elif action == 'edit':
            newsletter.status = 'in_review'
            newsletter.editor_comments = editor_comments
            newsletter.save()
            messages.info(request,
                          'Newsletter edited by editor.')
        elif action == 'revise':
            newsletter.status = 'revise'
            newsletter.editor_comments = editor_comments
            newsletter.save()
            messages.info(
                request,
                'Newsletter sent back to journalist '
                'for revisions.'
                )

        return redirect('view_requests')

    return render(request, 'news2u/review_newsletter.html', {
        'newsletter': newsletter})


@login_required
@user_passes_test(is_editor)
def accept_newsletter(request, newsletter_id):
    """ Editor can approve newsletters assigned to them."""

    try:
        editor = Editor.objects.get(user=request.user)
        newsletter = Newsletter.objects.get(
            id=newsletter_id,
            editor=editor,
            status='awaiting_editor')
    except (Editor.DoesNotExist, Newsletter.DoesNotExist):
        messages.error(request, "Newsletter not found.")
        return redirect('view_requests')

    if request.method == 'POST':
        action = request.POST.get('action')
        editor_comments = request.POST.get('editor_comments', '')

        if action == 'approve':
            newsletter.status = 'ready_to_publish'
            newsletter.is_approved = True
            newsletter.editor_comments = editor_comments
            newsletter.save()

            # Send email to subscribers
            send_newsletter_email(newsletter)

            messages.success(request,
                             f'Newsletter "{newsletter.newsletter_title}"'
                             f'approved!')
            return redirect('view_requests')

        elif action == 'edit':
            newsletter.status = 'draft'
            newsletter.editor_comments = editor_comments
            newsletter.save()

    return render(
        request,
        'news2u/accept_newsletter.html',
        {'newsletter': newsletter}
        )


# View Accepted Newsletters
@login_required
@user_passes_test(lambda u:
                  is_editor(u) or
                  is_journalist(u) or
                  is_publisher(u))
@permission_required('news2u.view_article', raise_exception=True)
def view_accepted_newsletters(request):
    """Show accepted articles journalist"""

    user = request.user

    try:
        if is_editor(user):
            editor = Editor.objects.get(user=request.user)
            newsletters = Newsletter.objects.filter(
                editor=editor,
                status='ready_to_publish'
            ).order_by('-submitted_at')

            accepted_newsletters = Newsletter.objects.filter(
                editor=editor,
                status='ready_to_publish').count()

        elif is_journalist(user):
            journalist = Journalist.objects.get(user=request.user)
            newsletters = Newsletter.objects.filter(
                journalist=journalist,
                status='ready_to_publish'
            ).order_by('-submitted_at')

            accepted_newsletters = Newsletter.objects.filter(
                journalist=journalist,
                status='ready_to_publish').count()

        elif is_publisher(user):
            publisher = Publisher.objects.get(user=request.user)
            newsletters = Newsletter.objects.filter(
                publisher=publisher,
                status='ready_to_publish'
            ).order_by('-submitted_at')

            accepted_newsletters = Newsletter.objects.filter(
                publisher=publisher,
                status='ready_to_publish').count()

    except (Editor.DoesNotExist, Journalist.DoesNotExist):
        messages.error(request,
                       "Editor or Journalist profile not found.")
        return redirect('home')

    return render(request, 'news2u/view_accepted_newsletters.html', {
        'newsletters': newsletters,
        'accepted_newsletters': accepted_newsletters,
        'is_editor': is_editor(user),
        'is_journalist': is_journalist(user)
    })


# ============================================================
# PUBLISHER FUNCTIONS
# ============================================================

# View Article Publication Requests
@login_required
@user_passes_test(is_publisher)
def view_article_publication_requests(request):
    """ Publisher can view article publication requests assigned to
    them
    """

    try:
        publisher = Publisher.objects.get(user=request.user)
        articles = Article.objects.filter(
            publisher=publisher,
            status='in_review_publisher'
        ).order_by('-submitted_at')
    except Publisher.DoesNotExist:
        messages.error(request, "Publisher profile not found.")
        return redirect('my_published_articles')

    return render(
        request,
        'news2u/view_article_publication_requests.html',
        {'articles': articles}
        )


# Publish Article by Publisher
@login_required
@user_passes_test(is_publisher)
def publish_by_publisher(request, article_id):
    """ Publisher can publish articles assigned to them."""

    try:
        publisher = Publisher.objects.get(user=request.user)
        article = Article.objects.get(
            id=article_id,
            publisher=publisher,
            status='in_review_publisher')
    except (Publisher.DoesNotExist, Article.DoesNotExist):
        messages.error(request, "Article not found.")
        return redirect('view_article_publication_requests')

    if request.method == 'POST':
        article.status = 'published_publisher'
        article.published_at = datetime.now()
        article.save()

        messages.success(request,
                         f'Article "{article.article_title}" published!')
        return redirect('newsletter_submit_success')

    return render(
        request,
        'news2u/publish_by_publisher.html',
        {'article': article}
        )


# Publisher Create Newsletter
@login_required
@user_passes_test(is_publisher)
@permission_required('news2u.add_newsletter', raise_exception=True)
def create_publisher_newsletter(request):
    try:
        publisher = Publisher.objects.get(user=request.user)
    except Publisher.DoesNotExist:
        messages.error(request, "Publisher profile not found.")
        return redirect('home')

    if request.method == 'POST':
        form = NewsletterForm(request.POST, publisher=publisher)
        if form.is_valid():
            newsletter = form.save(commit=False)
            newsletter.publisher = publisher
            newsletter.journalist = None
            newsletter.status = 'draft'
            newsletter.save()
            form.save_m2m()

            messages.success(request, 'Newsletter created!')
            return redirect('publisher_dashboard')
    else:
        form = NewsletterForm(publisher=publisher)

    return render(request,
                  'news2u/create_publisher_newsletter.html',
                  {'form': form})


# View Draft Newsletters
@login_required
@user_passes_test(lambda u:
                  is_journalist(u) or
                  is_editor(u) or
                  is_publisher(u))
def draft_newsletters(request):
    """Show draft newsletters for journalist, publisher OR editor"""

    if is_journalist(request.user):
        try:
            journalist = Journalist.objects.get(user=request.user)
            newsletters = Newsletter.objects.filter(
                journalist=journalist,
                status='draft'
            ).order_by('-submitted_at')
        except Journalist.DoesNotExist:
            messages.error(request, "Journalist profile not found.")
            return redirect('home')

    elif is_editor(request.user):
        try:
            editor = Editor.objects.get(user=request.user)
            # Editor sees articles assigned to them that are in draft
            newsletters = Newsletter.objects.filter(
                editor=editor,
                status='draft'
            ).order_by('-submitted_at')
        except Editor.DoesNotExist:
            messages.error(request, "Editor profile not found.")
            return redirect('home')

    elif is_publisher(request.user):
        try:
            publisher = Publisher.objects.get(user=request.user)
            newsletters = Newsletter.objects.filter(
                publisher=publisher,
                status='draft'
            ).order_by('-submitted_at')
        except Publisher.DoesNotExist:
            messages.error(request, "Publisher profile not found.")
            return redirect('home')

    else:
        messages.error(request, "Access denied.")
        return redirect('home')

    return render(request, 'news2u/draft_newsletters.html', {
        'newsletters': newsletters,
        'is_journalist': is_journalist(request.user),
        'is_editor': is_editor(request.user),
        'is_publisher': is_publisher(request.user)
    })


# View details of the Newsletter
@login_required
@user_passes_test(lambda u:
                  is_journalist(u) or
                  is_editor(u) or
                  is_publisher(u))
@permission_required('news2u.view_newsletter', raise_exception=True)
def newsletter_detail(request, newsletter_id):
    """ View newsletter details """

    user = request.user

    try:
        if is_journalist(user):
            journalist = Journalist.objects.get(user=request.user)
            newsletter = Newsletter.objects.get(
                id=newsletter_id,
                journalist=journalist)

        elif is_publisher(user):
            publisher = Publisher.objects.get(user=request.user)
            newsletter = Newsletter.objects.get(
                id=newsletter_id,
                publisher=publisher)

        elif is_editor(user):
            editor = Editor.objects.get(user=request.user)
            newsletter = Newsletter.objects.get(
                id=newsletter_id,
                editor=editor)

    except (Editor.DoesNotExist,
            Newsletter.DoesNotExist,
            Publisher.DoesNotExist,
            Journalist.DoesNotExist):
        messages.error(request, "Newsletter not found.")
        return redirect('home')

    return render(request, 'news2u/newsletter_detail.html',
                  {'newsletter': newsletter,
                   'is_journalist': is_journalist(user),
                   'is_editor': is_editor(user),
                   'is_publisher': is_publisher(user)
                   })


# Edit Newsletter by Journalist, Editor or Publisher
@login_required
@user_passes_test(lambda u:
                  is_journalist(u) or
                  is_editor(u) or
                  is_publisher(u))
@permission_required('news2u.change_newsletter', raise_exception=True)
def edit_newsletter(request, newsletter_id):
    """ Journalists, Editors or Publishers can edit newsletters:
    - Journalists can edit draft newsletters
    - Editors can edit newsletters awaiting their review
    - Publishers can edit draft newsletters
    """

    user = request.user
    journalist = None
    editor = None
    publisher = None

    # Fetch the newsletter based on user role
    # Journalists can edit their own draft newsletters
    # Editors can edit newsletters assigned to them awaiting review

    try:
        newsletter = Newsletter.objects.get(id=newsletter_id)

        if is_journalist(user):
            journalist = Journalist.objects.get(user=user)
            if newsletter.journalist != journalist:
                messages.error(request, "Access denied.")
                return redirect('journalist_dashboard')

        elif is_publisher(user):
            publisher = Publisher.objects.get(user=user)
            if newsletter.publisher != publisher:
                messages.error(request, "Access denied.")
                return redirect('publisher_dashboard')

        elif is_editor(user):
            editor = Editor.objects.get(user=user)
            if newsletter.editor != editor:
                messages.error(request, "Access denied.")
                return redirect('editor_dashboard')

        else:
            messages.error(request, "Access denied.")
            return redirect('home')

    except (Journalist.DoesNotExist,
            Editor.DoesNotExist,
            Newsletter.DoesNotExist):
        messages.error(request, "Newsletter not found.")
        if is_journalist(user):
            return redirect('journalist_dashboard')
        elif is_editor(user):
            return redirect('view_requests')
        elif is_publisher(user):
            return redirect('publisher_dashboard')
        else:
            return redirect('home')

    if request.method == 'POST':
        if journalist:
            form = NewsletterForm(request.POST,
                                  request.FILES,
                                  instance=newsletter,
                                  journalist=journalist)
        elif publisher:
            form = NewsletterForm(request.POST,
                                  request.FILES,
                                  instance=newsletter,
                                  publisher=publisher)
        elif editor:
            form = NewsletterForm(request.POST,
                                  request.FILES,
                                  instance=newsletter,
                                  editor=editor)
        else:
            return redirect('home')

        if form.is_valid():
            form.save(commit=False)
            form.save_m2m()

            messages.success(request, 'Newsletter Updated!')

            if is_journalist(user):
                return redirect('newsletter_detail',
                                newsletter_id=newsletter.id)
            elif is_editor(user):
                return redirect('view_requests')
            elif is_publisher(user):
                return redirect('newsletter_detail')
            else:
                return redirect('home')
    else:
        if journalist:
            form = NewsletterForm(
                instance=newsletter,
                journalist=journalist)
        elif publisher:
            form = NewsletterForm(
                instance=newsletter,
                publisher=publisher)
        elif editor:
            form = NewsletterForm(
                instance=newsletter, editor=editor)
        else:
            return redirect('home')

    return render(
        request,
        'news2u/edit_newsletter.html',
        {
            'form': form,
            'newsletter': newsletter,
            'is_journalist': is_journalist(user),
            'is_editor': is_editor(user),
            'is_publisher': is_publisher(user)
        }
    )


# Selectd published article to add to newsletter
@login_required
@user_passes_test(lambda u: is_journalist(u) or is_publisher(u))
def add_article_to_newsletter(request, article_id, newsletter_id):
    """Add an article to a newsletter"""

    try:
        journalist = Journalist.objects.get(user=request.user)
        article = Article.objects.get(
            id=article_id,
            journalist=journalist,
            status__in=['published_independent', 'published_publisher']
        )

        publisher = Publisher.objects.get(user=request.user)
        article = Article.objects.get(
            id=article_id,
            publisher=publisher,
            status__in=['published_independent', 'published_publisher']
        )
        newsletter = Newsletter.objects.get(
            id=newsletter_id,
            journalist=journalist,
            status='draft'  # Can only add to draft newsletters
        )

        # Add article to newsletter
        newsletter.articles.add(article)

        messages.success(
            request,
            f'Article "{article.article_title}" '
            'added to newsletter!')

    except (Journalist.DoesNotExist,
            Article.DoesNotExist,
            Newsletter.DoesNotExist):
        messages.error(request, "Article or newsletter not found.")

    return redirect('draft_newsletters', newsletter_id=newsletter_id)


# View Submitted Newsletters to Editor
@login_required
@user_passes_test(is_journalist)
@permission_required('news2u.view_newsletter', raise_exception=True)
def view_submitted_newsletters(request):
    """Show submitted newsletters for journalist"""

    try:
        journalist = Journalist.objects.get(user=request.user)
        newsletters = Newsletter.objects.filter(
            journalist=journalist,
            status='awaiting_editor'
        ).order_by('-submitted_at')
    except Journalist.DoesNotExist:
        messages.error(request, "Journalist profile not found.")
        return redirect('home')

    return render(request, 'news2u/view_submitted_newsletter.html', {
        'newsletters': newsletters
    })


# ============================================================
# SUBSCRIPTION FUNCTIONS
# ============================================================

# Manage Subscriptions
@login_required
@user_passes_test(is_reader)
def manage_subscriptions(request):
    reader = request.user.customuser

    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            action = request.POST.get('action')

            if action == 'subscribe':
                # ADD to existing subscriptions (don't clear the form)
                for journalist in form.cleaned_data['journalists']:
                    reader.subscribed_journalists.add(journalist)
                for publisher in form.cleaned_data['publishers']:
                    reader.subscribed_publishers.add(publisher)

                messages.success(request, 'New subscriptions added!')

            elif action == 'update':
                # Replace all subscriptions with selected ones
                reader.subscribed_journalists.set(
                    form.cleaned_data['journalists'])
                reader.subscribed_publishers.set(
                    form.cleaned_data['publishers'])

                messages.success(request, 'Subscriptions updated!')

            return redirect('manage_subscriptions')
    else:
        form = SubscriptionForm(initial={
            'journalists':
            reader.subscribed_journalists.all().values_list(
                'id', flat=True),
            'publishers':
            reader.subscribed_publishers.all().values_list(
                'id', flat=True),
        })

    return render(request, 'news2u/manage_subscriptions.html', {
        'form': form,
        'subscribed_publishers': reader.subscribed_publishers.all(),
        'subscribed_journalists': reader.subscribed_journalists.all(),
    })


# ============================================================
# VIEW ASSOCIATED USERS
# ============================================================

# View All Editors
@login_required
@user_passes_test(lambda u: is_journalist(u) or is_publisher(u))
def view_all_editors(request):
    """ View all Editors """

    editors = Editor.objects.all()  # Get ALL editors, not just yours!

    return render(request, 'news2u/view_all_editors.html', {
        'editors': editors,
    })


# View Associated Editors
@login_required
@user_passes_test(lambda u: is_journalist(u) or is_publisher(u))
def view_my_editors(request):
    """ View Editors associated with Journalist or Publisher """

    try:
        if is_journalist(request.user):
            journalist = Journalist.objects.get(user=request.user)
            editors = Editor.objects.filter(
                article_by_editor__journalist=journalist
            ).distinct()

        elif is_publisher(request.user):
            publisher = Publisher.objects.get(user=request.user)
            editor_ids = Article.objects.filter(
             publisher=publisher
            ).values_list('editor_id', flat=True).distinct()

            editors = Editor.objects.filter(
                id__in=editor_ids)

        else:
            messages.error(request, "Access denied.")
            return redirect('home')
    except (Journalist.DoesNotExist, Publisher.DoesNotExist):
        messages.error(request, "Profile not found.")
        return redirect('home')

    return render(request, 'news2u/view_my_editors.html', {
        'editors': editors,
        'is_journalist': is_journalist(request.user),
        'is_publisher': is_publisher(request.user),
    })


# View All Journalists
@login_required
@user_passes_test(lambda u: is_editor(u) or is_publisher(u))
def view_all_journalists(request):
    """ View all Journalists"""

    journalists = Journalist.objects.all()  # Get all journalists

    return render(request, 'news2u/view_all_journalists.html', {
        'journalists': journalists,
    })


# View Journalists associated with Editor
@login_required
@user_passes_test(lambda u: is_editor(u) or is_publisher(u))
def view_my_journalists(request):
    """ View Journalists associated with Editor or Publisher """

    try:
        if is_editor(request.user):
            editor = Editor.objects.get(user=request.user)
            journalist_ids = Article.objects.filter(
             editor=editor
            ).values_list('journalist_id', flat=True).distinct()

            journalists = Journalist.objects.filter(
                id__in=journalist_ids)

        elif is_publisher(request.user):
            publisher = Publisher.objects.get(user=request.user)

            # Get journalists who have published with this publisher
            journalists = Journalist.objects.filter(
                article_by_journalist__publisher=publisher,
                article_by_journalist__status='published_publisher'
            ).distinct()

        else:
            messages.error(request, "Access denied.")
            return redirect('home')
    except (Editor.DoesNotExist, Publisher.DoesNotExist):
        messages.error(request, "Profile not found.")
        return redirect('home')

    return render(request, 'news2u/view_my_journalists.html', {
        'journalists': journalists,
        'is_editor': is_editor(request.user),
        'is_publisher': is_publisher(request.user),
    })


# View all Publishers
@login_required
@user_passes_test(lambda u: is_journalist(u) or is_editor(u))
def view_all_publishers(request):
    """ View all Publishers """

    publishers = Publisher.objects.all()  # Get ALL publishers, not just yours!

    return render(request, 'news2u/view_all_publishers.html', {
        'publishers': publishers,
    })


# View Associated Publishers
@login_required
@user_passes_test(lambda u: is_journalist(u) or is_editor(u))
def view_my_publishers(request):
    """ View Publishers associated with Journalist or Editor """

    try:
        if is_journalist(request.user):
            journalist = Journalist.objects.get(user=request.user)

            publisher_ids = Article.objects.filter(
                journalist=journalist,
                status='published_publisher',
                publisher__isnull=False
            ).values_list('publisher_id', flat=True).distinct()

            publishers = Publisher.objects.filter(id__in=publisher_ids)

        elif is_editor(request.user):
            editor = Editor.objects.get(user=request.user)
            publisher_ids = Article.objects.filter(
             editor=editor
            ).values_list('publisher_id', flat=True).distinct()

            publishers = Publisher.objects.filter(
                id__in=publisher_ids)

        else:
            messages.error(request, "Access denied.")
            return redirect('home')
    except (Journalist.DoesNotExist, Editor.DoesNotExist):
        messages.error(request, "Profile not found.")
        return redirect('home')

    return render(request, 'news2u/view_my_publishers.html', {
        'publishers': publishers,
        'is_journalist': is_journalist(request.user),
        'is_editor': is_editor(request.user),
    })


# View Article Requests
@login_required
@user_passes_test(is_editor)
def view_requests(request):
    """ Editor can view article and newsletter requests assigned
    to them.
    """

    try:
        editor = Editor.objects.get(user=request.user)
        articles = Article.objects.filter(
            editor=editor,
            status='awaiting_editor'
        ).order_by('-submitted_at')

        newsletters = Newsletter.objects.filter(
            editor=editor,
            status='awaiting_editor'
        ).order_by('-submitted_at')

    except Editor.DoesNotExist:
        messages.error(request, "Editor profile not found.")
        return redirect('editor_dashboard')

    return render(request, 'news2u/view_requests.html', {
        'articles': articles,
        'newsletters': newsletters,
    })


# View Subscriber Newsletters
def view_subscriber_newsletters():
    pass


# ============================================================
# API FUNCTIONS
# ============================================================

# Login
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_user_login(request):
    """ API endpoint for user login """

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request,
                                username=username,
                                password=password)

            if user is not None:
                login(request, user)

                if is_publisher(user):
                    return redirect('publisher_dashboard')
                elif is_editor(user):
                    return redirect('editor_dashboard')
                elif is_journalist(user):
                    return redirect('journalist_dashboard')
                elif is_reader(user):
                    return redirect('reader_dashboard')
                else:
                    return redirect('home')
    else:
        form = AuthenticationForm()

    serializer = LoginFormSerializer(form)
    return JsonResponse(serializer.data, safe=False)


# Logout
def api_user_logout(request):
    if request.user.is_authenticated:
        # Clear pending messages
        storage = messages.get_messages(request)
        storage.used = True

        logout(request)
        messages.success(request,
                         'You have been logged out successfully.')

    serializer = LoginFormSerializer({})
    return JsonResponse(serializer.data, safe=False)


# Manage Subscriptions
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def api_manage_subscriptions(request):
    """
    GET: Get current subscriptions
    POST: Update subscriptions
    """
    try:
        custom_user = CustomUser.objects.get(user=request.user)
    except CustomUser.DoesNotExist:
        return Response(
            {'error': 'User profile not found'},
            status=404)

    if custom_user.role != 'reader':
        return Response({'error': 'Only readers can manage '
                        'subscriptions'}, status=403)

    if request.method == 'GET':
        # Return current subscriptions
        data = {
            'subscribed_journalists': JournalistSerializer(
                custom_user.subscribed_journalists.all(),
                many=True
            ).data,
            'subscribed_publishers': PublisherSerializer(
                custom_user.subscribed_publishers.all(),
                many=True
            ).data
        }
        return Response(data)

    elif request.method == 'POST':
        action = request.data.get('action')
        journalist_ids = request.data.get('journalists', [])
        publisher_ids = request.data.get('publishers', [])

        if action == 'subscribe':
            # ADD to existing subscriptions
            for journalist_id in journalist_ids:
                try:
                    journalist = Journalist.objects.get(id=journalist_id)
                    custom_user.subscribed_journalists.add(journalist)
                except Journalist.DoesNotExist:
                    pass

            for publisher_id in publisher_ids:
                try:
                    publisher = Publisher.objects.get(id=publisher_id)
                    custom_user.subscribed_publishers.add(publisher)
                except Publisher.DoesNotExist:
                    pass

            return Response({'message': 'Subscriptions added!'}, status=200)

        elif action == 'update':
            # REPLACE all subscriptions
            journalists = Journalist.objects.filter(id__in=journalist_ids)
            publishers = Publisher.objects.filter(id__in=publisher_ids)

            custom_user.subscribed_journalists.set(journalists)
            custom_user.subscribed_publishers.set(publishers)

            return Response(
                {'message': 'Subscriptions updated!'},
                status=200)

        else:
            return Response(
                {'error': 'Invalid action. Use "subscribe" or "update"'},
                status=400)


# Reader can retrieve published articles from subscribed journalists
# and publishers
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_my_published_articles(request):
    """ API endpoint to get published articles for the a subscriber """

    if not is_reader(request.user):
        return JsonResponse(
            {'error': 'Access denied.'},
            status=403)

    if request.method == "GET":
        # Get the CustomUser for this reader
        custom_user = CustomUser.objects.get(user=request.user)

        # Get articles from subscribed journalists
        # OR subscribed publishers
        articles = Article.objects.filter(
            journalist__in=custom_user.subscribed_journalists.all(),
            status__in=['published_independent', 'published_publisher']
        ) | Article.objects.filter(
            publisher__in=custom_user.subscribed_publishers.all(),
            status='published_publisher'
        )

        serializer = ArticleSerializer(articles, many=True)
        return JsonResponse(serializer.data, safe=False)


# Read Article
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_read_article(request, article_id):
    """ API endpoint to read a specific article """

    if not is_reader(request.user):
        return JsonResponse(
            {'error': 'Access denied.'},
            status=403)

    try:
        article = Article.objects.get(id=article_id)

        # Check if the article is from a subscribed journalist
        # or publisher
        custom_user = CustomUser.objects.get(user=request.user)

        if (article.journalist not in
                custom_user.subscribed_journalists.all() and
            article.publisher not in
                custom_user.subscribed_publishers.all()):
            return JsonResponse(
                {'error': 'Access denied to this article.'},
                status=403)

        serializer = ArticleSerializer(article)
        return JsonResponse(serializer.data, safe=False)

    except Article.DoesNotExist:
        return JsonResponse({'error': 'Article not found.'}, status=404)
