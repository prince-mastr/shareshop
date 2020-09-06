from core.models import Category


def add_variable_to_context(request):
    return {
        'category_list': Category.objects.all()
    }