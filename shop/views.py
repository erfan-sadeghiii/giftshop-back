

# Create your views here.
from rest_framework import viewsets, permissions
from .models import Cart, CartItem,Product,Category,ProductFeature, Feature,Comment,AmazingSlider
from .serializers import CartSerializer, CartItemSerializer ,ProductFeatureSerializer, ProductSerializer,ProductCreateSerializer, CategorySerializer, FeatureSerializer,CommentSerializer,AmazingSliderSerializer

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .utils import get_or_create_cart



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_cart(request):
    cart = get_or_create_cart(request.user)
    serializer = CartSerializer(cart)
    return Response(serializer.data)




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    cart = get_or_create_cart(request.user)
    product_id = request.data.get("product_id")
    quantity = int(request.data.get("quantity", 1))

    # now add or update CartItem
    item, created = cart.items.get_or_create(product_id=product_id)
    if not created:
        item.quantity += quantity
    item.save()

    return Response({"message": "Item added to cart", "cart_id": cart.id})












class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all().select_related("user").prefetch_related("items__product")
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all().select_related("cart", "product")
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        print(self.request.user)
        # Get or create the current user's pending cart
        cart, _ = Cart.objects.get_or_create(user=self.request.user, status="pending")
        serializer.save(cart=cart)





class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class FeatureViewSet(viewsets.ModelViewSet):
    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer
from rest_framework import serializers


class ProductFeatureViewSet(viewsets.ModelViewSet):
    serializer_class = ProductFeatureSerializer
    queryset = ProductFeature.objects.all()

    # ✅ Filtering by product ID (for ?product=9)
    def get_queryset(self):
        queryset = super().get_queryset()
        product_id = self.request.query_params.get("product")
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset

    # ✅ Handle creation with product ID from frontend
    def perform_create(self, serializer):
        product_id = self.request.data.get("product")
        if not product_id:
            raise serializers.ValidationError({"product": "This field is required."})

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError({"product": "Product not found."})

        serializer.save(product=product)
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"  # or "title" if you don’t use slug

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ProductCreateSerializer
        return ProductSerializer










class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by("-date")
    serializer_class = CommentSerializer
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Automatically set the logged-in user
        serializer.save(user=self.request.user)







from .models import Slider
from .serializers import SliderSerializer

class SliderViewSet(viewsets.ModelViewSet):
    queryset = Slider.objects.all()
    serializer_class = SliderSerializer







from .models import Banner
from .serializers import BannerSerializer

class BannerViewSet(viewsets.ModelViewSet):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    permission_classes = [permissions.AllowAny]

    # Optional: filter by position in URL /?position=left
    def get_queryset(self):
        position = self.request.query_params.get('position')
        if position in ['left', 'right']:
            return Banner.objects.filter(position=position)
        return super().get_queryset()








# shop/views.py
from rest_framework import generics
from django.db.models import Q
from .models import Product
from .serializers import ProductSerializer

class ProductSearchView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        search_query = self.request.query_params.get("search", "").strip()

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
                | Q(subtitle__icontains=search_query)
                | Q(category__name__icontains=search_query)  # ✅ assuming category has 'name'
            ).distinct()

        return queryset











from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Ticket, Reply
from .serializers import TicketSerializer, ReplySerializer

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all().order_by('-dateTime')
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        # Users can only see their own tickets (unless admin)
        user = self.request.user
        if user.is_staff:
            return Ticket.objects.all().order_by('-dateTime')
        return Ticket.objects.filter(user=user).order_by('-dateTime')

    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        """Add a reply to a ticket."""
        ticket = self.get_object()
        serializer = ReplySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, ticket=ticket)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class ReplyViewSet(viewsets.ModelViewSet):
    queryset = Reply.objects.all().order_by('-dateTime')
    serializer_class = ReplySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)





from rest_framework import generics, permissions
from .models import MenuCategory, MenuSection, MenuItem
from .serializers import MenuCategorySerializer, MenuSectionSerializer, MenuItemSerializer

# 🔹 MegaMenu: list & create categories
class MegaMenuView(generics.ListCreateAPIView):
    queryset = MenuCategory.objects.prefetch_related("sections__items").all()
    serializer_class = MenuCategorySerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

# 🔹 MegaMenu detail: retrieve, update, delete a category

class MegaMenuDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuCategory.objects.all()
    serializer_class = MenuCategorySerializer
    permission_classes = [permissions.IsAdminUser]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=204)  # No JSON body



# 🔹 CRUD for MenuSection
class MenuSectionListCreateView(generics.ListCreateAPIView):
    queryset = MenuSection.objects.prefetch_related("items").all()
    serializer_class = MenuSectionSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class MenuSectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuSection.objects.all()
    serializer_class = MenuSectionSerializer
    permission_classes = [permissions.IsAdminUser]

    def destroy(self, request, *args, **kwargs):
        try:
            section = self.get_object()
        except Http404:
           return Response(status=204) 

        section.delete()
        return Response(status=204) 

# 🔹 CRUD for MenuItem
class MenuItemListCreateView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAdminUser]

    def destroy(self, request, *args, **kwargs):
        try:
            item = self.get_object()
        except Http404:
            return Response({"error": "Item does not exist"}, status=status.HTTP_404_NOT_FOUND)

        try:
            item.delete()
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=204) 


class AmazingSliderViewSet(viewsets.ModelViewSet):
    queryset = AmazingSlider.objects.all()

    serializer_class = AmazingSliderSerializer

    # def get_queryset(self):
    #     # Only return the most recent slider
    #     return AmazingSlider.objects.prefetch_related('products').all()

    # def get_permissions(self):
    #     if self.request.method in permissions.SAFE_METHODS:
    #         return [permissions.AllowAny()]
    #     return [IsAdminOrOwner()]
    # def get_permissions(self):  
    # if self.request.method in permissions.SAFE_METHODS:
    #     return [permissions.AllowAny()]
    # return [permissions.IsAdminUser()]
    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
