from django.db import models
from django.utils.translation import gettext as _

class BookInstanceStatus(models.TextChoices):
    MAINTENANCE = 'm', _('Maintenance')
    ON_LOAN = 'o', _('On loan')
    AVAILABLE = 'a', _('Available')
    RESERVED = 'r', _('Reserved')