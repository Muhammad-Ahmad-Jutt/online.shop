from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from users.permissions import IsAuthenticatedAndVerified
from rest_framework.response import Response
from rest_framework import status   
from django.contrib.auth.models import update_last_login
from django.contrib.auth import logout
import datetime
import logging
from stores.serializer import CreateStoreSerializer,StoreUpdateSerializer,GetStoreSerializer
from stores.models import Store
# Create your views here.
class CreateUpdateStore(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
        try:
            serializer = CreateStoreSerializer(data = request.data)
            if serializer.is_valid():
                store_title = serializer.validated_data['title']
                serializer.save()
                return Response({
                    "success": True,
                    "message": f"Store {store_title}Created Successfully"
                    }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "success": False,
                    "errors": serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "success":False,
                "message":f"Unexpected error--> {str(e)}"
                }, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def put(self, request):
        try:
            serializer = StoreUpdateSerializer(data=request.data)
            if serializer.is_valid():
                serializer.update_store(serializer.validated_data)
                store_title=serializer.validated_data['title']
                return Response({
                    "success": True,
                    "message": f"Store {store_title}Created Successfully"
                    }, status=status.HTTP_200_OK)

            else:
                return Response({
                    "success": False,
                    "errors": serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "success":False,
                "message":f"Unexpected error--> {str(e)}"
                }, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
    def get(self, request):
        try:
            store = Store.objects.filter(user_id=request.user.id).first()
            if not store:
                return Response({"success": False, "message": "No Store Found"}, status=status.HTTP_404_NOT_FOUND)
              

            serializer = GetStoreSerializer(store)
            return Response({
                "success": True,
                "message": "Data Retrieved Successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "success": False,
                "message": f"Unexpected error → {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
