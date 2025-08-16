from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from .models import UserProfile
from utils import APIResponse

# Create your views here.
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        required = ["first_name", "last_name", "username", "email", "password", "confirm_password"]
        missing = [f for f in required if f not in data or not str(data[f]).strip()]
        if missing:
            return APIResponse.error(f"Field wajib: {', '.join(missing)}", http_status=400)

        if data["password"] != data["confirm_password"]:
            return APIResponse.error("Konfirmasi password tidak cocok", http_status=400)

        if User.objects.filter(Q(username=data["username"]) | Q(email=data["email"])).exists():
            return APIResponse.error("Email atau username sudah digunakan", http_status=400)

        try:
            validate_password(data["password"])
        except Exception as e:
            return APIResponse.error(" ".join(e.messages), http_status=400)

        user = User.objects.create_user(
            username=data["username"],
            email=data["email"],
            password=data["password"],
            first_name=data["first_name"],
            last_name=data["last_name"],
        )
        UserProfile.objects.create(user=user)

        return APIResponse.success("Registrasi berhasil", {
            "id": str(user.id),
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        }, http_status=201)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        identifier = request.data.get("identifier")
        password = request.data.get("password")

        if not identifier or not password:
            return APIResponse.error("identifier & password wajib", http_status=400)

        try:
            user = User.objects.get(Q(username=identifier) | Q(email=identifier))
        except User.DoesNotExist:
            return APIResponse.error("Kredensial salah", http_status=401)

        if not user.check_password(password):
            return APIResponse.error("Kredensial salah", http_status=401)

        tokens = RefreshToken.for_user(user)

        return APIResponse.success("Login berhasil", {
            "username": user.username,
            "access": str(tokens.access_token),
            "refresh": str(tokens),
        })


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return APIResponse.error("Refresh token wajib", http_status=400)

            token = RefreshToken(refresh_token)
            token.blacklist()
            return APIResponse.success("Logout berhasil")
        except Exception:
            return APIResponse.error("Token tidak valid atau sudah logout", http_status=400)


class SelfView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        u = request.user
        balance = getattr(getattr(u, "profile", None), "balance", 0)

        data = {
            "id": str(u.id),
            "username": u.username,
            "email": u.email,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "balance": balance,
        }
        return APIResponse.success("OK", data)