from django.urls import path
from . import views


urlpatterns = [
     # Authentication
     path("", views.home, name="home"),
     path("register/", views.register, name="register"),
     path("register_publisher/", views.register_publisher,
          name="register_publisher"),
     path("register_editor/", views.register_editor,
          name="register_editor"),
     path("register_journalist/", views.register_journalist,
          name="register_journalist"),
     path("register_reader/", views.register_reader,
          name="register_reader"),
     path("registration_pending/", views.registration_pending,
          name="registration_pending"),


     # Login and Logout
     path("login/", views.user_login, name="login"),
     path("logout/", views.user_logout, name="logout"),


     # Homepage
     path("home/", views.home, name="home"),


     # Password management
     path("forgot_password/", views.forgot_password,
          name="forgot_password"),
     path("send_password_reset/", views.send_password_reset,
          name="send_password_reset"),
     path("news2u/reset_password/<str:token>/", views.reset_password,
          name="reset_password"),


     # Dashboards
     path("publisher_dashboard/", views.publisher_dashboard,
          name="publisher_dashboard"),
     path("editor_dashboard/", views.editor_dashboard,
          name="editor_dashboard"),
     path("journalist_dashboard/", views.journalist_dashboard,
          name="journalist_dashboard"),
     path("reader_dashboard/", views.reader_dashboard,
          name="reader_dashboard"),

     # Published Articles and Newsletters - ALL Roles
     path("my_published_articles/", views.my_published_articles,
          name="my_published_articles"),
     path("my_published_newsletters/", views.my_published_newsletters,
          name="my_published_newsletters"),

     # ============================================================
     # CRUD FUNCTIONS
     # ============================================================

     path("create_newsletter/", views.create_newsletter,
          name="create_newsletter"),


     # VIEW
     path("view_subscriber_newsletters/",
          views.view_subscriber_newsletters,
          name="view_subscriber_newsletters"),
     path("article/<int:article_id>/", views.article_detail,
          name="article_detail"),
     path("newsletter/<int:newsletter_id>/", views.newsletter_detail,
          name="newsletter_detail"),


     # Create Functions
     path("create_article/", views.create_article,
          name="create_article"),
     path('article/<int:article_id>/select-editor/',
          views.select_editor,
          name='select_editor'),
     path('create_publisher_newsletter/',
          views.create_publisher_newsletter,
          name='create_publisher_newsletter'),
     path('select_editor_newsletter/<int:newsletter_id>/',
          views.select_editor_newsletter,
          name='select_editor_newsletter'),


     # Draft Articles
     path("draft_articles/", views.draft_articles,
          name="draft_articles"),
     path("draft_newsletters/", views.draft_newsletters,
          name="draft_newsletters"),


     # Edit Article & Newsletter
     path('article/<int:article_id>/edit/', views.edit_article,
          name='edit_article'),
     path('newsletter/<int:newsletter_id>/edit/', views.edit_newsletter,
          name='edit_newsletter'),
     path('newsletter/<int:newsletter_id>/add-article/<int:article_id>/',
          views.add_article_to_newsletter,
          name='add_article_to_newsletter'),


     # Submitted Articles
     path("article_submit_success/",
          views.article_submit_success,
          name="article_submit_success"),
     path("view_submitted_articles/",
          views.view_submitted_articles,
          name="view_submitted_articles"),
     path("view_submitted_newsletters/",
          views.view_submitted_newsletters,
          name="view_submitted_newsletters"),
     path("newsletter_submit_success/",
          views.newsletter_submit_success,
          name="newsletter_submit_success"),


     # Delete Article
     path('article/<int:article_id>/delete/',
          views.delete_article, name='delete_article'),
     path('newsletter/<int:newsletter_id>/delete/',
          views.delete_newsletter, name='delete_newsletter'),

     # Publish Article
     path('article/<int:article_id>/publish-independent/',
          views.publish_independent, name='publish_independent'),
     path('article/<int:article_id>/submit_to_publisher/',
          views.submit_to_publisher, name='submit_to_publisher'),
     path('my_published_articles/', views.my_published_articles,
          name='my_published_articles'),
     path('view_published_article/<int:article_id>/',
          views.view_published_article, name='view_published_article'),
     path('published_by_publisher/<int:article_id>/',
          views.published_by_publisher, name='published_by_publisher'),
     path('view_article_publication_requests/',
          views.view_article_publication_requests,
          name='view_article_publication_requests'),
     path('publish_newsletter_by_publisher/<int:newsletter_id>/',
          views.publish_newsletter_by_publisher,
          name='publish_newsletter_by_publisher'),
     path('publish_success/', views.publish_success,
          name='publish_success'),
     path('view_published_newsletter/<int:newsletter_id>/',
          views.view_published_newsletter,
          name='view_published_newsletter'),
     path('publish_newsletter_by_publisher/<int:newsletter_id>/',
          views.publish_newsletter_by_publisher,
          name='publish_newsletter_by_publisher'),
     path('publish_newsletter/<int:newsletter_id>/',
          views.publish_newsletter, name='publish_newsletter'),

     # Editor functions
     path("view_requests/", views.view_requests, name="view_requests"),
     path("review_article/<int:article_id>/",
          views.review_article, name="review_article"),
     path("review_newsletter/<int:newsletter_id>/",
          views.review_newsletter, name="review_newsletter"),
     path("accept_newsletter/<int:newsletter_id>/",
          views.accept_newsletter, name="accept_newsletter"),
     path('article/<int:article_id>/article_approved/',
          views.article_approved, name='article_approved'),
     path("accept_article/<int:article_id>/",
          views.accept_article, name="accept_article"),
     path("view_accepted_articles/",
          views.view_accepted_articles, name="view_accepted_articles"),
     path("decline_article/<int:article_id>/",
          views.decline_article, name="decline_article"),
     path("view_edited_article/<int:article_id>/",
          views.view_edited_article, name="view_edited_article"),
     path('view_edited_newsletter/<int:newsletter_id>/',
          views.view_edited_newsletter, name='view_edited_newsletter'),
     path("publish_by_publisher/<int:article_id>/",
          views.publish_by_publisher, name="publish_by_publisher"),
     path("view_accepted_newsletters/",
          views.view_accepted_newsletters,
          name="view_accepted_newsletters"),

     # Reader Functions
     path("manage_subscriptions/", views.manage_subscriptions,
          name="manage_subscriptions"),

     # View Editors, Publishers, Journalists
     path("view_all_editors/", views.view_all_editors,
          name="view_all_editors"),
     path("view_my_editors/", views.view_my_editors,
          name="view_my_editors"),
     path("view_all_journalists/", views.view_all_journalists,
          name="view_all_journalists"),
     path("view_my_journalists/", views.view_my_journalists,
          name="view_my_journalists"),
     path("view_all_publishers/", views.view_all_publishers,
          name="view_all_publishers"),
     path("view_my_publishers/", views.view_my_publishers,
          name="view_my_publishers"),


     # API Endpoints
     path("api/articles/", views.api_my_published_articles,
          name="api_my_published_articles"),
     path("api/articles/<int:article_id>/view/", views.api_read_article,
          name="api_read_article"),
     path("api/subscribe/", views.api_manage_subscriptions,
          name="api_manage_subscriptions"),
     path("api/login/", views.api_user_login,
          name="api_user_login"),
]
