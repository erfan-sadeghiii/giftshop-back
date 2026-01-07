from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import  MegaMenuDetailView,MenuSectionListCreateView,DiscountAdminViewSet,ApplyDiscountAPIView,user_checkouts,AdminCheckoutViewSet, MenuSectionDetailView, MenuItemListCreateView, MenuItemDetailView,MegaMenuView,get_user_cart,add_to_cart, TicketViewSet, ReplyViewSet, ProductSearchView,CartViewSet, CartItemViewSet,BannerViewSet, ProductViewSet,FeatureViewSet,CategoryViewSet,ProductFeatureViewSet,CommentViewSet,SliderViewSet,AmazingSliderViewSet,create_payment,verify_payment

router = DefaultRouter()
router.register(r'carts', CartViewSet, basename='cart')
router.register(r'cart-items', CartItemViewSet, basename='cartitem')

router.register(r'products', ProductViewSet, basename='product')
router.register(r'features', FeatureViewSet, basename='features')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'productsFeatures',ProductFeatureViewSet , basename='ProductFeatures')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'sliders', SliderViewSet, basename='slider')
router.register(r'banners', BannerViewSet, basename='banner')
router.register(r'tickets', TicketViewSet, basename='ticket')
router.register(r'replies', ReplyViewSet, basename='reply')
router.register(r"amazing-slider", AmazingSliderViewSet, basename='amazing-slider')
router.register(r'admin/checkouts', AdminCheckoutViewSet, basename='admin-checkouts')
router.register(r'offers', DiscountAdminViewSet, basename='discount')






urlpatterns = [
    path('products/search/', ProductSearchView.as_view(), name='product-search'),
    path("", include(router.urls)),
    path('payment/', create_payment, name='create_payment'),
    path('checkout/', verify_payment, name='verify_payment'),
    path('my-checkouts/', user_checkouts, name='user-checkouts'),
  
    path("megamenu/", MegaMenuView.as_view(), name="megamenu"),
    path("megamenu/<int:pk>/", MegaMenuDetailView.as_view(), name="megamenu-detail"),

    path("megamenu/sections/", MenuSectionListCreateView.as_view(), name="section-list-create"),
    path("megamenu/sections/<int:pk>/", MenuSectionDetailView.as_view(), name="section-detail"),

    path("megamenu/items/", MenuItemListCreateView.as_view(), name="item-list-create"),
    path("megamenu/items/<int:pk>/", MenuItemDetailView.as_view(), name="item-detail"),

    path('apply/', ApplyDiscountAPIView.as_view()),

    path('cart/', get_user_cart, name='get_user_cart'),
    path('cart/add/', add_to_cart, name='add_to_cart'),
]
