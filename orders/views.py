from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from .models import OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from django.views.generic import View

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_control

import hashlib
import hmac
import base64

from django.utils.crypto import get_random_string
from random import randint

secretKey = "TESTbb80ff9d3d2450b72d817b0727a95cc06234f1bb"


@csrf_exempt
def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            cart.clear()

        mode = "TEST"  # <-------Change to TEST for test server, PROD for production
        di = str(randint(100, 9999))
        di2 = str(randint(100, 999))
        print(di + get_random_string(1) + di2 + get_random_string(2))
        orderid = di + get_random_string(1) + di2 + get_random_string(2)

        print(request.POST['price']),

        postData = {
            "appId": "204434e28173cb6cfb60e28fb4434402",
            "orderId": orderid,
            "orderAmount": request.POST['price'],
            "orderCurrency": "INR",
            "orderNote": "paying",
            "customerName": request.POST['first_name'],
            "customerPhone": "1236547890",
            "customerEmail": request.POST['email'],
            "returnUrl": "http:127.0.0.1:8000/created/",
            "notifyUrl": "",
        }
        print(type(postData))
        print("initial dictionary = ", postData)

        sortedKeys = sorted(postData)
        print(sortedKeys)
        signatureData = ""
        for key in sortedKeys:
            signatureData += key + postData[key]
        message = signatureData.encode('utf-8')
        secret = secretKey.encode('utf-8')
        signature = base64.b64encode(
            hmac.new(secret, message, digestmod=hashlib.sha256).digest()).decode('utf-8')

        if mode == 'PROD':
            url = "https://www.cashfree.com/checkout/post/submit"
        else:
            url = "https://test.cashfree.com/billpay/checkout/post/submit"
        return render(request, 'orders/order/request.html',
                      {'postData': postData, 'signature': signature, 'url': url, })
    else:
        form = OrderCreateForm()
    return render(request, 'orders/order/create.html', {'cart': cart, 'form': form})


@csrf_exempt
def thankpg(request):
    return render(request, 'orders/order/create.html')


@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def handleresponse(request):
    if request.method == "POST":
        postData = {
            "orderId": request.POST.get('orderId'),
            "orderAmount": request.POST.get('orderAmount'),
            "referenceId": request.POST.get('referenceId'),
            "txStatus": request.POST.get('txStatus'),
            "paymentMode": request.POST.get('paymentMode'),
            "txMsg": request.POST.get('txMsg'),
            "signature": request.POST.get('signature'),
            "txTime": request.POST.get('txTime')
        }

        signature = request.POST.get('signature')
        status = request.POST.get('txStatus')
        print(status)

        signatureData = ""
        signatureData = postData['orderId'] + postData['orderAmount'] + postData['referenceId'] + \
                        postData['txStatus'] + postData['paymentMode'] + \
                        postData['txMsg'] + postData['txTime']

        message = signatureData.encode('utf-8')
        secret = secretKey.encode('utf-8')
        computedsignature = base64.b64encode(
            hmac.new(secret, message, digestmod=hashlib.sha256).digest()).decode('utf-8')

        print(computedsignature)

        if signature == computedsignature:
            if status == "SUCCESS":
                print("PAID")
            else:
                print("FAILED")
        else:
            print("NO")

    return render(request, 'orders/order/response.html', {'postData': postData, 'computedsignature': computedsignature})




