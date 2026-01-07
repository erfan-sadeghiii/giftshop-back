from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from .serializers import RegisterSerializer, UserSerializer, CustomTokenObtainPairSerializer
from .permissions import IsAdminOrOwner 
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
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=True,  # True in production (HTTPS)
            samesite="Strict",
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
        except User.DoesNotExist:
            return Response({"detail": "کاربری با این ایمیل یافت نشد"}, status=status.HTTP_404_NOT_FOUND)
        
        # Check password explicitly
        if not user_obj.check_password(password):
            return Response({"detail": "رمز عبور اشتباه است"}, status=status.HTTP_401_UNAUTHORIZED)
        
        user = user_obj  # authentication successful
    else:
        # Username login
        user = authenticate(username=identifier, password=password)
        if not user:
            # Distinguish between wrong username and wrong password
            if User.objects.filter(username=identifier).exists():
                return Response({"detail": "رمز عبور اشتباه است"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({"detail": "کاربری با این نام کاربری یافت نشد"}, status=status.HTTP_404_NOT_FOUND)

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
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        secure=True,  # True in production
        samesite="Strict",
        max_age=7 * 24 * 60 * 60
    )
    response.set_cookie(
        key='access',
        value=access_token,
        httponly=True,
        secure=True,  # True in production
        samesite="Strict",
        max_age=7 * 24 * 60 * 60
    )

    return response


# ---------------- REFRESH ----------------
@api_view(["POST"])
def refresh_view(request):
    # refresh_token = request.data.get("refresh")
    refresh_token = request.COOKIES.get("refresh_token")
    if not refresh_token:
        return Response({"detail": "No refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        refresh = RefreshToken(refresh_token)
        new_access = str(refresh.access_token)
    except Exception:
        return Response({"detail": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

    
    return   Response({"access": new_access})
    


# ---------------- LOGOUT ----------------
@api_view(['POST'])
def logout_view(request):
    response = Response({"detail": "Logged out successfully"})
    response.delete_cookie('refresh_token')
    response.delete_cookie('access')
    return response


# ---------------- ME ----------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)












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
#             return Response(
#                 {"detail": "فقط مالک می‌تواند نقش‌ها را تغییر دهد."},
#                 status=status.HTTP_403_FORBIDDEN
#             )

#         # Partial update — only update the fields sent in request
#         serializer = self.get_serializer(user, data=request.data, partial=True)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrOwner]

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        data = request.data.copy()  # Make a mutable copy

        # Only owner can change roles
        if "role" in data and request.user.role != "owner":
            return Response(
                {"detail": "فقط مالک می‌تواند نقش‌ها را تغییر دهد."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Normal users can only update their own discord
        if request.user == user and not request.user.is_admin and not request.user.is_owner:
            allowed_fields = ["discord"]
            data = {field: data[field] for field in data if field in allowed_fields}

        serializer = self.get_serializer(user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)  # ✅ must return








# import time
# from django.utils import timezone
# import random
# import requests
# from datetime import timedelta
# #sandbox
# API_KEY = "yaVb2gviOWyDiVJr2doB6XWXpyUQZCeDDrN83RtzCL26ckgZ"
# #real
# # API_KEY = "LDftCnqtoi6uou6T0M46V1Vt0tjgyuvUS7LNbcNHjwwkRWX2" 
# TEMPLATE_ID = 123456  
# LOCKOUT_TIME = timedelta(minutes=1)  # lockout duration


# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def send_verification_code(request):
#     mobile = request.data.get("mobile")
#     user = request.user

#     if user.next_request_permission + LOCKOUT_TIME > timezone.now():
#         remaining_seconds = int((user.next_request_permission + LOCKOUT_TIME - timezone.now()).total_seconds())
#         minutes, seconds = divmod(remaining_seconds, 60)
#         return Response(
#                              {
#                 "detail": "تلاش‌های شما بیش از حد مجاز بوده است. لطفاً بعداً دوباره امتحان کنید.",
#                 "lockout": {
#                     "minutes": minutes,
#                     "seconds": seconds,
#                     "total_seconds": remaining_seconds
#                 }
#             },
#             status=status.HTTP_403_FORBIDDEN
#         )

#     if not mobile:
#         return Response({"detail": "Mobile is required"}, status=400)

#     code = str(random.randint(100000, 999999))
    
#     user.next_request_permission = timezone.now()
#     user.save()

#     payload = {
#         "mobile": mobile,
#         "templateId": TEMPLATE_ID,
#         "parameters": [
#             {"name": "PARAMETER1", "value": code}
#         ]
#     }

#     headers = {
#         "Content-Type": "application/json",
#         "Accept": "text/plain",
#         "x-api-key": API_KEY
#     }

#     r = requests.post("https://api.sms.ir/v1/send/verify", json=payload, headers=headers)

#     # Save code temporarily
#     request.session[f"verify_{mobile}"] = code

#     return Response({"sent": True,
#                          "code": code,   # <--- return OTP (DEV ONLY)
#  "sms_response": r.json()})

from django.utils import timezone
from datetime import timedelta
import random
import requests





# API_KEY = "yaVb2gviOWyDiVJr2doB6XWXpyUQZCeDDrN83RtzCL26ckgZ"
API_KEY = "LDftCnqtoi6uou6T0M46V1Vt0tjgyuvUS7LNbcNHjwwkRWX2"
TEMPLATE_ID = 551725
LOCKOUT_TIME = timedelta(minutes=1)  # lockout duration

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_verification_code(request):
    try:
        mobile = request.data.get("mobile")
        user = request.user

        if not mobile:
            return Response({"detail": "Mobile is required"}, status=400)

        # Check lockout
        if user.next_request_permission and user.next_request_permission + LOCKOUT_TIME > timezone.now():
            remaining_seconds = int((user.next_request_permission + LOCKOUT_TIME - timezone.now()).total_seconds())
            minutes, seconds = divmod(remaining_seconds, 60)
            return Response({
                "detail": "تلاش‌های شما بیش از حد مجاز بوده است. لطفاً بعداً دوباره امتحان کنید.",
                "lockout": {"minutes": minutes, "seconds": seconds, "total_seconds": remaining_seconds}
            }, status=status.HTTP_403_FORBIDDEN)

        # Generate OTP
        code = str(random.randint(100000, 999999))

        # Save next request time
        user.next_request_permission = timezone.now()
        user.save()

        # Prepare SMS payload
        payload = {
            "mobile": mobile,
            "templateId": TEMPLATE_ID,
            "parameters": [{"name": "CODE", "value": code}]
        }
        headers = {"Content-Type": "application/json", "Accept": "text/plain", "x-api-key": API_KEY}

        # Send SMS
        try:
            r = requests.post("https://api.sms.ir/v1/send/verify", json=payload, headers=headers)
            sms_response = r.json()
        except Exception as e:
            return Response({"detail": "SMS sending failed", "error": str(e)}, status=500)

        # Save code in session
        request.session[f"verify_{mobile}"] = code

        return Response({"sent": True, 
                        #  "code": code,
                           "sms_response": sms_response})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({"detail": "Internal Server Error", "error": str(e)}, status=500)




@api_view(["POST"])
@permission_classes([IsAuthenticated])
def verify_code(request):
    mobile = request.data.get("mobile")
    code = request.data.get("code")

    if not mobile or not code:
        return Response({"detail": "Mobile & code required"}, status=400)

    saved_code = request.session.get(f"verify_{mobile}")

    if not saved_code:
        return Response({"detail": "No code found or session expired"}, status=400)

    if saved_code != code:
        return Response({"verified": False, "detail": "Invalid code"}, status=400)

    # Verified
    del request.session[f"verify_{mobile}"]
    user = request.user
    user.phone = mobile
    user.verified = True
    user.save()



    return Response({
        "verified": True,
        "user_id": user.id,
        "phone": user.phone
    })












User = get_user_model()




@api_view(["POST"])
def send_verification_code_login(request):
    try:
        mobile = request.data.get("phone")

        if not mobile:
            return Response({"detail": "Mobile is required"}, status=400)

        # Track attempts using session
        last_request = request.session.get("otp_last_request")

        if last_request:
            last_time = timezone.datetime.fromisoformat(last_request)
            if last_time + LOCKOUT_TIME > timezone.now():
                remaining = int((last_time + LOCKOUT_TIME - timezone.now()).total_seconds())
                m, s = divmod(remaining, 60)
                return Response({
                    "detail": "تلاش بیش از حد. لطفاً کمی صبر کنید.",
                    "lockout": {"minutes": m, "seconds": s, "total_seconds": remaining}
                }, status=403)

        # Generate OTP
        code = str(random.randint(100000, 999999))

        # Lockout timestamp
        request.session["otp_last_request"] = timezone.now().isoformat()

        # Send SMS
        payload = {
            "mobile": mobile,
            "templateId": TEMPLATE_ID,
            "parameters": [{"name": "CODE", "value": code}]
        }
        headers = {"Content-Type": "application/json", "x-api-key": API_KEY}

        try:
            r = requests.post("https://api.sms.ir/v1/send/verify", json=payload, headers=headers)
            sms_response = r.json()
        except Exception as e:
            return Response({"detail": "SMS sending failed", "error": str(e)}, status=500)

        # Save OTP in session
        request.session[f"login_verify_{mobile}"] = code

        return Response({"sent": True, 
                        #  "code": code,
                          "sms_response": sms_response})

    except Exception as e:
        return Response({"detail": "Internal Error", "error": str(e)}, status=500)









User = get_user_model()


@api_view(["POST"])
def verify_code_login(request):
    mobile = request.data.get("phone")
    code = request.data.get("code")

    if not mobile or not code:
        return Response(
            {"detail": "شماره موبایل و کد الزامی است"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    session_key = f"login_verify_{mobile}"
    saved_code = request.session.get(session_key)

    if saved_code is None:
        return Response(
            {"detail": "کد منقضی شده یا وجود ندارد"},
            status=status.HTTP_410_GONE,
        )

    if str(saved_code) != str(code):
        return Response(
            {"detail": "کد وارد شده نادرست است"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # OTP correct → remove it
    request.session.pop(session_key, None)

    try:
        user = User.objects.get(phone=mobile)
    except User.DoesNotExist:
        return Response(
            {"detail": "کاربری با این شماره یافت نشد"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        token_serializer = CustomTokenObtainPairSerializer()
        refresh = token_serializer.get_token(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # refresh = RefreshToken.for_user(user)
    except Exception:
        return Response(
            {"detail": "خطا در تولید توکن"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    response = Response(
        {
            "detail": "ورود موفق",
            "access": access_token,
            "refresh": refresh_token,
            "user": {
                "id": user.id,
                "phone": user.phone,
                "role": getattr(user, "role", None),
            },
        },
        status=status.HTTP_200_OK,
    )

    response.set_cookie(
        key="refresh_token",
        value=str(refresh),
        httponly=True,
        secure=True,
        samesite="Strict",
        max_age=7 * 24 * 60 * 60,
    )

    response.set_cookie(
        key='access',
        value=access_token,
        httponly=True,
        secure=True,  # True in production
        samesite="Strict",
        max_age=7 * 24 * 60 * 60
    )


    return response





