import os

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .helpers import convert_to_mp4, convert_to_thumbnail
from .models import ProductVideoImage


@receiver(post_save, sender=ProductVideoImage)
def process_video_after_upload(sender, instance, created, **kwargs):
    if not created or not instance.videoUrl:
        return

    input_path = instance.videoUrl.path
    base, _ = os.path.splitext(input_path)
    output_path = base.replace('originals', 'processed') + '.mp4'

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    success, _ = convert_to_mp4(input_path, output_path)

    if not success:
        return

    relative_output_path = os.path.relpath(output_path, settings.MEDIA_ROOT)
    instance.processedVideoUrl.name = relative_output_path.replace("\\", "/")
    instance.save(update_fields=['processedVideoUrl'])


@receiver(post_save, sender=ProductVideoImage)
def generate_thumbnail_after_video_processing(sender, instance, created, **kwargs):
    if not created or not instance.processedVideoUrl:
        return

    input_path = instance.processedVideoUrl.path
    base, _ = os.path.splitext(input_path)
    thumbnail_path = base.replace('processed', 'thumbnails') + '.jpg'

    os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)

    success, _ = convert_to_thumbnail(input_path, thumbnail_path)

    if not success:
        return

    relative_thumbnail_path = os.path.relpath(thumbnail_path, settings.MEDIA_ROOT)
    instance.thumbnail.name = relative_thumbnail_path.replace("\\", "/")
    instance.save(update_fields=['thumbnail'])
