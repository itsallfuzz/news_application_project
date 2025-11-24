from django import forms
from django.contrib.auth.models import User
from .models import Publisher, Editor, Journalist
from .models import AdminApproval, Article, Newsletter
from django.contrib.auth.forms import UserCreationForm
from rest_framework import serializers


class PublisherRegistrationForm(UserCreationForm):
    """ Form for registering a Publisher user.

    Fields:
    - publisher_name: CharField for the store name.
    - description: TextField for the store description.

    Meta class:
    - Defines the model to use (Store) and the fields to include in the
    form.

    :param forms.ModelForm: Django's ModelForm class.
    """

    publisher_name = forms.CharField(
        max_length=200, label='Publication House'
        )
    publisher_description = forms.CharField(
        widget=forms.Textarea, label='Description'
        )
    publisher_logo = forms.ImageField(
        required=False, label='Logo'
        )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class EditorRegistrationForm(UserCreationForm):
    """ Form for registering an Editor user.

    Fields:
    - editor_name: CharField for the editor name.
    - bio: TextField for the editor bio.
    - profile_picture: ImageField for the editor profile picture.

    Meta class:
    - Defines the model to use (Editor) and the fields to include in the
    form.

    :param forms.ModelForm: Django's ModelForm class.
    """

    editor_name = forms.CharField(
        max_length=200, label='Name'
        )
    editor_interests = forms.CharField(
        max_length=200, label='Interest Areas'
        )
    editor_bio = forms.CharField(
        widget=forms.Textarea, label='Bio'
        )
    editor_photo = forms.ImageField(
        required=False, label='Profile Picture'
        )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class JournalistRegistrationForm(UserCreationForm):
    """ Form for registering a Journalist user.

    Fields:
    - journalist_name: CharField for the journalist name.
    - bio: TextField for the journalist bio.
    - profile_picture: ImageField for the journalist profile picture.

    Meta class:
    - Defines the model to use (Journalist) and the fields to include
    in the form.

    :param forms.ModelForm: Django's ModelForm class.
    """

    journalist_name = forms.CharField(
        max_length=200, label='Name'
        )
    journalist_bio = forms.CharField(
        widget=forms.Textarea, label='Bio'
        )
    journalist_photo = forms.ImageField(
        required=False, label='Profile Picture'
        )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ReaderRegistrationForm(UserCreationForm):
    """ Form for registering a Reader user.

    Fields:
    - reader_name: CharField for the reader name.
    - subscription: Journalist or Publisher subscription

    Meta class:
    - Defines the model to use (Reader) and the fields to include in
    the form.

    :param forms.ModelForm: Django's ModelForm class.
    """

    reader_name = forms.CharField(
        max_length=200, label='Name'
        )
    reader_interests = forms.CharField(
        widget=forms.Textarea, label='Interests'
        )
    reader_photo = forms.ImageField(
        required=False, label='Profile Picture'
        )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class AdminApprovalForm(forms.ModelForm):
    """ Form for admin approval of user registrations.

    Fields:
    - is_approved: BooleanField to approve or decline the user.
    - declined_for: TextField for the reason of decline.

    Meta class:
    - Defines the model to use (AdminApproval) and the fields to
    include in the
    form.

    :param forms.ModelForm: Django's ModelForm class.
    """

    is_approved = forms.BooleanField(
        required=False, label='Approve User'
        )
    declined_for = forms.CharField(
        widget=forms.Textarea,
        required=False,
        label='Reason for Decline'
        )

    class Meta:
        model = AdminApproval
        fields = ['is_approved', 'declined_for']


class LoginForm(forms.Form):
    """ Form for user login.

    Fields:
    - username: CharField for the username.
    - password: CharField for the password.

    :param forms.Form: Django's Form class.
    """

    username = forms.CharField(max_length=150, label='Username')
    password = forms.CharField(
        widget=forms.PasswordInput, label='Password'
        )


class ArticleForm(forms.ModelForm):
    """Form for article submission
    - article title: Charfield
    - article content: TextField
    - article photo: ImageField

    :param forms.Django's Form class
    """

    class Meta:
        model = Article
        fields = ['article_title', 'article_content', 'article_photo']
        widgets = {
            'article_content': forms.Textarea(attrs={'rows': 10}),
        }


class NewsletterForm(forms.ModelForm):
    """Form for newsletter submission
    - newsletter title: Charfield
    - newsletter content: TextField

    :param forms.Django's Form class
    """

    class Meta:
        model = Newsletter
        fields = ['newsletter_title', 'newsletter_content', 'articles', ]
        widgets = {
                'newsletter_content': forms.Textarea(attrs={'rows': 10}),
                'articles': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        journalist = kwargs.pop('journalist', None)
        publisher = kwargs.pop('publisher', None)
        editor = kwargs.pop('editor', None)
        super().__init__(*args, **kwargs)

        # Filter articles based on who's creating the newsletter
        if journalist:
            # Journalist sees only their own published articles
            self.fields['articles'].queryset = Article.objects.filter(
                journalist=journalist,
                status__in=['published_independent',
                            'published_publisher']
            )
        elif publisher:
            # Publisher sees all articles published through them
            self.fields['articles'].queryset = Article.objects.filter(
                publisher=publisher,
                status='published_publisher'
            )
        elif editor:
            # Editor sees articles assigned to them
            self.fields['articles'].queryset = Article.objects.filter(
                editor=editor,
                status__in=['published_independent',
                            'published_publisher']
            )
        else:
            self.fields['articles'].queryset = Article.objects.none()

        self.fields['articles'].required = False
        self.fields['articles'].label = "Select articles to include:"


class SelectEditorForm(forms.Form):
    """ Journalist can choose to publish an article independently and
    select their editor of choice.
    """

    editor = forms.ModelChoiceField(
        queryset=Editor.objects.all(),
        required=True,
        label="Select Editor"
    )

    def __init__(self, *args, **kwargs):
        journalist = kwargs.pop('journalist', None)
        super().__init__(*args, **kwargs)

        if journalist:
            # Show editors this journalist works with
            self.fields['editor'].queryset = Editor.objects.all()


class SubmitToPublisherForm(forms.Form):
    """ Journalist can choose to submit to publication house
    in which case an editor will be assigned.
    """

    publisher = forms.ModelChoiceField(
        queryset=Publisher.objects.all(),  # Shows all publishers
        required=True,
        label="Select Publication House",
        empty_label="-- Choose a Publisher --"
    )


class SubscriptionForm(forms.Form):
    """ Form for readers to subscribe to journalists and publishers.

    Fields:
    - journalists: MultipleChoiceField for selecting journalists.
    - publishers: MultipleChoiceField for selecting publishers.

    :param forms.Form: Django's Form class.
    """

    journalists = forms.ModelMultipleChoiceField(
        queryset=Journalist.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Subscribe to Journalists'
        )
    publishers = forms.ModelMultipleChoiceField(
        queryset=Publisher.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Subscribe to Publication Houses'
        )


class LoginFormSerializer(serializers.Serializer):
    """ Serializer for LoginForm to convert form data to JSON format.

    Fields:
    - username: CharField for the username.
    - password: CharField for the password.

    :param serializers.Serializer: Django REST Framework's Serializer class.
    """

    class Meta:
        fields = ['username', 'password']


class SubscriptionFormSerializer(serializers.Serializer):
    """ Serializer for SubscriptionForm to convert form data to JSON format.

    Fields:
    - journalists: MultipleChoiceField for selecting journalists.
    - publishers: MultipleChoiceField for selecting publishers.

    :param serializers.Serializer: Django REST Framework's Serializer class.
    """

    class Meta:
        fields = ['journalists', 'publishers']
