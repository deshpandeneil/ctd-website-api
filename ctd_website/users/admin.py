from django.contrib import admin
from .models import (
    Profile,
    EventLine,
    Event,
    Order,
    # MultipleEventsOrder,
)

# Register your models here.

admin.site.register(Profile)
admin.site.register(EventLine)
admin.site.register(Event)
admin.site.register(Order)
# admin.site.register(MultipleEventsOrder)
