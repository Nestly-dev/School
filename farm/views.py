from django.views.generic import ListView
from .models import Produce


class ProduceListView(ListView):
    model = Produce
    template_name = 'farm/produce_list.html'
    context_object_name = 'produce_list'
