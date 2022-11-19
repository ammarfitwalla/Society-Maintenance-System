from django.db import models


# Create your models here.

# class BaseModel(models.Model):
#     objects = models.Manager()
#
#     class Meta:
#         abstract = True


class HouseNumber(models.Model):
    house_number = models.CharField(max_length=255, blank=False)

    def __str__(self):
        return str(self.house_number)


class CTSNumber(models.Model):
    house = models.ForeignKey(HouseNumber, on_delete=models.CASCADE)
    cts_number = models.CharField(max_length=255, blank=False)

    def __str__(self):
        return str(self.cts_number)


class RoomNumber(models.Model):
    house = models.ForeignKey(HouseNumber, on_delete=models.CASCADE)
    cts = models.ForeignKey(CTSNumber, on_delete=models.CASCADE)
    room_number = models.CharField(max_length=255, blank=False)

    def __str__(self):
        return str(self.room_number)


class TenantAttributes(models.Model):
    room = models.OneToOneField(RoomNumber, on_delete=models.CASCADE)
    tenant_name = models.CharField(max_length=255, null=False)
    tenant_permanent_address = models.CharField(max_length=1024, null=False)
    tenant_mobile_number = models.IntegerField(null=True, blank=True)
    tenant_dod = models.DateField(null=True, blank=True)
    tenant_gender = models.CharField(max_length=255, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.tenant_name)


class Bill(models.Model):
    house_number = models.CharField(max_length=255, blank=False)
    cts_number = models.CharField(max_length=255, blank=False)
    room_number = models.CharField(max_length=255, blank=False)
    tenant_name = models.CharField(max_length=255, null=False)
    tenant_permanent_address = models.CharField(max_length=1024, null=False)
    tenant_mobile_number = models.IntegerField(null=True, blank=True)
    tenant_dod = models.DateField(null=True, blank=True)
    tenant_gender = models.CharField(max_length=255, null=False)
    bill_for_month_of = models.CharField(max_length=20)
    book_number = models.IntegerField(null=True, blank=True)
    bill_number = models.IntegerField(null=True, blank=True)
    purpose_for = models.CharField(max_length=510)
    rent_from = models.CharField(max_length=20)
    rent_to = models.CharField(max_length=20)
    at_the_rate_of = models.IntegerField(null=True, blank=True)
    total_months = models.IntegerField(null=True, blank=True)
    total_rupees = models.IntegerField(null=True, blank=True)
    received_date = models.DateField(null=True, blank=True)
    extra_payment = models.IntegerField(null=True, blank=True)
    agreement_date = models.DateField(blank=True, null=True)
    notes = models.CharField(max_length=1020, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.bill_number)
