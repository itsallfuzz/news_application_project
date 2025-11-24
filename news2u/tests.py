from django.test import TestCase
from django.urls import reverse
from .models import CustomUser, Publisher, Editor, Journalist, Reader
from .models import Article, Newsletter, AdminApproval, ResetToken
from .models import ArticleSerializer, ReaderSerializer, CustomUserSerializer
from .models import JournalistSerializer, PublisherSerializer
from django.contrib.auth.models import User


# CustomUser Model Tests
class CustomUserModelTest(TestCase):
    def setUp(self):
        # Create a User object for testing
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass')
        self.custom_user = CustomUser.objects.create(
            user=self.user,
            role='reader')

    def test_custom_user_creation(self):
        # Test that a CustomUser can be created
        custom_user = CustomUser.objects.get(id=1)
        self.assertIsNotNone(custom_user)

    def test_custom_user_has_role(self):
        # Test that a CustomUser has the expected role
        custom_user = CustomUser.objects.get(id=1)
        self.assertEqual(custom_user.role, 'reader')

    def test_custom_user_str_method(self):
        # Test the __str__ method returns username
        custom_user = CustomUser.objects.get(id=1)
        self.assertEqual(str(custom_user), 'testuser')


# Publisher Model Tests
class PublisherModelTest(TestCase):
    def setUp(self):
        # Create a Publisher object for testing
        user = User.objects.create_user(
            username='testpublisher',
            password='testpass')
        self.publisher = Publisher.objects.create(
            custom_user=CustomUser.objects.create(
                user=user,
                role='publisher'),
            publisher_name='Test Publisher',
            description='This is a test publisher.')

    def test_publisher_creation(self):
        # Test that a Publisher can be created
        publisher = Publisher.objects.get(id=1)
        self.assertIsNotNone(publisher)

    def test_publisher_has_name(self):
        # Test that a Publisher has the expected name
        publisher = Publisher.objects.get(id=1)
        self.assertEqual(publisher.publisher_name, 'Test Publisher')

    def test_publisher_has_description(self):
        # Test that a Publisher has a description
        publisher = Publisher.objects.get(id=1)
        self.assertEqual(publisher.description, 'This is a test publisher.')

    def test_publisher_str_method(self):
        # Test the __str__ method returns name
        publisher = Publisher.objects.get(id=1)
        self.assertEqual(str(publisher), 'Test Publisher')


# Editor Model Tests
class EditorModelTest(TestCase):
    def setUp(self):
        # Create an Editor object for testing
        user = User.objects.create_user(
            username='testeditor',
            password='testpass')
        self.editor = Editor.objects.create(
            custom_user=CustomUser.objects.create(
                user=user,
                role='editor'),
            editor_name='Test Editor',
            bio='This is a test editor bio.')

    def test_editor_creation(self):
        # Test that an Editor can be created
        editor = Editor.objects.get(id=1)
        self.assertIsNotNone(editor)

    def test_editor_has_name(self):
        # Test that an Editor has the expected name
        editor = Editor.objects.get(id=1)
        self.assertEqual(editor.editor_name, 'Test Editor')

    def test_editor_has_bio(self):
        # Test that an Editor has a bio
        editor = Editor.objects.get(id=1)
        self.assertEqual(editor.bio, 'This is a test editor bio.')

    def test_editor_str_method(self):
        # Test the __str__ method returns name
        editor = Editor.objects.get(id=1)
        self.assertEqual(str(editor), 'Test Editor')


# Journalist Model Tests
class JournalistModelTest(TestCase):
    def setUp(self):
        # Create a Journalist object for testing
        user = User.objects.create_user(
            username='testjournalist',
            password='testpass')
        self.journalist = Journalist.objects.create(
            custom_user=CustomUser.objects.create(
                user=user,
                role='journalist'),
            journalist_name='Test Journalist',
            bio='This is a test journalist bio.')

    def test_journalist_creation(self):
        # Test that a Journalist can be created
        journalist = Journalist.objects.get(id=1)
        self.assertIsNotNone(journalist)

    def test_journalist_has_name(self):
        # Test that a Journalist has the expected name
        journalist = Journalist.objects.get(id=1)
        self.assertEqual(journalist.journalist_name, 'Test Journalist')

    def test_journalist_has_bio(self):
        # Test that a Journalist has a bio
        journalist = Journalist.objects.get(id=1)
        self.assertEqual(journalist.bio, 'This is a test journalist bio.')

    def test_journalist_str_method(self):
        # Test the __str__ method returns name
        journalist = Journalist.objects.get(id=1)
        self.assertEqual(str(journalist), 'Test Journalist')


# Reader Model Tests
class ReaderModelTest(TestCase):
    def setUp(self):
        # Create a Reader object for testing
        user = User.objects.create_user(
            username='testreader',
            password='testpass')
        self.reader = Reader.objects.create(
            custom_user=CustomUser.objects.create(
                user=user,
                role='reader'),
            reader_name='Test Reader')

    def test_reader_creation(self):
        # Test that a Reader can be created
        reader = Reader.objects.get(id=1)
        self.assertIsNotNone(reader)

    def test_reader_has_name(self):
        # Test that a Reader has the expected name
        reader = Reader.objects.get(id=1)
        self.assertEqual(reader.reader_name, 'Test Reader')

    def test_reader_str_method(self):
        # Test the __str__ method returns name
        reader = Reader.objects.get(id=1)
        self.assertEqual(str(reader), 'Test Reader')


# Article Model Tests
class ArticleModelTest(TestCase):
    def setUp(self):
        # Create an Article object for testing
        user = User.objects.create_user(
            username='testjournalist2',
            password='testpass')
        journalist = Journalist.objects.create(
            custom_user=CustomUser.objects.create(
                user=user,
                role='journalist'),
            journalist_name='Test Journalist 2',
            bio='This is another test journalist bio.')
        self.article = Article.objects.create(
            title='Test Article',
            content='This is the content of the test article.',
            journalist=journalist,
            status='draft')

    def test_article_creation(self):
        # Test that an Article can be created
        article = Article.objects.get(id=1)
        self.assertIsNotNone(article)

    def test_article_has_title(self):
        # Test that an Article has the expected title
        article = Article.objects.get(id=1)
        self.assertEqual(article.title, 'Test Article')

    def test_article_has_content(self):
        # Test that an Article has content
        article = Article.objects.get(id=1)
        self.assertEqual(article.content,
                         'This is the content of the test article.')

    def test_article_str_method(self):
        # Test the __str__ method returns title
        article = Article.objects.get(id=1)
        self.assertEqual(str(article), 'Test Article')


# Newsletter Model Tests
class NewsletterModelTest(TestCase):
    def setUp(self):
        # Create a Newsletter object for testing
        user = User.objects.create_user(
            username='testpublisher2',
            password='testpass')
        publisher = Publisher.objects.create(
            custom_user=CustomUser.objects.create(
                user=user,
                role='publisher'),
            publisher_name='Test Publisher 2',
            description='This is another test publisher.')
        self.newsletter = Newsletter.objects.create(
            newsletter_title='Test Newsletter',
            newsletter_content='This is the content of the test newsletter.',
            publisher=publisher)

    def test_newsletter_creation(self):
        # Test that a Newsletter can be created
        newsletter = Newsletter.objects.get(id=1)
        self.assertIsNotNone(newsletter)

    def test_newsletter_has_title(self):
        # Test that a Newsletter has the expected title
        newsletter = Newsletter.objects.get(id=1)
        self.assertEqual(newsletter.newsletter_title, 'Test Newsletter')

    def test_newsletter_has_content(self):
        # Test that a Newsletter has content
        newsletter = Newsletter.objects.get(id=1)
        self.assertEqual(newsletter.newsletter_content,
                         'This is the content of the test newsletter.')

    def test_newsletter_str_method(self):
        # Test the __str__ method returns title
        newsletter = Newsletter.objects.get(id=1)
        self.assertEqual(str(newsletter), 'Test Newsletter')


# AdminApproval Model Tests
class AdminApprovalModelTest(TestCase):
    def setUp(self):
        # Create an AdminApproval object for testing
        user = User.objects.create_user(
            username='testuser2',
            password='testpass')
        custom_user = CustomUser.objects.create(
            user=user,
            role='reader')
        self.admin_approval = AdminApproval.objects.create(
            custom_user=custom_user,
            is_approved=True,
            declined_for='')

    def test_admin_approval_creation(self):
        # Test that an AdminApproval can be created
        admin_approval = AdminApproval.objects.get(id=1)
        self.assertIsNotNone(admin_approval)

    def test_admin_approval_is_approved(self):
        # Test that AdminApproval has the expected approval status
        admin_approval = AdminApproval.objects.get(id=1)
        self.assertTrue(admin_approval.is_approved)

    def test_admin_approval_declined_for(self):
        # Test that AdminApproval has the expected declined reason
        admin_approval = AdminApproval.objects.get(id=1)
        self.assertEqual(admin_approval.declined_for, '')

    def test_admin_approval_str_method(self):
        # Test the __str__ method returns username with status
        admin_approval = AdminApproval.objects.get(id=1)
        self.assertEqual(str(admin_approval), 'testuser2 - Approved')


# ResetToken Model Tests
class ResetTokenModelTest(TestCase):
    def setUp(self):
        # Create a ResetToken object for testing
        user = User.objects.create_user(
            username='testuser3',
            password='testpass')
        custom_user = CustomUser.objects.create(
            user=user,
            role='reader')
        self.reset_token = ResetToken.objects.create(
            custom_user=custom_user,
            token='resettoken123')

    def test_reset_token_creation(self):
        # Test that a ResetToken can be created
        reset_token = ResetToken.objects.get(id=1)
        self.assertIsNotNone(reset_token)

    def test_reset_token_has_token(self):
        # Test that ResetToken has the expected token value
        reset_token = ResetToken.objects.get(id=1)
        self.assertEqual(reset_token.token, 'resettoken123')

    def test_reset_token_str_method(self):
        # Test the __str__ method returns token
        reset_token = ResetToken.objects.get(id=1)
        self.assertEqual(str(reset_token), 'resettoken123')


# Serializer Tests
class CustomUserSerializerTest(TestCase):
    def setUp(self):
        # Create a User and CustomUser for testing
        self.user = User.objects.create_user(
            username='serializeruser',
            password='testpass')
        self.custom_user = CustomUser.objects.create(
            user=self.user,
            role='reader')

    def test_custom_user_serialization(self):
        serializer = CustomUserSerializer(self.custom_user)
        data = serializer.data
        self.assertEqual(data['user']['username'], 'serializeruser')
        self.assertEqual(data['role'], 'reader')


# Publisher Serializer Tests
class PublisherSerializerTest(TestCase):
    def setUp(self):
        # Create a User, CustomUser, and Publisher for testing
        self.user = User.objects.create_user(
            username='serializerpublisher',
            password='testpass')
        self.custom_user = CustomUser.objects.create(
            user=self.user,
            role='publisher')
        self.publisher = Publisher.objects.create(
            custom_user=self.custom_user,
            publisher_name='Serializer Publisher',
            description='Publisher for serialization tests.')

    def test_publisher_serialization(self):
        # Test that Publisher can be serialized correctly

        serializer = PublisherSerializer(self.publisher)
        data = serializer.data
        self.assertEqual(data
                         ['custom_user']['user']['username'],
                         'serializerpublisher')
        self.assertEqual(data['publisher_name'], 'Serializer Publisher')
        self.assertEqual(data['description'],
                         'Publisher for serialization tests.')


# Journalist Serializer Tests
class JournalistSerializerTest(TestCase):
    def setUp(self):
        # Create a User, CustomUser, and Journalist for testing
        self.user = User.objects.create_user(
            username='serializerjournalist',
            password='testpass')
        self.custom_user = CustomUser.objects.create(
            user=self.user,
            role='journalist')
        self.journalist = Journalist.objects.create(
            custom_user=self.custom_user,
            journalist_name='Serializer Journalist',
            bio='Journalist for serialization tests.')

    def test_journalist_serialization(self):
        serializer = JournalistSerializer(self.journalist)
        data = serializer.data
        self.assertEqual(data['custom_user']['user']['username'],
                         'serializerjournalist')
        self.assertEqual(data['journalist_name'],
                         'Serializer Journalist')
        self.assertEqual(data['bio'],
                         'Journalist for serialization tests.')


# Article Serializer Tests
class ArticleSerializerTest(TestCase):
    def setUp(self):
        # Create a User, CustomUser, Journalist, and Article for testing
        self.user = User.objects.create_user(
            username='serializerarticle',
            password='testpass')
        self.custom_user = CustomUser.objects.create(
            user=self.user,
            role='journalist')
        self.journalist = Journalist.objects.create(
            custom_user=self.custom_user,
            journalist_name='Serializer Journalist',
            bio='Journalist for serialization tests.')
        self.article = Article.objects.create(
            title='Serializer Article',
            content='Content for serialization tests.',
            journalist=self.journalist,
            status='published')

    def test_article_serialization(self):
        serializer = ArticleSerializer(self.article)
        data = serializer.data
        self.assertEqual(data['title'],
                         'Serializer Article')
        self.assertEqual(data['content'],
                         'Content for serialization tests.')
        self.assertEqual(data
                         ['journalist']['custom_user']
                         ['user']['username'],
                         'serializerarticle')
        self.assertEqual(data['status'], 'published')


# Reader Serializer Tests
class ReaderSerializerTest(TestCase):
    def setUp(self):
        # Create a User, CustomUser, and Reader for testing
        self.user = User.objects.create_user(
            username='serializerreader',
            password='testpass')
        self.custom_user = CustomUser.objects.create(
            user=self.user,
            role='reader')
        self.reader = Reader.objects.create(
            custom_user=self.custom_user,
            reader_name='Serializer Reader')

    def test_reader_serialization(self):
        serializer = ReaderSerializer(self.reader)
        data = serializer.data
        self.assertEqual(data['custom_user']['user']['username'],
                         'serializerreader')
        self.assertEqual(data['reader_name'], 'Serializer Reader')
