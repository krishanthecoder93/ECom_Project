from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import Product,Order,OrderItems,ShippingAddress,Customer
# from django.contrib.auth.forms import UserCreationForm # beacuse we create a customised register form with the help of forms.py
from .forms import UserRegisterForm,CustomerForm
from django.contrib.auth import login,logout

from django.conf import settings # new
from django.http.response import JsonResponse # new
from django.views.decorators.csrf import csrf_exempt # new
import stripe


def index(request):
    if request.user.is_authenticated==True:
        customer=request.user.customer
        order,created = Order.objects.get_or_create(customer =customer,complete = False)


    else:
        order = {"gettotqty":0}
        customer={}
    prds =Product.objects.all().order_by('price')
    return render(request,"Store/index.html",{"prds":prds,"customer":customer,"order":order})


def updatecart(request):
    if request.method=="POST":
        if request.user.is_authenticated:
        
            customer = request.user.customer
            order,created = Order.objects.get_or_create(customer=customer,complete=False)
            if request.POST.get(("btnupd")):
                ctrl=[ct  for ct in request.POST if "txtqty" in ct ]
                pid = (int)(ctrl[0][6:])
                product=Product.objects.get(id=pid)
                orderitem = OrderItems.objects.get(order=order,product=product)
                qty =(int)(request.POST.get(("txtqty"+str(pid))))
                if qty<=0:
                    orderitem.delete()
                else:
                    orderitem.quantity = qty
                    orderitem.save()


            elif request.POST.get(("btndel")):
                ctrl=[ct  for ct in request.POST if "txtqty" in ct ]
                pid = (int)(ctrl[0][6:])
                product=Product.objects.get(id=pid)
                orderitem = OrderItems.objects.get(order=order,product=product)
                orderitem.delete()
            
                

            else:
                ctrls =[ ctrl  for ctrl in request.POST if "btn" in ctrl ]
                pid =(int)(ctrls[0][3:])
                product = Product.objects.get(id=pid)
                orderitem,created=OrderItems.objects.get_or_create(order=order,product=product)
                orderitem.quantity = orderitem.quantity+1
                orderitem.save()
                return redirect("/cart/")
        # return HttpResponse("Cart updated successfully")
        # code to add data to customer orde

        else:
            return redirect("/myauth/login")
        
   

def register(request):
    if request.method=="POST":
        userform = UserRegisterForm(request.POST)
        custform = CustomerForm(request.POST)
        if userform.is_valid() and custform.is_valid():
            user = userform.save()
            customer = custform.save(commit=False)
            customer.user=user
            customer.save()
            login(request,user) #auto login
            return redirect('index')

    else:
        userform = UserRegisterForm()
        custform= CustomerForm()
    return render (request,"registration/register.html",{"userform": userform,"custform":custform}) 

def mylogout(request):
    logout(request)
    return redirect('/myauth/login')

def cart(request):
    if request.user.is_authenticated:
        order,created = Order.objects.get_or_create(customer=request.user.customer,complete=False)
        orderitems=order.orderitems_set.all()
        return render(request,'Store/cart.html',{'order':order,'orderitems':orderitems})
    
    else:
        return redirect("/myauth/login/")

def checkout(request):
    if request.user.is_authenticated==True:
        customer=request.user.customer
        order,created = Order.objects.get_or_create(customer=customer,complete=False)
        orderitems = order.orderitems_set.all()
        return render(request,'Store/checkout.html',{"customer":customer,'orderitems':orderitems,'order':order})
    else:
        return redirect("/myauth/login")
    

@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)
    
@csrf_exempt
def create_checkout_session(request):
    if request.method == 'GET':
        domain_url = 'http://localhost:8000/'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            lst=[]
            customer = request.user.customer
            order,created = Order.objects.get_or_create(customer=customer,complete=False)
            orderitems= order.orderitems_set.all()
            for itm in orderitems:
                lst.append({
                    "price_data": {
                    "currency": "usd",
                    "product_data": {
                    "name": itm.product.prdname,
                    },
                    "unit_amount": (int)(itm.product.price*100),
                    },

                    "quantity": itm.quantity,
                    },)

            # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
            checkout_session = stripe.checkout.Session.create(
                success_url=domain_url + 'success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url + 'cancelled/',
                payment_method_types=['card'],
                mode='payment',
                line_items=lst,
                        metadata ={
                            'cust':request.user.customer.id,
                            'adr':request.GET.get('query')
                        }

                
                # [
                #       {
                #   "price_data": {
                #   "currency": "usd",
                #   "product_data": {
                #    "name": "My Course Fee",
                #    },
                #    "unit_amount": 2000,
                #   },
                #    "quantity": 1,
                #    }
                # ]
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})
        

def successview(request):
    return render(request,"Store/success.html",{"msg":"Payment Done Successfully(view)"})

def canview(request):
    return render(request,"Store/cancel.html",{"msg":"Payment are not  Successfull,Try AGAIN!"})


@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        print("Payment was successful.")
        # TODO: run some custom code here
        session=event['data']['object']
        metadata=session.get("metadata",{})
        # print(metadata)
        # print(session.get("payment_intent"))
        cust_id=metadata.get('cust')
        customer=Customer.objects.get(id=cust_id)
        print(customer.name)
        order = Order.objects.get(customer=customer,complete=False)
        print(order.id)
        transid =session.get("payment_intent")
        order.transaction_id = transid
        order.complete = True
        order.save()
        addr,cty,sta,zipcod=metadata.get("adr").split("|")
        customer=Customer.objects.get(id=metadata.get("cust"))
        ShippingAddress.objects.create(customer=customer,order=order,address=addr,city=cty,state=sta,zipcode=zipcod)
        print("Data Stored")


    return HttpResponse(status=200)

def myorders(request):
    if request.user.is_authenticated:
        customer=request.user.customer
        ords=Order.objects.filter(customer=customer,complete=True).prefetch_related("orderitems_set__product")
        return render(request,'Store/myorder.html',{"ords":ords})
    

# def product_detail_view(request):
#     if request.method == "POST":
#         ctrls=[ctrl for ctrl in request.POST if "btn" in ctrl]
#         pid=(int)(ctrls[0][3:])
#         product=Product.objects.get(id=pid)
#     return render(request, "Store/product_detail.html", {"product":product})


def product_detail_view(request, pid):

    product = Product.objects.get(id=pid)

    return render(request,"Store/product_detail.html",{"product":product})


