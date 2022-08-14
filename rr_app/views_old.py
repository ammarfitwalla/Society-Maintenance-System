from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from rr_app.models import *
import pandas as pd
from django.contrib import messages


def home(request):
    return render(request, 'home.html')


def master(request):
    all_tenant_db_data = TenantAttributes.objects.all().values()
    inserted = False
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

                                  '<a href=' + '"' + '/crud_operation/' + str(tenant_data['id']) +
                                  '"class="btn btn-info btn-sm"><span class="glyphicon glyphicon-edit"></span> Edit</a>'])


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
    }
    if inserted:
        return redirect('/master/')

    return render(request, 'master.html', context)


def crud_operation(request, tenant_id):
    all_tenant_db_data = TenantAttributes.objects.filter(id=tenant_id).values()[0]
    room_number = (RoomNumber.objects.filter(id=all_tenant_db_data['room_id']).values())[0]
    cts_number = (CTSNumber.objects.filter(id=room_number['cts_id']).values())[0]
    house_number = (HouseNumber.objects.filter(id=cts_number['house_id']).values())[0]

    tenant_mobile_number = all_tenant_db_data['tenant_mobile_number']
    if tenant_mobile_number is None:
        tenant_mobile_number = ''

    room_number_id = all_tenant_db_data['room_id']

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
               'house_number': house_number['house_number']}

    return render(request, 'crud_operation.html', context)
