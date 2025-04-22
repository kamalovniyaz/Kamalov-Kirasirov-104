from django.shortcuts import render

from .constants import URLS_FILENAME, OUTPUT_DIR
from .services.hw_5_search_vectors import load_pages_url, search


def index(request):
    if request.method == "POST":
        query = request.POST.get("query", "")
        urls_name = load_pages_url(URLS_FILENAME)
        results = search(query, OUTPUT_DIR, urls_name)
        links = [{"page": url, "similarity": similarity} for _, url, similarity in results]
        return render(request, "search/results.html", {"query": query, "results": links})

    return render(request, "search/index.html")
