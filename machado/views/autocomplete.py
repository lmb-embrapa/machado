from django.http import HttpResponse
from django.views import View
from machado.models import FeatureSearchIndex
from re import escape, search, IGNORECASE


class AutocompleteView(View):
    def get(self, request):
        """Handle HTTP GET request for autocomplete suggestions."""
        query = request.GET.get("q", "").strip()
        if not query or len(query) < 2:
            return HttpResponse("")

        max_items = 10
        queryset = FeatureSearchIndex.objects.filter(
            autocomplete_text__icontains=query
        )[: max_items * 10]

        result = set()
        for item in queryset:
            try:
                aux = list()
                for i in query.split(" "):
                    regex = r"\w*" + escape(i) + r"\w*"
                    match = search(regex, item.autocomplete_text, IGNORECASE)
                    if match:
                        aux.append(match.group())
                if aux:
                    result.add(" ".join(aux))
            except AttributeError:
                pass

        items = list(result)[:max_items]

        if not items:
            return HttpResponse("")

        html = '<div class="list-group position-absolute w-100 shadow-sm" style="z-index: 1000;">'
        for item in items:
            html += f"<button type=\"button\" class=\"list-group-item list-group-item-action py-2\" onclick=\"document.getElementById('q').value='{item}'; this.closest('form').submit();\">{item}</button>"
        html += "</div>"

        return HttpResponse(html)
