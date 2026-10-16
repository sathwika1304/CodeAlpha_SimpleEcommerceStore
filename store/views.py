from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from .forms import RegisterForm, CheckoutForm
from .models import Product, Order, OrderItem


def _cart_details(request):
    cart = request.session.get("cart", {})
    items = []
    total = Decimal("0.00")
    clean_cart = {}
    for product_id, raw_quantity in cart.items():
        try:
            quantity = int(raw_quantity)
            product = Product.objects.get(pk=int(product_id))
        except (ValueError, TypeError, Product.DoesNotExist):
            continue
        if quantity < 1 or product.stock < 1:
            continue
        quantity = min(quantity, product.stock)
        clean_cart[str(product.pk)] = quantity
        line_total = product.price * quantity
        items.append({"product": product, "quantity": quantity, "line_total": line_total})
        total += line_total
    if clean_cart != cart:
        request.session["cart"] = clean_cart
    return items, total


def home(request):
    products = Product.objects.all()
    return render(request, "store/home.html", {"products": products})


def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, "store/product_detail.html", {"product": product})


def add_to_cart(request, product_id):
    if request.method != "POST":
        return redirect("home")
    product = get_object_or_404(Product, pk=product_id)
    if product.stock < 1:
        messages.error(request, "This product is currently out of stock.")
        return redirect("product_detail", product_id=product.pk)
    cart = request.session.get("cart", {})
    key = str(product.pk)
    current_quantity = int(cart.get(key, 0))
    if current_quantity >= product.stock:
        messages.warning(request, "You have already added all available stock to your cart.")
    else:
        cart[key] = current_quantity + 1
        request.session["cart"] = cart
        messages.success(request, f"{product.name} added to your cart.")
    return redirect("cart")


def cart_view(request):
    items, total = _cart_details(request)
    return render(request, "store/cart.html", {"items": items, "total": total})


def update_cart(request, product_id):
    if request.method != "POST":
        return redirect("cart")
    product = get_object_or_404(Product, pk=product_id)
    try:
        quantity = int(request.POST.get("quantity", "1"))
    except ValueError:
        quantity = 1
    cart = request.session.get("cart", {})
    key = str(product.pk)
    if quantity <= 0:
        cart.pop(key, None)
    elif product.stock <= 0:
        cart.pop(key, None)
        messages.error(request, f"{product.name} is out of stock.")
    else:
        cart[key] = min(quantity, product.stock)
        if quantity > product.stock:
            messages.warning(request, f"Quantity adjusted to available stock ({product.stock}).")
    request.session["cart"] = cart
    return redirect("cart")


def remove_from_cart(request, product_id):
    if request.method == "POST":
        cart = request.session.get("cart", {})
        cart.pop(str(product_id), None)
        request.session["cart"] = cart
        messages.success(request, "Product removed from your cart.")
    return redirect("cart")


def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Your account has been created successfully.")
        return redirect("home")
    return render(request, "store/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        messages.success(request, "You are now logged in.")
        return redirect("home")
    return render(request, "store/login.html", {"form": form})


def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.info(request, "You have been logged out.")
    return redirect("home")


@login_required
def checkout(request):
    items, total = _cart_details(request)
    if not items:
        messages.info(request, "Your cart is empty. Add a product before checkout.")
        return redirect("home")
    form = CheckoutForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            locked_products = {}
            for item in items:
                product = Product.objects.select_for_update().get(pk=item["product"].pk)
                if product.stock < item["quantity"]:
                    messages.error(request, f"Not enough stock for {product.name}. Please update your cart.")
                    return redirect("cart")
                locked_products[product.pk] = product
            order = Order.objects.create(
                user=request.user,
                full_name=form.cleaned_data["full_name"],
                phone=form.cleaned_data["phone"],
                address=form.cleaned_data["address"],
                payment_method=form.cleaned_data["payment_method"],
                total=total,
            )
            for item in items:
                product = locked_products[item["product"].pk]
                quantity = item["quantity"]
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    price=product.price,
                    quantity=quantity,
                )
                product.stock -= quantity
                product.save(update_fields=["stock"])
        request.session["cart"] = {}
        messages.success(request, f"Order #{order.pk} placed successfully. Payment is Cash on Delivery.")
        return redirect("order_detail", order_id=order.pk)
    return render(request, "store/checkout.html", {"form": form, "items": items, "total": total})


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, "store/my_orders.html", {"orders": orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, "store/order_detail.html", {"order": order})
