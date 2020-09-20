from django.urls import path
from core.api.views import (
    UserIDView,
    ItemListView,
    ItemDetailView,
    AddToCartView,
    OrderDetailView,
    add_to_cart,
    add_to_share,
    add_to_share_category,
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
    SharedlistDetailView,
    PlaceOrder,
    DispatchDetailView,
    DispatchOrder,
    ProductStock,
    GeneratePdf,
    Categorypage,
    OrderListView,
    GenerateInvoicePdf,
    Checkoutpage

)


urlpatterns = [
    path('user-id/', UserIDView.as_view(), name='user-id'),
    path('countries/', CountryListView.as_view(), name='country-list'),
    path('addresses/', AddressListView.as_view(), name='address-list'),
    path('order-list/', OrderListView.as_view(), name='order-list'),
    path('addresses/create/', AddressCreateView.as_view(), name='address-create'),
    path('addresses/<pk>/update/',
         AddressUpdateView.as_view(), name='address-update'),
    path('addresses/<pk>/delete/',
         AddressDeleteView.as_view(), name='address-delete'),
    path('products/', ItemListView.as_view(), name='product-list'),
    path('products/<str:slug>/', ItemDetailView.as_view(), name='product-detail'),
    path('product-out-of-stock/', ProductStock , name='out-of-stock'),
    #path('addtocart/', AddToCartView.as_view(), name='add_to_cart'),
    path('addtocart/<slug>/', add_to_cart, name='add-to-cart'),
    path('addtoshare/<slug>/', add_to_share, name='add-to-share'),
    path('addtosharecategory/<int:categoryid>/', add_to_share_category ,name = "add_to_share_category" ),

    path('order-summary/<int:orderid>/', OrderDetailView.as_view(), name='order-summary'),
    path('share-summary/', ShareDetailView.as_view(), name='share-summary'),
    path('dispatch-list/', DispatchDetailView.as_view(), name='dispatch-summary'),
    path('dispatch-summary/<pk>/', DispatchOrder, name="dispatch-order"),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('order-items/<pk>/delete/',
         OrderItemDeleteView.as_view(), name='order-item-delete'),
    path('order-item/update-quantity/',
         OrderQuantityUpdateView.as_view(), name='order-item-update-quantity'),
    path('place_order/<pk>/', PlaceOrder, name="place-order-now"), 
    path('payments/', PaymentListView.as_view(), name='payment-list'),
    path('update-cart/', QuantityUpdate, name="quantityupdate"),
    path('share-list-url/', Sharedlist, name="share_list_url"),
    path('share-list-url/<str:slug>', SharedlistDetailView.as_view(), name="share_list_url-detail"),
    path('get-dispatch/<int:orderid>/',GeneratePdf.as_view(), name="generate_dispatch_pdf"),
    path('get-invoice/<int:orderid>/',GenerateInvoicePdf.as_view(), name="generate_invoice_pdf"),
    path('category/<int:categoryid>/', Categorypage, name="category-page"),
    path('checkout/<int:orderid>/', Checkoutpage, name="checkout_page"),


]
