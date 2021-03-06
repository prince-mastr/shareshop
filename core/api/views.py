from django_countries import countries
from django.db.models import Q
from django.contrib import messages
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect ,HttpResponse
from django.utils import timezone
from django.views import generic
from rest_framework.generics import (
    ListAPIView, RetrieveAPIView, CreateAPIView,
    UpdateAPIView, DestroyAPIView
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
import django
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from core.models import Item, OrderItem, Order
from .serializers import (
    ItemSerializer, OrderSerializer, ItemDetailSerializer, AddressSerializer,
    PaymentSerializer, ShareSerializer
)
from core.models import Item, OrderItem, Order, Address, Payment, Coupon, Refund, UserProfile, Variation, ItemVariation ,SharedItem,Share, Sharelist, Category

from django.http import HttpResponseRedirect
from uuid import uuid4 
import stripe
from django.template.loader import get_template

from django.http import HttpResponse
from django.views.generic import View

from core.api.utils import render_to_pdf #created in step 4

import datetime
from core.forms import AddressForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import pytz


#stripe.api_key = settings.STRIPE_SECRET_KEY


class UserIDView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'userID': request.user.id}, status=HTTP_200_OK)


class ItemListView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = ItemSerializer
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.userprofile.owner:
                csrf_token = django.middleware.csrf.get_token(request) 
                queryset = Item.objects.filter(stock = True)
                page = request.GET.get('page', 1)
                paginator = Paginator(queryset, 10)
                try:
                    users = paginator.page(page)
                except PageNotAnInteger:
                    users = paginator.page(1)
                except EmptyPage:
                    users = paginator.page(paginator.num_pages)

                return render(request,"core/products.html",{"object_list":users,
                "csrf_token": csrf_token})
            else:
                csrf_token = django.middleware.csrf.get_token(request)
                queryset = Sharelist.objects.filter(shared_user = request.user,share__shared = True)
                items =[]
                for my_sharelist in queryset:
                    for my_share_item in my_sharelist.share.items.all():
                        if my_share_item.item.stock:
                            items.append(my_share_item.item)
                if len(items):
                    page = request.GET.get('page', 1)
                    paginator = Paginator(list(set(items)), 10)
                    try:
                        users = paginator.page(page)
                    except PageNotAnInteger:
                        users = paginator.page(1)
                    except EmptyPage:
                        users = paginator.page(paginator.num_pages)


                    return render(request,"core/products.html",{"object_list":users,
                    "csrf_token": csrf_token})
                else:
                    users=[]
                    return render(request,"core/products.html",{"object_list":users,
                    "csrf_token": csrf_token})
        else:
            return redirect('accounts:login')
            


class ItemDetailView(generic.DetailView):
    model = Item
    template_name = "core/single.html"
    def get(self, request, *args, **kwargs):
        try:
            pk = kwargs.get("pk",None)
            item = Item.objects.get(id=pk)
            item_list = Item.objects.filter(category = item.category)
            related_items = list(item_list)[:4]
            return render(request, "core/single.html",{"object":item,"object_list":related_items})
        except Item.DoesNotExist:
            #messages.warning(self.request, "You do not have an active order")
            print("hero")
            return redirect("order-list")





class OrderQuantityUpdateView(APIView):
    def post(self, request, *args, **kwargs):
        slug = request.data.get('slug', None)
        if slug is None:
            return Response({"message": "Invalid data"}, status=HTTP_400_BAD_REQUEST)
        item = get_object_or_404(Item, slug=slug)
        order_qs = Order.objects.filter(
            user=request.user,
            ordered=False
        )
        if order_qs.exists():
            order = order_qs[0]
            # check if the order item is in the order
            if order.items.filter(item__slug=item.slug).exists():
                order_item = OrderItem.objects.filter(
                    item=item,
                    user=request.user,
                    ordered=False
                )[0]
                if order_item.quantity > 1:
                    order_item.quantity -= 1
                    order_item.save()
                else:
                    order.items.remove(order_item)
                return Response(status=HTTP_200_OK)
            else:
                return Response({"message": "This item was not in your cart"}, status=HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "You do not have an active order"}, status=HTTP_400_BAD_REQUEST)



def add_to_cart(request, pk):
    item = get_object_or_404(Item, id=pk)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__pk=item.pk).exists():
            order_item.quantity =  order_item.quantity  + 1
            order_item.save()
            return redirect(request.META['HTTP_REFERER'])
        else:
            order.items.add(order_item)
            return redirect(request.META['HTTP_REFERER'])
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        return redirect(request.META['HTTP_REFERER'])


        
    


def add_to_share(request, pk):
    item = get_object_or_404(Item, pk=pk,stock =True)
    share_item, created = SharedItem.objects.get_or_create(
        item=item,
        user=request.user,
        shared=False
    )
    print(share_item, created)
    share_qs = Share.objects.filter(user=request.user, shared=False)
    if share_qs.exists():
        share = share_qs[0]
        # check if the order item is in the order
        if share.items.filter(item__pk=item.pk).exists():
            return redirect(request.META['HTTP_REFERER'])
        else:
            share.items.add(share_item)
            return redirect(request.META['HTTP_REFERER'])
        
    else:
        shared_date = timezone.now()
        share = Share.objects.create(
            user=request.user, shared_date=shared_date)
        share.items.add(share_item)
        return redirect(request.META['HTTP_REFERER'])

def add_to_share_category(request,categoryid):
    items = Item.objects.filter(category__id = categoryid, stock = True)
    for item in items:
        share_item, created = SharedItem.objects.get_or_create(
        item=item,
        user=request.user,
        shared=False
        )
        share_qs = Share.objects.filter(user=request.user, shared=False)
        if not share_qs.exists():
            shared_date = timezone.now()
            share = Share.objects.create(
                user=request.user, shared_date=shared_date)
            share.items.add(share_item)
            messages.info(request, "This item was added to your Sharelist")
    
    return redirect(request.META['HTTP_REFERER'])

class OrderItemDeleteView(DestroyAPIView):
    permission_classes = (IsAuthenticated, )
    queryset = OrderItem.objects.all()


class AddToCartView(APIView):
    def post(self, request, *args, **kwargs):
        pk = request.data.get('pk', None)
        variations = request.data.get('variations', [])
        if pk is None:
            return Response({"message": "Invalid request"}, status=HTTP_400_BAD_REQUEST)

        item = get_object_or_404(Item, pk=pk)

        minimum_variation_count = Variation.objects.filter(item=item).count()
        if len(variations) < minimum_variation_count:
            return Response({"message": "Please specify the required variation types"}, status=HTTP_400_BAD_REQUEST)

        order_item_qs = OrderItem.objects.filter(
            item=item,
            user=request.user,
            ordered=False
        )
        for v in variations:
            order_item_qs = order_item_qs.filter(
                Q(item_variations__exact=v)
            )

        if order_item_qs.exists():
            order_item = order_item_qs.first()
            order_item.quantity += 1
            order_item.save()
        else:
            order_item = OrderItem.objects.create(
                item=item,
                user=request.user,
                ordered=False
            )
            order_item.item_variations.add(*variations)
            order_item.save()

        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            if not order.items.filter(item__id=order_item.id).exists():
                order.items.add(order_item)
                return Response(status=HTTP_200_OK)

        else:
            ordered_date = timezone.now()
            order = Order.objects.create(
                user=request.user, ordered_date=ordered_date)
            order.items.add(order_item)
            return Response(status=HTTP_200_OK)


class OrderDetailView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, *args, **kwargs):
        try:
            orderid = kwargs.get(
                        "orderid",
                        None
                        )
            address = Address.objects.filter(user = self.request.user)
            order = Order.objects.get(user=self.request.user, ordered=False,id = orderid)
            context = {
                'order_placed': 1,
                'object': order,
                "address_list": address
            }
            return render(self.request, 'core/checkout.html', context)
        except ObjectDoesNotExist:
            #messages.warning(self.request, "You do not have an active order")
            return redirect("order-list")

class OrderListView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, *args, **kwargs):
        try:
            qs = Order.objects.all()
            my_order = qs.filter(user=self.request.user)
            if len(my_order):
                context = {
                    'order_list':1,
                    'object': my_order,
                }
            else:
                context = {
                    'no_order':1,
                    'order_list':1,
                    'object': my_order
                }
            return render(self.request, 'core/checkout.html', context)
        except ObjectDoesNotExist:
            #messages.warning(self.request, "You do not have an active order")
            print("hero")
            return redirect("/")
        except Exception as e:
            print(str(e))
            return redirect("/")
    
        


class DispatchDetailView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, *args, **kwargs):
        try:
            address = Address.objects.filter(user = self.request.user)
            order = Order.objects.filter( ordered=True)
            my_order =[]
            for check_order in order:
                if check_order.get_total():
                    my_order.append(check_order)
                else:
                    check_order.delete()
            if len(my_order):
                context = {
                    'dispatch':1,
                    'object': my_order,
                    "address_list": address,
                }
            else:
                context = {
                    'no_order':1,
                    'dispatch':1,
                    'object': my_order,
                    "address_list": address
                }

            return render(self.request, 'core/checkout.html', context)
        except ObjectDoesNotExist:
            #messages.warning(self.request, "You do not have an active order")
            return redirect("/")



class SharelistAPI(RetrieveAPIView):
    serializer_class = ShareSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, *args, **kwargs):
        try:
            share = Sharelist.objects.filter(created_by=self.request.user)
            print(share)
            context = {
                'share_list':1,
                'object': share
            }
            return render(self.request, 'core/checkout.html', context)
        except ObjectDoesNotExist:
            #messages.warning(self.request, "You do not have an active order")
            return redirect("/")



class ShareDetailView(RetrieveAPIView):
    serializer_class = ShareSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, *args, **kwargs):
        try:
            share = Share.objects.get(user=self.request.user, shared=False)
            Users = User.objects.all()
            context = {
                'object': share,
                'user_list': Users
            }
            return render(self.request, 'core/shareout.html', context)
        except ObjectDoesNotExist:
            #messages.warning(self.request, "You do not have an active order")
            return redirect("/")


class PaymentView(APIView):

    def post(self, request, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        userprofile = UserProfile.objects.get(user=self.request.user)
        #token = request.data.get('stripeToken')
        billing_address_id = request.data.get('selectedBillingAddress')
        shipping_address_id = request.data.get('selectedShippingAddress')

        billing_address = Address.objects.get(id=billing_address_id)
        shipping_address = Address.objects.get(id=shipping_address_id)

        if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
            customer = stripe.Customer.retrieve(
                userprofile.stripe_customer_id)
            customer.sources.create(source=token)

        else:
            customer = stripe.Customer.create(
                email=self.request.user.email,
            )
            customer.sources.create(source=token)
            userprofile.stripe_customer_id = customer['id']
            userprofile.one_click_purchasing = True
            userprofile.save()

        amount = int(order.get_total() * 100)

        try:

                # charge the customer because we cannot charge the token more than once
            charge = stripe.Charge.create(
                amount=amount,  # cents
                currency="usd",
                customer=userprofile.stripe_customer_id
            )
            # charge once off on the token
            # charge = stripe.Charge.create(
            #     amount=amount,  # cents
            #     currency="usd",
            #     source=token
            # )

            # create the payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            # assign the payment to the order

            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()

            order.ordered = True
            order.payment = payment
            order.billing_address = billing_address
            order.shipping_address = shipping_address
            # order.ref_code = create_ref_code()
            order.save()

            return Response(status=HTTP_200_OK)

        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            return Response({"message": f"{err.get('message')}"}, status=HTTP_400_BAD_REQUEST)

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            #messages.warning(self.request, "Rate limit error")
            return Response({"message": "Rate limit error"}, status=HTTP_400_BAD_REQUEST)

        except stripe.error.InvalidRequestError as e:
            print(e)
            # Invalid parameters were supplied to Stripe's API
            return Response({"message": "Invalid parameters"}, status=HTTP_400_BAD_REQUEST)

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            return Response({"message": "Not authenticated"}, status=HTTP_400_BAD_REQUEST)

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            return Response({"message": "Network error"}, status=HTTP_400_BAD_REQUEST)

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            return Response({"message": "Something went wrong. You were not charged. Please try again."}, status=HTTP_400_BAD_REQUEST)

        except Exception as e:
            # send an email to ourselves
            return Response({"message": "A serious error occurred. We have been notifed."}, status=HTTP_400_BAD_REQUEST)

        return Response({"message": "Invalid data received"}, status=HTTP_400_BAD_REQUEST)


class AddCouponView(APIView):
    def post(self, request, *args, **kwargs):
        code = request.data.get('code', None)
        if code is None:
            return Response({"message": "Invalid data received"}, status=HTTP_400_BAD_REQUEST)
        order = Order.objects.get(
            user=self.request.user, ordered=False)
        coupon = get_object_or_404(Coupon, code=code)
        order.coupon = coupon
        order.save()
        return Response(status=HTTP_200_OK)


class CountryListView(APIView):
    def get(self, request, *args, **kwargs):
        return Response(countries, status=HTTP_200_OK)


class AddressListView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = AddressSerializer
    template_name = "core/checkout.html"
    def get_queryset(self):
        address_type = self.request.query_params.get('address_type', None)
        qs = Address.objects.all()
        if address_type is None:
            return qs
        return qs.filter(user=self.request.user, address_type=address_type)




class AddressCreateView(CreateAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = AddressSerializer
    template_name = "core/beverages.html"
    queryset = Address.objects.all()
    


class AddressUpdateView(UpdateAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = AddressSerializer
    queryset = Address.objects.all()


class AddressDeleteView(DestroyAPIView):
    permission_classes = (IsAuthenticated, )
    queryset = Address.objects.all()


class PaymentListView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

def QuantityUpdate(request):
    if request.method == 'POST':
        if 'id' in request.POST:
            found_item = OrderItem.objects.get(id = request.POST["item"])
            found_order = Order.objects.get(id=request.POST["id"])
            if int(request.POST["quantity"]):
                found_item.quantity = request.POST["quantity"]
                found_item.save()
                found_order.save()
            else:
                found_order.items.remove(found_item)
                found_item.quantity = 1
                found_item.save()
                found_order.save()
        return redirect(request.META['HTTP_REFERER'])
    else:
        return redirect("index") 


def QuantityShareUpdate(request):
    if request.method == 'POST':
        if 'id' in request.POST:
            print("cgvhbjnm")
            found_item = SharedItem.objects.get(id = request.POST["item"])
            found_order = Share.objects.get(id=request.POST["id"])
            found_order.items.remove(found_item)
            found_item.save()
            found_order.save()
        return redirect(request.META['HTTP_REFERER'])
    else:
        return redirect("index") 

def Sharedlist(request):
    if request.method == 'POST':
        if "share" in request.POST:
            share = Share.objects.get(id = request.POST["share"])
            try:
                if share.shared:
                    Share_list = Sharelist.objects.get(share = share)
                    return render( request, 'core/share_now.html',{"url_for_share":Share_list.url})
                else:
                    share.shared = True
                    share.end_date = request.POST['enddate']
                    share.save()
                    user = User.objects.get(username = request.POST["shared_user"])
                    slug = str(uuid4())[:8]
                    Share_list = Sharelist.objects.create(
                        share = share,
                        shared_user = user,
                        slug = slug,
                        created_by = request.user
                    )
                    Share_list.save()
                    Share_list.get_absolute_url()
                    Share_list.url = request.build_absolute_uri(Share_list.get_absolute_url())
                    Share_list.save()
                    return render( request, 'core/share_now.html',{"url_for_share":Share_list.url})
            except:
                pass
            
        else:
            return redirect('home')

def PlaceOrder(request,pk):
    if request.method =="POST" :
        if "order" in request.POST:
            order = Order.objects.get(id  = request.POST["order"])
            billing_address_id = request.POST.get('billing_address')
            shipping_address_id = request.POST.get('shipping_address')
            billing_address = Address.objects.get(id=billing_address_id)
            shipping_address = Address.objects.get(id=shipping_address_id)
            
            if not order.ordered:
                for order_item in  order.items.all():
                    order_item.ordered = True
                    order.billing_address = billing_address
                    order.billing_address = shipping_address
                    order.ordered_date = datetime.date.today()
                    order_item.save()
                order.ordered = True
                order.save()
                return render( request, 'core/share_now.html',{"order_placed" : 1,"object":order})
            else:
                return redirect('index')

        
    else:
        return redirect('index')

def ProductStock(request,pk):
    if request.method =="GET" :
        item = Item.objects.get(id=pk)
        item.stock = False
        item.save()
        return redirect(request.META['HTTP_REFERER'])
    elif request.method == "POST":
        item = Item.objects.get(id = request.POST["item"])
        item.stock = False
        item.save()
        return redirect(request.META['HTTP_REFERER'])
    else:
        return redirect('index')


def DispatchOrder(request,pk):
    if request.method =="GET" :
        order = Order.objects.get(id=pk)
        return render( request, 'core/checkout.html',{'dispatch_final':1,"object":order})
    else:
        return redirect('index')


class SharedlistDetailView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, *args, **kwargs):
        try:
            share = Share.objects.get(user=self.request.user, shared=False)
            context = {
                'object': share
            }
            return render(self.request, 'core/checkout.html', context)
        except ObjectDoesNotExist:
            #messages.warning(self.request, "You do not have an active order")
            return redirect("/")




class GeneratePdf(View):
    def get(self, request, *args, **kwargs):
        template = get_template('invoice.html')
        orderid = kwargs.get(
            "orderid",
            None
        )
        order = Order.objects.get(id=orderid)
        order.dispatched = True
        order.save()
        context = {
            "customer_name": request.user.username,
            "amount": order.get_total(),
            "object" : order,
        }
        return render(request, "invoice.html",context)
        html = template.render(context)
        pdf = render_to_pdf('invoice.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "Invoice_%s.pdf" %("12341231")
            content = "inline; filename='%s'" %(filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename='%s'" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found") 


class GenerateInvoicePdf(View):
    def get(self, request, *args, **kwargs):
        template = get_template('invoice.html')
        orderid = kwargs.get(
            "orderid",
            None
        )
        order = Order.objects.get(id=orderid)
        order.dispatched = True
        order.save()
        context = {
            "customer_name": request.user.username,
            "amount": order.get_total(),
            "object" : order,
        }
        return render(request, "invoice.html",context)
        html = template.render(context)
        pdf = render_to_pdf('invoice.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "Invoice_%s.pdf" %("12341231")
            content = "inline; filename='%s'" %(filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename='%s'" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found") 




def Categorypage(request, *args, **kwargs):
    if request.method == 'GET':
        category_id = kwargs.get(
            "categoryid",
            None
        )
        category = Category.objects.get(id = category_id)
        if request.user.userprofile.owner:
            csrf_token = django.middleware.csrf.get_token(request) 
            query = Q(stock = True)
            query.add(Q(category = category), Q.AND)
            query.add(Q(category__parent = category), Q.OR,)
            query.add(Q(category__parent__parent = category), Q.OR,)
            queryset = Item.objects.filter(query)
            page = request.GET.get('page', 1)
            paginator = Paginator(queryset, 10)
            try:
                users = paginator.page(page)
            except PageNotAnInteger:
                users = paginator.page(1)
            except EmptyPage:
                users = paginator.page(paginator.num_pages)

            return render(request,"core/products.html",{"object_list":users,"category":category
            "csrf_token": csrf_token})
        else:
            csrf_token = django.middleware.csrf.get_token(request)
            query = Q(stock = True)
            query.add(Q(category = category), Q.AND)
            query.add(Q(category__parent = category), Q.OR,)
            query.add(Q(category__parent__parent = category), Q.OR,)

            queryset = Sharelist.objects.filter(query)
            items =[]
            for my_sharelist in queryset:
                print()
                for my_share_item in my_sharelist.share.items.all():
                    if my_share_item.item.stock and my_share_item.item.category == category :
                        items.append(my_share_item.item)
            if len(items):
                page = request.GET.get('page', 1)
                paginator = Paginator(list(set(items)), 10)
                try:
                    users = paginator.page(page)
                except PageNotAnInteger:
                    users = paginator.page(1)
                except EmptyPage:
                    users = paginator.page(paginator.num_pages)


                return render(request,"core/products.html",{"object_list":users,"category":category
                "csrf_token": csrf_token})
            else:
                users=[]
                return render(request,"core/products.html",{"object_list":users,"category":category
                "csrf_token": csrf_token})

def Checkoutpage(request, *args, **kwargs):
    try:
        if request.method == 'GET':
            order_id = kwargs.get(
                "orderid",
                None
            )
            address = Address.objects.filter(user = request.user)
            order = Order.objects.get(id = order_id)
            if request.user.is_authenticated:
                csrf_token = django.middleware.csrf.get_token(request) 
                return render(request,"core/order_checkout.html",
                {"csrf_token": csrf_token ,
                "order_checkout": 1,
                "object" : order,
                "address_list": address
                })
    except Order.DoesNotExist:
        return redirect('index')

def shareoutpage(request, *args, **kwargs):
    try:
        if request.method == 'GET':
            share_id = kwargs.get(
                "shareid",
                None
            )
            users = User.objects.all()
            share = Share.objects.get(id = share_id)
            if request.user.is_authenticated:
                csrf_token = django.middleware.csrf.get_token(request) 
                return render(request,"core/order_checkout.html",
                {"csrf_token": csrf_token ,
                "share_checkout":1,
                "object" : share,
                "user_list": users
                })
    except Order.DoesNotExist:
        return redirect('index')


            
def search(request):
    if request.method == "POST":
        query = request.POST["search"]
        query_list = query.split()
        search_list = []
        csrf_token = django.middleware.csrf.get_token(request)
        if request.user.userprofile.owner:
            Item_qs = Item.objects.all()
        else:
            queryset = Sharelist.objects.filter(shared_user = request.user,share__shared = True,share__items__item__stock= True)
            Item_qs = queryset
        try:
            if request.user.userprofile.owner:
                for q in query_list:
                    search_list = search_list + list(Item_qs.filter(
                        Q(title__icontains=q)))
                for q in query_list:
                    search_list = search_list + list(Item_qs.filter(
                        Q(description__icontains=q)))
                for q in query_list:
                    search_list = search_list + list(Item_qs.filter(
                        Q(category__name__icontains=q)))
                if len(search_list):
                    page = request.GET.get('page', 1)
                    paginator = Paginator(list(set(search_list)), 10)
                    try:
                        users = paginator.page(page)
                    except PageNotAnInteger:
                        users = paginator.page(1)
                    except EmptyPage:
                        users = paginator.page(paginator.num_pages)
                    return render(request,"core/products.html",{"object_list":users, "csrf_token": csrf_token})
                return render(request,"core/products.html",{"object_list":0,"No_search_found":1,"csrf_token": csrf_token})


            else:
                for q in query_list:
                    search_list = search_list + list(Item_qs.filter(
                        Q(title__icontains=q)))
                for q in query_list:
                    search_list = search_list + list(Item_qs.filter(
                        Q(description__icontains=q)))
                
                if len(search_list):
                    items=[]
                    for my_sharelist in search_list:
                        for my_share_item in my_sharelist.share.items.all():
                            if my_share_item.item.stock:
                                items.append(my_share_item.item)
                    page = request.GET.get('page', 1)
                    paginator = Paginator(list(set(items)), 10)
                    try:
                        users = paginator.page(page)
                    except PageNotAnInteger:
                        users = paginator.page(1)
                    except EmptyPage:
                        users = paginator.page(paginator.num_pages)
                    return render(request,"core/products.html",{"object_list":users, "csrf_token": csrf_token})
                return render(request,"core/products.html",{"object_list":0,"No_search_found":1,"csrf_token": csrf_token})
                    

        except Exception as e:
            print(str(e))
            return redirect('index')
    else:
        return redirect('index')


def New_address(request):
    return render("core/beverages.html",{'form':AddressForm})
    


