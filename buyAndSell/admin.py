from django.contrib import admin
from .models import *

# Register your models here.
class UserAdmin(admin.ModelAdmin):
  list_display = ['id', 'username', 'email', 'first_name', 'last_name']
  list_display_links = ['id', 'username', 'email', 'first_name', 'last_name']
  list_filter = ['is_superuser', 'is_staff', 'date_joined']
  search_fields = ('username', 'first_name', 'last_name', 'is_superuser')

  
admin.site.register(User, UserAdmin)
admin.site.register(Store)
admin.site.register(Product)
admin.site.register(Post)
admin.site.register(Account)
admin.site.register(Cart)
admin.site.register(User_profile)
admin.site.register(Comment)
admin.site.register(Like)