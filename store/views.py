from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
import stripe
from django.conf import settings
from django.http import JsonResponse
from .models import Product, Order, Review, Wishlist
from .forms import ProductForm, ReviewForm, UserProfileForm, OrderStatusForm
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.contrib.admin.views.decorators import staff_member_required

stripe.api_key = settings.STRIPE_SECRET_KEY
@login_required
def create_checkout_session(request):
    if request.method == 'POST':
        YOUR_DOMAIN = "http://127.0.0.1:8000"
        cart = request.session.get('cart', {})
        line_items = []

        total = 0

        for product_id, quantity in cart.items():
            product = get_object_or_404(Product, pk=product_id)
            subtotal = int(product.price * quantity * 100)  # Convert ₹ to paise
            line_items.append({
                'price_data': {
                    'currency': 'inr',
                    'product_data': {
                        'name': product.name,
                    },
                    'unit_amount': int(product.price * 100),  # price in paise
                },
                'quantity': quantity,
            })
            total += subtotal

        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=YOUR_DOMAIN + '/success/',
                cancel_url=YOUR_DOMAIN + '/cart/',
            )
            return JsonResponse({'id': checkout_session.id})
        except Exception as e:
            return JsonResponse({'error': str(e)})


def product_list(request):
    category = request.GET.get('category')
    query = request.GET.get('q')
    page_number = request.GET.get('page')

    products = Product.objects.all()

    if category:
        products = products.filter(category=category)

    if query:
        products = products.filter(name__icontains=query) | products.filter(description__icontains=query)

    paginator = Paginator(products, 6)  # Show 6 products per page
    page_obj = paginator.get_page(page_number)

    categories = Product.CATEGORY_CHOICES
    return render(request, 'store/product_list.html', {
        'products': page_obj.object_list,
        'categories': categories,
        'selected_category': category,
        'page_obj': page_obj
    })



@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        cart[str(product_id)] += 1
    else:
        cart[str(product_id)] = 1

    request.session['cart'] = cart
    return redirect('product_list')
@login_required
def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, pk=product_id)
        subtotal = product.price * quantity
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })
        total += subtotal

    return render(request, 'store/cart.html', {'cart_items': cart_items, 'total': total,
                                                'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY})
@login_required
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
    return redirect('view_cart')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'store/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('product_list')
        print("Logged in:", user.username)

    else:
        form = AuthenticationForm()
    return render(request, 'store/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('product_list')

@login_required
@login_required
def payment_success(request):
    cart = request.session.get('cart', {})
    message_lines = []

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, pk=product_id)
        Order.objects.create(user=request.user, product=product, quantity=quantity)
        message_lines.append(f"{product.name} x {quantity} - ₹{product.price * quantity}")

    request.session['cart'] = {}  # Clear cart

    # ✅ Email logic
    subject = 'Thank you for your order!'
    message = f"Hi {request.user.username},\n\nYour order was successful:\n\n"
    message += '\n'.join(message_lines)
    message += "\n\nWe'll notify you once it's shipped!\n\nTeam E-Commerce"

    send_mail(subject, message, None, [request.user.email])

    return render(request, 'store/payment_success.html')

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-ordered_at')
    return render(request, 'store/my_orders.html', {'orders': orders})
@login_required
def update_quantity(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            cart[str(product_id)] = quantity
            request.session['cart'] = cart
    return redirect('view_cart')

from .forms import ProductForm

@staff_member_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product added successfully.")
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'store/add_product.html', {'form': form})

def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    reviews = product.reviews.select_related('user').order_by('-created_at')
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:3]
    review_form = ReviewForm()
    return render(request, 'store/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'related_products': related_products,
        'review_form': review_form
    })

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
    return redirect('product_detail', product_id=product.id)

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    return redirect('product_detail', product_id=product.id)

@login_required
def wishlist(request):
    items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'store/wishlist.html', {'items': items})

@login_required
@require_POST
def remove_from_wishlist(request, product_id):
    Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
    return redirect('wishlist')

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        pwd_form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
        if pwd_form.is_valid():
            user = pwd_form.save()
            update_session_auth_hash(request, user)
        return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
        pwd_form = PasswordChangeForm(request.user)
    return render(request, 'store/profile.html', {'form': form, 'pwd_form': pwd_form})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    total = order.product.price * order.quantity
    return render(request, 'store/order_detail.html', {'order': order, 'total': total})

@staff_member_required
def manage_orders(request):
    orders = Order.objects.all().order_by('-ordered_at')
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, f"Order #{order.id} status updated.")
            return redirect('manage_orders')
    else:
        form = OrderStatusForm()
    return render(request, 'store/manage_orders.html', {'orders': orders, 'form': form})

