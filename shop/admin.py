from django.contrib import admin
from .models import Cart,Product,CartItem,Feature,ProductFeature,Category,Comment,MenuCategory,MenuItem,MenuSection,AmazingSlider,Checkout
# Register your models here.
admin.site.register(Cart)
admin.site.register(Checkout)
admin.site.register(AmazingSlider)
admin.site.register(CartItem)
admin.site.register(Product)
admin.site.register(Feature)
admin.site.register(ProductFeature)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(MenuCategory)
admin.site.register(MenuSection)
admin.site.register(MenuItem)


from .models import Ticket, Reply

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'status', 'dateTime')
    list_filter = ('status', 'dateTime')
    search_fields = ('title', 'content', 'user__username')

@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket', 'user', 'dateTime')
    search_fields = ('ticket__title', 'content', 'user__username')
