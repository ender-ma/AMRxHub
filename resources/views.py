from django.shortcuts import render, get_object_or_404
from .models import ResourceCategory, ResourceItem
from django.http import FileResponse, Http404
from .models import Resource  # or whatever your model is called
import os

def resources_list(request):
    categories = ResourceCategory.objects.prefetch_related('items').all()
    return render(request, 'resources/resources.html', {'categories': categories})

def resource_detail(request, pk):
    resource = get_object_or_404(ResourceItem, pk=pk)
    if not resource.pdf_file:
        raise Http404("No file attached to this resource.")
    file_path = resource.pdf_file.path
    if not os.path.exists(file_path):
        raise Http404("File does not exist.")
    response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
    return response

def category_resources(request, pk):
    category = get_object_or_404(ResourceCategory, pk=pk)
    return render(request, 'resources/category_resources.html', {'category': category})

def search_resources(request):
    query = request.GET.get('q', '')
    results = ResourceItem.objects.filter(title__icontains=query)
    return render(request, 'resources/search_results.html', {'results': results, 'query': query})