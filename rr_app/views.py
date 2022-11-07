import os
import calendar
import subprocess
import cv2
import numpy as np
import pandas as pd
from PIL import Image
from rr_app.models import *
from datetime import datetime
from django.contrib import messages
from django.http import JsonResponse
from rr_project.settings import MEDIA_ROOT
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_control
from django.contrib.humanize.templatetags.humanize import ordinal
from django.http import HttpResponse


def check_dir_exists(path):
    """
    :param path: /path/to/dir
    :return: if dir not present, it creates a dir
    """
    if not os.path.isdir(path):
        os.mkdir(path)


def num_date_to_string(num_date, short_form=True):
    """
    :param num_date: year-month : 2022-01
    :param short_form: True/False
    :return: month_name : Jan-2022/January-2022
    """
    year_ = str(num_date).split('-')[0]
    month_num_ = str(num_date).split('-')[1]

    if short_form:
        month_name = calendar.month_name[int(month_num_)][:3] + "-" + year_
    else:
        month_name = calendar.month_name[int(month_num_)] + '-' + year_

    return month_name


def month_name_to_int(month_name_year):
    m_name_y = month_name_year.split('-')
    name = m_name_y[0]
    year = m_name_y[1]
    m_num = datetime.strptime(name, '%b').month
    if m_num <= 9:
        return year + '-0' + str(m_num)
    return year + '-' + str(m_num)


def home(request):
    return render(request, 'home.html')


def master(request):
    master_values = []

    if request.method == 'POST':
        # TODO : Need to fix this operation
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
            get_house_number_id = HouseNumber.objects.get(
                house_number=get_house_number)
        else:
            insert_house_number = HouseNumber(house_number=get_house_number)
            insert_house_number.save()
            get_house_number_id = HouseNumber.objects.last()

        if CTSNumber.objects.filter(house=get_house_number_id, cts_number=get_cts_number).exists():
            get_cts_number_id = CTSNumber.objects.get(
                house=get_house_number_id, cts_number=get_cts_number)
        else:
            insert_cts_number = CTSNumber(
                house=get_house_number_id, cts_number=get_cts_number)
            insert_cts_number.save()
            get_cts_number_id = CTSNumber.objects.last()


        if request.session['master_crud'] == 'Edit':
            all_tenant_db_data = TenantAttributes.objects.filter(
                id=request.session['tenant_id']).values()[0]
            room_number = (RoomNumber.objects.filter(
                id=all_tenant_db_data['room_id']).values())[0]
            room_number_id = all_tenant_db_data['room_id']

            if room_number['room_number'] != get_room_number and RoomNumber.objects.filter(house=get_house_number_id,
                                                                                           room_number=get_room_number).exists():
                messages.error(
                    request, 'Entered Room Number already exist for different tenant !')
                return redirect('/master/')

            else:
                insert_room_number = RoomNumber(id=room_number_id, house=get_house_number_id, cts=get_cts_number_id,
                                                room_number=get_room_number)
                insert_room_number.save()
                get_room_number_id = RoomNumber.objects.get(id=room_number_id)

            insert_tenant_attributes = TenantAttributes(id=request.session['tenant_id'], room=get_room_number_id, tenant_name=get_tenant_name,
                                                        tenant_permanent_address=get_permanent_address,
                                                        tenant_mobile_number=get_tenant_mobile_number,
                                                        tenant_dod=get_tenant_dod, tenant_gender=get_tenant_gender)
            
            insert_tenant_attributes.save()

            messages.success(request, "Tenant '" + get_tenant_name + "' Updated Successfully!")
        else:

            if RoomNumber.objects.filter(house=get_house_number_id, room_number=get_room_number).exists():
                messages.error(
                request, 'Entered Room Number already exist for different tenant !!!')
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
            messages.success(request, "New Tenant '" + get_tenant_name + "' Added Successfully!")
        return redirect('/master/')

    request.session['master_crud'] = 'Add'
    request.session['tenant_id'] = 'new'
    all_tenant_db_data = TenantAttributes.objects.all().values()
    inserted = False
    temp = list(HouseNumber.objects.all().values_list(
        'house_number', flat=True))
    """
    fetching records from db, inserting into DataFrame and displaying on Master page.
    """
    if all_tenant_db_data:
        for tenant_data in all_tenant_db_data:
            all_room_number = (RoomNumber.objects.filter(
                id=tenant_data['room_id']).values())[0]
            all_cts_number = (CTSNumber.objects.filter(
                id=all_room_number['cts_id']).values())[0]
            all_house_number = (HouseNumber.objects.filter(
                id=all_cts_number['house_id']).values())[0]

            if tenant_data['tenant_dod'] is not None:
                tenant_dod = tenant_data['tenant_dod'].strftime("%d-%m-%Y")
            else:
                tenant_dod = None

            master_values.append(
                [all_house_number['house_number'], all_room_number['room_number'], all_cts_number['cts_number'],
                 tenant_data['tenant_name'], tenant_dod, tenant_data['tenant_gender'],
                 str(tenant_data['tenant_mobile_number']
                     ), tenant_data['tenant_permanent_address'],
                 '<a href=' + '"' + 'javascript:updateMaster(' + str(tenant_data['id']) + ');">Edit</a>']
            )

    """
    -> Fetching user input data from master form page, 
    -> checking room number duplication, 
    -> inserting into db.
    """

    master_df = pd.DataFrame(master_values,
                             columns=['House No.', 'Room No.', 'CTS No.', 'Tenant Name', 'DOD', 'Gender', 'Mobile No.',
                                      'Notes', 'Edit'])
    master_df = master_df.to_html(index_names=False, index=False,
                                  classes="table table-bordered table-sm table-responsive-sm table-hover", escape=False,
                                  render_links=True)
    if inserted:
        return redirect('/master/')

    context = {
        'master_df': master_df, 
        'temp': temp
    }
    return render(request, 'master.html', context)


def crud_operation(request):
    try:
        request.session['tenant_id'] = request.POST['t_id']
        request.session['master_crud'] = 'Edit'

        all_tenant_db_data = TenantAttributes.objects.filter(
            id=request.session['tenant_id']).values()[0]
        room_number = (RoomNumber.objects.filter(
            id=all_tenant_db_data['room_id']).values())[0]
        cts_number = (CTSNumber.objects.filter(
            id=room_number['cts_id']).values())[0]
        house_number = (HouseNumber.objects.filter(
            id=cts_number['house_id']).values())[0]
        temp = list(HouseNumber.objects.all().values_list(
            'house_number', flat=True))

        tenant_mobile_number = all_tenant_db_data['tenant_mobile_number']
        if tenant_mobile_number is None:
            tenant_mobile_number = ''

        return JsonResponse(
            {
                'tenant_name': all_tenant_db_data['tenant_name'],
                'tenant_permanent_address': all_tenant_db_data['tenant_permanent_address'],
                'tenant_mobile_number': tenant_mobile_number,
                'tenant_dod': str(all_tenant_db_data['tenant_dod']),
                'tenant_gender': all_tenant_db_data['tenant_gender'],
                'room_number': room_number['room_number'],
                'cts_number': cts_number['cts_number'], 'house_number': house_number['house_number'],
                'temp': temp
            }
        )

    except Exception as e:
        print('Edit Data Fetch Failed!! -> Error: ', str(e))


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def tenant_bill(request):

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
        print_button = request.POST.get('print')
        print('print_button:: ', print_button)

        if agreement_date == "":
            agreement_date = None

        rent_for_month_from_long = num_date_to_string(
            rent_for_month_from, short_form=False)
        rent_for_month_to_long = num_date_to_string(
            rent_for_month_to, short_form=False)

        bill_for_month_of_short = num_date_to_string(bill_for_month_of)
        rent_for_month_from_short = num_date_to_string(rent_for_month_from)
        rent_for_month_to_short = num_date_to_string(rent_for_month_to)

        get_house_id = HouseNumber.objects.get(house_number=bill_house_number)
        get_cts_id = CTSNumber.objects.get(
            house=get_house_id, cts_number=bill_cts_number)
        get_room_number = (RoomNumber.objects.filter(
            house=get_house_id, cts=get_cts_id, room_number=bill_room_number).values()[0])
        get_tenant_attrs = (TenantAttributes.objects.filter(
            room=get_room_number['id']).values())[0]

        print("request.session[]=====", request.session['bill_id'])
        if request.session['bill_crud'] == 'Edit':
            # print(request.session['bill_id'])

            Bill.objects.filter(id=request.session['bill_id']).update(house_number=bill_house_number, cts_number=bill_cts_number, room_number=bill_room_number,
                                                            tenant_name=get_tenant_attrs['tenant_name'], tenant_permanent_address=get_tenant_attrs[
                                                                'tenant_permanent_address'],
                                                            tenant_mobile_number=get_tenant_attrs[
                                                                'tenant_mobile_number'], tenant_dod=get_tenant_attrs['tenant_dod'],
                                                            tenant_gender=get_tenant_attrs[
                                                                'tenant_gender'], bill_for_month_of=bill_for_month_of_short, book_number=bill_book_number,
                                                            bill_number=bill_number, purpose_for=purpose_for, rent_from=rent_for_month_from_short, rent_to=rent_for_month_to_short,
                                                            at_the_rate_of=at_the_rate_of, total_months=total_months, total_rupees=total_rupees, received_date=received_date,
                                                            extra_payment=extra_payment, agreement_date=agreement_date, notes=notes)

            if print_button and print_button != "":
                # TODO: check if data is present in db, if not, ask user to save first

                check_dir_exists(os.path.join(MEDIA_ROOT, bill_house_number))
                check_dir_exists(os.path.join(
                    MEDIA_ROOT, bill_house_number, bill_cts_number))
                check_dir_exists(os.path.join(
                    MEDIA_ROOT, bill_house_number, bill_cts_number, bill_room_number))
                check_dir_exists(os.path.join(MEDIA_ROOT, bill_house_number,
                                bill_cts_number, bill_room_number, get_tenant_attrs['tenant_name']))

                today = datetime.today()
                day = '{:02d}'.format(today.day)
                ordinal_ = str(ordinal(day))[2:]
                month = today.strftime("%b")
                year = '{:02d}'.format(today.year)

                for i in range(2):
                    if i == 0:
                        image = os.path.join(
                            MEDIA_ROOT, 'bill_sample', 'rr_bill.jpg')
                        img_arr = cv2.imread(image)
                    else:
                        img_arr = np.zeros([2561, 1763, 3], dtype=np.uint8)
                        img_arr.fill(255)

                    img_arr = cv2.putText(img_arr, bill_for_month_of_short, (
                        600, 830), cv2.FONT_HERSHEY_TRIPLEX, 1.6, (0, 0, 0), 2)  # bill for month of
                    img_arr = cv2.putText(img_arr, bill_book_number, (1127, 830),
                                        cv2.FONT_HERSHEY_TRIPLEX, 1.6, (0, 0, 0), 2)  # book number
                    img_arr = cv2.putText(img_arr, bill_number, (1414, 830),
                                        cv2.FONT_HERSHEY_TRIPLEX, 1.6, (0, 0, 0), 2)  # bill number
                    img_arr = cv2.putText(img_arr, "For residence", (235, 940),
                                        cv2.FONT_HERSHEY_TRIPLEX, 1.6, (0, 0, 0), 2)  # for residence
                    img_arr = cv2.putText(img_arr, bill_cts_number, (1127, 935),
                                        cv2.FONT_HERSHEY_TRIPLEX, 1.6, (0, 0, 0), 2)  # cts number
                    img_arr = cv2.putText(img_arr, bill_room_number, (600, 1050),
                                        cv2.FONT_HERSHEY_TRIPLEX, 1.6, (0, 0, 0), 2)  # room number
                    img_arr = cv2.putText(img_arr, bill_house_number, (1127, 1050),
                                        cv2.FONT_HERSHEY_TRIPLEX, 1.6, (0, 0, 0), 2)  # house number
                    img_arr = cv2.putText(img_arr, get_tenant_attrs['tenant_name'], (
                        378, 1341), cv2.FONT_HERSHEY_TRIPLEX, 1.5, (0, 0, 0), 2)  # Tenant name
                    img_arr = cv2.putText(img_arr, rent_for_month_from_long + " to " + rent_for_month_to_long,
                                        (747, 1455), cv2.FONT_HERSHEY_TRIPLEX, 1.4, (0, 0, 0), 2)  # month from and to
                    img_arr = cv2.putText(img_arr, total_rupees, (1127, 1610),
                                        cv2.FONT_HERSHEY_TRIPLEX, 1.6, (0, 0, 0), 2)  # total rupees
                    img_arr = cv2.putText(
                        img_arr, "00.", (1483, 1610), cv2.FONT_HERSHEY_TRIPLEX, 1.6, (0, 0, 0), 2)  # month from and to
                    img_arr = cv2.putText(
                        img_arr, "@", (730, 1540), cv2.FONT_HERSHEY_TRIPLEX, 1.6, (0, 0, 0), 2)  # @
                    img_arr = cv2.putText(
                        img_arr, f"Rs. {at_the_rate_of}/-", (665, 1595), cv2.FONT_HERSHEY_TRIPLEX, 1.2, (0, 0, 0), 2)  # rs
                    img_arr = cv2.putText(img_arr, "per month", (665, 1640),
                                        cv2.FONT_HERSHEY_TRIPLEX, 1.2, (0, 0, 0), 2)  # per month
                    img_arr = cv2.putText(
                        img_arr, day, (993, 1850), cv2.FONT_HERSHEY_TRIPLEX, 1.3, (0, 0, 0), 2)  # current date
                    img_arr = cv2.putText(img_arr, ordinal_, (1046, 1828),
                                        cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 0, 0), 2)  # ordinal
                    img_arr = cv2.putText(
                        img_arr, month, (1260, 1850), cv2.FONT_HERSHEY_TRIPLEX, 1.3, (0, 0, 0), 2)  # current month
                    img_arr = cv2.putText(
                        img_arr, year, (1493, 1850), cv2.FONT_HERSHEY_TRIPLEX, 1.3, (0, 0, 0), 2)  # current year

                    img_arr = cv2.resize(img_arr, (1748, 2480))
                    im = cv2.cvtColor(img_arr, cv2.COLOR_BGR2RGB)
                    im = Image.fromarray(im)
                    a5im = Image.new('RGB', (1748, 2480), (255, 255, 255))
                    a5im.paste(im, im.getbbox())

                    if i == 0:
                        pdf_name = os.path.join(MEDIA_ROOT, bill_house_number, bill_cts_number, bill_room_number,
                                                get_tenant_attrs['tenant_name'], rent_for_month_from_long + "-to-" + rent_for_month_to_long + ".pdf")
                        a5im.save(pdf_name, 'PDF', quality=100)
                    else:
                        pdf_name = os.path.join(MEDIA_ROOT, bill_house_number, bill_cts_number, bill_room_number,
                                                get_tenant_attrs['tenant_name'], rent_for_month_from_long + "-to-" + rent_for_month_to_long + "_blank.pdf")
                        a5im.save(pdf_name, 'PDF', quality=100)
                        subprocess.Popen([pdf_name], shell=True)
                messages.success(request, "Bill '" + bill_number + "' Printed & Updated Successfully!")
            else:       
                messages.success(request, "Bill '" + bill_number + "' Updated Successfully!")

        else:
            # TODO: Check if data is present in db, if present, return message saying data already exists
            save_bill_details = Bill(house_number=bill_house_number, cts_number=bill_cts_number, room_number=bill_room_number,
                                    tenant_name=get_tenant_attrs['tenant_name'], tenant_permanent_address=get_tenant_attrs[
                                        'tenant_permanent_address'],
                                    tenant_mobile_number=get_tenant_attrs[
                                        'tenant_mobile_number'], tenant_dod=get_tenant_attrs['tenant_dod'],
                                    tenant_gender=get_tenant_attrs[
                                        'tenant_gender'], bill_for_month_of=bill_for_month_of_short, book_number=bill_book_number,
                                    bill_number=bill_number, purpose_for=purpose_for, rent_from=rent_for_month_from_short, rent_to=rent_for_month_to_short,
                                    at_the_rate_of=at_the_rate_of, total_months=total_months, total_rupees=total_rupees, received_date=received_date,
                                    extra_payment=extra_payment, agreement_date=agreement_date, notes=notes)

            save_bill_details.save()
            messages.success(request, "New Bill '" + bill_number + "' Added Successfully!")
        return redirect('/tenant_bill/')
        
    request.session['bill_crud'] = 'Add'
    request.session['bill_id'] = 'new'
    all_bill_data = Bill.objects.all()

    house_ = list(HouseNumber.objects.all().values_list(
        'house_number', flat=True))

    context = {'house_': house_, 'all_bill_data': all_bill_data}
    return render(request, 'tenant_bill.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def tenant_bill_crud(request):
    try:
        request.session['bill_id'] = request.POST['bill_id']
        request.session['bill_crud'] = 'Edit'

        filtered_one_bill_data = Bill.objects.filter(
            id=request.session['bill_id']).all()[0]

        bill_for_month_of = month_name_to_int(
            filtered_one_bill_data.bill_for_month_of)
        rent_for_month_from = month_name_to_int(
            filtered_one_bill_data.rent_from)
        rent_for_month_to = month_name_to_int(filtered_one_bill_data.rent_to)

        return JsonResponse(
            {
                'house_number': filtered_one_bill_data.house_number,
                'cts_number': filtered_one_bill_data.cts_number,
                'room_number': filtered_one_bill_data.room_number,
                'tenant_name': filtered_one_bill_data.tenant_name,
                'tenant_permanent_address': filtered_one_bill_data.tenant_permanent_address,
                'tenant_mobile_number': filtered_one_bill_data.tenant_mobile_number,
                'tenant_dod': filtered_one_bill_data.tenant_dod,
                'tenant_gender': filtered_one_bill_data.tenant_gender,
                'bill_for_month_of': bill_for_month_of,
                'book_number': filtered_one_bill_data.book_number,
                'bill_number': filtered_one_bill_data.bill_number,
                'purpose_for': filtered_one_bill_data.purpose_for,
                'rent_from': rent_for_month_from,
                'rent_to': rent_for_month_to,
                'at_the_rate_of': filtered_one_bill_data.at_the_rate_of,
                'total_months': filtered_one_bill_data.total_months,
                'total_rupees': filtered_one_bill_data.total_rupees,
                'received_date': filtered_one_bill_data.received_date,
                'extra_payment': filtered_one_bill_data.extra_payment,
                'agreement_date': filtered_one_bill_data.agreement_date,
                'notes': filtered_one_bill_data.notes,
            }
        )
    except Exception as e:
        print('Edit Data Fetch Failed!! -> Error: ', str(e))


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def name_room_list(request):
    get_house = HouseNumber.objects.filter(
        house_number=request.POST['h_num'])[0]
    all_room_number = RoomNumber.objects.filter(house=get_house)
    all_tenant_number = TenantAttributes.objects.all()

    tname_room = [t.tenant_name + '---' +
                  t.room.room_number for t in all_tenant_number if t.room in all_room_number]

    return JsonResponse({'tname_room': tname_room})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def get_old_bill(request):
    print('=======', request.POST['room'])
    old_bill = Bill.objects.filter(
        house_number=request.POST['house_num'], room_number=request.POST['room']).order_by('-id')

    if len(old_bill) != 0:
        old_bill = old_bill[0]

        bill_for_month_of = month_name_to_int(old_bill.bill_for_month_of)
        rent_for_month_from = month_name_to_int(old_bill.rent_from)
        rent_for_month_to = month_name_to_int(old_bill.rent_to)

        return JsonResponse({'cts': old_bill.cts_number, 'tmn': old_bill.tenant_mobile_number, 'tdod': old_bill.tenant_dod, 'bfm': bill_for_month_of,
                             'bkn': old_bill.book_number, 'bln': old_bill.bill_number, 'pf': old_bill.purpose_for, 'rfm': rent_for_month_from, 'rto': rent_for_month_to,
                             'atr': old_bill.at_the_rate_of, 'tmnth': old_bill.total_months, 'trp': old_bill.total_rupees, 'rdte': old_bill.received_date, 'expm': old_bill.extra_payment,
                             'agdt': old_bill.agreement_date, 'note': old_bill.notes})
    else:
        try:
            house_obj = HouseNumber.objects.get(
                house_number=request.POST['house_num'])
            room_num_obj = RoomNumber.objects.get(
                house=house_obj, room_number=request.POST['room'])
            get_cts = room_num_obj.cts.cts_number
            old_ta = TenantAttributes.objects.filter(
                room=room_num_obj, tenant_name=request.POST['name']).order_by('-id')[0]

            return JsonResponse({'tmn': old_ta.tenant_mobile_number, 'cts': get_cts, 'tdod': old_ta.tenant_dod})
        except Exception as e:
            print('CTS Data Fetch Failed!!', str(e))


def bill_crud_operation(request):
    print('asdfasdfasdf')
    pass
