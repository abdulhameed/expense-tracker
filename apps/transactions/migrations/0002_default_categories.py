from django.db import migrations

DEFAULT_CATEGORIES = [
    # Expense categories
    {"name": "Food & Dining", "category_type": "expense", "icon": "utensils", "color": "#F59E0B"},
    {"name": "Transportation", "category_type": "expense", "icon": "car", "color": "#3B82F6"},
    {"name": "Shopping", "category_type": "expense", "icon": "shopping-bag", "color": "#EC4899"},
    {"name": "Entertainment", "category_type": "expense", "icon": "film", "color": "#8B5CF6"},
    {"name": "Healthcare", "category_type": "expense", "icon": "heart", "color": "#EF4444"},
    {"name": "Housing", "category_type": "expense", "icon": "home", "color": "#10B981"},
    {"name": "Utilities", "category_type": "expense", "icon": "zap", "color": "#F97316"},
    {"name": "Education", "category_type": "expense", "icon": "book", "color": "#06B6D4"},
    {"name": "Travel", "category_type": "expense", "icon": "plane", "color": "#14B8A6"},
    {"name": "Other Expense", "category_type": "expense", "icon": "more-horizontal", "color": "#6B7280"},
    # Income categories
    {"name": "Salary", "category_type": "income", "icon": "briefcase", "color": "#10B981"},
    {"name": "Freelance", "category_type": "income", "icon": "code", "color": "#3B82F6"},
    {"name": "Investment", "category_type": "income", "icon": "trending-up", "color": "#8B5CF6"},
    {"name": "Gift", "category_type": "income", "icon": "gift", "color": "#EC4899"},
    {"name": "Other Income", "category_type": "income", "icon": "more-horizontal", "color": "#6B7280"},
]


def create_default_categories(apps, schema_editor):
    Category = apps.get_model("transactions", "Category")
    import uuid

    for cat in DEFAULT_CATEGORIES:
        Category.objects.get_or_create(
            name=cat["name"],
            category_type=cat["category_type"],
            project=None,
            is_default=True,
            defaults={
                "id": uuid.uuid4(),
                "icon": cat["icon"],
                "color": cat["color"],
            },
        )


def remove_default_categories(apps, schema_editor):
    Category = apps.get_model("transactions", "Category")
    Category.objects.filter(is_default=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("transactions", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_default_categories, remove_default_categories),
    ]
