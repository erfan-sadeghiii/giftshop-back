

# Create your views here.



# discounts/views.py
from rest_framework.views import APIView

from rest_framework.response import Response

from .serializers import ApplyDiscountSerializer
from .services import apply_discount,final_apply_discount










from django.http import Http404
from rest_framework import viewsets, permissions
from .models import Cart, CartItem,Product,Category,ProductFeature, Feature,Comment,AmazingSlider,Checkout
from .serializers import CartSerializer, CartItemSerializer ,ProductFeatureSerializer, ProductSerializer,ProductCreateSerializer, CategorySerializer, FeatureSerializer,CommentSerializer,AmazingSliderSerializer,CheckoutSerializer

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
            return Response({"error": "Item does not exist"}, status=404)

        try:
            item.delete()
        except Exception as e:
            return Response({"error": str(e)}, status=400)

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












import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings

# Optional: you can create a Payment model to store pending payments
# from .models import Payment
@api_view(['POST'])
def create_payment(request):
    try:
        amount = request.data.get("amount")
        offerCode = request.data.get("code")
        cartItems = request.data.get("cartItems")
        description = request.data.get("description", "Transaction")
        metadata = request.data.get("metadata", {})

        if not amount:
            return Response({"error": "Amount is required"}, status=400)

        amount = int(amount)

        # ---------- APPLY DISCOUNT (CALC ONLY) ----------
        discount_amount = 0
        if offerCode:
            discount_amount = apply_discount(
                code=offerCode,
                user=request.user,
                order_price=amount,
                order_id=None
            )

        final_amount = amount - discount_amount

        if final_amount <= 0:
            return Response(
                {"error": "amount after discount is invalid"},
                status=400
            )

        # ---------- ZARINPAL REQUEST ----------
        payload = {
            "merchant_id": settings.ZARINPAL_MERCHANT_ID,
            "amount": final_amount,
            "callback_url": settings.ZARINPAL_CALLBACK_URL,
            "description": description,
            "metadata": metadata,
        }

        res = requests.post(
            settings.ZARINPAL_BASE_URL + "request.json",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        res_data = res.json()

        # ❗️IMPORTANT CHECK
        if res_data.get("errors"):
            return Response(
                {"error": res_data["errors"]["message"]},
                status=400
            )

        authority = res_data["data"]["authority"]
        payment_url = f"{settings.ZARINPAL_PAYMENT_BASE_URL}{authority}"

        # ---------- SAVE CHECKOUT ----------
        Checkout.objects.create(
            user=request.user,
            authority=authority,
            amount=final_amount,
            items=cartItems,
            offer_code=offerCode
        )

        # ❗️DON'T finalize discount here
        # finalize in callback after payment success

        return Response({
            "authority": authority,
            "payment_url": payment_url
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)




from django.db import transaction


from django.shortcuts import redirect
@api_view(['GET'])
def verify_payment(request):
    try:
        authority = request.GET.get("Authority")
        status = request.GET.get("Status")

        if not authority or not status:
            return Response({"error": "Missing Authority or Status"}, status=400)

        # If canceled
        if status != "OK":
            redirect_url = "https://tixogame.com/final-check/?status=failed"
            return redirect(redirect_url)

        # Get checkout record
        try:
            checkout = Checkout.objects.get(authority=authority)
        except Checkout.DoesNotExist:
            redirect_url = "https://tixogame.com/final-check/?status=not_found"
            return redirect(redirect_url)

        # Verify with Zarinpal
        payload = {
            "merchant_id": settings.ZARINPAL_MERCHANT_ID,
            "amount": checkout.amount,
            "authority": authority
        }

        res = requests.post(
            settings.ZARINPAL_BASE_URL + "verify.json",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        res_data = res.json()
        data = res_data.get("data", {})
        errors = res_data.get("errors", {})

        # SUCCESS (100 or 101)
        if data.get("code") in [100, 101]:
            with transaction.atomic():  # ensure atomic operation
                for item in checkout.items:
                    product_id = item.get("product", {}).get("id")
                    quantity = item.get("quantity", 0)
                    
                    if not product_id or quantity <= 0:
                        continue  # skip invalid entries

                    try:
                        product = Product.objects.get(id=product_id)
                        product.stock_quantity = max(product.stock_quantity - quantity, 0)
                        product.save()
                    except Product.DoesNotExist:
                        # optionally log missing product
                        continue
            checkout.is_paid = True
            checkout.ref_id = data.get("ref_id")
            checkout.card_pan = data.get("card_pan")
            checkout.card_hash = data.get("card_hash")
            checkout.fee_type = data.get("fee_type")
            checkout.fee = data.get("fee")
            checkout.save()
            if checkout.offer_code:
                try:
                    final_apply_discount(
                        code=checkout.offer_code,
                        user=checkout.user,
                        order_price=checkout.amount,
                        order_id=checkout.ref_id
                    )
                except :
                    # optionally log this error
                    pass
            # Redirect with full info
            redirect_url = (
                "https://tixogame.com/final-check/"
                f"?status=success"
                f"&ref_id={checkout.ref_id}"
                f"&amount={checkout.amount}"
                f"&authority={authority}"
                f"&card_pan={checkout.card_pan}"
                
            )

            # ✔ delete if you want:
            # checkout.delete()

            return redirect(redirect_url)

        # FAIL
        else:
            checkout.is_paid = False
            checkout.error_code = errors.get("code")
            checkout.error_message = errors.get("message")
            checkout.save()

            redirect_url = (
                "https://tixogame.com/final-check/"
                f"?status=failed"
                f"&error_code={checkout.error_code}"
                f"&error_message={checkout.error_message}"
                f"&errors={errors}"
            )

            return redirect(redirect_url)

    except Exception as e:
        return redirect(f"https://tixogame.com/final-check/?status=error&message={str(e)}")



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_checkouts(request):
    user = request.user
    checkouts = Checkout.objects.filter(user=user).order_by('-created_at')
    serializer = CheckoutSerializer(checkouts, many=True)
    return Response(serializer.data)



class AdminCheckoutViewSet(viewsets.ModelViewSet):
    queryset = Checkout.objects.all().order_by('-created_at')
    serializer_class = CheckoutSerializer
    permission_classes = [permissions.IsAdminUser]

    # Optional: custom action to toggle is_paid quickly
    @action(detail=True, methods=['patch'])
    def toggle_paid(self, request, pk=None):
        checkout = self.get_object()
        checkout.is_paid = not checkout.is_paid
        checkout.save()
        return Response({"id": checkout.id, "is_paid": checkout.is_paid})








class ApplyDiscountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ApplyDiscountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        discount_amount = apply_discount(
            code=serializer.validated_data['code'],
            user=request.user,
            order_price=serializer.validated_data['order_price'],
            order_id=serializer.validated_data['order_id'],
        )

        final_price = serializer.validated_data['order_price'] - discount_amount

        return Response({
            "discount_amount": discount_amount,
            "final_price": final_price
        })






from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from .models import Discount
from .serializers import DiscountSerializer


class DiscountAdminViewSet(viewsets.ModelViewSet):

    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = [IsAdminUser]
