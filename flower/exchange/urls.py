from django.urls import path, include
from . import views

lot_urlpatterns = [
    path('', views.ShopListView.as_view(), name="shop"),
    path('my', views.SalesmanLotsListView.as_view(), name="list-lots"),
    path('<slug:slug>-<uuid:uuid>', views.LotDetailView.as_view(), name="lot-detail"),
    path('update/<uuid:uuid>', views.LotUpdate.as_view(), name="lot-update"),
    path('create_comment/<slug:slug>-<uuid:uuid>', views.CommentCreateView.as_view(), name="create-comment"),
]

order_urlpatterns = [
    path('', views.SalesmanOrderListView.as_view(), name="list-order"),
    path('my', views.UserOrderListView.as_view(), name="my-order"),
    path('<pk>', views.OrderDetailView.as_view(), name="order-detail"),
]

salesman_urlpatterns = [
    path('<pk>', views.SalesmanDetailView.as_view(), name="salesman-detail"),
    path('create_comment/<pk>', views.CommentSalesmanCreateView.as_view(), name="create-comment-salesman"),
]

urlpatterns = [
    path('', views.index, name="index"),
    path('lot/', include(lot_urlpatterns)),
    path('order/', include(order_urlpatterns)),
    path('salesman/', include(salesman_urlpatterns)),
    path('order_list/', views.OrderListView.as_view(), name="statistic"),
]


