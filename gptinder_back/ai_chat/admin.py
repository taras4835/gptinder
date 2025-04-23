from django.contrib import admin
from .models import Chat, Message

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('created_at',)

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'created_at', 'updated_at', 'message_count')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title', 'user__username')
    date_hierarchy = 'created_at'
    inlines = [MessageInline]
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'role', 'short_content', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('content', 'chat__title')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    
    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = 'Content'
