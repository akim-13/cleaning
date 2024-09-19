from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Location, User, Zone, Mark, Comment, Sector
from .forms import CustomUserCreationForm, CustomUserChangeForm

# ??: BaseUserAdmin is the same as UserAdmin, so what does this inheritance mean?
class AdminPanel(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    # These fields are displayed on the admin page.
    list_display = ('username', 'is_staff', 'is_active', 'role')
    list_filter = ('is_staff', 'is_active', 'role')
    fieldsets = (
        (None, {'fields': ('username', 'password', 'role', 'location')}),
        ('Доступы', {'fields': ('is_active',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'location', 'role', 'is_active'),
        }),
    )
    search_fields = ('username',)
    ordering = ('username',)
    filter_horizontal = ('location',)

    # Adding the action to activate users
    actions = ['activate_users']

    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
    activate_users.short_description = 'Активировать выбранных пользователей'

admin.site.register(User, AdminPanel)
admin.site.register(Location)
admin.site.register(Zone)
admin.site.register(Mark)
admin.site.register(Comment)
admin.site.register(Sector)
