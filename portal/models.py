from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import MinLengthValidator

class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True, validators=[MinLengthValidator(5)])
    course = models.CharField(max_length=100)
    year_level = models.PositiveSmallIntegerField(default=1)
    contact_no = models.CharField(max_length=30, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name() or self.user.username}"

class DocumentType(models.Model):
    name = models.CharField(max_length=120, unique=True)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    processing_days = models.PositiveSmallIntegerField(default=3)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class DocumentRequest(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("RELEASED", "Released"),
    ]

    reference_no = models.CharField(max_length=14, unique=True, editable=False)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="document_requests")
    doc_type = models.ForeignKey(DocumentType, on_delete=models.PROTECT)
    purpose = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    remarks = models.TextField(blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.reference_no:
            stamp = timezone.now().strftime("%y%m%d%H%M%S")
            self.reference_no = f"DR{stamp}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.reference_no

class Appointment(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("CANCELLED", "Cancelled"),
        ("DONE", "Done"),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="appointments")
    office = models.CharField(max_length=120)
    topic = models.CharField(max_length=200)
    schedule = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-schedule"]

    def __str__(self):
        return f"{self.office} - {self.schedule:%Y-%m-%d %I:%M %p}"

class FeePayment(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("VERIFIED", "Verified"),
        ("REJECTED", "Rejected"),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="payments")
    fee_name = models.CharField(max_length=140)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=60, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    admin_note = models.TextField(blank=True)
    paid_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-paid_at"]

    def __str__(self):
        return f"{self.fee_name} - {self.student.student_id}"

class Inquiry(models.Model):
    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("ANSWERED", "Answered"),
        ("CLOSED", "Closed"),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="inquiries")
    subject = models.CharField(max_length=160)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="OPEN")
    reply = models.TextField(blank=True)
    replied_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="replies")
    created_at = models.DateTimeField(auto_now_add=True)
    replied_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.subject
