from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from . import views

router = DefaultRouter()
router.register('perfumes', views.PerfumeViewSet)

urlpatterns = [
    path('', views.home, name='home'),
    path('perfume/<int:perfume_id>/', views.detail, name='detail'),
    path('cart/', views.cart, name='cart'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='myapp/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('api/', include(router.urls)),
    path('cart/add/<int:perfume_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:perfume_id>/', views.remove_from_cart, name='remove_from_cart'),
]