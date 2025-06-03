# app/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class ClothingCategory(models.Model):
    name = models.CharField(_("Tên loại"), max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Loại quần áo")
        verbose_name_plural = _("Các loại quần áo")
        ordering = ['name']

class ClothingItem(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='clothing_items',
        verbose_name=_("Người dùng")
    )
    name = models.CharField(_("Tên món đồ"), max_length=200)
    category = models.ForeignKey(
        ClothingCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='items',
        verbose_name=_("Loại")
    )
    color = models.CharField(_("Màu sắc"), max_length=50, blank=True)
    brand = models.CharField(_("Thương hiệu"), max_length=100, blank=True)

    # THAY ĐỔI Ở ĐÂY: Bỏ image_url và dùng ImageField
    # image_url = models.URLField(_("Link ảnh"), max_length=500, blank=True, null=True)
    image = models.ImageField(
        _("Ảnh"),
        upload_to='clothing_images/', # Ảnh sẽ được lưu vào thư mục media/clothing_images/
        blank=True,
        null=True
    )
    # END THAY ĐỔI

    notes = models.TextField(_("Ghi chú"), blank=True)
    date_added = models.DateTimeField(_("Ngày thêm"), auto_now_add=True)
    last_modified = models.DateTimeField(_("Lần sửa cuối"), auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    # Tùy chọn: Thêm một property để lấy URL đầy đủ của ảnh
    @property
    def image_full_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url # Django sẽ tự thêm MEDIA_URL vào đây
        return None

    class Meta:
        verbose_name = _("Món đồ")
        verbose_name_plural = _("Các món đồ")
        ordering = ['-last_modified']

# Model Outfit giữ nguyên
class Outfit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='outfits', verbose_name=_("Người dùng"))
    name = models.CharField(_("Tên bộ đồ"), max_length=200)
    description = models.TextField(_("Mô tả"), blank=True)
    clothing_items = models.ManyToManyField(ClothingItem, related_name='outfits', verbose_name=_("Các món đồ"), blank=True)
    created_at = models.DateTimeField(_("Ngày tạo"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Lần cập nhật cuối"), auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    class Meta:
        verbose_name = _("Bộ đồ")
        verbose_name_plural = _("Các bộ đồ")
        ordering = ['-updated_at']