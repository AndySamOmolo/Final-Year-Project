from .models import Category

def global_footer_context(request):
    footer_categories = Category.objects.all()
    
    category_slug = request.GET.get('category')
    return {
        'footer_categories': footer_categories,
    }
