from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from .serializers import RegisterSerializer, UserSerializer, CustomTokenObtainPairSerializer

User = get_user_model()

# ---------------- REGISTER ----------------
@api_view(['POST'])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        # Use custom token serializer to embed role and username
        token_serializer = CustomTokenObtainPairSerializer()
        refresh = token_serializer.get_token(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response({
            "detail": "Registration successful",
            "access": access_token,
            "refresh": refresh_token
        }, status=status.HTTP_201_CREATED)

        # Set refresh token in HttpOnly cookie
        response.set_cookie(
            key='refresh',
            value=refresh_token,
            httponly=True,
            secure=False,  # True in production (HTTPS)
            samesite="None",
            max_age=7 * 24 * 60 * 60  # 7 days
        )
        return response

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------- LOGIN ----------------
@api_view(['POST'])
def login_view(request):
    identifier = request.data.get('username')  # could be email OR username
    password = request.data.get('password')
    user = None

    # Handle email or username login
    if "@" in identifier:
        try:
            user_obj = User.objects.get(email=identifier)
            user = authenticate(username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None
    else:
        user = authenticate(username=identifier, password=password)

    if not user:
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    # Use custom token serializer for role embedding
    token_serializer = CustomTokenObtainPairSerializer()
    refresh = token_serializer.get_token(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    response = Response({
        "detail": "Login successful",
        "access": access_token,
        "refresh": refresh_token
    })

    # Set refresh token in HttpOnly cookie
    response.set_cookie(
        key='refresh',
        value=refresh_token,
        httponly=True,
        secure=False,  # True in production
        samesite="None",
        max_age=7 * 24 * 60 * 60
    )

    return response


# ---------------- REFRESH ----------------
@api_view(["POST"])
def refresh_view(request):
    refresh_token = request.data.get("refresh")
    if not refresh_token:
        return Response({"detail": "No refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        refresh = RefreshToken(refresh_token)
        new_access = str(refresh.access_token)
    except Exception:
        return Response({"detail": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

    return Response({"access": new_access})


# ---------------- LOGOUT ----------------
@api_view(['POST'])
def logout_view(request):
    response = Response({"detail": "Logged out successfully"})
    response.delete_cookie('refresh')
    return response


# ---------------- ME ----------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)









from rest_framework.permissions import BasePermission

class IsAdminOrOwner(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.role in ['admin', 'owner'])
        )



from rest_framework import generics





class UserListView(generics.ListAPIView): 
    queryset = User.objects.all() 
    serializer_class = UserSerializer 
    permission_classes = [IsAdminOrOwner]


# class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [IsAdminOrOwner]

#     def patch(self, request, *args, **kwargs):
#         user = self.get_object()
#         # Only owner can change roles
#         if request.user.role != "owner" and request.data.get("role"):
#             return Response({"detail": "فقط مالک می‌تواند نقش‌ها را تغییر دهد."}, status=status.HTTP_403_FORBIDDEN)
#         return self.update(request, *args, **kwargs)
#   # Partial update allows sending only the 'role' field
#         serializer = self.get_serializer(user, data=request.data, partial=True)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)

#     def delete(self, request, *args, **kwargs):
#         user = self.get_object()
#         # Prevent deleting the owner
#         if user.role == "owner":
#             return Response({"detail": "نمی‌توانید مالک را حذف کنید."}, status=status.HTTP_403_FORBIDDEN)
#         return self.destroy(request, *args, **kwargs)

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrOwner]

    def patch(self, request, *args, **kwargs):
        user = self.get_object()

        # Only owner can change roles
        if request.user.role != "owner" and request.data.get("role"):
            return Response(
                {"detail": "فقط مالک می‌تواند نقش‌ها را تغییر دهد."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Partial update — only update the fields sent in request
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)