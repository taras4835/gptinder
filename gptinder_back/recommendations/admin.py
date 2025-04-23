from django.contrib import admin
from .models import UserRecommendation, UserChat, UserMessage

class UserMessageInline(admin.TabularInline):
    model = UserMessage
    extra = 0
    readonly_fields = ('created_at',)

@admin.register(UserRecommendation)
class UserRecommendationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recommended_user', 'similarity_score', 'is_viewed', 'created_at')
    list_filter = ('is_viewed', 'created_at')
    search_fields = ('user__username', 'recommended_user__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    list_editable = ('is_viewed',)

@admin.register(UserChat)
class UserChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'participants_list', 'message_count', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    inlines = [UserMessageInline]
    filter_horizontal = ('participants',)
    
    def participants_list(self, obj):
        return ", ".join([p.username for p in obj.participants.all()])
    participants_list.short_description = 'Participants'
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'

@admin.register(UserMessage)
class UserMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'sender', 'short_content', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('content', 'sender__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    list_editable = ('is_read',)
    
    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = 'Content'
