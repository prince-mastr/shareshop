from core.models import Category ,Order , Share , Sharelist
from accounts.forms import SignInViaUsernameForm
import django
import datetime

def add_variable_to_context(request):
    csrf_token = django.middleware.csrf.get_token(request) 
    return {
        'csrf_token':csrf_token,
        'category_list': Category.objects.all()
    }


def add_form_to_context(request):
    return {
        'loginform': SignInViaUsernameForm
    }

def present_order(request):
    try:
        if request.user.is_authenticated:
            Present_order = Order.objects.get(user = request.user, ordered = False)
            return {
                'present_order': Present_order
            }
        else:
            return {
            'present_order': 0
            }
    except Order.DoesNotExist:
        return {
            'present_order': 0
        }

def check_user(request):
    try:
        if request.user.is_authenticated:
            if not request.user.userprofile.owner:
                my_share_lists = Sharelist.objects.filter(shared_user = request.user)
                for myshare in my_share_lists:
                    if myshare.share.end_date >= datetime.datetime.now():
                        return {
                            'user_valid': 1
                            }
                else:
                    return {
                            'user_valid': 0
                        }
            else:
                return {
                        'user_valid': 1
                    }
    except:
        pass




