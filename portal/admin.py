from django.contrib import admin
from .models import StudentProfile, DocumentType, DocumentRequest, Appointment, FeePayment, Inquiry

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("student_id", "user", "course", "year_level", "created_at")
    search_fields = ("student_id", "user__username", "user__first_name", "user__last_name")

@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "fee", "processing_days", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)

@admin.register(DocumentRequest)
class DocumentRequestAdmin(admin.ModelAdmin):
    list_display = ("reference_no", "student", "doc_type", "status", "requested_at")
    list_filter = ("status", "doc_type")
    search_fields = ("reference_no", "student__student_id", "student__user__username")

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("student", "office", "schedule", "status")
    list_filter = ("office", "status")
    search_fields = ("student__student_id", "office", "topic")

@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ("student", "fee_name", "amount", "status", "paid_at")
    list_filter = ("status",)
    search_fields = ("student__student_id", "fee_name", "reference")

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ("student", "subject", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("student__student_id", "subject")
