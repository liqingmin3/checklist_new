from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Checklist(models.Model):
    title = models.CharField(max_length=200)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_items = models.IntegerField(default=0)
    total_items = models.IntegerField(default=0)

    def __str__(self):
        return self.title

class TemplateCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="分类名称")
    order = models.PositiveIntegerField(default=0, help_text="用于排序的字段")

    class Meta:
        ordering = ['order']
        verbose_name = "模板分类"
        verbose_name_plural = "模板分类"

    def __str__(self):
        return self.name

class ChecklistTemplate(models.Model):
    category = models.ForeignKey(TemplateCategory, related_name='templates', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="所属分类")
    title = models.CharField(max_length=200)
    usage_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    creation_count = models.PositiveIntegerField(default=0, help_text="记录模板被发布的次数")
    last_created_at = models.DateTimeField(null=True, blank=True, help_text="记录模板最后一次被发布的时间")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('template_detail', args=[str(self.id)])

class TemplateItem(models.Model):
    template = models.ForeignKey(ChecklistTemplate, related_name='items', on_delete=models.CASCADE)
    group_title = models.CharField(max_length=200, help_text="项目组标题，如 '炸服'")
    title = models.CharField(max_length=200, verbose_name="确认项")
    description = models.TextField(blank=True, null=True, verbose_name="说明")
    image = models.ImageField(upload_to='template_images/', blank=True, null=True, verbose_name="模板图片")
    order = models.PositiveIntegerField(default=0, help_text="用于排序的字段")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.group_title} - {self.title}"

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.checklist.title}'

class ChecklistItem(models.Model):
    checklist = models.ForeignKey(Checklist, related_name='items', on_delete=models.CASCADE)
    group_title = models.CharField(max_length=200, help_text="项目组标题，如 '炸服'")
    title = models.CharField(max_length=200, verbose_name="确认项")
    description = models.TextField(blank=True, null=True, verbose_name="说明")
    image = models.ImageField(upload_to='checklist_images/', blank=True, null=True, verbose_name="模板图片")
    order = models.PositiveIntegerField(default=0, help_text="用于排序的字段")
    is_completed = models.BooleanField(default=False, verbose_name="是否完成")
    modified_at = models.DateTimeField(auto_now=True, verbose_name="修改时间")
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='modified_items', verbose_name="修改人")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.group_title} - {self.title}"
