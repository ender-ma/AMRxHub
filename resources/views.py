from django.shortcuts import render, get_object_or_404, redirect
from .models import ResourceCategory, ResourceItem
from django.http import FileResponse
import os

def resources_list(request):
    categories = ResourceCategory.objects.prefetch_related('items').all()
    return render(request, 'resources/resources.html', {'categories': categories})


def category_resources(request, pk):
    category = get_object_or_404(ResourceCategory, pk=pk)
    return render(request, 'resources/category_resources.html', {'category': category})

def resource_detail(request, pk):
    resource = get_object_or_404(ResourceItem, pk=pk)
    return render(request, 'resources/resource_detail.html', {'resource': resource})

# def resource_detail(request, pk):
#     resource = get_object_or_404(ResourceItem, pk=pk)

#     # Prefer returning the PDF file if present and exists on disk
#     if resource.pdf_file:
#         file_path = resource.pdf_file.path
#         if os.path.exists(file_path):
#             return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
#         # fall through to render detail page with a warning if file missing

#     # If the resource is an external link, redirect there
#     if resource.link:
#         return redirect(resource.link)

#     # Otherwise render a detail page (handles image-only or description-only resources)
#     return render(request, 'resources/resource_detail.html', {'resource': resource})


# def search_resources(request):
#     query = request.GET.get('q', '')
#     results = ResourceItem.objects.filter(title__icontains=query)
#     return render(request, 'resources/search_results.html', {'results': results, 'query': query})