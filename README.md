# CheckList

CheckList 是一个基于 Django 框架的**检查清单管理系统**，主要用于游戏测试或其他业务流程的标准化检查。

## 功能概述

### 1. 首页（个人中心）

- **最近新建**：显示用户最近创建的 15 个检查单
- **快速新建**：基于模板快速创建检查单，支持按"最多创建"或"最近创建"排序
- **我的收藏**：显示用户收藏的检查单

### 2. 模板管理

- **模板列表**：展示所有检查清单模板，支持分类浏览
- **模板详情**：
  - **查看模式**：浏览模板内容
  - **编辑模式**：在线编辑模板标题、分组、检查项、说明和图片
- **动态增删**：可在编辑模式下动态添加/删除分组和检查项
- **发布生成**：基于模板创建实际的检查单实例

### 3. 检查单管理

- **检查单列表**：分页展示所有检查单（每页 30 条）
- **检查单详情**：查看检查单内容及完成状态
- **执行检查**：勾选已完成的项目，实时更新进度（已完成/总数）
- **编辑检查单**：修改检查单的勾选状态

### 4. 收藏功能

- 用户可收藏常用的检查单
- 收藏后可在首页快速访问

### 5. 分类管理

- 支持为模板设置分类（TemplateCategory）
- 分类可排序

## 数据模型

### Checklist（检查单实例）
| 字段 | 说明 |
|------|------|
| title | 标题 |
| creator | 创建人 |
| created_at | 创建时间 |
| completed_items | 已完成项数 |
| total_items | 总项数 |

### ChecklistTemplate（检查单模板）
| 字段 | 说明 |
|------|------|
| category | 所属分类 |
| title | 标题 |
| usage_count | 使用次数（预留） |
| creation_count | 发布次数 |
| last_created_at | 最后发布时间 |

### TemplateItem（模板检查项）
| 字段 | 说明 |
|------|------|
| template | 关联模板 |
| group_title | 分组标题（如"炸服"） |
| title | 检查项名称 |
| description | 说明 |
| image | 模板图片 |
| order | 排序字段 |

### ChecklistItem（检查单实际项）
| 字段 | 说明 |
|------|------|
| checklist | 关联检查单 |
| group_title | 分组标题 |
| title | 检查项名称 |
| description | 说明 |
| is_completed | 是否完成 |
| modified_at | 修改时间 |
| modified_by | 修改人 |

### Favorite（收藏）
| 字段 | 说明 |
|------|------|
| user | 用户 |
| checklist | 收藏的检查单 |
| created_at | 收藏时间 |

## 技术栈

- **后端**：Django 5.2.5 + Python 3
- **数据库**：MySQL
- **前端**：Bootstrap 5 + Font Awesome
- **图片存储**：Django FileField（本地存储）

## 路由说明

| URL | 视图函数 | 说明 |
|-----|---------|------|
| `/` | home | 首页/个人中心 |
| `/checklists/` | checklist_list | 检查单列表 |
| `/templates/` | template_list | 模板列表 |
| `/template/<id>/` | template_detail | 模板详情/编辑 |
| `/template/<id>/publish/` | publish_template | 发布模板生成检查单 |
| `/checklist/<id>/edit/` | edit_checklist | 编辑检查单状态 |

## 项目结构

```
CheckList/
├── manage.py              # Django 管理脚本
├── CheckList/             # 项目配置目录
│   ├── settings.py        # 项目设置
│   ├── urls.py            # 根路由配置
│   ├── wsgi.py
│   └── asgi.py
├── dashboard/             # 核心应用
│   ├── models.py          # 数据模型
│   ├── views.py           # 视图函数
│   ├── urls.py            # 应用路由
│   ├── admin.py           # 后台管理
│   ├── migrations/        # 数据库迁移
│   └── templates/         # HTML 模板
│       └── dashboard/
│           ├── home.html
│           ├── template_list.html
│           ├── template_detail.html
│           ├── checklist_list.html
│           ├── checklist_detail.html
│           ├── publish_template.html
│           └── execute_checklist.html
├── media/                 # 用户上传文件存储
│   ├── template_images/
│   └── checklist_images/
└── venv/                  # Python 虚拟环境
```

## 快速开始

### 1. 安装依赖

```bash
cd CheckList
source venv/bin/activate
pip install django mysqlclient
```

### 2. 配置数据库

编辑 `CheckList/settings.py` 中的数据库配置：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'checklist_db',
        'USER': 'root',
        'PASSWORD': 'your_password',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

### 3. 初始化数据库

```bash
cd CheckList
python manage.py migrate
python manage.py createsuperuser
```

### 4. 运行服务器

```bash
python manage.py runserver
```

访问 http://127.0.0.1:8000/ 进入系统。

## 使用流程

1. **创建模板**：在模板列表页面创建新的检查清单模板
2. **编辑模板**：添加分组（如"功能检查"、"炸服测试"等）和具体检查项
3. **发布检查单**：从模板发布生成实际的检查单
4. **执行检查**：勾选已完成的项目，系统自动计算完成进度
5. **编辑状态**：可在事后修改检查项的完成状态

## 注意事项

- 图片文件存储在 `media/` 目录
- 数据库密码等敏感信息建议使用环境变量管理
- 生产环境请关闭 `DEBUG` 模式并设置 `ALLOWED_HOSTS`
- 系统使用 Django 内置认证，需为用户分配适当的权限
