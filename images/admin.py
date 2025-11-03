from django.contrib import admin
from .models import ImageItem, ProcessedVersion


@admin.register(ImageItem)
class ImageItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'owner', 'created_at')
    search_fields = ('title', 'owner__username')
    list_filter = ('created_at',)


@admin.register(ProcessedVersion)
class ProcessedVersionAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'note', 'created_at')
    search_fields = ('note', 'item__title')
    list_filter = ('created_at',)
