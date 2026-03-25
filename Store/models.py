from django.db import models
from django.contrib.auth.models import User
  



class Customer(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=100,null=False,blank=False)
    phone = models.CharField(max_length=15,null=False,blank=False)


    def __str__(self):
        return self.name.title()


class Product(models.Model):
    prdname = models.CharField(max_length=100,null=False,blank=False)
    description=models.CharField(max_length=800,null=False,blank=False)
    stock = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    picture = models.ImageField(upload_to="Store/")

    def __str__(self):
        return self.prdname.title()
    
    

class Order(models.Model):
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=500,null=True)


    def __str__(self):
        return str(self.id)
    
    @property
    def gettotqty(self):
        tot =sum([ item.quantity  for item in  self.orderitems_set.all()])
        return tot
    
    @property
    def gettotbill(self):
        totbill=sum([ item.getitemtot for item in self.orderitems_set.all()])
        return totbill


class OrderItems(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0,null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.prdname
    

    @property
    def getitemtot(self):
        return self.quantity*self.product.price

    
class ShippingAddress(models.Model):
    customer =models.ForeignKey(Customer,on_delete=models.CASCADE)
    address = models.CharField(max_length=250,null=False)
    city = models.CharField(max_length=250,null=False)
    state = models.CharField(max_length=250,null=False)
    zipcode = models.CharField(max_length=50,null=False)
    order = models.ForeignKey(Order,on_delete=models.CASCADE)

    def __str__(self):
        return self.address