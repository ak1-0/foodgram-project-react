import base64
import re

from django.core.files.base import ContentFile
from rest_framework.serializers import ImageField


class Base64ImageField(ImageField):
    """Сериализатор изображений"""

    _base64_image_pattern = re.compile(
        r"data:image/(?P<extension>\w+);base64,(?P<encoded_image>.*)")

    def to_internal_value(self, base64_data):
        """Преобразует base64-кодированное
        изображение во внутреннее значение"""
        if isinstance(base64_data, str):
            match = self._base64_image_pattern.match(base64_data)
            if match:
                extension = match.group("extension")
                encoded_image = match.group("encoded_image")
                decoded_image = base64.b64decode(encoded_image)
                content_file = ContentFile(decoded_image,
                                           name=f"temp.{extension}")

        return super().to_internal_value(content_file)
