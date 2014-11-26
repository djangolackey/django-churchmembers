from django.contrib import admin
from churchmembers.models import *
from churchmembers.forms import ContactForm


class MemberInline(admin.StackedInline):
    model = Member
    max_num = 1
    can_delete = False


class OfficeHolderInline(admin.StackedInline):
    model = OfficeHolder


class PersonAdmin(admin.ModelAdmin):
    model = Person
    inlines = (MemberInline,)


class FamilyAdmin(admin.ModelAdmin):
    model = Family


class ContactAdmin(admin.ModelAdmin):
    model = Contact
    form = ContactForm

class OfficeAdmin(admin.ModelAdmin):
    inlines = (OfficeHolderInline, )

admin.site.register(Person, PersonAdmin)
admin.site.register(Family, FamilyAdmin)
admin.site.register(Office, OfficeAdmin)
admin.site.register(Contact, ContactAdmin)
