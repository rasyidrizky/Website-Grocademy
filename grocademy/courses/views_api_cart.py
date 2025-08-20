from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Cart, CartItem, Course, UserCourse
from .serializers import CartSerializer
from django.shortcuts import get_object_or_404
from django.db import transaction

class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def post(self, request):
        course_id = request.data.get('course_id')
        if not course_id:
            return Response({"error": "Course ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        course = get_object_or_404(Course, id=course_id)
        cart, created = Cart.objects.get_or_create(user=request.user)

        if UserCourse.objects.filter(user=request.user, course=course).exists():
             return Response({"error": "You have already purchased this course"}, status=status.HTTP_400_BAD_REQUEST)

        if CartItem.objects.filter(cart=cart, course=course).exists():
            return Response({"error": "Course is already in the cart"}, status=status.HTTP_400_BAD_REQUEST)

        CartItem.objects.create(cart=cart, course=course)
        return Response({"message": "Course added to cart"}, status=status.HTTP_201_CREATED)

class CartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart = get_object_or_404(Cart, user=request.user)
        cart_items = cart.items.all()

        if not cart_items.exists():
            return Response({"error": "Your cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        total_price = sum(item.course.price for item in cart_items)

        if request.user.balance < total_price:
            return Response({"error": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                request.user.balance -= total_price
                request.user.save()

                for item in cart_items:
                    UserCourse.objects.create(user=request.user, course=item.course)

                cart_items.delete()
        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "message": "Checkout successful!",
            "new_balance": request.user.balance
        }, status=status.HTTP_200_OK)