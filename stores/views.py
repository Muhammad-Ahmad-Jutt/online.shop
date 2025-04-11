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
from stores.serializer import CreateStoreSerializer,StoreUpdateSerializer,GetStoreSerializer,CreateCategorySerializer,CategoryListingSerializer,UpdateCategorySerializer,PostReviewSerializer,GetReviewSerializer
from stores.models import Store,Category,Store_Review,Store_Images
# Create your views here.
class CreateUpdateStore(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
        try:
            serializer = CreateStoreSerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                store = serializer.save()
                store_title = store.title
                return Response({
                    "success": True,
                    "message": f"Store {store_title} Created Successfully"
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
            store = Store.objects.filter(user_id=request.user.id).first()
            if not store:
                return Response({
                    "success": False,
                    "message": 'Store Not Found'
                    }, status=status.HTTP_400_BAD_REQUEST)
            serializer = StoreUpdateSerializer(store,data = request.data,context={"request": request},partial=True)
            if serializer.is_valid():
                store_object = serializer.save()
                complete_data = StoreUpdateSerializer(store_object).data
                return Response({
                    "success": True,
                    "message": f"Resource Update Successful",
                    "data": complete_data
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
              

            serializer = GetStoreSerializer(store, context={"request":request})
            # if serializer.is_valid():    
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
    def delete(self,request):
        try:
            store = Store.objects.filter(user_id=request.user.id).first()
            if not store:
                return Response({"success": False, "message": "No Store Found"}, status=status.HTTP_404_NOT_FOUND)
            store.delete()
            return Response({
                "success": True,
                "message": "Store Deleted Successfully"
                }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "message": f"Unexpected error → {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CreateUpdateCategory(APIView):
    # permission_classes=[IsAuthenticated]
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        else:
            return [IsAuthenticated()]
        return super().get_permissions()

    def post(self, request):
        try:
            if not 'parent_category' in request.data:
                request.data['parent_category']=None
                category_check = Category.objects.filter(category_title=request.data.get('category_title')).first()
                if category_check:
                    return Response({"success":False, "message": "Category Already Exist", "Name":category_check.category_title}, status=status.HTTP_400_BAD_REQUEST)
            serializer = CreateCategorySerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success":True,
                    "message": "Category Create Successful",
                    "category_title": serializer.data['category_title']
                },status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "success": False,
                    "errors": serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "success": False,
                "message": f"Unexpected error → {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def get(self, request):
        try:
            categories = Category.objects.filter(parent_category=request.data.get('parent_category'))

            # Serialize the categories
            serializer = CategoryListingSerializer(categories, many=True)

            # Return the response
            return Response({
                "success": True,
                "message": "Categories retrieved successfully",
                "data": serializer.data
                }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "message": f"Unexpected error → {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def delete(self, request):
        try:
            title = request.query_params.get('title')
            parent_id = request.data.get('parent_id',None)
            if isinstance(parent_id,int):
                category = Category.objects.filter(category_title=title,user_id=request.user.id,parent_id=parent_id).first()
            else:
                category = Category.objects.filter(category_title=title,user_id=request.user.id,parent_id=null).first()
            if not category:
                return Response({
                    "success": False,
                    "errors": "Category Not found"
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            category.delete()
            return Response({
                "success": True,
                "message": "Category Deleted Successfully"
                }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "message": f"Inexpected error → {str(e)}"
                },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def put(self, request):
        try:
            category = None
            if not 'new_category_title' in request.data and not 'new_parent_category' in request.data:
                category = Category.objects.filter(category_title=request.data.get('category_title'),user_id=request.user.id).first() # getting old category object to manipulate
            if 'new_category_title' in request.data: # save the title
                category = Category.objects.filter(category_title=request.data.get('category_title'),user_id=request.user.id).first() # getting old category object to manipulate
            if 'new_parent_category' in request.data: # save the title
                category = Category.objects.filter(category_title=request.data.get('category_title'),user_id=request.user.id,parent_category=request.data.get("parent_category")).first() # getting old category object to manipulate
                request.data['parent_category'] = request.data.get('new_parent_category') # map the title as new title in place of title
                request.data.pop('new_parent_category')
            if 'new_category_title' in request.data:
                request.data['category_title'] = request.data.get('new_category_title') # map the title as new title in place of title
                request.data.pop('new_category_title')

            if not category:
                return Response({
                    "success": False,
                    "errors": "Category Not found"
                    }, status=status.HTTP_400_BAD_REQUEST)
            serializer = UpdateCategorySerializer(category,data=request.data, context={'request': request},partial=True)# sending category object, and title data

            if serializer.is_valid():
                new_data = serializer.save()
                complete_data = UpdateCategorySerializer(new_data).data
                return Response({
                    "success": True,
                    "message": "Category Update Successful",
                    "data":complete_data
                    }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "success": False,
                    "errors": serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "success": False,
                "message": f"Unexpected error → {str(e)}"
                },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class CreateUpdateStoreReview(APIView):
    permission_classes=[IsAuthenticated]
    def delete(self, request):
        try:
            review_id = request.data.get("review_id")
            review =Store_Review.objects.filter(id=review_id).first()
            if not review:
                return Response({
                    "success": False,
                    "errors": "Review Not found"
                    }, status=status.HTTP_400_BAD_REQUEST)

            review.delete()
            return Response({
                "success": True,
                "message": "Review Deleted Successfully"
                }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success":False,
                "message":f"Unexpected Error → {str(e)}"
            },status = status.HTTP_500_INTERNAL_SERVER_ERROR)
    def put(self, request):
        try:
        
            # Serialize the review data and validate
            review_id = request.data.get("review_id")
            review =Store_Review.objects.filter(id=review_id).first()
            serializer = PostReviewSerializer(review,data=request.data, context={"request": request})
            
            if serializer.is_valid():
                # Save the review and return the response
                review = serializer.save()
                return Response({
                    "success": True,
                    "message": "Review Updated successfully",
                    "review": serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "success": False,
                    "message": "Invalid data",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "success":False,
                "message":f"Unexpected Error → {str(e)}"
            },status = status.HTTP_500_INTERNAL_SERVER_ERROR)
    def get(self, request):
        try:
            store_id = request.data.get("store_id")
            store = Store.objects.filter(id = store_id)
            store_reviews = Store_Review.objects.filter(store_id=store_id)
            serializer = GetReviewSerializer(store_reviews, many=True)
            return Response({
                "success":True,
                "data":serializer.data
            })
        except Exception as e:
            return Response({
                "success":False,
                "message":f"Unexpected Error → {str(e)}"
            },status = status.HTTP_500_INTERNAL_SERVER_ERROR)
    def post(self, request):
        try:
            store_id = request.data.get('store_id')
            if not store_id:
                return Response({
                    "success": False,
                    "message": "store_id is required"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Try to retrieve the store
            try:
                store = Store.objects.get(id=store_id)
            except Store.DoesNotExist:
                return Response({
                    "success": False,
                    "message": "Store not found"
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Serialize the review data and validate
            serializer = PostReviewSerializer(data=request.data, context={"request": request})
            
            if serializer.is_valid():
                # Save the review and return the response
                review = serializer.save(store_id=store)
                return Response({
                    "success": True,
                    "message": "Review added successfully",
                    "review": serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "success": False,
                    "message": "Invalid data",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "success": False,
                "message": f"Unexpected error → {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StoreImages(APIView):
    permission_classes=[IsAuthenticated]
    def put(self,request):
        try:
            image_id = request.data.get('image_id')
            flag = request.data.get('flag')
            if not image_id or not flag:
                return Response({
                    "success": False,
                    "errors": "image_id and flag is required"
                    }, status=status.HTTP_400_BAD_REQUEST)
            image = Store_Images.objects.get(id=image_id,user_id =request.user.id).first()
            store_id = image.store_id
            if not image:
                return Response({
                    "success": False,
                    "errors": "Image Not found"
                    }, status=status.HTTP_400_BAD_REQUEST)
            # getting the store
            image = Store_Images.objects.filter(id=image_id,user_id =request.user.id).first()
            store_id = image.store_id
            store = Store.objects.filter(id=store_id).first()
            if not request.user.id == store.user_id:
                return Response({
                    "success": False,
                    "errors": "Only owner can change the dp"
                    }, status=status.HTTP_400_BAD_REQUEST)
            images = Store_Images.objects.filter(store_id=store,).exclude(image).update(display=!flag)
            image = Store_Images.objects.filter(id=image_id,user_id =request.user.id).first()
