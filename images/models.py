import os
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


# === Utility upload paths ===
def upload_to_original(instance, filename):
    """Generate unique path for original uploads: uploads/originals/<name>_<timestamp>.<ext>"""
    name, ext = os.path.splitext(filename)
    timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c for c in name if c.isalnum() or c in ('-', '_'))[:50]
    return f"uploads/originals/{safe_name}_{timestamp}{ext.lower()}"


def upload_to_processed(instance, filename):
    """Generate unique path for processed versions: uploads/processed/<name>_<timestamp>.<ext>"""
    name, ext = os.path.splitext(filename)
    timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c for c in name if c.isalnum() or c in ('-', '_'))[:50]
    return f"uploads/processed/{safe_name}_{timestamp}{ext.lower()}"


# === Model for original uploads ===
class ImageItem(models.Model):
    """
    Represents an uploaded image.
    Each uploaded image can have multiple processed/manipulated versions.
    """

    title = models.CharField(max_length=200, blank=True)
    owner = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="uploaded_images"
    )
    original = models.ImageField(upload_to=upload_to_original)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Image Item"
        verbose_name_plural = "Image Items"

    def __str__(self):
        return self.title or f"Image {self.pk}"

    @property
    def filename(self):
        """Return the base filename (without path) of the original image."""
        return os.path.basename(self.original.name)

    @property
    def latest_version(self):
        """Return the most recent processed version, if any."""
        return self.versions.first() if self.versions.exists() else None

    @property
    def original_url(self):
        """Return the URL of the original image."""
        return self.original.url if self.original else None

    def delete(self, *args, **kwargs):
        """Delete associated image files from storage when record is removed."""
        if self.original and os.path.exists(self.original.path):
            os.remove(self.original.path)
        for version in self.versions.all():
            version.delete()
        super().delete(*args, **kwargs)


# === Model for processed versions ===
class ProcessedVersion(models.Model):
    """
    Represents a processed or manipulated version of an uploaded image.
    Each version is stored separately but linked to its original ImageItem.
    """

    item = models.ForeignKey(
        ImageItem,
        related_name="versions",
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to=upload_to_processed)
    note = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Processed Version"
        verbose_name_plural = "Processed Versions"

    def __str__(self):
        return f"Processed Version {self.pk} ({self.note or 'No note'})"

    @property
    def filename(self):
        """Return the base filename (without path) of the processed image."""
        return os.path.basename(self.image.name)

    @property
    def image_url(self):
        """Return the URL for easy template access."""
        return self.image.url if self.image else None

    def delete(self, *args, **kwargs):
        """Remove image file from storage when record is deleted."""
        if self.image and os.path.exists(self.image.path):
            os.remove(self.image.path)
        super().delete(*args, **kwargs)
