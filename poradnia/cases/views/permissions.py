from braces.views import FormValidMessageMixin
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.views.generic.edit import FormMixin
from guardian.shortcuts import assign_perm, get_perms
from poradnia.users.forms import (TranslatedManageObjectPermissionForm,
                         TranslatedUserObjectPermissionsForm)
from ..forms import CaseGroupPermissionForm
from ..models import Case


def assign_perm_check(user, case):
    if case.status == case.STATUS.free:
        if not user.has_perm('cases.can_assign'):
            raise PermissionDenied
    else:
        case.perm_check(user, 'can_manage_permission')
    return True


class UserPermissionCreateView(FormView):
    form_class = TranslatedManageObjectPermissionForm
    template_name = 'cases/case_form_permission_add.html'

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(UserPermissionCreateView, self).get_form_kwargs(*args, **kwargs)
        self.case = get_object_or_404(Case, pk=self.kwargs['pk'])
        assign_perm_check(self.request.user, self.case)
        kwargs.update({'obj': self.case, 'actor': self.request.user})
        return kwargs

    def form_valid(self, form):
        form.save_obj_perms()
        for user in form.cleaned_data['users']:
            self.case.send_notification(actor=self.request.user, staff=True, verb='granted')
            messages.success(self.request,
                             _("Success granted permission of %(user)s to %(case)s").
                             format(user=user, case=self.case))
        self.case.status_update()
        return super(UserPermissionCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('cases:detail', kwargs={'pk': str(self.case.pk)})

    def get_context_data(self, **kwargs):
        context = super(UserPermissionCreateView, self).get_context_data(**kwargs)
        context['object'] = self.case
        return context


class UserPermissionUpdateView(FormValidMessageMixin, FormView):
    form_class = TranslatedUserObjectPermissionsForm
    template_name = 'cases/case_form_permission_update.html'

    def get_form_kwargs(self):
        kwargs = super(UserPermissionUpdateView, self).get_form_kwargs()
        self.case = get_object_or_404(Case, pk=self.kwargs['pk'])
        assign_perm_check(self.request.user, self.case)
        self.action_user = get_object_or_404(get_user_model(), username=self.kwargs['username'])
        kwargs.update({'user': self.action_user,
                       'obj': self.case})
        del kwargs['initial']
        return kwargs

    def get_obj_perms_field_initial(self, *args, **kwargs):
        return get_perms(self.action_user, self.case)

    def get_context_data(self, **kwargs):
        context = super(UserPermissionUpdateView, self).get_context_data(**kwargs)
        context['object'] = self.case
        context['action_user'] = self.action_user
        return context

    def form_valid(self, form):
        form.save_obj_perms()
        return super(UserPermissionUpdateView, self).form_valid(form)

    def get_form_valid_message(self):
        return _("Updated permission %(user)s to %(case)s!") %\
            ({'user': self.action_user, 'case': self.case})

    def get_success_url(self):
        return reverse('cases:detail', kwargs={'pk': str(self.case.pk)})

    def test_view_loads_correctly(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.object.name)

    def test_invalid_user_used(self):
        resp = self.client.post(self.url, data={'permissions': ['can_view', ],
                                                'user': self.user_with_permission.pk})
        self.assertEqual(resp.status_code, 200)

    def test_valid_user_used(self):
        assign_perm('users.can_view_other', self.user)
        resp = self.client.post(self.url, data={'permissions': ['can_view', ],
                                                'user': self.user_with_permission.pk})
        self.assertEqual(resp.status_code, 302)


class CaseGroupPermissionView(FormValidMessageMixin, FormView):
    model = Case
    form_class = CaseGroupPermissionForm
    template_name = 'cases/case_form.html'

    def get_form_valid_message(self):
        return _("%(user)s granted permissions from %(group)s!") % (self.form.cleaned_data)

    def get_form_kwargs(self):
        self.object = self.get_object()
        kwargs = super(CaseGroupPermissionView, self).get_form_kwargs()
        kwargs.update({'case': self.object, 'user': self.request.user})
        return kwargs

    def form_valid(self, form, *args, **kwargs):
        self.form = form
        form.assign()
        return super(CaseGroupPermissionView, self).form_valid(form=form, *args, **kwargs)

    def get_success_url(self):
        return reverse('cases:detail', kwargs={'pk': str(self.object.pk)})

    def get_context_data(self, *args, **kwargs):
        context = super(CaseGroupPermissionView, self).get_context_data(*args, **kwargs)
        context['object'] = self.object
        return context

    def get_object(self):
        obj = get_object_or_404(Case, pk=self.kwargs['pk'])
        assign_perm_check(self.request.user, obj)
        return obj
