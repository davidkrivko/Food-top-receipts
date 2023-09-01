from django.contrib.auth import authenticate, login, logout
from rest_framework import status, views
from rest_framework.response import Response
from .serializers import UserModelSerializer


class RegistrationAPIView(views.APIView):
    def post(self, request):
        serializer = UserModelSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(serializer.validated_data["password"])
            user.save()
            login(request, user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(views.APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({"message": "Logged in successfully."})
        return Response(
            {"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutAPIView(views.APIView):
    def get(self, request):
        logout(request)
        return Response({"message": "Logged out successfully."})
