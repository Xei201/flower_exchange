from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, F, Avg
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from .models import Lot, Order, OrderItem, LotReview, SalesmanReview, CustomUser


def index(request):
    """View displaying general page"""

    return render(request, "index.html")


class ShopListView(LoginRequiredMixin, generic.ListView):

    model = Lot
    template_name = 'lot/lots_list.html'
    context_object_name = "list_lots"
    paginate_by = 10

    def get_queryset(self):
        return Lot.objects.filter(hide=False)


class SalesmanLotsListView(LoginRequiredMixin, generic.ListView):

    model = Lot
    template_name = 'lot/lots_list.html'
    context_object_name = "list_lots"
    paginate_by = 10

    def get_queryset(self):
        return Lot.objects.filter(salesman=self.request.user)


class UserOrderListView(LoginRequiredMixin, generic.ListView):

    model = Order
    template_name = 'order/orders_list.html'
    context_object_name = "list_orders"
    paginate_by = 10

    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user)


class SalesmanOrderListView(LoginRequiredMixin, generic.ListView):

    model = OrderItem
    template_name = 'order/orders_item_list.html'
    context_object_name = "list_orders"
    paginate_by = 10

    def get_queryset(self):
        return OrderItem.objects.select_related("lot").filter(lot__salesman=self.request.user)


class OrderDetailView(LoginRequiredMixin, generic.DetailView):

    model = Order
    context_object_name = "order"
    template_name = "order/detail_order.html"

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        return Order.objects.prefetch_related("item").get(pk=pk)


class SalesmanDetailView(LoginRequiredMixin, generic.DetailView):

    model = CustomUser
    context_object_name = "salesman"
    template_name = "detail_salesman.html"


class LotDetailView(LoginRequiredMixin, generic.DetailView):

    model = Lot
    context_object_name = "lot"
    template_name = "lot/detail_lot.html"

    def get_object(self, queryset=None):
        uuid_num = self.kwargs.get('uuid')
        return Lot.objects.select_related("flower").get(pk=uuid_num)


class LotUpdate(LoginRequiredMixin, generic.UpdateView):

    permission_required = ("catalog.can_mark_returned",)
    model = Lot
    fields = ["title", "amount", "hide"]
    template_name = "lot/lot_form.html"

    def get_object(self, queryset=None):
        uuid_num = self.kwargs.get('uuid')
        return Lot.objects.select_related("flower").get(pk=uuid_num)


class CommentCreateView(LoginRequiredMixin, generic.CreateView):

    model = LotReview
    fields = ["context"]
    template_name = "create_comment.html"

    def get_success_url(self):
        return reverse_lazy("lot-detail", kwargs={
            'uuid': self.kwargs.get('uuid'),
            'slug': self.kwargs.get('slug')
        })

    def form_valid(self, form):
        user = self.request.user
        lot = Lot.objects.get(id=self.kwargs.get('uuid'))
        form.instance.user = user
        form.instance.lot = lot
        return super(CommentCreateView, self).form_valid(form)


class CommentSalesmanCreateView(LoginRequiredMixin, generic.CreateView):

    model = SalesmanReview
    fields = ["context"]
    template_name = "create_comment.html"

    def get_success_url(self):
        return reverse_lazy("salesman-detail", args=self.kwargs.get('pk'))

    def form_valid(self, form):
        user = self.request.user
        salesman = CustomUser.objects.get(id=self.kwargs.get('pk'))
        form.instance.user = user
        form.instance.salesman = salesman
        return super(CommentSalesmanCreateView, self).form_valid(form)


class OrderListView(generic.ListView):

    template_name = 'list_all_order.html'
    context_object_name = "payments"

    def get_queryset(self):
        payments = OrderItem.objects.select_related(
            "order"
        ).select_related(
            "lot"
        ).values(
            "lot__salesman__username",
            "order__buyer__username"
        ).order_by().annotate(
            price_sum=Sum(
                F("amount") *
                F("lot__unit_price")
            )
        )

        return payments