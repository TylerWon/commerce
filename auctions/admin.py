from django.contrib import admin

from .models import User, Category, Bid, Listing, Comment

# Register your models here.
class ListingAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Bid)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Comment)