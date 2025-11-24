# News2U - Django News Platform

A multi-user news platform built with Django that allows journalists to
create articles and newsletters, editors to review content, publishers
to distribute content, and readers to subscribe to their favorite
journalists and publishers.

# Features

- **Multi-role users**: Journalists, Editors, Publishers, and
Readers
- **Article workflow for Journalists**: Create → Submit to Editor →
Approve → Publish (independently or via publisher)
- **Newsletter system**: Create newsletters with multiple articles
- **Subscription system**: Readers can subscribe to journalists and
publishers
- **Email notifications**: Subscribers receive emails when content is
approved
- **Associations**: Journalists can submit to various editors and
publishers, Editors can work with various journalists and publishers,
publishers can work with various journalists and editors.
- **Admin approval**: All new users require admin approval before
accessing the system, i.e Journalists, Editors and Publishers need to
be approved by admin (superuser) but readers are immediately active. If
the application is to be monetised, the readers will only be able to
access content after payment.
- **API Endpoint** - Creating API endpoints for subscribing and
retrieving of articles and newsletters (See Planning Folder)


## User Roles

### Admin
- Superuser
- Logs in to Django Admin
- Can view ALL users
- Can view ALL publications
- Can add, edit, delete any content in the application

### Journalist
- Create and edit articles and newsletters
- View draft articles, revise articles and save for later
- Submit content to editors for review
- Publish articles and newsletters independently or through publishers
- View published articles and newsletters
- View subscribers and associated publishers
- Delete articles or newsletters

### Editor
- Review and approve/decline articles and newsletters
- Edit content before approval
- View published articles and newsletters
- Delete articles or newsletters

### Publisher
- Review journalist requests for publication
- Publish articles through their publication house
- Create newsletters
- View associated journalists and editors

### Reader
- Subscribe to journalists and publishers
- Receive email notifications for new content
- View published articles and newsletters

## Installation

### Prerequisites (Install requirements.txt)
- asgiref==3.10.0
- crispy-bootstrap4==2025.6
- Django==5.2.8
- django-crispy-forms==2.5
- djangorestframework==3.16.1
- mysqlclient==2.2.7
- pillow==12.0.0
- sqlparse==0.5.3
- pip
- Virtual environment (recommended)

### Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure email settings in `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

5. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Create a superuser for the admin role and application control:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

8. Access the application at `http://127.0.0.1:8000/`

## Usage

### First Steps

1. **Register an account** - Choose your role (Journalist, Editor,
Publisher, or Reader)
2. **Wait for admin approval** - The admin must approve your account
before you can log in
3. **Log in** and start using the platform based on your role

### For Journalists

1. Create an article from your dashboard
2. Select articles to include in newsletters (optional)
3. Submit to an editor for review
4. After approval, choose to publish independently or via a publisher

### For Editors

1. View pending review requests
2. Review, edit, or approve content
3. Provide feedback to journalists

### For Publishers

1. View articles submitted to your publication
2. Publish approved articles
3. Create newsletters featuring published content

### For Readers

1. Browse available journalists and publishers
2. Subscribe to your favorites
3. Receive email notifications when new content is published


## Key Models

- **CustomUser**: Extended user model with role-based access
- **Journalist**: Journalist profile with bio and interests
- **Editor**: Editor profile with field of interest
- **Publisher**: Publication house profile
- **Article**: News articles with workflow states
- **Newsletter**: Collections of articles

## Technologies Used

- **Backend**: Django 5.2.8
- **Database**: SQLite (development)
- **Frontend**: HTML, CSS, Bootstrap
- **Forms**: Django Crispy Forms
- **Email**: Django email backend with Gmail SMTP
- **API Endpoints**: For readers to subscribe and retrieve publications

## Known Issues

- Email notifications require proper Gmail app password configuration
- Image uploads require media file configuration
- Some features require specific user permissions

## Future Improvements

- Social media integration
- Advanced search functionality
- Article analytics
- Mobile responsiveness improvements
- Real-time notifications

## Author

Created as part of a Django web development course project.
Elizabeth Füzy


## Current users if reviewer wishes to login and test

Journalists usernames (all passwords = journalist):
Jane
Samantha
Nelly

Editors usernames (all passwords = editor!!)
Jack
Gideon
Dineo
Vernon Gouws

Publisher usernames (all passwords = publisher)
Molly
Craig
Jason

Reader usernames (all passwords = reader!!)
Paula
Brandon

## Personal Feedback Notes to Reviewer

Assignment Feedback: Django News Platform (News2U)
Project Completion
I have successfully completed all core requirements for this assignment,
implementing a fully functional multi-role news platform with the
following features:

- Multi-user authentication system (Journalists, Editors, Publishers, Readers)
- Article creation, submission, and approval workflow
- Newsletter creation with article integration
- Editor review and approval system
- Email notifications to subscribers upon article approval (I opted to
not use Django signals although I wanted to but I was under time
pressure and included the email funcitonality in the view logic.)
- Subscription management for readers
- Django REST API endpoints for article retrieval
- Role-based permissions and access control
- Admin approval workflow for new users
- Unit Testing
- Migrated to mariaDB

Code Quality
Throughout development, I used Flake8 for code linting to maintain
Python code quality standards and ensure consistent formatting across
the project. I couldn't change the settings.py flake flags and two view
flags were not used in the code but it ws used in the backend.

Challenges and Timeline Concerns
This assignment presented significant complexity that exceeded the
expected time guidelines and it took me 18 days working more than 4 hours
most days. The various roles with their permissions and subsequent views,
templates and urls most definitely requires adequate time and without
continous assistance from Github co-pilot, Google, Claude A.I and
StackOverflow, it would have probably taken me at least another month. I
would love to troubleshoot to learn from it but had to often ask A.I
to help troubleshoot for the sake of time and I think that robbed me of
a great learning opportunity.

Time Management Trade-offs:
While all functional requirements have been met, I made the strategic
decision to prioritise working functionality over extensive UI polish.
Given that I am currently behind on multiple assignments in this course,
I allocated my time to ensure:

All features work correctly
The code is clean and maintainable
Core user workflows are complete and functional
I adhere to PEP 8 Guidelines

Areas for Future Enhancement that I would have
liked to include (given additional time):

Enhanced CSS styling and responsive design
More sophisticated UI/UX improvements
Additional error handling and user feedback
More comprehensive testing coverage
Performance optimizations

Reflection
This assignment provided valuable hands-on experience with complex
Django concepts including signals alternatives, many-to-many
relationships, role-based permissions, REST API development, and email
integration. While the timeline was challenging given the scope, I
believe I successfully delivered a working application that meets all
specified requirements.

I believe this feedback is important for future cohorts: the assignment
scope should either be reduced or the timeline extended to allow
students adequate time for both functionality and polish, particularly
for those who are new to Django.

## Note to the reviewer
I would really like to focus on the next assignments, if something is
incomplete I am happy to resubmit, but can I kindly ask that you have
some leniency with marking and not request a resubmission for menial
things that are not actually required. I am aware that the UI can be
improved but I did my absolute best within the time frame and focused on
functionality and meeting requirements for the assignment.


