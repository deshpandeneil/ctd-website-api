from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    country_code = models.CharField(max_length=4)
    phone_no = models.CharField(max_length=10)
    # college = models.CharField(max_length=255) --> not needed since this is an intra college event
    reg_no = models.CharField(max_length=11) # asking for clg reg no to ensure 'pictians only' participation
    senior = models.BooleanField(default=False)

# event line can have entries such as 'technical', 'non-technical', etc.
# better to have it just in case we add other type of events in the future
# database will be more ordered

class EventLine(models.Model):
    event_line_name = models.CharField(max_length=255)

class Event(models.Model):
    event_line_fk = models.ForeignKey(EventLine, on_delete=models.CASCADE)
    event_name = models.CharField(max_length=255)
    event_description = models.CharField(max_length=255)
    price_for_junior = models.IntegerField(default=0)
    price_for_senior = models.IntegerField(default=0)
    event_start_date = models.DateTimeField()
    event_end_date = models.DateTimeField()

class Order(models.Model):

    payment_methods = [
        ('cc', 'credit_card'),
        ('dc', 'debit_card'),
        ('upi', 'upi'),
    ]

    user_id_fk = models.ForeignKey(User, on_delete=models.CASCADE)
    # event_id = models.ForeignKey(Event, on_delete=models.CASCADE)
    order_date_time = models.DateTimeField(auto_now_add=True) # automatically saved when object is first created
    payment_method = models.CharField(max_length=3, choices=payment_methods, default='upi')
    payment_status = models.IntegerField(default=2) # 0 for failed, 1 for successful, 2 for pending
    payment_date_time = models.DateTimeField()

    # might require additional fields based on the payment api used


# one order by a user can have multiple events in it
# all those registration for events must come under same order id, hence the separate model

class MultipleEventsOrder(models.Model):
    order_id_fk = models.ForeignKey(Order, on_delete=models.CASCADE)
    event_id_fk = models.ForeignKey(Event, on_delete=models.CASCADE)
    event_password = models.CharField(max_length=15) # unique auto generated password for each entry