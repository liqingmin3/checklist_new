from django.contrib import admin
from .models import Checklist, ChecklistTemplate, Favorite, ChecklistItem, TemplateCategory, TemplateItem

# Register your models here.
admin.site.register(Checklist)
admin.site.register(ChecklistTemplate)
admin.site.register(Favorite)
admin.site.register(ChecklistItem)
admin.site.register(TemplateCategory)
admin.site.register(TemplateItem)
