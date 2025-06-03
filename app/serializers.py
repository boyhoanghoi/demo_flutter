# app/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ClothingCategory, ClothingItem, Outfit

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer cho User model, dùng cho việc đăng ký và lấy thông tin cơ bản.
    """
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password']
        extra_kwargs = {
            'email': {'required': True, 'allow_blank': False},
            'password': {'write_only': True}, # Mật khẩu chỉ để ghi, không trả về
            'first_name': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'], # create_user sẽ hash password
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user

class ClothingCategorySerializer(serializers.ModelSerializer):
    """
    Serializer cho ClothingCategory model.
    """
    class Meta:
        model = ClothingCategory
        fields = ['id', 'name']

class ClothingItemSerializer(serializers.ModelSerializer):
    """
    Serializer cho ClothingItem model, hỗ trợ upload ảnh.
    """
    category_name = serializers.CharField(source='category.name', read_only=True, allow_null=True)
    # Cho phép client gửi category_id khi tạo/cập nhật.
    category = serializers.PrimaryKeyRelatedField(
        queryset=ClothingCategory.objects.all(),
        allow_null=True,
        required=False, # Cho phép không có category
        write_only=True # Chỉ dùng để ghi, khi đọc sẽ dùng category_detail
    )
    category_detail = ClothingCategorySerializer(source='category', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)

    # Trường này sẽ trả về URL đầy đủ của ảnh để hiển thị
    image_display_url = serializers.SerializerMethodField(read_only=True)
    
    # Trường 'image' (ImageField) sẽ được dùng để upload file.
    # DRF sẽ tự động xử lý việc nhận file upload.
    # Khi đọc, nó sẽ trả về đường dẫn tương đối của file ảnh.
    # `required=False` và `allow_null=True` cho phép tạo item mà không cần ảnh.
    image = serializers.ImageField(required=False, allow_null=True, use_url=False) # use_url=False để nó trả về path, ta sẽ build full URL bằng SerializerMethodField


    class Meta:
        model = ClothingItem
        fields = [
            'id', 'user_username', 'name',
            'category', 'category_name', 'category_detail', # category là write_only, còn lại read_only
            'color', 'brand',
            'image',                # Dùng để upload và có thể trả về path
            'image_display_url',    # Dùng để hiển thị URL đầy đủ khi GET
            'notes', 'date_added', 'last_modified'
        ]
        read_only_fields = [
            'user_username', 'date_added', 'last_modified',
            'category_name', 'category_detail', 'image_display_url'
        ]
        # Trường 'image' có thể được ghi (upload) và đọc (lấy path).
        # Nếu chỉ muốn ghi, có thể thêm 'image': {'write_only': True} vào extra_kwargs

    def get_image_display_url(self, obj):
        """
        Tạo URL đầy đủ cho ảnh.
        """
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request:
                # request.build_absolute_uri sẽ tạo URL đầy đủ bao gồm http://host và MEDIA_URL
                return request.build_absolute_uri(obj.image.url)
            # Fallback nếu không có context request, trả về URL tương đối (ít xảy ra với ViewSet)
            return obj.image.url
        return None


class OutfitSerializer(serializers.ModelSerializer):
    """
    Serializer cho Outfit model.
    """
    user_username = serializers.CharField(source='user.username', read_only=True)
    # Hiển thị chi tiết các clothing_items khi đọc
    # ClothingItemSerializer đã được cập nhật để xử lý ảnh, nên ở đây cũng sẽ hiển thị ảnh đúng
    clothing_items_details = ClothingItemSerializer(source='clothing_items', many=True, read_only=True)
    
    clothing_items = serializers.PrimaryKeyRelatedField(
        queryset=ClothingItem.objects.all(),
        many=True,
        write_only=True,
        required=False
    )

    class Meta:
        model = Outfit
        fields = [
            'id', 'user_username', 'name', 'description',
            'clothing_items',           # Dùng để ghi (gửi list ID)
            'clothing_items_details',   # Dùng để đọc (hiển thị chi tiết items, bao gồm ảnh)
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user_username', 'created_at', 'updated_at', 'clothing_items_details']

    def create(self, validated_data):
        user = self.context['request'].user
        items_data = validated_data.pop('clothing_items', [])
        outfit = Outfit.objects.create(user=user, **validated_data)
        valid_items_to_add = []
        for item in items_data:
            if item.user == user:
                valid_items_to_add.append(item)
        if valid_items_to_add:
            outfit.clothing_items.set(valid_items_to_add)
        return outfit

    def update(self, instance, validated_data):
        user = self.context['request'].user
        items_data = validated_data.pop('clothing_items', None)
        
        # Cập nhật các trường của instance outfit
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        # Không cập nhật user ở đây, vì owner không nên thay đổi
        instance.save()

        if items_data is not None: # Nếu có gửi danh sách items mới
            valid_items_to_set = []
            for item in items_data:
                if item.user == user: # Đảm bảo item thuộc về user
                    valid_items_to_set.append(item)
            instance.clothing_items.set(valid_items_to_set) # .set() sẽ thay thế toàn bộ items cũ
        return instance