from django.shortcuts import render
from django.http import HttpResponse

from rest_framework import generics, status, mixins
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

from .models import *
from .serializers import *

import random
import array
import  csv


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
    permission_classes = [AllowAny]


class EventsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [AllowAny]


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
            return Response({'detail': 'You do not have permission to perform this action.'}, status=403)


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
            # only one event can be ordered at a time

            # events = []
            # events_in_order = MultipleEventsOrder.objects.filter(order_id_fk=order.pk)
            # for event in events_in_order:
            #     event_details = Event.objects.get(pk=event.event_id_fk.pk)
            #     events.append(event_details.event_name)
            context = {
                'pk': order.pk,
                'user_id_fk': order.user_id_fk.pk,
                'order_date_time': order.order_date_time,
                'event_name': order.event_id_fk.event_name,
                'event_password': order.event_password,
                # 'payment_method': order.payment_method,
                # 'payment_status': order.payment_status,
                # 'payment_date_time': order.payment_date_time,
                # 'events': events,
            }
            return Response(context, status=201)
        context = {
            'detail': 'You don\'t have any orders to display or the order ID is not yours',
        }

        return Response(context, status=403)


class PlaceOrder(APIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def randomPasswordGenerator(self):
        # maximum length of password needed
        # this can be changed to suit your password length
        max_len = 8

        # declare arrays of the character that we need in out password
        # Represented as chars to enable easy string concatenation
        digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        lowercase_characters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
                                'i', 'j', 'k', 'm', 'n', 'o', 'p', 'q',
                                'r', 's', 't', 'u', 'v', 'w', 'x', 'y',
                                'z']

        uppercase_characters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
                                'I', 'J', 'K', 'M', 'N', 'O', 'p', 'Q',
                                'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y',
                                'Z']

        symbols = ['@', '#', '$', '%', '?', '*']

        # combines all the character arrays above to form one array
        combined_list = digits + uppercase_characters + lowercase_characters + symbols

        # randomly select at least one character from each character set above
        rand_digit = random.choice(digits)
        rand_upper = random.choice(uppercase_characters)
        rand_lower = random.choice(lowercase_characters)
        rand_symbol = random.choice(symbols)

        # combine the character randomly selected above
        # at this stage, the password contains only 4 characters but
        # we want a 12-character password
        temp_pass = rand_digit + rand_upper + rand_lower + rand_symbol

        # now that we are sure we have at least one character from each
        # set of characters, we fill the rest of
        # the password length by selecting randomly from the combined
        # list of character above.
        for x in range(max_len - 4):
            temp_pass = temp_pass + random.choice(combined_list)

            # convert temporary password into array and shuffle to
            # prevent it from having a consistent pattern
            # where the beginning of the password is predictable
            temp_pass_list = array.array('u', temp_pass)
            random.shuffle(temp_pass_list)

        # traverse the temporary password array and append the chars
        # to form the password
        password = ""
        for x in temp_pass_list:
            password = password + x

        # print out password
        return password

    def post(self, request):

        event_id = request.data['event_id_fk']  # event ordered by user
        event = Event.objects.get(pk=event_id)
        prev_order = Order.objects.filter(user_id_fk=request.user.id, event_id_fk=event_id)
        if prev_order:
            return Response({'detail': 'You have already registered for this event'})  # status code?
        # this is first order for the event
        # do normal registration
        # generate random password
        password = self.randomPasswordGenerator()
        create_order = Order(user_id_fk=request.user, event_id_fk=event, event_password=password)
        create_order.save()
        return Response({'detail': 'Your order has been placed'}, status=201)
        # registered_for = customer_profile.registered_for --> should return a list

        # for event in events:
        #     event_obj = Event.objects.get(event_name=str(event).lower())
        #     if event_obj.event_name in registered_for:
        #         return Response({'error': str('You have already registered for ' + event_obj.event_name + ' before.')}, status=204)

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
        #
        # order_amount = 0  # initial amount
        # currency = 'INR'
        # payment_modes = Order.payment_methods
        # print(payment_modes)
        # customer_name = str(request.user.first_name) + str(request.user.last_name)
        # customer_email = str(request.user.email)
        # customer_phone_number = str(customer_profile.country_code) + str(customer_profile.phone_no)

        # update order amount as per selected events

        # for event in events:
        #     event_obj = Event.objects.get(event_name=str(event).lower())
        #     if customer_profile.senior:
        #         order_amount += event_obj.price_for_senior
        #     else:
        #         order_amount += event_obj.price_for_junior
        #
        # print(order_amount)

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

def exportToCSV(request):
    if request.user.is_superuser:
        event_lines = EventLine.objects.all()
        for event_line in event_lines:
            print(event_line)
            events = Event.objects.filter(event_line_fk=event_line)
            if events:
                for event in events:
                    with open('{}.csv'.format(event.event_name), 'w') as file:
                        # fetch all registered users and their passwords and write
                        # will need to use user, profile, event and order models
                        writer = csv.writer(file)
                        objects = Order.objects.filter(event_id_fk=event)
                        if objects:
                            writer.writerow(['username', 'password'])
                            for object in objects:
                                entry = ['{}'.format(object.user_id_fk.username), '{}'.format(object.event_password)]
                                # print(entry)
                                writer.writerow(entry)
                # print(events)
        return HttpResponse("CSVs have been created")
    return HttpResponse("You are not allowed to perform this action")
