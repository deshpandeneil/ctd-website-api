from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    country_code = models.CharField(max_length=5, validators=[RegexValidator('^\+\d+$', 'Invalid Country Code.')])
    phone_no = models.CharField(max_length=10, validators=[RegexValidator('^\d+$', 'Invalid Phone Number')])
    # college = models.CharField(max_length=255) --> not needed since this is an intra college event
    reg_no = models.CharField(max_length=11, validators=[RegexValidator('^(C|I|E)(2K)[0-9]+$',
                                                                        'Invalid Registration Number')],
                              unique=True)  # asking for clg reg no to ensure 'pictians only' participation
    senior = models.BooleanField(default=False)

    # create an registered_for list variable

    def __str__(self):
        return str(self.user) + "'s profile (pk=" + str(self.pk) + ")"


# event line can have entries such as 'technical', 'non-technical', etc.
# better to have it just in case we add other type of events in the future
# database will be more ordered

class EventLine(models.Model):
    event_line_name = models.CharField(max_length=255)

    def __str__(self):
        return str(self.event_line_name) + " (pk=" + str(self.pk) + ")"


class Event(models.Model):
    event_line_fk = models.ForeignKey(EventLine, on_delete=models.CASCADE)
    event_name = models.CharField(max_length=255)
    event_description = models.CharField(max_length=255)
    # price_for_junior = models.IntegerField(default=0)
    # price_for_senior = models.IntegerField(default=0)
    event_start_date = models.DateField()
    event_end_date = models.DateField()

    def __str__(self):
        return str(self.event_name) + " (pk=" + str(self.pk) + ")"


class Order(models.Model):
    # payment_methods = [
    #     ('cc', 'credit_card'),
    #     ('dc', 'debit_card'),
    #     ('upi', 'upi'),
    # ]

    user_id_fk = models.ForeignKey(User, on_delete=models.CASCADE)

    # this block has been added here as cart feature is truncated
    event_id_fk = models.ForeignKey(Event, on_delete=models.CASCADE)
    event_password = models.CharField(max_length=8, unique=True)  # unique auto generated password for each entry
    # block ends

    order_date_time = models.DateTimeField(auto_now_add=True)  # automatically saved when object is first created

    # payment system truncated as event is free smh (╯°□°)╯︵ ┻━┻

    # payment_method = models.CharField(max_length=3, choices=payment_methods, default='upi')
    # payment_status = models.IntegerField(default=2)  # 0 for failed, 1 for successful, 2 for pending
    # payment_date_time = models.DateTimeField()

    # might require additional fields based on the payment api used

    def __str__(self):
        return str(self.user_id_fk.username) + "'s order for event " + self.event_id_fk.event_name + " (pk=" + str(
            self.pk) + ")"

# one order by a user can have multiple events in it
# all those registration for events must come under same order id, hence the separate model

# class truncated as cart feature dropped from implementation

# class MultipleEventsOrder(models.Model):
#     order_id_fk = models.ForeignKey(Order, on_delete=models.CASCADE)
#     event_id_fk = models.ForeignKey(Event, on_delete=models.CASCADE)
#     event_password = models.CharField(max_length=15, unique=True)  # unique auto generated password for each entry
