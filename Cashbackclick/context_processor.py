from core.models import Category ,Order , Share , Sharelist
from accounts.forms import SignInViaUsernameForm
import django
import datetime ,datetime
import pytz

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
                users = 1
                count =0
                date_today = datetime.date.today()
                my_share_lists = Sharelist.objects.filter(shared_user = request.user)
                for myshare in my_share_lists:
                    if myshare.share.end_date < datetime.datetime(year= int(date_today.year), month = int(date_today.month) , day = int(date_today.day) , tzinfo=pytz.UTC):
                        count = count +1
                if count == len(my_share_lists):
                    users = 0
                else:
                    users =1
            else:
                users =1
        else:
            users =0

        return {
            'user_valid': users
        }
            
    except Sharelist.DoesNotExist:
        return {
            'user_valid': 0
        }
    except:
        return {
            'user_valid': 0
        }





