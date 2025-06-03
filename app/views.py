from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
from .models import ClothingCategory, ClothingItem, Outfit
from .serializers import (
    UserSerializer, ClothingCategorySerializer,
    ClothingItemSerializer, OutfitSerializer
)
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly # Import custom permissions
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.authtoken.models import Token # Cho TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken # View đăng nhập sẵn có

class RegisterView(generics.CreateAPIView):
    """
    View để đăng ký người dùng mới.
    Không yêu cầu xác thực.
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny] # Ai cũng có thể truy cập để đăng ký
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save() # Serializer's create method handles user creation and password hashing
        token, created = Token.objects.get_or_create(user=user) # Tạo token cho user mới
        headers = self.get_success_headers(serializer.data)
        # Trả về thông tin user (không có password) và token
        user_data = UserSerializer(user, context=self.get_serializer_context()).data
        # Loại bỏ password khỏi user_data nếu nó vô tình được thêm vào
        user_data.pop('password', None)

        return Response(
            {
                'message': 'User registered successfully.',
                'user': user_data,
                'token': token.key
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class CustomObtainAuthToken(ObtainAuthToken):
    """
    View đăng nhập, trả về token cùng với thông tin user cơ bản.
    """
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        # Sử dụng UserSerializer để lấy thông tin user, loại bỏ password
        user_data = UserSerializer(user, context={'request': request}).data
        user_data.pop('password', None)

        return Response({
            'token': token.key,
            'user': user_data
        })

class ClothingCategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint cho phép xem hoặc sửa các loại quần áo.
    """
    queryset = ClothingCategory.objects.all()
    serializer_class = ClothingCategorySerializer
    permission_classes = [IsAdminOrReadOnly] # Chỉ admin mới có quyền tạo/sửa/xóa. Người dùng thường chỉ có quyền đọc.

class ClothingItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint cho phép người dùng quản lý quần áo của họ.
    """
    serializer_class = ClothingItemSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly] # Yêu cầu đăng nhập và là chủ sở hữu

    def get_queryset(self):
        """
        Chỉ trả về các món đồ thuộc về người dùng đang đăng nhập.
        """
        # Đảm bảo user đã được xác thực trước khi truy vấn
        user = self.request.user
        if user and user.is_authenticated:
            return ClothingItem.objects.filter(user=user)
        return ClothingItem.objects.none() # Trả về queryset rỗng nếu user chưa xác thực

    def perform_create(self, serializer):
        """
        Tự động gán `user` là người dùng đang đăng nhập khi tạo món đồ mới.
        """
        serializer.save(user=self.request.user) # user được gán ở đây

    def get_serializer_context(self):
        """
        Pass request to serializer context, useful for nested serializers or custom logic.
        """
        return {'request': self.request}


class OutfitViewSet(viewsets.ModelViewSet):
    """
    API endpoint cho phép người dùng quản lý các bộ đồ của họ.
    """
    serializer_class = OutfitSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        """
        Chỉ trả về các bộ đồ thuộc về người dùng đang đăng nhập.
        Bao gồm cả các clothing_items liên quan để tối ưu query nếu cần.
        """
        user = self.request.user
        if user and user.is_authenticated:
            # prefetch_related để tối ưu query khi lấy clothing_items_details
            return Outfit.objects.filter(user=user).prefetch_related('clothing_items__category')
        return Outfit.objects.none()

    def get_serializer_class(self):
        """
        Sử dụng serializer khác nhau cho các action khác nhau nếu cần.
        Ví dụ, một serializer đơn giản hơn cho list view.
        """
        # if self.action == 'list':
        #     return OutfitListSerializer # Một serializer khác nếu có
        return OutfitSerializer # Mặc định

    def get_serializer_context(self):
        """
        Truyền 'request' vào context của serializer.
        Điều này cần thiết để OutfitSerializer có thể truy cập request.user
        khi xử lý `clothing_items` (ví dụ, để filter queryset của PrimaryKeyRelatedField).
        """
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    def perform_create(self, serializer):
        """
        Tự động gán `user` là người dùng đang đăng nhập khi tạo bộ đồ mới.
        Serializer đã được cấu hình để xử lý `clothing_items` dựa trên ID.
        """
        # user đã được truyền vào context, serializer sẽ sử dụng nó
        serializer.save() # Không cần truyền user ở đây nữa vì serializer sẽ tự lấy từ context

    # Các action tùy chỉnh `add_clothing_item` và `remove_clothing_item` có thể hữu ích
    # nhưng với cách serializer hiện tại xử lý ManyToManyField (gửi list ID),
    # client có thể cập nhật toàn bộ list items của outfit qua PUT/PATCH request thông thường.
    # Tuy nhiên, nếu muốn API tường minh hơn cho việc thêm/xóa từng item, bạn có thể giữ chúng.

    @action(detail=True, methods=['post'], url_path='add-item', permission_classes=[IsAuthenticated, IsOwnerOrReadOnly])
    def add_clothing_item_to_outfit(self, request, pk=None):
        """
        Action tùy chỉnh để thêm một món đồ vào bộ đồ.
        Gửi body: { "clothing_item_id": <id> }
        """
        outfit = self.get_object() # Lấy outfit hiện tại (đã check permission IsOwner)
        clothing_item_id = request.data.get('clothing_item_id')

        if not clothing_item_id:
            return Response({'error': 'clothing_item_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Đảm bảo item thuộc về user hiện tại
            clothing_item = ClothingItem.objects.get(id=clothing_item_id, user=request.user)
        except ClothingItem.DoesNotExist:
            return Response({'error': 'Clothing item not found or does not belong to you.'}, status=status.HTTP_404_NOT_FOUND)

        if clothing_item in outfit.clothing_items.all():
             return Response({'message': 'Clothing item already in this outfit.'}, status=status.HTTP_200_OK)

        outfit.clothing_items.add(clothing_item)
        # Trả về outfit đã cập nhật
        serializer = self.get_serializer(outfit)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='remove-item', permission_classes=[IsAuthenticated, IsOwnerOrReadOnly])
    def remove_clothing_item_from_outfit(self, request, pk=None):
        """
        Action tùy chỉnh để xóa một món đồ khỏi bộ đồ.
        Gửi body: { "clothing_item_id": <id> }
        """
        outfit = self.get_object()
        clothing_item_id = request.data.get('clothing_item_id')

        if not clothing_item_id:
            return Response({'error': 'clothing_item_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Không cần check user ở đây vì nếu item không thuộc outfit của user thì nó sẽ không bị remove
            clothing_item = ClothingItem.objects.get(id=clothing_item_id)
        except ClothingItem.DoesNotExist:
            return Response({'error': 'Clothing item not found.'}, status=status.HTTP_404_NOT_FOUND)

        if clothing_item not in outfit.clothing_items.all():
            return Response({'error': 'Clothing item is not in this outfit.'}, status=status.HTTP_400_BAD_REQUEST)

        outfit.clothing_items.remove(clothing_item)
        serializer = self.get_serializer(outfit)
        return Response(serializer.data, status=status.HTTP_200_OK)