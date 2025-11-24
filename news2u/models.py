from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from rest_framework import serializers


# Model for custom user
class CustomUser(models.Model):
    """Model representing the user profile.
    Fields:
    - User type: Publisher, Editor, Journalist or Reader
    - created_at: DateTimeField set to the current date and time when
    the user is created

    Methods: - __str__: Returns a string representation of the post,
    showing the title. :param models.Model: Django's base model class.
    """

    ROLES = (
        ("publisher", "Publisher"),
        ("editor", "Editor"),
        ("journalist", "Journalist"),
        ("reader", "Reader")
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # For the sake of this assignment and having to test multiple users
    # but not having mutliple email addresses available,
    # the email field is NOT set to unique. It also allows users who
    # might have multiple roles to register with the same email.
    # But in a real-world app, this should be unique and I would change
    # it to models.EmailField(unique=True) and enforce users to sign
    # up with unique email addresses for each role. Currently this is
    # enforced with journalists and readers not being able to access
    # the different dashboards with the same account, they need separate
    # accounts.
    email = models.EmailField(blank=True, null=True)

    role = models.CharField(max_length=10, choices=ROLES)
    created_at = models.DateTimeField(auto_now_add=True)

    # Approval status
    is_approved = models.BooleanField(default=False)
    declined_for = models.TextField(blank=True, null=True)

    # Articles published independently by journalist (no publisher
    @property
    def journalist_articles(self):
        if self.role == 'journalist' and hasattr(self, 'journalist'):
            return self.journalist.articles.filter(
                status='published_independent',
                publisher__isnull=True)
        return Article.objects.none()

    @property
    # Newsletters published independently (no publisher)
    def journalist_newsletters(self):
        if self.role == 'journalist' and hasattr(self, 'journalist'):
            return self.journalist.newsletters.filter(
                status='published_independent',
                publisher__isnull=True,
                is_approved=True
                )
        return Article.objects.none()

    # Reader fields
    subscribed_publishers = models.ManyToManyField(
        'Publisher',
        blank=True,
        related_name='reader_subscribers'
    )
    subscribed_journalists = models.ManyToManyField(
        'Journalist',
        blank=True,
        related_name='reader_subscribers'
    )

    # If journalist, subscriptions are empty/None
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.role != 'reader':
            # Clear subscriptions for non-readers (make them "None")
            self.subscribed_publishers.clear()
            self.subscribed_journalists.clear()

    def __str__(self):
        return f"{self.user.username} - {self.role}"


# Model for Publisher
class Publisher(models.Model):
    """Model representing a publisher
    - A publisher can have multiple journalists and editors
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='new_publisher',
        blank=True,
        null=True
        )

    # Basic fields
    publisher_name = models.CharField(max_length=200)
    publisher_description = models.TextField()
    publisher_logo = models.ImageField(
        upload_to='publisher_logo/',
        blank=True,
        null=True
        )

    journalists = models.ManyToManyField(
        'Journalist',
        related_name='publishers',
        blank=True
        )

    def __str__(self):
        return self.publisher_name


# Model for Editor
class Editor(models.Model):
    """Model representing an editor
    - An editor can edit multiple articles and work for multiple
    publishers
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='new_editor',
        blank=True,
        null=True
        )

    # Basic fields
    editor_name = models.CharField(max_length=200)
    editor_interests = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        )
    editor_bio = models.TextField()
    editor_photo = models.ImageField(
        upload_to='editor_photos/',
        blank=True,
        null=True
        )

    publishers = models.ManyToManyField(
        'Publisher',
        related_name='editors',
        blank=True
        )

    @property
    def associated_publishers(self):
        """Get publishers this editor has worked with through articles"""
        return Publisher.objects.filter(
            published_by_publisher__editor=self,
            published_by_publisher__status='published_publisher'
        ).distinct()

    def __str__(self):
        return f"{self.editor_name} ({self.editor_interests})"


# Model for Journalist
class Journalist(models.Model):
    """Model representing a journalist
    - A journalist can write multiple articles and work for multiple
    publishers
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='new_journalist',
        blank=True,
        null=True
        )

    # Basic fields
    journalist_name = models.CharField(max_length=200)
    journalist_bio = models.TextField()
    journalist_photo = models.ImageField(
        upload_to='journalist_photos/',
        blank=True,
        null=True
        )

    created_at = models.DateTimeField(auto_now_add=True)

    editors = models.ManyToManyField(
        'Editor',
        related_name='journalists',
        blank=True
        )

    @property
    def associated_publishers(self):
        # Get publishers this journalist has published with
        return Publisher.objects.filter(
            published_by_publisher__journalist=self
        ).exclude(
            published_by_publisher__publisher__isnull=True
        ).distinct()

    def __str__(self):
        return self.journalist_name


# Model for Articles
class Article(models.Model):
    """Model representing a news article.
    Fields:
    - title: CharField for the article title
    - content: TextField for the article content
    - journalist: ForeignKey to CustomUser representing the author
    - publisher: ForeignKey to CustomUser representing the publisher
    - editor: ForeignKey to CustomUser representing the editor
    - published_at: DateTimeField set to the current date and time when
    the article is published
    - is approved: BooleanField indicating if the article is approved
    """

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('awaiting_editor', 'Awaiting Editor Review'),
        ('in_review', 'Being Edited'),
        ('ready_to_publish', 'Approved for Publication'),
        ('in_review_publisher', 'Under Publisher Review'),
        ('published_independent', 'Published Independently'),
        ('published_publisher', 'Published by Publisher'),
        ('revise', 'Revise'),
    ]

    article_title = models.CharField(max_length=255)
    article_content = models.TextField()
    article_photo = models.ImageField(
        upload_to='article_photos/',
        blank=True,
        null=True
        )

    journalist = models.ForeignKey(
        Journalist, on_delete=models.CASCADE,
        related_name='article_by_journalist')

    # Journalist requests Publisher
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        related_name='published_by_publisher',
        null=True,
        blank=True)

    # Editor - chosen by journalist for independent articles or
    # selected by publisher for submitted articles
    editor = models.ForeignKey(
        Editor,
        on_delete=models.SET_NULL,
        related_name='article_by_editor',
        null=True,
        blank=True)
    editor_comments = models.TextField(
        blank=True,
        null=True,
        help_text="Editor feedback")

    # Tracking submissions
    submitted_at = models.DateTimeField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    status = models.CharField(
        max_length=30, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.article_title

    # Create a preview of an article
    def article_preview(self):
        return f"{self.article_title}: {self.article_content[:100]}..."


# Model for Newsletters
class Newsletter(models.Model):
    """Model representing a newsletter.
    Fields:
    - title: CharField for the newsletter title
    - content: TextField for the newsletter content
    - journalist: ForeignKey to CustomUser representing the author
    - publisher: ForeignKey to CustomUser representing the publisher
    - editor: ForeignKey to CustomUser representing the editor
    - published_at: DateTimeField set to the current date and time when
    the article is published
    """

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('awaiting_editor', 'Awaiting Editor Review'),
        ('in_review', 'Being Edited'),
        ('in_review_publisher', 'Under Publisher Review'),
        ('ready_to_publish', 'Approved for Publication'),
        ('published_newsletter', 'Published by Journalist'),
        ('published_newsletter_by_publisher', 'Published by Publisher'),
    ]

    newsletter_title = models.CharField(max_length=255)
    newsletter_content = models.TextField()

    journalist = models.ForeignKey(
        Journalist,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='journalist_newsletters'
        )
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        related_name='newsletters',
        null=True,
        blank=True,
        help_text="Publisher if newsletter is from a publication"
        )
    editor = models.ForeignKey(
        Editor,
        on_delete=models.SET_NULL,
        related_name='edited_newsletters',
        null=True,
        blank=True,
        help_text="Newsletter edited by ..."
        )

    # Articles included in the newsletter
    articles = models.ManyToManyField(
        Article,
        related_name='articles_in_newsletters',
        blank=True,
        help_text="Articles included in this newsletter"
        )

    submitted_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default='draft')
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.newsletter_title


# Model for Reader subscriptions
class Reader(models.Model):
    """Model representing a reader's subscription to newsletters.
    Fields:
    - newsletter: ForeignKey to Newsletter representing the subscribed
    newsletter
    - journalist: ForeignKey to CustomUser representing the subscribed
    journalist
    - subscribed_at: DateTimeField set to the current date and time when
    the subscription is created
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        )
    reader_name = models.CharField(max_length=200, blank=True, null=True)
    reader_interests = models.TextField(blank=True, null=True)
    reader_photo = models.ImageField(
        upload_to='reader_photos/',
        blank=True,
        null=True
        )

    subscribed_at = models.DateTimeField(auto_now_add=True)

    @property
    def email(self):
        """Get email from the linked User"""
        return self.user.email

    def __str__(self):
        return f"Subscriber: {self.user.username}"


# Model for Admin Approvals of users
class AdminApproval(models.Model):
    """Model representing admin approvals for publishers, editors,
    and journalists.
    Fields:
    - user: ForeignKey to CustomUser representing the user awaiting
    approval
    - role: CharField indicating the role of the user
    - is_approved: BooleanField indicating if the user is approved
    - requested_at: DateTimeField set to the current date and time when
    the approval request is created
    """

    DECLINE_REASONS = (
        ('incomplete', 'Incomplete Information'),
        ('duplicate', 'Duplicate Account'),
        ('spam', 'Suspected Spam/Fraud'),
        ('other', 'Other (see notes)'),
    )

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        )
    role = models.CharField(max_length=10, choices=CustomUser.ROLES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    requested_at = models.DateTimeField(auto_now_add=True)
    declined_for = models.CharField(
        max_length=50,
        choices=DECLINE_REASONS,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"Approval for {self.user.user.username} as {self.role}"


# Reset token for password reset
class ResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=500)
    expiry_date = models.DateTimeField()
    used = models.BooleanField(default=False)

    def is_valid(self):
        return self.expiry_date > datetime.now() and not self.used


# Models for Serializers
class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'


class JournalistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Journalist
        fields = '__all__'


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = '__all__'


class ReaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reader
        fields = '__all__'


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'
