from django.shortcuts import get_object_or_404, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.db import transaction

from django.forms import inlineformset_factory

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView

from basketapp.models import Basket
from ordersapp.models import Order, OrderItem
from ordersapp.forms import OrderItemForm


class FormValidMixin:

    def form_valid(self, form):
        context = self.get_context_data()
        orderitems = context['orderitems']

        with transaction.atomic():
            assert isinstance(self.request.user, object)
            form.instance.user = self.request.user
            self.object = form.save()
            if orderitems.is_valid():
                orderitems.instance = self.object
                orderitems.save()

        if self.object.get_total_cost() == 0:
            self.object.delete()
        return super().form_valid(form)


class OrderList(FormValidMixin, ListView):
    model = Order
    extra_context = {'title': 'Список заказов'}

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


def forming_complete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.status = Order.SENT_TO_PROCEED
    order.save()

    return HttpResponseRedirect(reverse('order:list'))


class OrderCreate(FormValidMixin, CreateView):
    model = Order
    fields = []
    success_url = reverse_lazy('order:list')
    extra_context = {'title': 'Создание заказа'}

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        OrderFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemForm, extra=1)

        if self.request.POST:
            formset = OrderFormSet(self.request.POST)
        else:
            basket_items = Basket.objects.filter(user=self.request.user)
            if len(basket_items):
                OrderFormSet = inlineformset_factory(
                    Order,
                    OrderItem,
                    form=OrderItemForm,
                    extra=len(basket_items))
                formset = OrderFormSet()
                for num, form in enumerate(formset.forms):
                    form.initial['product'] = basket_items[num].product
                    form.initial['quantity'] = basket_items[num].quantity
                basket_items.delete()
            else:
                formset = OrderFormSet()

        data['orderitems'] = formset
        return data


class OrderRead(DetailView):
    model = Order
    extra_context = {'title': 'Просмотр заказа'}


class OrderUpdate(FormValidMixin, UpdateView):
    model = Order
    fields = []
    success_url = reverse_lazy('order:list')
    extra_context = {'title': 'Изменение заказа'}

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        OrderFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemForm, extra=1)

        if self.request.POST:
            formset = OrderFormSet(self.request.POST, instance=self.object)
        else:
            formset = OrderFormSet(instance=self.object)

        data['orderitems'] = formset
        return data


class OrderDelete(DeleteView):
    model = Order
    success_url = reverse_lazy('order:list')
    extra_context = {'title': 'Удаление заказа'}
