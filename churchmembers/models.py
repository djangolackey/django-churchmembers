from django.db import models
from django.db.models import permalink
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group
from localflavor.us.models import PhoneNumberField, USStateField
from autoslug import AutoSlugField


class Person(models.Model):
    """Person model"""
    STATUS_CHOICES = (
        (0, 'Removed'),
        (1, 'Member'),
        (2, 'Friend'),
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True)
    status = models.IntegerField(_('status'), choices=STATUS_CHOICES, default=2)
    family = models.ForeignKey('churchmembers.Family', blank=True, null=True, limit_choices_to={'status':1})
    head_of_household = models.BooleanField(_('Head of Household'), default=False, 
                                            help_text=_("Check if user is the family's head of household. There can only be one."))
    contact = models.ForeignKey('churchmembers.Contact', blank=True, null=True)
    notes = models.TextField(blank=True, help_text=_("Notes should not be made public"))
    photo = models.FileField(upload_to='member_photos', blank=True, help_text=_('An image that will be used as a thumbnail.'))

    class Meta:
        unique_together = (("family", "head_of_household"),)

    def __unicode__(self):
        if self.status == 1:
            return '{0} membership information'.format(self.user.get_full_name())
        else:
            return '{0} information'.format(self.user.get_full_name())

    @permalink
    def get_absolute_url(self):
        return ('profile_detail', None, {'username': self.user.username})

    @property
    def primary_contact(self):
        if self.contact is not None and self.contact.primary is True:
            return self.contact
        elif self.family is not None and self.family.contact is not None:
            return self.family.contact
        else:
            return ''


class Family(models.Model):
    """Family model"""
    STATUS_CHOICES = (
        (0, 'Inactive'),
        (1, 'Active'),
    )
    name = models.CharField(max_length=256)
    slug = AutoSlugField(populate_from='name', unique=True)
    contact = models.ForeignKey('churchmembers.Contact', blank=True, null=True)
    status = models.IntegerField(_('status'), choices=STATUS_CHOICES, default=1)
    notes = models.TextField(blank=True)
    photo = models.FileField(upload_to='family_photos', blank=True, 
                             help_text=_('An image that will be used as a thumbnail.'))

    class Meta:
        verbose_name_plural = 'families'

    def __unicode__(self):
        return '{0} family'.format(self.name)

    @property
    def head_of_household(self):
        try:
            head_of_household = self.person_set.get('head_of_household' is True)
        except self.DoesNotExist:
            head_of_household = ''
        return head_of_household

    @permalink
    def get_absolute_url(self):
        return ('family_detail', None, {'slug': self.slug})


class Member(models.Model):
    """Member model"""
    METHOD_CHOICES = (
        (1, 'Baptism'),
        (2, 'Letter'),
        (3, 'Other'),
    )
    person = models.OneToOneField(Person, primary_key=True)
    date_joined = models.DateField(blank=True, null=True)
    method = models.IntegerField(_('method'), choices=METHOD_CHOICES, default=1, 
                                 help_text=_("How was membership confirmed"))
    lettering_church = models.CharField(_('Church Name'), blank=True, null=True, max_length=320, 
                                        help_text=_("If method was by letter, please provide the name of the church supplying letter"))
    date_baptised = models.DateField(blank=True, null=True)
    conversion_story = models.TextField(blank=True, null=True)

    class Meta:
        permissions = (
              ("view_data", "Can view member data"),
        )


class Contact(models.Model):
    """Contact information model"""
    address = models.CharField(max_length=256, blank=True)
    city = models.CharField(max_length=128, blank=True)
    state = USStateField(blank=True, default='TX')
    zip_code = models.CharField(_('zip'), max_length=10, blank=True)
    mobile = PhoneNumberField(_('mobile phone'), blank=True)
    home_phone = PhoneNumberField(_('home phone'), blank=True)
    email = models.EmailField(_('public email'), max_length=254, blank=True)
    website = models.URLField(max_length=256, blank=True)
    primary = models.BooleanField(help_text=_('Primary contact information'), default=False)

    def __unicode__(self):
        return '{0}, {1}, {2}  {3}'.format(self.address, self.city, self.state, self.zip)


class Office(models.Model):
    """Office model"""
    STATUS_CHOICES = (
        (0, 'Inactive'),
        (1, 'Active'),
    )
    title = models.CharField(max_length=256)
    slug = AutoSlugField(populate_from='title', unique=True)
    status = models.IntegerField(_('status'), choices=STATUS_CHOICES, default=1)
    office_responsibilities = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    members = models.ManyToManyField(Person, through='churchmembers.OfficeHolder')

    def __unicode__(self):
        return '{0}'.format(self.title)

    @permalink
    def get_absolute_url(self):
        return ('office_detail', None, {'slug': self.slug})


class OfficeHolder(models.Model):
    """OfficeHolders model with is through model for Office"""
    office = models.ForeignKey(Office)
    person = models.ForeignKey(Person)
    official_photo = models.FileField(upload_to='officer_photos', blank=True, 
                                      help_text=_('An image that will be used as a thumbnail.'))
    start_date = models.DateField(blank=True, null=True)
    ordained = models.BooleanField(help_text=_("Was an Ordaination performed for this office"), default=False)

    def __unicode__(self):
        return '{0}, {1}'.format(self.person.user.get_full_name(), self.office.title)
