from django.urls import path
from core.api.views import (
    UserIDView,
    ItemListView,
    ItemDetailView,
    AddToCartView,
    OrderDetailView,
    add_to_cart,
    add_to_share,
    OrderQuantityUpdateView,
    PaymentView,
    AddCouponView,
    CountryListView,
    AddressListView,
    AddressCreateView,
    AddressUpdateView,
    AddressDeleteView,
    OrderItemDeleteView,
    PaymentListView,
    QuantityUpdate,
    ShareDetailView,
    Sharedlist,
    SharedlistDetailView
)


urlpatterns = [
    path('user-id/', UserIDView.as_view(), name='user-id'),
    path('countries/', CountryListView.as_view(), name='country-list'),
    path('addresses/', AddressListView.as_view(), name='address-list'),
    path('addresses/create/', AddressCreateView.as_view(), name='address-create'),
    path('addresses/<pk>/update/',
         AddressUpdateView.as_view(), name='address-update'),
    path('addresses/<pk>/delete/',
         AddressDeleteView.as_view(), name='address-delete'),
    path('products/', ItemListView.as_view(), name='product-list'),
    path('products/<str:slug>/', ItemDetailView.as_view(), name='product-detail'),
    #path('addtocart/', AddToCartView.as_view(), name='add_to_cart'),
    path('addtocart/<slug>/', add_to_cart, name='add-to-cart'),
    path('addtoshare/<slug>/', add_to_share, name='add-to-share'),

    path('order-summary/', OrderDetailView.as_view(), name='order-summary'),
    path('share-summary/', ShareDetailView.as_view(), name='share-summary'),
    path('checkout/', PaymentView.as_view(), name='checkout'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('order-items/<pk>/delete/',
         OrderItemDeleteView.as_view(), name='order-item-delete'),
    path('order-item/update-quantity/',
         OrderQuantityUpdateView.as_view(), name='order-item-update-quantity'),
    path('payments/', PaymentListView.as_view(), name='payment-list'),
    path('update-cart/', QuantityUpdate, name="quantityupdate"),
    path('share-list-url/', Sharedlist, name="share_list_url"),
    path('share-list-url/<str:slug>', SharedlistDetailView.as_view(), name="share_list_url-detail")



]
