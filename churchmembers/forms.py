from django import forms
from django.forms.models import inlineformset_factory, formset_factory, modelform_factory, BaseInlineFormSet
from django.forms.formsets import BaseFormSet
from django.forms import ModelForm
from churchmembers.models import Family, Member, Contact, Person
from localflavor.us.forms import USZipCodeField


class FamilyForm(ModelForm):
    class Meta:
        model = Family
        fields = ('name', 'photo',)


class PersonForm(ModelForm):
    class Meta:
        model = Person
        exclude = ['user', 'notes', 'status']

    def clean(self):
        head_of_household = self.cleaned_data['head_of_household']
        family = self.cleaned_data['family']
        if head_of_household is True and family is not None:
            existing_head = family.head_of_household
            if existing_head and (self.instance.pk is None or (self.instance.pk and self.instance != existing_head)):
                existing_head.head_of_household = False
                existing_head.save()
        return self.cleaned_data


class ContactForm(ModelForm):
    zip_code = USZipCodeField()
    class Meta:
        model = Contact


class PartialMemberForm(ModelForm):
    class Meta:
        model = Member
        exclude = ['person']

#FamilyContactFormSet = inlineformset_factory(Family, Contact)
#PersonContactFormSet = inlineformset_factory(Person, Contact)
MemberForm = modelform_factory(Member, form=PartialMemberForm)
