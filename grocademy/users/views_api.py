from rest_framework import generics, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from .serializers import RegisterSerializer, UserSerializer, AdminUserSerializer, UserBalanceSerializer
from .models import CustomUser
from django.contrib.auth import login
from rest_framework_simplejwt.views import TokenObtainPairView

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        # -- DEBUG PRINT 1 --
        print("--- 1. MASUK KE CUSTOM LOGIN VIEW ---")
        
        response = super().post(request, *args, **kwargs)

        # -- DEBUG PRINT 2 --
        print(f"--- 2. STATUS CODE DARI JWT LOGIN: {response.status_code} ---")
        
        if response.status_code == 200:
            # -- DEBUG PRINT 3 --
            print("--- 3. JWT Login Berhasil, Mencoba Membuat Sesi Django ---")
            serializer = self.get_serializer(data=request.data)
            
            try:
                serializer.is_valid(raise_exception=True)
                user = serializer.user
                
                # -- DEBUG PRINT 4 --
                print(f"--- 4. User ditemukan: {user.username} ---")

                # Fungsi kritis yang seharusnya membuat cookie
                login(request, user)
                
                # -- DEBUG PRINT 5 --
                print("--- 5. Fungsi login() dari Django Telah Dipanggil ---")
                
                # Pengecekan krusial: apakah objek session ada di request?
                if request.session and request.session.session_key:
                    print(f"--- 6. BERHASIL! Objek session dibuat. Key: {request.session.session_key} ---")
                else:
                    print("--- 6. GAGAL! Tidak ada objek session di request. Masalah ada di middleware. ---")

            except Exception as e:
                print(f"--- !!! TERJADI ERROR SAAT MEMBUAT SESI: {e} ---")
        
        return response

class RegisterAPIView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

class UserDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
    
class UserAdminViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk admin mengelola pengguna.
    """
    queryset = CustomUser.objects.all().order_by('id')
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAdminUser] # Hanya admin yang bisa akses
    filter_backends = [SearchFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Mencegah admin menghapus dirinya sendiri
        if instance == request.user:
            return Response(
                {'error': 'You cannot delete your own account.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], serializer_class=UserBalanceSerializer)
    def balance(self, request, pk=None):
        """Action kustom untuk menambah saldo pengguna."""
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            increment = serializer.validated_data['increment']
            user.balance += increment
            user.save()
            return Response(
                {'status': 'balance updated', 'new_balance': user.balance},
                status=status.HTTP_200_OK
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)