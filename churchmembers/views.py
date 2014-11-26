from churchmembers.models import Family, Person 
from churchmembers.forms import *
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView, ListView
from django.conf import settings


User = settings.AUTH_USER_MODEL


@login_required
def family_info_form(request):
    user = request.user
    try:
        person = Person.objects.get(user=user)
    except Person.DoesNotExist:
        person = Person.objects.create(user=user, status=2)
    try:
        family = Family.objects.get(person=user, status=1)
    except Family.DoesNotExist:
        family = Family.objects.create(name=user.last_name)
        person.family = family
        person.save()

    if request.method == "POST":
        family_form = FamilyForm(request.POST, instance=family)
        family_contact_formset = FamilyContactFormSet(request.POST, instance=family)
        user_formset = NewUserFormSet(request.POST)
        if family_form.is_valid() and family_contact_formset.is_valid() and user_formset.is_valid():
            family_form.save()
            family_contact_formset.save()
            new_user = user_formset.save(family)
            return HttpResponseRedirect(reverse('churchmembers_family_detail', args=(family.slug, )))
    else:
        family_form = FamilyForm(instance=family)
        user_formset = NewUserFormSet()
        family_contact_formset = FamilyContactFormSet(instance=family)
    t = 'churchmembers/update_family_info.html'
    c = {
         'family_form': family_form,
         'user_formset': user_formset,
         'contact_formset': family_contact_formset,
         'family': family,
         'id' : request.user.id,
        }
    return render_to_response(t, c, context_instance=RequestContext(request))

@login_required
def person_edit(request, username, template_name='churchmembers/profile_form.html'):
    """Edit churchmember Person profile."""
    
    user = get_object_or_404(User, username=username)
    if user != request.user: 
        if user.person.family != request.user.person.family:
            raise Http404 

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        person_form = PersonForm(request.POST, request.FILES, instance=user.person)
        member_form = MemberForm(request.POST, instance=user.person)

        if user_form.is_valid() and person_form.is_valid() and member_form.is_valid():
            user_form.save()
            person_form.save()
            member_form.save()
            return HttpResponseRedirect(reverse('profile_detail', kwargs={'username': user.username}))
        else:
            context = {
                'object': user.person,
                'user_form': user_form,
                'person_form': person_form,
                'member_form': member_form,
            }
    else:
        try:
            person = Person.objects.get(user=user)
        except Person.DoesNotExist:
            person = Person.objects.create(user=user, status=2)
        context = {
            'object': person, 
            'user_form': UserForm(instance=user),
            'person_form': PersonForm(instance=person),
            'member_form': MemberForm(instance=person),
        }
    return render_to_response(template_name, context, context_instance=RequestContext(request))


    (r'^(?P<slug>[-\w]+)/$', DetailView.as_view(
        model=Family,
        
        queryset=Family.objects.all().exclude(status=0)
        
    )),


class PersonDetail(DetailView):

    context_object_name = "person",
    template_name = "person_detail.html"
    model = Person

    def get_object(self):
        if self.args[0] == 'members':
            return get_object_or_404(Person, status='member', user__username__iexact=self.args[1])
        else:
            return get_object_or_404(Person, status='friend', user__username__iexact=self.args[1])


class PersonList(ListView):

    context_object_name = "person_list",
    template_name = "person_list.html"
    model = Person

    def get_queryset(self):
        if self.args[0] == 'members':
            return Person.objects.filter(status='member')
        else:
            return Person.objects.filter(status='friend')

    def get_context_data(self, **kwargs):
        context = super(PersonList, self).get_context_data(**kwargs)
        context['type'] = self.args[0]
        return context
