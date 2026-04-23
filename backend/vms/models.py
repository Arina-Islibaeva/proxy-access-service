from django.conf import settings
from django.db import models


class VirtualMachine(models.Model):
    PROTOCOL_CHOICES = [
        ("http", "HTTP"),
        ("https", "HTTPS"),
        ("socks5", "SOCKS5"),
    ]

    name = models.CharField(max_length=100, unique=True)
    host = models.CharField(max_length=255)
    port = models.PositiveIntegerField()
    protocol = models.CharField(max_length=10, choices=PROTOCOL_CHOICES)
    is_active = models.BooleanField(default=True)
    current_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_vms",
    )
    last_used_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Virtual machine"
        verbose_name_plural = "Virtual machines"
        ordering = ["id"]

    def __str__(self):
        return f"{self.name} ({self.protocol}://{self.host}:{self.port})"
