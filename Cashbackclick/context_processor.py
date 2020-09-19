from core.models import Category
from accounts.forms import SignInViaUsernameForm


def add_variable_to_context(request):
    return {
        'category_list': Category.objects.all()
    }


def add_form_to_context(request):
    return {
        'loginform': SignInViaUsernameForm
    }