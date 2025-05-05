from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class CreateRoutesView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/routes/create_routearea.html'

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
