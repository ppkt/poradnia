import django_filters
from atom.filters import CrispyFilterMixin
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, Layout, Submit, Div
from django.utils.translation import ugettext_lazy as _

from poradnia.users.filters import UserChoiceFilter

from .models import Advice


class AdviceFilter(CrispyFilterMixin, django_filters.FilterSet):
    advicer = UserChoiceFilter(label=_("Advicer"))
    created_by = UserChoiceFilter(label=_("Created by"))
    created_on = django_filters.DateRangeFilter(label=_("Created on"))

    class Meta:
        model = Advice
        fields = ['advicer', 'created_by', 'created_on',
                  'area', 'issues', 'person_kind', 'institution_kind', 'helped']
        order_by = (
            ('created_on', _('Creation date')),
            ('modified_on', _('Modification date')),
            ('id', _('ID')),
            ('advicer', _('Advicer')),
            ('person_kind', _('Person kind')),
            ('institution_kind', _('Institution kind'))
        )

    @property
    def form(self):
        self._form = super(CrispyFilterMixin, self).form
        self._form.helper = FormHelper(self._form)
        self._form.helper.form_method = 'get'
        self._form.helper.form_class = 'form-inline'
        self._form.helper.layout = Layout(
            Fieldset(
                _('Statistic data'),
                Div(
                    Div('area', css_class="col-sm-12 col-md-2"),
                    Div('issues', css_class="col-sm-12 col-md-4"),
                    Div('person_kind', css_class="col-sm-12 col-md-2"),
                    Div('institution_kind', css_class="col-sm-12 col-md-2"),
                    Div('helped', css_class="col-sm-12 col-md-2"),
                    css_class='row')
            ),
            Fieldset(
                _('Details'),
                'advicer', 'created_by', 'created_on',
            ),
        )
        self._form.helper.add_input(Submit('filter', _('Filter')))
        return self._form
