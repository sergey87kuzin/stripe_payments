import os
import logging

import stripe
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

from .models import Item, Order
from .literals import CURR_PRICE

load_dotenv()
logger = logging.getLogger('django')
stripe.api_key = os.getenv('API_KEY')


def index(request):
    return render(request, 'index.html')


def get_item(request, id):
    item = get_object_or_404(Item, id=id)
    publishable_key = os.getenv('PUBLISHABLE_KEY')
    print(CURR_PRICE)
    context = {
        'item': item,
        'key': publishable_key,
        'price': getattr(item, CURR_PRICE[item.currency])}
    return render(request, 'item.html', context)


@csrf_exempt
def buy_item(request, id):
    if request.method == 'GET':
        item = get_object_or_404(Item, id=id)
        items = {
            'price': item.price_id,
            'quantity': 1,
            'tax_rates': [tax.stripes_id for tax in item.taxes.all()]
        }
        try:
            session = stripe.checkout.Session.create(
                line_items=[items],
                mode='payment',
                discounts=[{'coupon': item.discount.stripes_id}],
                success_url='http://localhost:8000/success/',
                cancel_url='http://localhost:8000/bad_request/',
            )
            return JsonResponse({'sessionId': session['id']})
        except Exception as e:
            logger.warning(str(e))
            return JsonResponse({'error': str(e)})


def get_order(request, id):
    order = get_object_or_404(Order, id=id)
    items = order.items.all()
    publishable_key = os.getenv('PUBLISHABLE_KEY')
    context = {'order': order, 'items': items, 'key': publishable_key}
    return render(request, 'order.html', context)


@csrf_exempt
def buy_order(request, id):
    if request.method == 'GET':
        order = get_object_or_404(Order, id=id)
        count_list = order.order_counts.all()
        items = [{
            'price': count.item.price_id,
            'quantity': count.quantity,
            'tax_rates': [
                tax.stripes_id for tax in count.item.taxes.all()
            ]
        } for count in count_list]
        try:
            session = stripe.checkout.Session.create(
                line_items=items,
                mode='payment',
                currency='usd',
                discounts=[{'coupon': order.discount.stripes_id}],
                success_url='http://localhost:8000/success/',
                cancel_url='http://localhost:8000/bad_request/',
            )
            return JsonResponse({'sessionId': session['id']})
        except Exception as e:
            logger.warning(str(e))
            return JsonResponse({'error': str(e)})


def success(request):
    return render(request, 'success.html')


def bad_request(request):
    return render(request, 'cancel.html')
