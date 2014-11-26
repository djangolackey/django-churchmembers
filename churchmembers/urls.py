from django.conf.urls import *
from churchmembers.models import Family
from churchmembers.views import PersonDetail, PersonList
from django.views.generic import ListView, DetailView

urlpatterns = patterns('churchmembers.views',
    url(r'^update/$',
        view='family_info_form',
        name='membership_family_edit',
       ),
    url(r'^edit/(?P<username>[-\w]+)$',
         view='person_edit',
         name='membership_person_edit',
       ),
)

urlpatterns += patterns('',
    (r'^(members|friends)/(?P<username>[-\w]+)/$', PersonDetail.as_view()),
    (r'^(members|friends)/$', PersonList.as_view()),
    (r'^$', ListView.as_view(
        model=Family,
        context_object_name="family_list",
        queryset=Family.objects.all().exclude(status=0).order_by('name', 'slug'),
        template_name="family_list.html"
    )),
    (r'^(?P<slug>[-\w]+)/$', DetailView.as_view(
        model=Family,
        context_object_name="family",
        queryset=Family.objects.all().exclude(status=0).order_by('name', 'slug'),
        template_name="family_detail.html"
    )),
)
