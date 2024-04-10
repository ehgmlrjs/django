import jwt
from rest_framework.views import APIView
from .serializers import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import authenticate


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "성공"}, status=status.HTTP_201_CREATED)
        errors = serializer.errors
        if errors.get('email') is not None:
            return Response({'message':'이미 있는 이메일'}, status=status.HTTP_400_BAD_REQUEST)
        elif errors.get('nickname') is not None:
            return Response({'message':'이미 있는 닉네임'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "입력한 정보를 확인해 주세요"}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response({'error': 'Please provide both email and password'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=email, password=password)
        if user:
            refresh = TokenObtainPairSerializer.get_token(user)
            access = refresh.access_token
            serializer = UserSerializer(user)

            response = Response({'message':'로그인 성공','user':serializer.data},status=status.HTTP_201_CREATED)
            response.set_cookie('access_token', access, httponly=True, secure=False)
            response.set_cookie('refresh_token', refresh, httponly=True, secure=False, max_age=86400)
            return response
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    def delete(self, request):
        response = Response({
                'message': 'Logout success'
            }, status=status.HTTP_200_OK)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response
    

class TestView(APIView):
    def post(self, request):
        access = request.COOKIES.get('access_token')
        refresh = request.COOKIES.get('refresh_token')
        return Response({'access':access,'refresh':refresh})