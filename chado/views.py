"""Views."""

from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render

from chado.models import Cvterm


def index(request):
    """Index."""
    return HttpResponse('Hello, world.')


def stats(request):
    """General stats."""
    cv = Cvterm.objects.values('cv__name')
    cv = cv.annotate(Count('cv_id'))
    cv = cv.filter(cv_id__count__gt=5)
    cv = cv.order_by('cv__name')

    data = {
        'Controled vocabularies': cv,
    }

    return render(request, 'stats.html', {'context': data})
