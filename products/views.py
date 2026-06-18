from django.shortcuts import render, get_object_or_404

# Create your views here.
from .models import Product

def product_list(request):
    # データベースからすべての商品データを取得する
    products = Product.objects.filter(is_available=True).order_by('-created_at')
    
    # 取得したデータを、'products/product_list.html' という画面に渡して表示する
    return render(request, 'products/product_list.html', {'products': products})

def product_detail(request, pk):
    # 指定されたID(pk)の商品を取得する。もし存在しなければ404エラー（ページが見つかりません）を出す
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/product_detail.html', {'product': product})