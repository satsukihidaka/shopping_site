from django.db.models import Case, Count, IntegerField, Value, When
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Category, Product

CATEGORY_ORDER = [
    'tops',
    'bottoms',
    'one-piece',
    'set-up',
    'outwear',
    'bag',
    'shoes',
    'acc',
]


def ordered_categories():
    order_cases = [
        When(slug=slug, then=Value(index))
        for index, slug in enumerate(CATEGORY_ORDER)
    ]
    return (
        Category.objects.annotate(
            product_count=Count('products'),
            category_order=Case(
                *order_cases,
                default=Value(len(CATEGORY_ORDER)),
                output_field=IntegerField(),
            ),
        )
        .order_by('category_order', 'name')
    )


def get_cart(request):
    return request.session.get('cart', {})


def get_cart_count(request):
    return sum(get_cart(request).values())


def build_common_context(request, current_category=None):
    return {
        'categories': ordered_categories(),
        'current_category': current_category,
        'cart_count': get_cart_count(request),
    }


def cart_items(request):
    cart = get_cart(request)
    product_ids = [int(product_id) for product_id in cart.keys()]
    products = Product.objects.filter(pk__in=product_ids, is_available=True).select_related('category')
    products_by_id = {product.pk: product for product in products}

    items = []
    total_price = 0
    for product_id in product_ids:
        product = products_by_id.get(product_id)
        if not product:
            continue
        quantity = cart.get(str(product_id), 0)
        line_total = product.price * quantity
        total_price += line_total
        items.append(
            {
                'product': product,
                'quantity': quantity,
                'line_total': line_total,
            }
        )

    return items, total_price


def category_list(request):
    categories = ordered_categories()
    return render(
        request,
        'products/category_list.html',
        {
            'categories': categories,
            'cart_count': get_cart_count(request),
            'current_category': None,
        },
    )


def product_list(request):
    products = Product.objects.filter(is_available=True).select_related('category').order_by('-created_at')
    context = build_common_context(request)
    context.update(
        {
            'products': products,
        }
    )
    return render(request, 'products/product_list.html', context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = (
        category.products.filter(is_available=True)
        .select_related('category')
        .order_by('-created_at')
    )
    context = build_common_context(request, category)
    context.update(
        {
            'category': category,
            'products': products,
        }
    )
    return render(request, 'products/category_detail.html', context)


def product_detail(request, pk):
    product = get_object_or_404(Product.objects.select_related('category'), pk=pk)
    context = build_common_context(request, product.category)
    context.update({'product': product})
    return render(request, 'products/product_detail.html', context)


@require_POST
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk, is_available=True)
    cart = get_cart(request)
    product_key = str(product.pk)
    cart[product_key] = cart.get(product_key, 0) + 1
    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart_detail')


def cart_detail(request):
    items, total_price = cart_items(request)
    context = build_common_context(request)
    context.update(
        {
            'cart_items': items,
            'total_price': total_price,
        }
    )
    return render(request, 'products/cart_detail.html', context)


@require_POST
def remove_from_cart(request, pk):
    cart = get_cart(request)
    cart.pop(str(pk), None)
    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart_detail')
