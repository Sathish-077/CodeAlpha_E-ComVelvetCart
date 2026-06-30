from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
import json

from .models import Product, Category, Order, OrderItem, UserProfile
from .forms import (
    UserRegistrationForm, UserLoginForm, CheckoutForm,
    UserProfileForm, UserUpdateForm
)


# ─── Cart helpers ────────────────────────────────────────────────────────────

def get_cart(request):
    return request.session.get('cart', {})


def save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True


# ─── Product views ───────────────────────────────────────────────────────────

def product_list(request):
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    category_slug = request.GET.get('category')
    current_category = None
    search_query = request.GET.get('q', '')
    sort = request.GET.get('sort', 'name')

    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=current_category)

    if search_query:
        products = products.filter(name__icontains=search_query)

    sort_options = {
        'name': 'name',
        'price_asc': 'price',
        'price_desc': '-price',
        'newest': '-created',
    }
    products = products.order_by(sort_options.get(sort, 'name'))

    sort_choices = [
        ('name', 'Name (A–Z)'),
        ('price_asc', 'Price: Low to High'),
        ('price_desc', 'Price: High to Low'),
        ('newest', 'Newest First'),
    ]
    context = {
        'categories': categories,
        'products': products,
        'current_category': current_category,
        'search_query': search_query,
        'sort': sort,
        'sort_choices': sort_choices,
    }
    return render(request, 'store/product_list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    related = Product.objects.filter(
        category=product.category, available=True
    ).exclude(id=product.id)[:4]

    context = {'product': product, 'related': related}
    return render(request, 'store/product_detail.html', context)


# ─── Cart views ──────────────────────────────────────────────────────────────

def cart_detail(request):
    cart = get_cart(request)
    cart_items = []
    total = 0

    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=int(product_id))
            subtotal = product.price * item['quantity']
            total += subtotal
            cart_items.append({
                'product': product,
                'quantity': item['quantity'],
                'subtotal': subtotal,
            })
        except Product.DoesNotExist:
            pass

    context = {'cart_items': cart_items, 'total': total}
    return render(request, 'store/cart.html', context)


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    cart = get_cart(request)
    key = str(product_id)
    quantity = int(request.POST.get('quantity', 1))

    if key in cart:
        cart[key]['quantity'] = min(
            cart[key]['quantity'] + quantity, product.stock
        )
    else:
        cart[key] = {'quantity': min(quantity, product.stock)}

    save_cart(request, cart)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        count = sum(v['quantity'] for v in cart.values())
        return JsonResponse({'success': True, 'cart_count': count})

    messages.success(request, f'"{product.name}" added to cart.')
    return redirect('store:cart_detail')


@require_POST
def cart_remove(request, product_id):
    cart = get_cart(request)
    key = str(product_id)
    if key in cart:
        del cart[key]
        save_cart(request, cart)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        count = sum(v['quantity'] for v in cart.values())
        return JsonResponse({'success': True, 'cart_count': count})

    messages.info(request, 'Item removed from cart.')
    return redirect('store:cart_detail')


@require_POST
def cart_update(request, product_id):
    cart = get_cart(request)
    key = str(product_id)
    quantity = int(request.POST.get('quantity', 1))

    if quantity > 0 and key in cart:
        cart[key]['quantity'] = quantity
    elif key in cart:
        del cart[key]

    save_cart(request, cart)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        count = sum(v['quantity'] for v in cart.values())
        # Recalculate subtotal for this item
        try:
            product = Product.objects.get(id=int(product_id))
            subtotal = float(product.price) * quantity
        except Product.DoesNotExist:
            subtotal = 0
        cart_total = sum(
            float(Product.objects.get(id=int(pid)).price) * v['quantity']
            for pid, v in cart.items()
            if Product.objects.filter(id=int(pid)).exists()
        )
        return JsonResponse({
            'success': True,
            'cart_count': count,
            'subtotal': subtotal,
            'cart_total': cart_total,
        })

    return redirect('store:cart_detail')


# ─── Checkout & Orders ───────────────────────────────────────────────────────

@login_required
def checkout(request):
    cart = get_cart(request)
    if not cart:
        messages.warning(request, 'Your cart is empty.')
        return redirect('store:cart_detail')

    cart_items = []
    total = 0
    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=int(product_id))
            subtotal = product.price * item['quantity']
            total += subtotal
            cart_items.append({
                'product': product,
                'quantity': item['quantity'],
                'subtotal': subtotal,
            })
        except Product.DoesNotExist:
            pass

    profile = getattr(request.user, 'profile', None)
    initial = {}
    if profile:
        initial = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'address': profile.address,
            'city': profile.city,
            'postal_code': profile.postal_code,
        }

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                order.user = request.user
                order.save()

                for ci in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=ci['product'],
                        price=ci['product'].price,
                        quantity=ci['quantity'],
                    )
                    # Decrement stock
                    ci['product'].stock = max(0, ci['product'].stock - ci['quantity'])
                    ci['product'].save()

            # Clear cart
            request.session['cart'] = {}
            request.session.modified = True

            messages.success(request, f'Order #{order.id} placed successfully!')
            return redirect('store:order_confirmation', order_id=order.id)
    else:
        form = CheckoutForm(initial=initial)

    context = {
        'form': form,
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'store/checkout.html', context)


@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_confirmation.html', {'order': order})


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'store/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_detail.html', {'order': order})


# ─── Auth views ──────────────────────────────────────────────────────────────

def register(request):
    if request.user.is_authenticated:
        return redirect('store:product_list')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, f'Welcome, {user.username}! Account created.')
            return redirect('store:product_list')
    else:
        form = UserRegistrationForm()

    return render(request, 'store/register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('store:product_list')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                next_url = request.GET.get('next', 'store:product_list')
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()

    return render(request, 'store/login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('store:product_list')


@login_required
def profile(request):
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile_obj)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('store:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile_obj)

    orders = Order.objects.filter(user=request.user)[:5]
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'orders': orders,
    }
    return render(request, 'store/profile.html', context)
