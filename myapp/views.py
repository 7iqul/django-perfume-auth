
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Perfume
from .serializers import PerfumeSerializer
from rest_framework import viewsets, permissions


def cart_count(request):
    # Total number of bottles in the cart
    return sum(request.session.get('cart', {}).values())


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'myapp/signup.html', {
        'form': form,
        'cart_count': cart_count(request),
    })


def home(request):
    perfumes = Perfume.objects.all()
    return render(request, 'myapp/home.html', {
        'perfumes': perfumes,
        'cart_count': cart_count(request),
    })


def detail(request, perfume_id):
    perfume = get_object_or_404(Perfume, id=perfume_id)
    return render(request, 'myapp/detail.html', {
        'perfume': perfume,
        'cart_count': cart_count(request),
    })


@require_POST
def add_to_cart(request, perfume_id):
    perfume = get_object_or_404(Perfume, id=perfume_id)

    if perfume.in_stock:
        cart = request.session.get('cart', {})
        key = str(perfume_id)
        cart[key] = cart.get(key, 0) + 1
        request.session['cart'] = cart

    return redirect(request.META.get('HTTP_REFERER', 'home'))


@require_POST
def remove_from_cart(request, perfume_id):
    cart = request.session.get('cart', {})
    cart.pop(str(perfume_id), None)
    request.session['cart'] = cart
    return redirect('cart')


@login_required
def cart(request):
    items = []
    total = 0

    for pid, qty in request.session.get('cart', {}).items():
        perfume = Perfume.objects.filter(id=pid).first()

        if perfume:
            subtotal = perfume.price * qty
            total += subtotal
            items.append({
                'perfume': perfume,
                'qty': qty,
                'subtotal': subtotal,
            })

    return render(request, 'myapp/cart.html', {
        'items': items,
        'total': total,
        'cart_count': cart_count(request),
    })


# ---------- REST API ----------

class IsAdminOrReadOnly(permissions.BasePermission):
    # Everyone can read, only admin users can modify
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_staff
        )


class PerfumeViewSet(viewsets.ModelViewSet):
    queryset = Perfume.objects.all()
    serializer_class = PerfumeSerializer
    permission_classes = [IsAdminOrReadOnly]
