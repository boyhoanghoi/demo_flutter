from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ClothingCategoryViewSet, ClothingItemViewSet, OutfitViewSet,
    RegisterView, CustomObtainAuthToken
)

# DefaultRouter tự động tạo các URL pattern cho ViewSets.
# Ví dụ: /clothing-items/, /clothing-items/{id}/
router = DefaultRouter()
router.register(r'categories', ClothingCategoryViewSet, basename='clothingcategory')
router.register(r'clothing-items', ClothingItemViewSet, basename='clothingitem')
router.register(r'outfits', OutfitViewSet, basename='outfit')

# Các URL cho API của app này
urlpatterns = [
    path('', include(router.urls)), # Bao gồm các URL được tạo bởi router
    # Các URL cho authentication
    path('auth/register/', RegisterView.as_view(), name='auth_register'),
    path('auth/login/', CustomObtainAuthToken.as_view(), name='auth_login'),
    # Bạn có thể thêm logout view nếu cần.
    # Với TokenAuthentication, logout thường được xử lý ở client bằng cách xóa token.
    # Nếu dùng session, bạn có thể tạo một view gọi django.contrib.auth.logout.
]
