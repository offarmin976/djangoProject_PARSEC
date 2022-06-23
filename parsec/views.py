from django.forms import Form, CharField

from django.views.generic import FormView

from algo import algo, sendmail
from parsec.models import Client


class RequestForm(Form):
    ident = CharField(required=True)


class AlgoView(FormView):
    template_name = 'algo.html'
    form_class = RequestForm

    def form_valid(self, form):
        ident = form.cleaned_data['ident']

        res = algo(ident)

        for c in Client.objects.all():
            sendmail(ident, res, c.email)

        return self.render_to_response(context=form.cleaned_data)