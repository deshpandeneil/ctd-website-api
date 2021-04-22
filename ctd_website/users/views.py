from django.shortcuts import render

from rest_framework import generics, status, mixins
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

from .models import *
from .serializers import *

# Create your views here.

class Register(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class Accounts(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class EventLinesList(generics.ListCreateAPIView):
    queryset = EventLine.objects.all()
    serializer_class = EventLineSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class EventLinesDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = EventLine.objects.all()
    serializer_class = EventLineSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class EventsList(generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

class EventsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class OrdersList(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Order.objects.all()
        else:
            return Order.objects.filter(user_id_fk=self.request.user.pk)

    def create(self, request, *args, **kwargs):
        if request.user.is_superuser:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail':'You do not have permission to perform this action.'}, status=403)

class OrderDetail(APIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        order_id = self.kwargs['pk']
        if self.request.user.is_superuser:
            return Order.objects.filter(pk=order_id)
        return Order.objects.filter(pk=order_id, user_id_fk=self.request.user.pk)

    def get(self, request, **kwargs):
        order = self.get_queryset().first()
        if order:
            print(type(order))
            events = []
            events_in_order = MultipleEventsOrder.objects.filter(order_id_fk=order.pk)
            for event in events_in_order:
                event_details = Event.objects.get(pk=event.event_id_fk.pk)
                events.append(event_details.event_name)
            context = {
                'pk': order.pk,
                'user_id_fk': order.user_id_fk.pk,
                'order_date_time': order.order_date_time,
                'payment_method': order.payment_method,
                'payment_status': order.payment_status,
                'payment_date_time': order.payment_date_time,
                'events': events,
            }
            return Response(context, status=201)
        context = {
            'detail': 'You are not allowed to access this order detail',
        }

        return Response(context, status=403)
    
class PlaceOrder(APIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):

        ''' 
        user will enter the following in the post request:
            1. list of events they want to register for
        '''

        '''
        before placing an order check if user has already registered for an event in the list
        add new profile model field for this requirement
        '''

        events = request.data.events # list of events ordered by user

        customer_profile = Profile.objects.get(user=request.user)
        # registered_for = customer_profile.registered_for --> should return a list

        # for event in events:
        #     event_obj = Event.objects.get(event_name=str(event).lower())
        #     if event_obj.event_name in registered_for:
        #         return Response({'error': str('You have already registered for ' + event_obj.event_name + ' before.')}, status=500)

        '''
        ippo pay api expects following details:
            1. order amount
            2. currency
            3. payment modes
            4. customer details
                1. name
                2. email
                3. phone number
        '''

        order_amount = 0 # initial amount
        currency = 'INR'
        payment_modes = Order.payment_methods
        print(payment_modes)
        customer_name = str(request.user.first_name) + str(request.user.last_name)
        customer_email = str(request.user.email)
        customer_phone_number = str(customer_profile.country_code) + str(customer_profile.phone_no)

        # update order amount as per selected events

        for event in events:
            event_obj = Event.objects.get(event_name=str(event).lower())
            if customer_profile.senior:
                order_amount += event_obj.price_for_senior
            else:
                order_amount += event_obj.price_for_junior
        
        print(order_amount)

        # pass the above details in the post request to create order on ippo pay api
        # get the order id as response from ippo pay api
        
        # create_order_response_data = http.post('ippo pay ka create order url', above data)

        # use the order id to initiate transaction on ippo pay

        # ippo_pay_order_id = create_order_response_data['order_id']
        # ippo_pay_payment_url = create_order_response_data['payment_url']

        # somehow initiate the transaction lol

        # get transaction details from ippo pay api using order id
        # if status is 200 OK make entry in order table of django

        # transaction_details_response_data = http.get('ippo pay ka transaction details url', order id)
        # if transaction_details_response_data.status == 200:
            # payment_mode = transaction_details_response_data['gateway']

            # create_order = Order(
            #   user_id_fk=request.user.pk
            #   payment_method=payment_mode['pay_mode_id'],
            #   payment_status=transaction_details_response_data['status'],
            #   payment_date_time=transaction_details_response_data['settlement_date'],
            # )
            # create_order.save()

            # for event in events:
            #     event_obj = Event.objects.get(event_name=str(event).lower())
            #     multiple_events_order = MultipleEventsOrder(
            #       order_id_fk=create_order.pk  --> this will probably give an error idk
            #       event_id_fk=event_obj.pk,
            #       event_password = somehow generate random password everytime and assign here
            #     )
            #     multiple_events_order.save()
            #     customer_profle.registered_for.append(event_obj.event_name)
            # customer_profile.save()
            # return Response({'detail':'Your order has been placed and confirmed'}, status=201)
        # else:
            # customer_profile.save()
            # context = {'failure_reason': transaction_details_response_data['failure_reason'],}
            # return Response(context, status=transaction_details_response_data.status)