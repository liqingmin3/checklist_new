from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Checklist, ChecklistTemplate, Favorite, ChecklistItem, TemplateCategory, TemplateItem
from collections import defaultdict
from django.db import transaction
from django.db.models import F

@login_required
def home(request):
    # 获取最近新建的15个Checklist
    recent_checklists = Checklist.objects.filter(creator=request.user).order_by('-created_at')[:15]

    # 获取用于“快速新建”的模板，并根据查询参数排序
    quick_create_sort = request.GET.get('quick_create_sort', 'most_created')
    if quick_create_sort == 'recent_created':
        popular_templates = ChecklistTemplate.objects.order_by(F('last_created_at').desc(nulls_last=True))[:15]
    else:
        # 默认按创建次数排序
        quick_create_sort = 'most_created'
        popular_templates = ChecklistTemplate.objects.order_by(F('creation_count').desc(nulls_last=True))[:15]

    # 获取当前用户的收藏
    favorites = Favorite.objects.filter(user=request.user)

    context = {
        'recent_checklists': recent_checklists,
        'popular_templates': popular_templates,
        'favorites': favorites,
        'quick_create_sort': quick_create_sort,
    }
    return render(request, 'dashboard/home.html', context)

@login_required
def checklist_detail(request, checklist_id):
    checklist = get_object_or_404(Checklist, pk=checklist_id)
    
    # 按 group_title 分组
    items_by_group = defaultdict(list)
    for item in checklist.items.all():
        items_by_group[item.group_title].append(item)

    context = {
        'checklist': checklist,
        'items_by_group': dict(items_by_group),
    }
    return render(request, 'dashboard/checklist_detail.html', context)

@login_required
def execute_checklist(request, checklist_id):
    checklist = get_object_or_404(Checklist, pk=checklist_id)

    if request.method == 'POST':
        completed_item_ids = request.POST.getlist('completed_items')
        
        # 更新所有相关 item 的状态
        for item in checklist.items.all():
            if str(item.id) in completed_item_ids:
                if not item.is_completed:
                    item.is_completed = True
                    item.modified_by = request.user
                    item.save()
            else:
                if item.is_completed:
                    item.is_completed = False
                    item.modified_by = request.user
                    item.save()

        # 更新 Checklist 的完成计数
        checklist.completed_items = checklist.items.filter(is_completed=True).count()
        checklist.total_items = checklist.items.count()
        checklist.save()

    # 按 group_title 分组
    items_by_group = defaultdict(list)
    for item in checklist.items.all():
        items_by_group[item.group_title].append(item)

    context = {
        'checklist': checklist,
        'items_by_group': dict(items_by_group),
    }
    return render(request, 'dashboard/execute_checklist.html', context)

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger # Import paginator classes

@login_required
def checklist_list(request):
    all_checklists = Checklist.objects.all().order_by('-created_at')
    
    paginator = Paginator(all_checklists, 30) # Show 30 checklists per page

    page = request.GET.get('page')
    try:
        checklists = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        checklists = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        checklists = paginator.page(paginator.num_pages)

    context = {
        'checklists': checklists,
    }
    return render(request, 'dashboard/checklist_list.html', context)

@login_required
def template_list(request):
    # prefetch_related a good practice to reduce database queries
    categories = TemplateCategory.objects.prefetch_related('templates').all()
    all_templates = ChecklistTemplate.objects.all()
    context = {
        'categories': categories,
        'all_templates': all_templates,
    }
    return render(request, 'dashboard/template_list.html', context)

@login_required
def template_detail(request, template_id):
    template = get_object_or_404(ChecklistTemplate, pk=template_id)
    mode = request.GET.get('mode', 'view')

    if request.method == 'POST' and mode == 'edit':
        with transaction.atomic():
            template.title = request.POST.get('title', template.title)
            template.save()

            processed_item_ids = set()
            group_index = 0
            while f'group-{group_index}-title' in request.POST:
                group_title = request.POST[f'group-{group_index}-title']
                item_index = 0
                while f'item-{group_index}-{item_index}-title' in request.POST:
                    item_prefix = f'item-{group_index}-{item_index}'
                    title = request.POST[f'{item_prefix}-title']
                    description = request.POST.get(f'{item_prefix}-description', '')
                    item_id = request.POST.get(f'{item_prefix}-id')
                    
                    item_data = {
                        'template': template,
                        'group_title': group_title,
                        'title': title,
                        'description': description,
                        'order': (group_index * 1000) + item_index
                    }

                    image_file = request.FILES.get(f'{item_prefix}-image')
                    if image_file:
                        item_data['image'] = image_file

                    if item_id:
                        # Update existing item
                        TemplateItem.objects.filter(pk=item_id, template=template).update(**item_data)
                        # If image is being updated, we need to fetch the object and save it
                        if image_file:
                            item = TemplateItem.objects.get(pk=item_id)
                            item.image = image_file
                            item.save()
                        processed_item_ids.add(int(item_id))
                    else:
                        # Create new item
                        new_item = TemplateItem.objects.create(**item_data)
                        processed_item_ids.add(new_item.id)
                    
                    item_index += 1
                group_index += 1

            # Delete items that were not in the form
            template.items.exclude(id__in=processed_item_ids).delete()

        return redirect(f"{template.get_absolute_url()}?mode=view")

    items_by_group = defaultdict(list)
    for item in template.items.all().order_by('order'):
        items_by_group[item.group_title].append(item)
    
    context = {
        'template': template,
        'items_by_group': dict(items_by_group),
        'is_edit_mode': mode == 'edit'
    }
    return render(request, 'dashboard/template_detail.html', context)

from django.utils import timezone # Import timezone

@login_required
def publish_template(request, template_id):
    template = get_object_or_404(ChecklistTemplate, pk=template_id)
    
    if request.method == 'POST':
        with transaction.atomic():
            selected_item_ids = request.POST.getlist('selected_items')
            
            # 1. Create a new Checklist instance
            new_checklist_title = template.title # Use template title directly
            new_checklist = Checklist.objects.create(
                title=new_checklist_title,
                creator=request.user,
                total_items=0, # Will be updated later
                completed_items=0 # Will be updated later
            )

            total_items_count = 0
            completed_items_count = 0

            # 2. Convert selected TemplateItems to ChecklistItems
            all_template_items = template.items.all().order_by('order')
            for item in all_template_items:
                is_selected = str(item.id) in selected_item_ids
                
                ChecklistItem.objects.create(
                    checklist=new_checklist,
                    group_title=item.group_title,
                    title=item.title,
                    description=item.description,
                    image=item.image, # Copy image from template item
                    order=item.order,
                    is_completed=is_selected, # Set based on selection
                    modified_at=timezone.now(),
                    modified_by=request.user
                )
                total_items_count += 1
                if is_selected:
                    completed_items_count += 1
            
            # Update total_items and completed_items for the new Checklist
            new_checklist.total_items = total_items_count
            new_checklist.completed_items = completed_items_count
            new_checklist.save()

            # 更新模板的使用统计
            template.creation_count += 1
            template.last_created_at = timezone.now()
            template.save()

            # 3. Redirect to home page
            return redirect('home')

    # GET request logic
    items_by_group = defaultdict(list)
    all_items = template.items.all().order_by('order')
    
    global_item_counter = 0
    for item in all_items:
        item.global_order = global_item_counter + 1
        global_item_counter += 1
        items_by_group[item.group_title].append(item)

    context = {
        'main_object': template, # Use a generic name for template/checklist
        'items_by_group': dict(items_by_group),
        'is_edit_checklist_mode': False, # Indicate this is for new checklist creation
    }
    return render(request, 'dashboard/publish_template.html', context)


@login_required
def edit_checklist(request, checklist_id):
    checklist = get_object_or_404(Checklist, pk=checklist_id)

    if request.method == 'POST':
        with transaction.atomic():
            selected_item_ids = request.POST.getlist('selected_items')
            
            total_items_count = 0
            completed_items_count = 0

            # Update existing ChecklistItems
            all_checklist_items = checklist.items.all().order_by('order')
            for item in all_checklist_items:
                was_completed = item.is_completed
                is_now_selected = str(item.id) in selected_item_ids
                
                if was_completed != is_now_selected: # Only update if status changed
                    item.is_completed = is_now_selected
                    item.modified_at = timezone.now()
                    item.modified_by = request.user
                    item.save()
                
                total_items_count += 1
                if is_now_selected:
                    completed_items_count += 1
            
            # Update Checklist's total_items and completed_items
            checklist.total_items = total_items_count
            checklist.completed_items = completed_items_count
            checklist.save()

            return redirect('home')

    # GET request logic
    items_by_group = defaultdict(list)
    all_items = checklist.items.all().order_by('order')
    
    global_item_counter = 0
    for item in all_items:
        item.global_order = global_item_counter + 1
        global_item_counter += 1
        items_by_group[item.group_title].append(item)

    context = {
        'main_object': checklist, # Use a generic name for template/checklist
        'items_by_group': dict(items_by_group),
        'is_edit_checklist_mode': True, # Indicate this is for editing existing checklist
    }
    return render(request, 'dashboard/publish_template.html', context)
