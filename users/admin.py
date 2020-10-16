from django.contrib import admin
from users.models import Profile, Follow
from django.contrib.auth.admin import UserAdmin


# Register your models here.

class ProfileAdmin(UserAdmin):
    
    list_display = ('name', 'email', 'username', 'date_joined', 'last_login',
                    'is_admin', 'is_active')
    search_fields = ('email', 'username')
    readonly_fields = ('date_joined', 'last_login')
    

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    exclude = ('groups','user_permissions',)


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Follow)