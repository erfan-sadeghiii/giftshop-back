from rest_framework import serializers
from .models import Product, Cart, CartItem,ProductImage,Category,Feature,ProductFeature,Comment,AmazingSlider,Checkout

from accounts.serializers import UserSerializer 


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image"]


class CategoryParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]  # Only show these for parent


class CategorySerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        allow_null=True,
        required=False
    )
    parent_detail = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "parent", "parent_detail"]

    def get_parent_detail(self, obj):
        if obj.parent:
            return {"id": obj.parent.id, "name": obj.parent.name}
        return None



class FeatureSerializer(serializers.ModelSerializer):
    

    class Meta:
        model = Feature
        fields = ["id", "name", "is_general"]


class ProductFeatureSerializer(serializers.ModelSerializer):

    feature = serializers.PrimaryKeyRelatedField(
        queryset=Feature.objects.all()
    )
    feature_detail = FeatureSerializer(source="feature", read_only=True)

    class Meta:
        model = ProductFeature
        fields = ["id", "feature","feature_detail", "value", "product"]




# Serializer for creating product with multiple images
from django.conf import settings

class ProductCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    product_features = ProductFeatureSerializer(many=True, required=False)
    
    # <-- Changed to CharField for URLs
    remove_images = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )
    
    remove_features = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = Product
        fields = [
            "id", "title", "slug", "subtitle", "description", "price", "discount", "final_price",
            "stock_quantity", "date", "category", "images", "product_features",
            "remove_images", "remove_features"
        ]

    def create(self, validated_data):
        images_data = validated_data.pop("images", [])
        features_data = validated_data.pop("product_features", [])
        product = Product.objects.create(**validated_data)

        # Create features
        for feature in features_data:
            ProductFeature.objects.create(
                product=product,
                feature=feature["feature"],
                value=feature["value"]
            )

        # Create images
        for image in images_data:
            ProductImage.objects.create(product=product, image=image)

        return product

    def update(self, instance, validated_data):
        # Remove specified images by URL
        remove_images = validated_data.pop("remove_images", [])
        print(remove_images)
        if remove_images:
            paths_to_remove = [url.replace(settings.MEDIA_URL, '') for url in remove_images]
            ProductImage.objects.filter(image__in=paths_to_remove, product=instance).delete()
            # ProductImage.objects.filter(image__in=remove_images, product=instance).delete()

        # Remove specified features by ID
        remove_features = validated_data.pop("remove_features", [])
        if remove_features:
            ProductFeature.objects.filter(id__in=remove_features, product=instance).delete()

        # Update basic fields
        for attr, value in validated_data.items():
            if attr not in ["images", "product_features"]:
                setattr(instance, attr, value)
        instance.save()

        # Add new features
        features_data = validated_data.pop("product_features", [])
        for feature in features_data:
            ProductFeature.objects.create(
                product=instance,
                feature=feature["feature"],
                value=feature["value"]
            )

        # Add new images
        images_data = validated_data.pop("images", [])
        for image in images_data:
            ProductImage.objects.create(product=instance, image=image)

        return instance


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "product", "user", "title", "content", "isLiked", "date"]
        read_only_fields = ["id", "user", "date"]


class ProductSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    category = CategorySerializer()
    comments = CommentSerializer(many=True, read_only=True)  # <-- fix here
    product_features = ProductFeatureSerializer(many=True)

    class Meta:
        model = Product
        fields = [
            "id", "title","slug","subtitle", "description", "price", "discount", "final_price",
            "stock_quantity", "comments", "date", "category", "images", "product_features"
        ]

    def get_images(self, obj):
        return [img.image.url for img in obj.images.all()]




class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source="product",
        write_only=True
    )
    cart = serializers.PrimaryKeyRelatedField(read_only=True)  # ✅ mark read-only

    class Meta:
        model = CartItem
        fields = ["id", "product", "cart", "product_id", "quantity"]




class CartSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "status", "created_at", "items", "total_price"]



# shop/serializers.py

from .models import Slider

class SliderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slider
        fields = ['id', 'picture', 'link']



from rest_framework import serializers
from .models import Banner

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ['id', 'position', 'image', 'link']



from .models import Ticket, Reply

class ReplySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Reply
        fields = ['id', 'user', 'user_name', 'ticket', 'content', 'dateTime']
        read_only_fields = ['user', 'dateTime']


class TicketSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    replies = ReplySerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'title', 'content', 'file', 'user', 'user_name',
            'dateTime', 'status', 'replies'
        ]
        read_only_fields = ['user', 'dateTime']





# serializers.py

from .models import MenuCategory, MenuSection, MenuItem


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ["id", "name", "link", "query", "order", "section"]


class MenuSectionSerializer(serializers.ModelSerializer):
    items = MenuItemSerializer(many=True, read_only=True)

    class Meta:
        model = MenuSection
        fields = ["id", "title", "order", "items", "menuCategory"]


class MenuCategorySerializer(serializers.ModelSerializer):
    sections = MenuSectionSerializer(many=True, read_only=True)

    class Meta:
        model = MenuCategory
        fields = ["id", "name", "icon", "order", "sections"]


class AmazingSliderSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    product_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True
    )

    class Meta:
        model = AmazingSlider
        fields = ['id', 'products', 'product_ids', 'duration', 'created_at']

    def create(self, validated_data):
        product_ids = validated_data.pop("product_ids")
        slider = AmazingSlider.objects.create(**validated_data)
        slider.products.set(product_ids)
        return slider

class CheckoutSerializer(serializers.ModelSerializer):
    # user_name = serializers.CharField(source='user.username', read_only=True)
    user = UserSerializer( read_only=True)
    class Meta:
        model = Checkout
        fields = '__all__'