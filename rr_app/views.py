import re
import os
import cv2
import json
import locale
import calendar
import win32print
import subprocess
import ghostscript
import numpy as np
import pandas as pd
from PIL import Image
from rr_app.models import *
from win32 import win32print
from datetime import datetime
from django.db.models import Sum
from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.http import JsonResponse
from rr_project.settings import MEDIA_ROOT
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import cache_control
from django.contrib.humanize.templatetags.humanize import ordinal

default_printer = win32print.GetDefaultPrinter()


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

        if request.session['master_crud'] == 'Edit':
            all_tenant_db_data = TenantAttributes.objects.filter(id=request.session['tenant_id']).values()[0]
            room_number = (RoomNumber.objects.filter(id=all_tenant_db_data['room_id']).values())[0]
            room_number_id = all_tenant_db_data['room_id']
            if room_number['room_number'] != get_room_number and RoomNumber.objects.filter(house=get_house_number_id, room_number=get_room_number).exists():
                messages.error(request, 'Entered Room Number already exist for different tenant !')
                return redirect('/master/')
            else:
                insert_room_number = RoomNumber(id=room_number_id, house=get_house_number_id, cts=get_cts_number_id, room_number=get_room_number)
                insert_room_number.save()
                get_room_number_id = RoomNumber.objects.get(id=room_number_id)

            # TODO: Need to update "House number" and "CTS Number" as like "Room Number"

            insert_tenant_attributes = TenantAttributes(id=request.session['tenant_id'], room=get_room_number_id, tenant_name=get_tenant_name, tenant_permanent_address=get_permanent_address, tenant_mobile_number=get_tenant_mobile_number, tenant_dod=get_tenant_dod, tenant_gender=get_tenant_gender)
            insert_tenant_attributes.save(update_fields=['room', 'tenant_name', 'tenant_permanent_address', 'tenant_mobile_number', 'tenant_dod', 'tenant_gender'])
            messages.success(request, "Tenant '" + get_tenant_name + "' Updated Successfully!")
        else:
            if RoomNumber.objects.filter(house=get_house_number_id, room_number=get_room_number).exists():
                messages.error(request, 'Entered Room Number already exist for different tenant !!!')
                return redirect('/master/')
            else:
                insert_room_number = RoomNumber(house=get_house_number_id, cts=get_cts_number_id, room_number=get_room_number)
                insert_room_number.save()
                get_room_number_id = RoomNumber.objects.last()

            insert_tenant_attributes = TenantAttributes(room=get_room_number_id, tenant_name=get_tenant_name, tenant_permanent_address=get_permanent_address, tenant_mobile_number=get_tenant_mobile_number, tenant_dod=get_tenant_dod, tenant_gender=get_tenant_gender)
            insert_tenant_attributes.save()
            last_tenant_db_data = TenantAttributes.objects.last()
            master_values.append([last_tenant_db_data.id, get_house_number, get_room_number, get_cts_number, get_tenant_name, get_tenant_dod, get_tenant_gender, get_tenant_mobile_number, get_permanent_address])
            messages.success(request, "New Tenant '" + get_tenant_name + "' Added Successfully!")
        return redirect('/master/')

    request.session['master_crud'] = 'Add'
    request.session['tenant_id'] = 'new'
    all_tenant_db_data = TenantAttributes.objects.all().values()
    temp = list(HouseNumber.objects.all().values_list('house_number', flat=True))
    """
    fetching records from db, inserting into DataFrame and displaying on Master page.
    """
    if all_tenant_db_data:
        for tenant_data in all_tenant_db_data:
            all_room_number = (RoomNumber.objects.filter(id=tenant_data['room_id']).values())[0]
            all_cts_number = (CTSNumber.objects.filter(id=all_room_number['cts_id']).values())[0]
            all_house_number = (HouseNumber.objects.filter(id=all_cts_number['house_id']).values())[0]

            if tenant_data['tenant_dod'] is not None:
                tenant_dod = tenant_data['tenant_dod'].strftime("%d-%m-%Y")
            else:
                tenant_dod = None
            master_values.append([all_house_number['house_number'], all_room_number['room_number'], all_cts_number['cts_number'], tenant_data['tenant_name'], tenant_dod, tenant_data['tenant_gender'], str(tenant_data['tenant_mobile_number']), tenant_data['tenant_permanent_address'], '<a href=' + '"' + 'javascript:updateMaster(' + str(tenant_data['id']) + ');">Edit</a>'])

    """
    -> Fetching user input data from master form page, 
    -> checking room number duplication, 
    -> inserting into db.
    """

    master_df = pd.DataFrame(master_values, columns=['House No.', 'Room No.', 'CTS No.', 'Tenant Name', 'DOD', 'Gender', 'Mobile No.', 'Notes', 'Edit'])
    master_df = master_df.sort_values(['House No.', 'Room No.'])
    master_df = master_df.reset_index(drop=True)
    master_df.index += 1
    master_df = master_df.to_html(index_names=False, classes="table table-bordered table-sm table-responsive-sm table-hover", escape=False, render_links=True, table_id="masterTable")

    context = {'master_df': master_df, 'temp': temp}
    return render(request, 'master.html', context)


def crud_operation(request):
    try:
        request.session['tenant_id'] = request.POST['t_id']
        request.session['master_crud'] = 'Edit'
        all_tenant_db_data = TenantAttributes.objects.filter(id=request.session['tenant_id']).values()[0]
        room_number = (RoomNumber.objects.filter(id=all_tenant_db_data['room_id']).values())[0]
        cts_number = (CTSNumber.objects.filter(id=room_number['cts_id']).values())[0]
        house_number = (HouseNumber.objects.filter(id=cts_number['house_id']).values())[0]
        temp = list(HouseNumber.objects.all().values_list('house_number', flat=True))
        tenant_mobile_number = all_tenant_db_data['tenant_mobile_number']
        if tenant_mobile_number is None:
            tenant_mobile_number = ''
        return JsonResponse({'tenant_name': all_tenant_db_data['tenant_name'], 'tenant_permanent_address': all_tenant_db_data['tenant_permanent_address'], 'tenant_mobile_number': tenant_mobile_number, 'tenant_dod': str(all_tenant_db_data['tenant_dod']), 'tenant_gender': all_tenant_db_data['tenant_gender'], 'room_number': room_number['room_number'], 'cts_number': cts_number['cts_number'], 'house_number': house_number['house_number'], 'temp': temp})
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

        rent_for_month_from_long = num_date_to_string(rent_for_month_from, short_form=False)
        rent_for_month_to_long = num_date_to_string(rent_for_month_to, short_form=False)
        bill_for_month_of_short = num_date_to_string(bill_for_month_of)
        rent_for_month_from_short = num_date_to_string(rent_for_month_from)
        rent_for_month_to_short = num_date_to_string(rent_for_month_to)

        # get_house_id = HouseNumber.objects.get(house_number=bill_house_number)
        # get_cts_id = CTSNumber.objects.get(house=get_house_id.id, cts_number=bill_cts_number)

        get_house_id = get_object_or_404(HouseNumber, house_number=bill_house_number)
        print("----------------")
        print(bill_house_number, get_house_id)
        print("----------------")
        get_cts_id = get_object_or_404(CTSNumber, house=get_house_id.id, cts_number=bill_cts_number)
        get_room_number_id = RoomNumber.objects.filter(room_number=bill_room_number, house=get_house_id.id, cts=get_cts_id.id).values()[0]
        get_tenant_attrs = (TenantAttributes.objects.filter(room=get_room_number_id['id']).values())[0]

        if request.session['bill_crud'] == 'Edit':
            Bill.objects.filter(id=request.session['bill_id']).update(house_number=bill_house_number, cts_number=bill_cts_number, room_number=bill_room_number, tenant_name=get_tenant_attrs['tenant_name'], tenant_permanent_address=get_tenant_attrs['tenant_permanent_address'], tenant_mobile_number=get_tenant_attrs['tenant_mobile_number'], tenant_dod=get_tenant_attrs['tenant_dod'], tenant_gender=get_tenant_attrs['tenant_gender'], bill_for_month_of=bill_for_month_of_short, book_number=bill_book_number, bill_number=bill_number, purpose_for=purpose_for, rent_from=rent_for_month_from_short, rent_to=rent_for_month_to_short, at_the_rate_of=at_the_rate_of, total_months=total_months, total_rupees=total_rupees, received_date=received_date, extra_payment=extra_payment, agreement_date=agreement_date, notes=notes)
            if print_button and print_button != "":
                # TODO: check if data is present in db, if not, ask user to save first
                bill_house_number_dir = re.sub('[^A-Za-z0-9]+', '_', str(bill_house_number))
                bill_cts_number_dir = re.sub('[^A-Za-z0-9]+', '_', str(bill_cts_number))
                bill_room_number_dir = re.sub('[^A-Za-z0-9]+', '_', str(bill_room_number))
                tenant_name_dir = re.sub('[^A-Za-z0-9]+', '_', str(get_tenant_attrs['tenant_name']))

                check_dir_exists(os.path.join(MEDIA_ROOT, bill_house_number_dir))
                check_dir_exists(os.path.join(MEDIA_ROOT, bill_house_number_dir, bill_cts_number_dir))
                check_dir_exists(os.path.join(MEDIA_ROOT, bill_house_number_dir, bill_cts_number_dir, bill_room_number_dir))
                check_dir_exists(os.path.join(MEDIA_ROOT, bill_house_number_dir, bill_cts_number_dir, bill_room_number_dir, tenant_name_dir))

                today = datetime.today()
                day = '{:02d}'.format(today.day)
                ordinal_ = str(ordinal(day))[2:]
                month = today.strftime("%b")
                year = '{:02d}'.format(today.year)

                for i in range(2):
                    if i == 0:
                        image = os.path.join(MEDIA_ROOT, 'bill_sample', 'rr_bill.jpg')
                        img_arr = cv2.imread(image)
                    else:
                        img_arr = np.zeros([2561, 1763, 3], dtype=np.uint8)
                        img_arr.fill(255)

                    img_arr = cv2.putText(img_arr, bill_for_month_of_short, (600, 830), cv2.FONT_HERSHEY_TRIPLEX, 1.6, (0, 0, 0), 2)  # bill for month of
                    img_arr = cv2.putText(img_arr, bill_book_number, (1127, 830), cv2.FONT_HERSHEY_TRIPLEX, 1.6, (0, 0, 0), 2)  # book number
                    img_arr = cv2.putText(img_arr, bill_number, (1414, 830), cv2.FONT_HERSHEY_TRIPLEX, 1.6, (0, 0, 0), 2)  # bill number
                    img_arr = cv2.putText(img_arr, "For residence", (235, 940), cv2.FONT_HERSHEY_TRIPLEX, 1.6, (0, 0, 0), 2)  # for residence
                    img_arr = cv2.putText(img_arr, bill_cts_number, (1127, 935), cv2.FONT_HERSHEY_TRIPLEX, 1.6, (0, 0, 0), 2)  # cts number
                    img_arr = cv2.putText(img_arr, bill_room_number, (600, 1050), cv2.FONT_HERSHEY_TRIPLEX, 1.6, (0, 0, 0), 2)  # room number
                    img_arr = cv2.putText(img_arr, bill_house_number, (1127, 1050), cv2.FONT_HERSHEY_TRIPLEX, 1.6, (0, 0, 0), 2)  # house number
                    img_arr = cv2.putText(img_arr, get_tenant_attrs['tenant_name'], (378, 1341), cv2.FONT_HERSHEY_TRIPLEX, 1.5, (0, 0, 0), 2)  # Tenant name
                    img_arr = cv2.putText(img_arr, rent_for_month_from_long + " to " + rent_for_month_to_long, (747, 1455), cv2.FONT_HERSHEY_TRIPLEX, 1.4, (0, 0, 0), 2)  # month from and to
                    img_arr = cv2.putText(img_arr, total_rupees, (1127, 1610), cv2.FONT_HERSHEY_TRIPLEX, 1.6, (0, 0, 0), 2)  # total rupees
                    img_arr = cv2.putText(img_arr, "00.", (1483, 1610), cv2.FONT_HERSHEY_TRIPLEX, 1.6, (0, 0, 0), 2)  # month from and to
                    img_arr = cv2.putText(img_arr, "@", (730, 1540), cv2.FONT_HERSHEY_TRIPLEX, 1.6, (0, 0, 0), 2)  # @
                    img_arr = cv2.putText(img_arr, f"Rs. {at_the_rate_of}/-", (665, 1595), cv2.FONT_HERSHEY_TRIPLEX, 1.2, (0, 0, 0), 2)  # rs
                    img_arr = cv2.putText(img_arr, "per month", (665, 1640), cv2.FONT_HERSHEY_TRIPLEX, 1.2, (0, 0, 0), 2)  # per month
                    img_arr = cv2.putText(img_arr, day, (993, 1850), cv2.FONT_HERSHEY_TRIPLEX, 1.3, (0, 0, 0), 2)  # current date
                    img_arr = cv2.putText(img_arr, ordinal_, (1046, 1828), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 0, 0), 2)  # ordinal
                    img_arr = cv2.putText(img_arr, month, (1260, 1850), cv2.FONT_HERSHEY_TRIPLEX, 1.3, (0, 0, 0), 2)  # current month
                    img_arr = cv2.putText(img_arr, year, (1493, 1850), cv2.FONT_HERSHEY_TRIPLEX, 1.3, (0, 0, 0), 2)  # current year
                    img_arr = cv2.resize(img_arr, (1748, 2480))
                    im = cv2.cvtColor(img_arr, cv2.COLOR_BGR2RGB)
                    im = Image.fromarray(im)
                    a5im = Image.new('RGB', (1748, 2480), (255, 255, 255))
                    a5im.paste(im, im.getbbox())

                    if i == 0:
                        pdf_name = os.path.join(MEDIA_ROOT, bill_house_number_dir, bill_cts_number_dir, bill_room_number_dir, tenant_name_dir, rent_for_month_from_long + "-to-" + rent_for_month_to_long + ".pdf")
                        a5im.save(pdf_name, 'PDF', quality=100)
                    else:
                        pdf_name = os.path.join(MEDIA_ROOT, bill_house_number_dir, bill_cts_number_dir, bill_room_number_dir, tenant_name_dir, rent_for_month_from_long + "-to-" + rent_for_month_to_long + "_blank.pdf")
                        a5im.save(pdf_name, 'PDF', quality=100)
                        # subprocess.Popen([pdf_name], shell=True)  # Uncomment to open the pdf automatically
                        try:
                            args = ["-dPrinted", "-dBATCH", "-dNOSAFER", "-dNOPAUSE", "-dNOPROMPT"
                                                                                      "-q", "-dNumCopies#1", "-sDEVICE#mswinpr2", f'-sOutputFile#"%printer%{default_printer}"', f'"{pdf_name}"']
                            encoding = locale.getpreferredencoding()
                            args = [a.encode(encoding) for a in args]
                            ghostscript.Ghostscript(*args)
                        except:
                            pass
                messages.success(request, "Bill '" + bill_number + "' Printed & Updated Successfully!")
            else:
                messages.success(request, "Bill '" + bill_number + "' Updated Successfully!")
        else:
            # TODO: Check if data is present in db, if present, return message saying data already exists
            print("bill_room_number", bill_room_number)
            print("tenant details", get_tenant_attrs['tenant_name'])
            save_bill_details = Bill(house_number=bill_house_number, cts_number=bill_cts_number, room_number=bill_room_number, tenant_name=get_tenant_attrs['tenant_name'], tenant_permanent_address=get_tenant_attrs['tenant_permanent_address'], tenant_mobile_number=get_tenant_attrs['tenant_mobile_number'], tenant_dod=get_tenant_attrs['tenant_dod'], tenant_gender=get_tenant_attrs['tenant_gender'], bill_for_month_of=bill_for_month_of_short, book_number=bill_book_number, bill_number=bill_number, purpose_for=purpose_for, rent_from=rent_for_month_from_short, rent_to=rent_for_month_to_short, at_the_rate_of=at_the_rate_of, total_months=total_months, total_rupees=total_rupees, received_date=received_date, extra_payment=extra_payment, agreement_date=agreement_date, notes=notes)
            save_bill_details.save()
            messages.success(request, "New Bill '" + bill_number + "' Added Successfully!")
        return redirect('/tenant_bill/')

    request.session['bill_crud'] = 'Add'
    request.session['bill_id'] = 'new'
    all_bill_data = Bill.objects.all().order_by('-id')
    house_ = list(HouseNumber.objects.all().values_list('house_number', flat=True))
    if all_bill_data:
        last_bill_number = 1 if int(all_bill_data.last().bill_number) == 100 else int(all_bill_data.last().bill_number) + 1
        last_book_number = int(all_bill_data.last().book_number) + 1 if last_bill_number == 1 else all_bill_data.last().book_number
    else:
        last_bill_number = 1
        last_book_number = 1
    context = {'house_': house_, 'all_bill_data': all_bill_data, 'last_book_number': last_book_number, 'last_bill_number': last_bill_number}
    return render(request, 'tenant_bill.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def tenant_bill_crud(request):
    try:
        request.session['bill_id'] = request.POST['bill_id']
        request.session['bill_crud'] = 'Edit'
        filtered_one_bill_data = Bill.objects.filter(id=request.session['bill_id']).all()[0]
        bill_for_month_of = month_name_to_int(filtered_one_bill_data.bill_for_month_of)
        rent_for_month_from = month_name_to_int(filtered_one_bill_data.rent_from)
        rent_for_month_to = month_name_to_int(filtered_one_bill_data.rent_to)
        return JsonResponse(
            {'house_number': filtered_one_bill_data.house_number, 'cts_number': filtered_one_bill_data.cts_number, 'room_number': filtered_one_bill_data.room_number, 'tenant_name': filtered_one_bill_data.tenant_name, 'tenant_permanent_address': filtered_one_bill_data.tenant_permanent_address, 'tenant_mobile_number': filtered_one_bill_data.tenant_mobile_number, 'tenant_dod': filtered_one_bill_data.tenant_dod, 'tenant_gender': filtered_one_bill_data.tenant_gender, 'bill_for_month_of': bill_for_month_of, 'book_number': filtered_one_bill_data.book_number, 'bill_number': filtered_one_bill_data.bill_number, 'purpose_for': filtered_one_bill_data.purpose_for, 'rent_from': rent_for_month_from, 'rent_to': rent_for_month_to, 'at_the_rate_of': filtered_one_bill_data.at_the_rate_of, 'total_months': filtered_one_bill_data.total_months, 'total_rupees': filtered_one_bill_data.total_rupees, 'received_date': filtered_one_bill_data.received_date, 'extra_payment': filtered_one_bill_data.extra_payment,
             'agreement_date': filtered_one_bill_data.agreement_date, 'notes': filtered_one_bill_data.notes, })
    except Exception as e:
        print('Edit Data Fetch Failed!! -> Error: ', str(e))


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def name_room_list(request):
    get_house = HouseNumber.objects.filter(house_number=request.POST['h_num'])[0]
    all_room_number = RoomNumber.objects.filter(house=get_house)
    all_tenant_number = TenantAttributes.objects.all()
    tname_room = [t.tenant_name + '---' + t.room.room_number for t in all_tenant_number if t.room in all_room_number]
    return JsonResponse({'tname_room': tname_room})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def room_cts_list(request):
    get_house = HouseNumber.objects.filter(house_number=request.POST['house_val'])[0]
    all_room_num = list(RoomNumber.objects.filter(house=get_house).order_by('room_number').values_list('room_number', flat=True).distinct())
    all_cts_num = list(CTSNumber.objects.filter(house=get_house).order_by('cts_number').values_list('cts_number', flat=True).distinct())

    return JsonResponse({'all_room_num': all_room_num, 'all_cts_num': all_cts_num, })


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def get_old_bill(request):
    # all_bill_data = Bill.objects.all()
    # if all_bill_data:
    #     last_bill_number = 1 if int(all_bill_data.last().bill_number) == 100 else int(all_bill_data.last().bill_number) + 1
    #     last_book_number = int(all_bill_data.last().book_number) + 1 if last_bill_number == 1 else all_bill_data.last().book_number
    # else:
    #     last_bill_number = 1
    #     last_book_number = 1
    print('=======', request.POST['room'])
    old_bill = Bill.objects.filter(house_number=request.POST['house_num'], room_number=request.POST['room']).order_by('-id')

    if len(old_bill) != 0:
        old_bill = old_bill[0]
        bill_for_month_of = month_name_to_int(old_bill.bill_for_month_of)
        rent_for_month_from = month_name_to_int(old_bill.rent_from)
        rent_for_month_to = month_name_to_int(old_bill.rent_to)
        return JsonResponse({'cts': old_bill.cts_number, 'tmn': old_bill.tenant_mobile_number, 'tdod': old_bill.tenant_dod, 'bfm': bill_for_month_of, 'bkn': old_bill.book_number, 'bln': old_bill.bill_number, 'pf': old_bill.purpose_for, 'rfm': rent_for_month_from, 'rto': rent_for_month_to, 'atr': old_bill.at_the_rate_of, 'tmnth': old_bill.total_months, 'trp': old_bill.total_rupees, 'rdte': old_bill.received_date, 'expm': old_bill.extra_payment, 'agdt': old_bill.agreement_date, 'note': old_bill.notes})
    else:
        try:
            house_obj = HouseNumber.objects.get(house_number=request.POST['house_num'])
            room_num_obj = RoomNumber.objects.get(house=house_obj, room_number=request.POST['room'])
            get_cts = room_num_obj.cts.cts_number
            old_ta = TenantAttributes.objects.filter(room=room_num_obj, tenant_name=request.POST['name']).order_by('-id')[0]
            return JsonResponse({'tmn': old_ta.tenant_mobile_number, 'cts': get_cts, 'tdod': old_ta.tenant_dod})
        except Exception as e:
            print('CTS Data Fetch Failed!!', str(e))


def bill_crud_operation(request):
    print('asdfasdfasdf')
    pass


def report_page(request):
    house_obj = Bill.objects.all().order_by().values_list('house_number', flat=True).distinct()
    if request.method == 'POST':
        if not house_obj:
            messages.error(request, 'No Data Available.')
            return redirect('/report_page/')
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        house_number = request.POST['house']
        cts_number = request.POST.get('cts')
        room_number = request.POST.get('room')
        tenant_name = request.POST.get('tenant_name')

        if house_number and room_number and tenant_name:
            filtered_bill_data = Bill.objects.filter(received_date__range=(from_date, to_date), house_number=house_number, room_number=room_number, tenant_name=tenant_name)
        elif house_number and room_number:
            filtered_bill_data = Bill.objects.filter(received_date__range=(from_date, to_date), house_number=house_number, room_number=room_number)
        elif house_number:
            filtered_bill_data = Bill.objects.filter(received_date__range=(from_date, to_date), house_number=house_number)
        else:
            filtered_bill_data = Bill.objects.all()

        total_tenants = filtered_bill_data.count()
        if total_tenants:
            total_months = filtered_bill_data.aggregate(Sum('total_months'))['total_months__sum']
            total_amounts = filtered_bill_data.aggregate(Sum('total_rupees'))['total_rupees__sum']
            total_extra_amounts = filtered_bill_data.aggregate(Sum('extra_payment'))['extra_payment__sum']
            grand_total = int(total_amounts) + int(total_extra_amounts)

            context = {'house_obj': house_obj, 'bill_table_data': filtered_bill_data, 'total_tenants': total_tenants, 'total_months': total_months, 'total_amounts': total_amounts, 'total_extra_amounts': total_extra_amounts, 'grand_total': grand_total, 'from_date': from_date, 'to_date': to_date}
            return render(request, 'report_page.html', context)
        else:
            messages.info(request, 'No Data Available.')
            context = {'house_obj': house_obj, 'from_date': from_date, 'to_date': to_date}
            return render(request, 'report_page.html', context)

    # house_obj = HouseNumber.objects.all()
    context = {'house_obj': house_obj}
    return render(request, 'report_page.html', context)


def load_room_numbers(request):
    if request.is_ajax():
        house_number = request.GET.get('house_id')
        room_number = list(Bill.objects.filter(house_number=house_number).order_by().values('room_number').distinct())
        return JsonResponse(json.dumps(room_number), safe=False)


def load_cts_numbers(request):
    if request.is_ajax():
        room_number = request.GET.get('room_id')
        cts_number = list(Bill.objects.filter(room_number=room_number).order_by().values('cts_number').distinct())
        # json_cts_numbers = serializers.serialize('json', cts_number)
        # return JsonResponse(json_cts_numbers, safe=False)
        return JsonResponse(json.dumps(cts_number), safe=False)


def load_tenant_names(request):
    if request.is_ajax():
        room_number = request.GET.get('room_id')
        house_number = request.GET.get('house_id')
        tenant_names = list(Bill.objects.filter(house_number=house_number, room_number=room_number).order_by().values('tenant_name').distinct())
        # json_tenant_names = serializers.serialize('json', tenant_name)
        # return JsonResponse(json_tenant_names, safe=False)
        return JsonResponse(json.dumps(tenant_names), safe=False)
