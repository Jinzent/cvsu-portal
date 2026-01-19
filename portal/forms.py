from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from .models import StudentProfile, DocumentType, DocumentRequest, Appointment, FeePayment, Inquiry

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    student_id = forms.CharField(required=True)
    course = forms.CharField(required=True)
    year_level = forms.IntegerField(min_value=1, max_value=6, required=True)
    contact_no = forms.CharField(required=False)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "student_id",
            "course",
            "year_level",
            "contact_no",
            "password1",
            "password2",
        )

class DocumentTypeForm(forms.ModelForm):
    class Meta:
        model = DocumentType
        fields = ("name", "fee", "processing_days", "is_active")

class DocumentRequestForm(forms.ModelForm):
    class Meta:
        model = DocumentRequest
        fields = ("doc_type", "purpose")

class DocumentRequestStaffForm(forms.ModelForm):
    class Meta:
        model = DocumentRequest
        fields = ("status", "remarks")

class AppointmentForm(forms.ModelForm):
    schedule = forms.DateTimeField(widget=forms.DateTimeInput(attrs={"type": "datetime-local"}))

    class Meta:
        model = Appointment
        fields = ("office", "topic", "schedule")

    def clean_schedule(self):
        val = self.cleaned_data["schedule"]
        if val <= timezone.now():
            raise forms.ValidationError("Schedule must be in the future.")
        return val

class AppointmentStaffForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ("status", "notes")

class FeePaymentForm(forms.ModelForm):
    class Meta:
        model = FeePayment
        fields = ("fee_name", "amount", "reference", "paid_at")
        widgets = {
            "paid_at": forms.DateTimeInput(attrs={"type": "datetime-local"})
        }

class FeePaymentStaffForm(forms.ModelForm):
    class Meta:
        model = FeePayment
        fields = ("status", "admin_note")

class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ("subject", "message")

class InquiryStaffForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ("status", "reply")
