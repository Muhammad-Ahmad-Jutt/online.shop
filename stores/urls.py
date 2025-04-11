from django.urls import path, include
from stores.views import CreateUpdateStore,CreateUpdateCategory,CreateUpdateStoreReview

urlpatterns =[
    path('store_management/',CreateUpdateStore.as_view(),name='Store_CRUD'),# get for getting a store, put for updating a store and post for creating a store
    path('category_management/',CreateUpdateCategory.as_view(),name='Category CRUD'),
    path('category_management/<slug:title>/',CreateUpdateCategory.as_view(),name='Category CRUD'),
    path('review/',CreateUpdateStoreReview.as_view(),name='Review Crud'),

]