from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .models import Product

def product_list(request):
    # データベースからすべての商品データを取得する
    products = Product.objects.filter(is_available=True).order_by('-created_at')
    
    # 取得したデータを、'products/product_list.html' という画面に渡して表示する
    return render(request, 'products/product_list.html', {'products': products})