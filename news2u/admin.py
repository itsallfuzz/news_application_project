from django.contrib import admin
from .models import AdminApproval, CustomUser, Editor, Journalist
from .models import Publisher, Article, Newsletter, Reader
from django.core.mail import send_mail

# Register your models here.

# Publisher model
admin.site.register(Publisher)

# Editor model
admin.site.register(Editor)

# Journalist model
admin.site.register(Journalist)

# Article model
admin.site.register(Article)

# Newsletter model
admin.site.register(Newsletter)

# Reader model
admin.site.register(Reader)


# CustomUser admin
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'role', 'created_at', 'is_approved')
    search_fields = ('user__username', 'role')
    list_filter = ('role', 'created_at', 'is_approved')
    actions = ['approve_user', 'decline_user']

    readonly_fields = ('user', 'role', 'created_at', 'get_bio')
    fields = (
        'user',
        'role',
        'created_at',
        'get_bio',
        'is_approved',
        'declined_for'
        )

    def get_username(self, obj):
        """Display the username from the related User object"""
        return obj.user.username  # obj is CustomUser, obj.user is User
    get_username.short_description = 'Username'
    get_username.admin_order_field = 'user__username'

    def get_bio(self, obj):
        """Show bio/description from profile"""
        if obj.role == 'journalist' and hasattr(obj.user, 'journalist'):
            return obj.user.new_journalist.journalist_bio
        elif obj.role == 'editor' and hasattr(obj.user, 'editor'):
            return obj.user.new_editor.editor_bio
        elif obj.role == 'publisher' and hasattr(obj.user, 'publisher'):
            return obj.user.publisher.publisher_description
        return "No bio available"
    get_bio.short_description = 'Bio/Description'

    def approve_user(self, request, queryset):
        queryset.update(is_approved=True)
        for custom_user in queryset:
            custom_user.user.is_active = True
            custom_user.user.save()
        self.message_user(request, f"{queryset.count()} user(s) approved.")
    approve_user.short_description = "Approve selected users"

    def decline_user(self, request, queryset):
        """Decline user registrations and notify via email."""
        for custom_user in queryset:
            send_mail(
                subject='Registration Declined',
                message=(
                    f'Sorry, your {custom_user.role} registration was '
                    f'declined.\n\nReason: {custom_user.declined_for}'
                ),
                from_email='admin@news2u.com',
                recipient_list=[custom_user.user.email],
                fail_silently=True,
            )
            custom_user.user.delete()
        self.message_user(
            request,
            f"{queryset.count()} user(s) declined and notified."
            )
    decline_user.short_description = "Decline selected users"


# AdminApproval admin - SEPARATE CLASS!
@admin.register(AdminApproval)
class AdminApprovalAdmin(admin.ModelAdmin):
    list_display = (
        'get_username',
        'role',
        'is_approved',
        'requested_at',
        'declined_for'
        )
    list_editable = ('declined_for',)
    # Note: double user__ because AdminApproval.user is CustomUser
    search_fields = ('user__user__username', 'role')
    list_filter = ('role', 'is_approved', 'requested_at')
    actions = ['approve_user', 'decline_user']

    readonly_fields = ('user', 'role', 'requested_at')
    fields = ('user', 'role', 'is_approved', 'declined_for', 'requested_at')

    def get_username(self, obj):
        """Display the username from the related User object"""
        return obj.user.user.username
    get_username.short_description = 'Username'
    get_username.admin_order_field = 'user__user__username'

    def approve_user(self, request, queryset):
        queryset.update(is_approved=True)
        for approval in queryset:
            # Activate the user
            approval.user.user.is_active = True
            approval.user.user.save()
            # Update CustomUser
            approval.user.is_approved = True
            approval.user.save()
        self.message_user(request, f"{queryset.count()} user(s) approved.")
    approve_user.short_description = "Approve selected users"

    def decline_user(self, request, queryset):
        """Decline user registrations and notify via email."""

        for approval in queryset:
            # Make sure a reason was provided
            if not approval.declined_for:
                self.message_user(
                    request, "Please add a decline reason in the "
                    "'Declined for' field first.", level='error')
                return

        for approval in queryset:
            send_mail(
                subject='Registration Declined',
                message=(
                    f'Sorry, your {approval.role} registration was '
                    f'declined.\n\nReason: {approval.declined_for}'
                ),
                from_email='admin@news2u.com',
                recipient_list=[approval.user.user.email],
                fail_silently=True,
            )
            approval.user.user.delete()
        self.message_user(
            request, f"{queryset.count()} user(s) declined and notified.")
    decline_user.short_description = "Decline selected users"
