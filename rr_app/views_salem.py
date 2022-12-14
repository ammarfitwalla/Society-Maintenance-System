import sys
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from rr_app.models import *
import pandas as pd
from django.contrib import messages
from datetime import datetime
from django.core import serializers
import json
from django.views.decorators.cache import cache_control
from django.http import JsonResponse
import calendar


def home(request):
    return render(request, 'home.html')


def master(request):
    all_tenant_db_data = TenantAttributes.objects.all().values()
    all_house_number = HouseNumber.objects.all()
    temp = []
    inserted = False
    for i in all_house_number:
        temp.append(i)
    """
    fetching records from db, inserting into DataFrame and displaying on Master page.
    """
    master_values = []
    if all_tenant_db_data:
        for tenant_data in all_tenant_db_data:
            all_room_number = (RoomNumber.objects.filter(id=tenant_data['room_id']).values())[0]
            all_cts_number = (CTSNumber.objects.filter(id=all_room_number['cts_id']).values())[0]
            all_house_number = (HouseNumber.objects.filter(id=all_cts_number['house_id']).values())[0]

            # tenant_data['id'] : to get the id of records

            # print('<a href=' + '"' + '/crud_operation/' + str(tenant_data['id']) + '">Edit</a>')
            if tenant_data['tenant_dod'] is not None:
                tenant_dod = tenant_data['tenant_dod'].strftime("%d-%m-%Y")
            else:
                tenant_dod = None

            master_values.append([all_house_number['house_number'], all_room_number['room_number'],
                                  all_cts_number['cts_number'], tenant_data['tenant_name'], tenant_dod,
                                  tenant_data['tenant_gender'], str(tenant_data['tenant_mobile_number']),
                                  tenant_data['tenant_permanent_address'],
                                  # '<a href=' + '"' + '{% url ' + "'crud_operation' " + str(tenant_data['id']) + ' %}">Edit</a>'])
                                  # '<a href=' + '"' + '/crud_operation/?tenant_id=' + str(tenant_data['id']) + '">Edit</a>'])
                                  '<a href=' + '"' + '/crud_operation/' + str(tenant_data['id']) + '">Edit</a>'])

            # print(tenant_data['tenant_mobile_number'])

    """
    -> Fetching user input data from master form page, 
    -> checking room number duplication, 
    -> inserting into db.
    """

    if request.method == 'POST':
        get_house_number = request.POST.get('house')
        get_cts_number = request.POST.get('cts')
        get_room_number = request.POST.get('room')
        get_tenant_name = request.POST.get('tenant_name')
        get_permanent_address = request.POST.get('permanent_address')
        get_tenant_dod = request.POST.get('tenant_dod')
        get_tenant_gender = request.POST.get('tenant_gender')
        get_tenant_mobile_number = request.POST.get('tenant_mobile_number')

        if get_tenant_mobile_number == '':
            get_tenant_mobile_number = None
        if get_tenant_dod == '':
            get_tenant_dod = None

        if HouseNumber.objects.filter(house_number=get_house_number).exists():
            get_house_number_id = HouseNumber.objects.get(house_number=get_house_number)
        else:
            insert_house_number = HouseNumber(house_number=get_house_number)
            insert_house_number.save()
            get_house_number_id = HouseNumber.objects.last()

        if CTSNumber.objects.filter(house=get_house_number_id, cts_number=get_cts_number).exists():
            get_cts_number_id = CTSNumber.objects.get(house=get_house_number_id, cts_number=get_cts_number)
        else:
            insert_cts_number = CTSNumber(house=get_house_number_id, cts_number=get_cts_number)
            insert_cts_number.save()
            get_cts_number_id = CTSNumber.objects.last()

        if RoomNumber.objects.filter(house=get_house_number_id, room_number=get_room_number).exists():
            messages.error(request, 'Entered Room Number already exist for different tenant !!!')
            return redirect('/master/')

        else:
            insert_room_number = RoomNumber(house=get_house_number_id, cts=get_cts_number_id,
                                            room_number=get_room_number)
            insert_room_number.save()
            get_room_number_id = RoomNumber.objects.last()

        insert_tenant_attributes = TenantAttributes(room=get_room_number_id, tenant_name=get_tenant_name,
                                                    tenant_permanent_address=get_permanent_address,
                                                    tenant_mobile_number=get_tenant_mobile_number,
                                                    tenant_dod=get_tenant_dod, tenant_gender=get_tenant_gender)
        insert_tenant_attributes.save()

        last_tenant_db_data = TenantAttributes.objects.last()

        master_values.append(
            [last_tenant_db_data.id, get_house_number, get_room_number, get_cts_number, get_tenant_name, get_tenant_dod,
             get_tenant_gender, get_tenant_mobile_number, get_permanent_address])

        inserted = True

    master_df = pd.DataFrame(master_values,
                             columns=['House Number', 'Room Number', 'CTS Number', 'Tenant Name', 'DOD',
                                      'Gender', 'Mobile No.', 'Notes', 'Edit'])

    master_df = master_df.to_html(index_names=False, index=False, classes="table table-bordered", escape=False,
                                  render_links=True)
    context = {
        'master_df': master_df,
        'temp': temp
    }
    if inserted:
        return redirect('/master/')

    # return render(request, 'master.html', context)
    return render(request, 'master_1.html', context)


# TODO : Need to fix this function
def crud_operation(request, tenant_id):
    all_tenant_db_data = TenantAttributes.objects.filter(id=tenant_id).values()[0]
    room_number = (RoomNumber.objects.filter(id=all_tenant_db_data['room_id']).values())[0]
    cts_number = (CTSNumber.objects.filter(id=room_number['cts_id']).values())[0]
    house_number = (HouseNumber.objects.filter(id=cts_number['house_id']).values())[0]
    house_number_list = HouseNumber.objects.all()
    temp = []
    for i in house_number_list:
        temp.append(i)

    tenant_mobile_number = all_tenant_db_data['tenant_mobile_number']
    if tenant_mobile_number is None:
        tenant_mobile_number = ''

    room_number_id = all_tenant_db_data['room_id']
    cts_number_id = room_number['cts_id']
    house_number_id = cts_number['house_id']

    if request.method == 'POST':
        get_house_number = request.POST.get('house')
        get_cts_number = request.POST.get('cts')
        get_room_number = request.POST.get('room')
        get_tenant_name = request.POST.get('tenant_name')
        get_permanent_address = request.POST.get('permanent_address')
        get_tenant_dod = request.POST.get('tenant_dod')
        get_tenant_gender = request.POST.get('tenant_gender')
        get_tenant_mobile_number = request.POST.get('tenant_mobile_number')

        if get_tenant_mobile_number == '':
            get_tenant_mobile_number = None
        if get_tenant_dod == '':
            get_tenant_dod = None

        if HouseNumber.objects.filter(house_number=get_house_number).exists():
            get_house_number_id = HouseNumber.objects.get(house_number=get_house_number)
        else:
            insert_house_number = HouseNumber(house_number=get_house_number)
            insert_house_number.save()
            get_house_number_id = HouseNumber.objects.last()

        if CTSNumber.objects.filter(house=get_house_number_id, cts_number=get_cts_number).exists():
            get_cts_number_id = CTSNumber.objects.get(house=get_house_number_id, cts_number=get_cts_number)
        else:
            insert_cts_number = CTSNumber(house=get_house_number_id, cts_number=get_cts_number)
            insert_cts_number.save()
            get_cts_number_id = CTSNumber.objects.last()

        if room_number['room_number'] != get_room_number and RoomNumber.objects.filter(house=get_house_number_id,
                                                                                       room_number=get_room_number).exists():
            messages.error(request, 'Entered Room Number already exist for different tenant !!!')
            return redirect('/master/')

        else:
            insert_room_number = RoomNumber(id=room_number_id, house=get_house_number_id, cts=get_cts_number_id,
                                            room_number=get_room_number)
            insert_room_number.save()
            get_room_number_id = RoomNumber.objects.get(id=room_number_id)

        insert_tenant_attributes = TenantAttributes(id=tenant_id, room=get_room_number_id, tenant_name=get_tenant_name,
                                                    tenant_permanent_address=get_permanent_address,
                                                    tenant_mobile_number=get_tenant_mobile_number,
                                                    tenant_dod=get_tenant_dod, tenant_gender=get_tenant_gender)
        insert_tenant_attributes.save()

        return redirect('/master/')

    context = {'tenant_name': all_tenant_db_data['tenant_name'],
               'tenant_permanent_address': all_tenant_db_data['tenant_permanent_address'],
               'tenant_mobile_number': tenant_mobile_number,
               'tenant_dod': str(all_tenant_db_data['tenant_dod']),
               'tenant_gender': all_tenant_db_data['tenant_gender'],
               'room_number': room_number['room_number'],
               'cts_number': cts_number['cts_number'],
               'house_number': house_number['house_number'],
               'temp': temp}

    # return render(request, 'crud_operation.html', context)
    return render(request, 'crud_operation_1.html', context)


# OLD TENANT_BILL CODE ==============
# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
# def tenant_bill(request):
#     house_ = []
#     room_ = []
#     cts_ = []
#     ta_ = []
#
#     all_house_number = HouseNumber.objects.all()
#     for h in all_house_number:
#         house_.append(h)
#
#     all_room_number = RoomNumber.objects.all()
#     for r in all_room_number:
#         room_.append(r.house.house_number)
#         room_.append(r.room_number)
#         room_.append(r.cts.cts_number)
#
#     all_tenant_number = TenantAttributes.objects.all()
#     for t in all_tenant_number:
#         ta_.append(t.tenant_name)
#         ta_.append(t.room.room_number)
#         ta_.append(t.tenant_permanent_address)
#         ta_.append(t.tenant_mobile_number)
#         ta_.append(str(t.tenant_dod))
#         ta_.append(t.tenant_gender)
#
#
#
#
#     context = {
#             'house_': house_,
#             'room_': room_,
#             'ta_': ta_,
#
#         }
#     return render(request, 'tenant_bill.html', context)

def month_name_to_int(month_name_year):
    m_name_y = month_name_year.split('-')
    name = m_name_y[0]
    year = m_name_y[1]
    # mname = 'Mar'
    m_num = datetime.strptime(name, '%b').month
    print(m_num, type(m_num))
    if m_num < 9:
        return year + '-0' + str(m_num)
    return year + '-' + str(m_num)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def get_old_bill(request):
    old_bill = Bill.objects.filter(house_number=request.POST['house_num'],
                                   room_number=request.POST['room']).order_by('-id')

    # print('bill_numberbill_number')
    # print(old_bill)
    # print(old_bill.received_date)

    if len(old_bill) != 0:
        old_bill = old_bill[0]

        bill_for_month_of = month_name_to_int(old_bill.bill_for_month_of)
        rent_for_month_from = month_name_to_int(old_bill.rent_from)
        rent_for_month_to = month_name_to_int(old_bill.rent_to)
        print('====', bill_for_month_of)

        # print('in get old bill function', request.POST['house_num'])
        # return JsonResponse({'response': 'Hello! how can I help you?', 'pre': [], 'detection': []})

        return JsonResponse({'cts': old_bill.cts_number, 'tmn': old_bill.tenant_mobile_number,
                             'tdod': old_bill.tenant_dod, 'bfm': bill_for_month_of,
                             'bkn': old_bill.book_number, 'bln': old_bill.bill_number, 'pf': old_bill.purpose_for,
                             'rfm': rent_for_month_from, 'rto': rent_for_month_to, 'atr': old_bill.at_the_rate_of,
                             'tmnth': old_bill.total_months, 'trp': old_bill.total_rupees,
                             'rdte': old_bill.received_date,
                             'expm': old_bill.extra_payment, 'agdt': old_bill.agreement_date, 'note': old_bill.notes,
                             })
    else:
        try:
            house_obj = HouseNumber.objects.get(house_number=request.POST['house_num'])
            room_num_obj = RoomNumber.objects.get(house=house_obj,
                                                  room_number=request.POST['room'])
            print(room_num_obj)
            get_cts = room_num_obj.cts.cts_number
            print('got cts', get_cts)

            old_ta = TenantAttributes.objects.filter(room=room_num_obj,
                                                     tenant_name=request.POST['name']).order_by('-id')[0]

            return JsonResponse({'tmn': old_ta.tenant_mobile_number, 'cts': get_cts,
                                 'tdod': old_ta.tenant_dod
                                 })
        except:
            print('CTS Data Fetch Failed!!')


def num_date_to_string(num_date):
    print("num_date")
    print(num_date)
    string_date = calendar.month_name[int(str(num_date).split("-")[1])][:3] + "-" + str(num_date).split("-")[0]
    return string_date


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def tenant_bill(request):
    all_bill_data = Bill.objects.all()

    house_ = list(HouseNumber.objects.all().values_list('house_number', flat=True))

    if request.method == 'POST':
        bill_house_number = request.POST.get('house')
        bill_room_number = request.POST.get('room')
        bill_cts_number = request.POST.get('cts')
        # bill_tenant_mobile_number = request.POST.get('tenant_mobile_number')
        # bill_tenant_name = request.POST.get('tenant_name')
        # bill_tenant_dod = request.POST.get('tenant_dod')
        bill_for_month_of = request.POST.get('bill_for_month_of')
        bill_book_number = request.POST.get('book_number')
        bill_number = request.POST.get('bill_number')
        purpose_for = request.POST.get('purpose_for')
        rent_for_month_from = request.POST.get('rent_for_month_from')
        rent_for_month_to = request.POST.get('rent_for_month_to')
        at_the_rate_of = request.POST.get('at_the_rate_of')
        total_months = request.POST.get('total_months')
        total_rupees = request.POST.get('total_rupees')
        extra_payment = request.POST.get('extra_payment')
        received_date = request.POST.get('received_date')
        agreement_date = request.POST.get('agreement_date')
        notes = request.POST.get('notes')

        if agreement_date == "":
            agreement_date = None
        # print('--===-', bill_for_month_of)
        bill_for_month_of = num_date_to_string(bill_for_month_of)
        rent_for_month_from = num_date_to_string(rent_for_month_from)
        rent_for_month_to = num_date_to_string(rent_for_month_to)
        # print('----', bill_for_month_of)

        get_house_id = HouseNumber.objects.get(house_number=bill_house_number)
        get_cts_id = CTSNumber.objects.get(house=get_house_id, cts_number=bill_cts_number)
        get_room_number = (
            RoomNumber.objects.filter(house=get_house_id, cts=get_cts_id, room_number=bill_room_number).values()[0])
        get_tenant_attrs = (TenantAttributes.objects.filter(room=get_room_number['id']).values())[0]

        save_bill_details = Bill(house_number=bill_house_number, cts_number=bill_cts_number,
                                 room_number=bill_room_number, tenant_name=get_tenant_attrs['tenant_name'],
                                 tenant_permanent_address=get_tenant_attrs['tenant_permanent_address'],
                                 tenant_mobile_number=get_tenant_attrs['tenant_mobile_number'],
                                 tenant_dod=get_tenant_attrs['tenant_dod'],
                                 tenant_gender=get_tenant_attrs['tenant_gender'],
                                 bill_for_month_of=bill_for_month_of, book_number=bill_book_number,
                                 bill_number=bill_number, purpose_for=purpose_for,
                                 rent_from=rent_for_month_from, rent_to=rent_for_month_to,
                                 at_the_rate_of=at_the_rate_of, total_months=total_months,
                                 total_rupees=total_rupees, received_date=received_date,
                                 extra_payment=extra_payment, agreement_date=agreement_date, notes=notes)

        save_bill_details.save()

        return redirect('/tenant_bill/')

    context = {
        'house_': house_,
        'all_bill_data': all_bill_data
    }
    return render(request, 'tenant_bill.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def name_room_list(request):
    tname_room = []
    get_house = HouseNumber.objects.filter(house_number=request.POST['h_num'])[0]
    all_room_number = RoomNumber.objects.filter(house=get_house)

    all_tenant_number = TenantAttributes.objects.all()
    for t in all_tenant_number:
        if t.room in all_room_number:
            tname_room.append(t.tenant_name + '---' + t.room.room_number)

    return JsonResponse({'tname_room': tname_room})


# 1. Room number display nai hora hai kuch room ka (hyphen issue) & (clear Cache of names)
# 2. Jan to march 3 months not 2 ----
# 5. when tenant name is selected, auto-fill all previous details if any
