from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Count
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import (
    RegisterForm,
    DocumentTypeForm,
    DocumentRequestForm,
    DocumentRequestStaffForm,
    AppointmentForm,
    AppointmentStaffForm,
    FeePaymentForm,
    FeePaymentStaffForm,
    InquiryForm,
    InquiryStaffForm,
)
from .models import StudentProfile, DocumentType, DocumentRequest, Appointment, FeePayment, Inquiry

def is_staff_user(user):
    return user.is_authenticated and user.is_staff

def home(request):
    return render(request, "portal/home.html")

def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data["email"]
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.save()

            StudentProfile.objects.create(
                user=user,
                student_id=form.cleaned_data["student_id"],
                course=form.cleaned_data["course"],
                year_level=form.cleaned_data["year_level"],
                contact_no=form.cleaned_data.get("contact_no", ""),
            )

            login(request, user)
            messages.success(request, "Account created. Welcome!")
            return redirect("dashboard")
    else:
        form = RegisterForm()

    return render(request, "portal/register.html", {"form": form})

def _profile_or_403(user):
    try:
        return user.studentprofile
    except StudentProfile.DoesNotExist:
        return None

@login_required
def dashboard(request):
    profile = _profile_or_403(request.user)
    staff = request.user.is_staff

    if staff:
        req_counts = DocumentRequest.objects.values("status").annotate(total=Count("id")).order_by()
        appt_counts = Appointment.objects.values("status").annotate(total=Count("id")).order_by()
        pay_counts = FeePayment.objects.values("status").annotate(total=Count("id")).order_by()
        inq_counts = Inquiry.objects.values("status").annotate(total=Count("id")).order_by()

        recent_requests = DocumentRequest.objects.select_related("student", "doc_type").order_by("-requested_at")[:8]
        recent_appointments = Appointment.objects.select_related("student").order_by("-created_at")[:8]

        return render(
            request,
            "portal/dashboard_staff.html",
            {
                "req_counts": req_counts,
                "appt_counts": appt_counts,
                "pay_counts": pay_counts,
                "inq_counts": inq_counts,
                "recent_requests": recent_requests,
                "recent_appointments": recent_appointments,
            },
        )

    if not profile:
        return HttpResponseForbidden("Student profile not found.")

    my_requests = profile.document_requests.select_related("doc_type").order_by("-requested_at")[:6]
    my_appointments = profile.appointments.order_by("-schedule")[:6]
    my_payments = profile.payments.order_by("-paid_at")[:6]
    my_inquiries = profile.inquiries.order_by("-created_at")[:6]

    return render(
        request,
        "portal/dashboard_student.html",
        {
            "profile": profile,
            "my_requests": my_requests,
            "my_appointments": my_appointments,
            "my_payments": my_payments,
            "my_inquiries": my_inquiries,
        },
    )

@login_required
def doc_type_list(request):
    if not request.user.is_staff:
        qs = DocumentType.objects.filter(is_active=True).order_by("name")
    else:
        qs = DocumentType.objects.all().order_by("name")

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(name__icontains=q)

    return render(request, "portal/doc_type_list.html", {"items": qs, "q": q})

@user_passes_test(is_staff_user)
def doc_type_create(request):
    if request.method == "POST":
        form = DocumentTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Document type created.")
            return redirect("doc_type_list")
    else:
        form = DocumentTypeForm()
    return render(request, "portal/form.html", {"form": form, "title": "New Document Type"})

@user_passes_test(is_staff_user)
def doc_type_update(request, pk):
    obj = get_object_or_404(DocumentType, pk=pk)
    if request.method == "POST":
        form = DocumentTypeForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Document type updated.")
            return redirect("doc_type_list")
    else:
        form = DocumentTypeForm(instance=obj)
    return render(request, "portal/form.html", {"form": form, "title": "Edit Document Type"})

@user_passes_test(is_staff_user)
def doc_type_delete(request, pk):
    obj = get_object_or_404(DocumentType, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Document type deleted.")
        return redirect("doc_type_list")
    return render(request, "portal/confirm_delete.html", {"obj": obj, "title": "Delete Document Type"})

@login_required
def request_list(request):
    staff = request.user.is_staff
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()

    if staff:
        qs = DocumentRequest.objects.select_related("student", "doc_type").all()
    else:
        profile = _profile_or_403(request.user)
        if not profile:
            return HttpResponseForbidden("Student profile not found.")
        qs = profile.document_requests.select_related("doc_type").all()

    if status:
        qs = qs.filter(status=status)

    if q:
        qs = qs.filter(
            Q(reference_no__icontains=q)
            | Q(doc_type__name__icontains=q)
            | Q(purpose__icontains=q)
            | Q(student__student_id__icontains=q)
        )

    qs = qs.order_by("-requested_at")
    return render(request, "portal/request_list.html", {"items": qs, "q": q, "status": status, "staff": staff})

@login_required
def request_detail(request, pk):
    staff = request.user.is_staff
    if staff:
        obj = get_object_or_404(DocumentRequest.objects.select_related("student", "doc_type"), pk=pk)
    else:
        profile = _profile_or_403(request.user)
        if not profile:
            return HttpResponseForbidden("Student profile not found.")
        obj = get_object_or_404(DocumentRequest.objects.select_related("doc_type"), pk=pk, student=profile)
    return render(request, "portal/request_detail.html", {"obj": obj, "staff": staff})

@login_required
def request_create(request):
    profile = _profile_or_403(request.user)
    if not profile:
        return HttpResponseForbidden("Student profile not found.")

    if request.method == "POST":
        form = DocumentRequestForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.student = profile
            obj.save()
            messages.success(request, f"Request submitted. Ref: {obj.reference_no}")
            return redirect("request_list")
    else:
        form = DocumentRequestForm()

    return render(request, "portal/form.html", {"form": form, "title": "New Document Request"})

@login_required
def request_update(request, pk):
    profile = _profile_or_403(request.user)
    if not profile:
        return HttpResponseForbidden("Student profile not found.")

    obj = get_object_or_404(DocumentRequest, pk=pk, student=profile)
    if obj.status != "PENDING":
        return HttpResponseForbidden("Only pending requests can be edited.")

    if request.method == "POST":
        form = DocumentRequestForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Request updated.")
            return redirect("request_detail", pk=obj.pk)
    else:
        form = DocumentRequestForm(instance=obj)

    return render(request, "portal/form.html", {"form": form, "title": "Edit Document Request"})

@login_required
def request_delete(request, pk):
    profile = _profile_or_403(request.user)
    if not profile:
        return HttpResponseForbidden("Student profile not found.")

    obj = get_object_or_404(DocumentRequest, pk=pk, student=profile)
    if obj.status != "PENDING":
        return HttpResponseForbidden("Only pending requests can be deleted.")

    if request.method == "POST":
        obj.delete()
        messages.success(request, "Request deleted.")
        return redirect("request_list")

    return render(request, "portal/confirm_delete.html", {"obj": obj, "title": "Delete Document Request"})

@user_passes_test(is_staff_user)
def request_process(request, pk):
    obj = get_object_or_404(DocumentRequest, pk=pk)
    if request.method == "POST":
        form = DocumentRequestStaffForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Request processed.")
            return redirect("request_detail", pk=obj.pk)
    else:
        form = DocumentRequestStaffForm(instance=obj)

    return render(request, "portal/form.html", {"form": form, "title": f"Process Request {obj.reference_no}"})

@login_required
def appointment_list(request):
    staff = request.user.is_staff
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()

    if staff:
        qs = Appointment.objects.select_related("student").all()
    else:
        profile = _profile_or_403(request.user)
        if not profile:
            return HttpResponseForbidden("Student profile not found.")
        qs = profile.appointments.all()

    if status:
        qs = qs.filter(status=status)

    if q:
        qs = qs.filter(Q(office__icontains=q) | Q(topic__icontains=q) | Q(student__student_id__icontains=q))

    return render(request, "portal/appointment_list.html", {"items": qs, "q": q, "status": status, "staff": staff})

@login_required
def appointment_create(request):
    profile = _profile_or_403(request.user)
    if not profile:
        return HttpResponseForbidden("Student profile not found.")

    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.student = profile
            obj.save()
            messages.success(request, "Appointment requested.")
            return redirect("appointment_list")
    else:
        form = AppointmentForm()

    return render(request, "portal/form.html", {"form": form, "title": "New Appointment"})

@login_required
def appointment_update(request, pk):
    profile = _profile_or_403(request.user)
    if not profile:
        return HttpResponseForbidden("Student profile not found.")

    obj = get_object_or_404(Appointment, pk=pk, student=profile)
    if obj.status != "PENDING":
        return HttpResponseForbidden("Only pending appointments can be edited.")

    if request.method == "POST":
        form = AppointmentForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Appointment updated.")
            return redirect("appointment_list")
    else:
        form = AppointmentForm(instance=obj)

    return render(request, "portal/form.html", {"form": form, "title": "Edit Appointment"})

@login_required
def appointment_delete(request, pk):
    profile = _profile_or_403(request.user)
    if not profile:
        return HttpResponseForbidden("Student profile not found.")

    obj = get_object_or_404(Appointment, pk=pk, student=profile)
    if obj.status != "PENDING":
        return HttpResponseForbidden("Only pending appointments can be deleted.")

    if request.method == "POST":
        obj.delete()
        messages.success(request, "Appointment deleted.")
        return redirect("appointment_list")

    return render(request, "portal/confirm_delete.html", {"obj": obj, "title": "Delete Appointment"})

@user_passes_test(is_staff_user)
def appointment_process(request, pk):
    obj = get_object_or_404(Appointment, pk=pk)
    if request.method == "POST":
        form = AppointmentStaffForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Appointment processed.")
            return redirect("appointment_list")
    else:
        form = AppointmentStaffForm(instance=obj)

    return render(request, "portal/form.html", {"form": form, "title": "Process Appointment"})

@login_required
def payment_list(request):
    staff = request.user.is_staff
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()

    if staff:
        qs = FeePayment.objects.select_related("student").all()
    else:
        profile = _profile_or_403(request.user)
        if not profile:
            return HttpResponseForbidden("Student profile not found.")
        qs = profile.payments.all()

    if status:
        qs = qs.filter(status=status)

    if q:
        qs = qs.filter(Q(fee_name__icontains=q) | Q(reference__icontains=q) | Q(student__student_id__icontains=q))

    return render(request, "portal/payment_list.html", {"items": qs, "q": q, "status": status, "staff": staff})

@login_required
def payment_create(request):
    profile = _profile_or_403(request.user)
    if not profile:
        return HttpResponseForbidden("Student profile not found.")

    if request.method == "POST":
        form = FeePaymentForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.student = profile
            obj.save()
            messages.success(request, "Payment submitted for verification.")
            return redirect("payment_list")
    else:
        form = FeePaymentForm()

    return render(request, "portal/form.html", {"form": form, "title": "New Fee Payment"})

@login_required
def payment_update(request, pk):
    profile = _profile_or_403(request.user)
    if not profile:
        return HttpResponseForbidden("Student profile not found.")

    obj = get_object_or_404(FeePayment, pk=pk, student=profile)
    if obj.status != "PENDING":
        return HttpResponseForbidden("Only pending payments can be edited.")

    if request.method == "POST":
        form = FeePaymentForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Payment updated.")
            return redirect("payment_list")
    else:
        form = FeePaymentForm(instance=obj)

    return render(request, "portal/form.html", {"form": form, "title": "Edit Fee Payment"})

@login_required
def payment_delete(request, pk):
    profile = _profile_or_403(request.user)
    if not profile:
        return HttpResponseForbidden("Student profile not found.")

    obj = get_object_or_404(FeePayment, pk=pk, student=profile)
    if obj.status != "PENDING":
        return HttpResponseForbidden("Only pending payments can be deleted.")

    if request.method == "POST":
        obj.delete()
        messages.success(request, "Payment deleted.")
        return redirect("payment_list")

    return render(request, "portal/confirm_delete.html", {"obj": obj, "title": "Delete Fee Payment"})

@user_passes_test(is_staff_user)
def payment_process(request, pk):
    obj = get_object_or_404(FeePayment, pk=pk)
    if request.method == "POST":
        form = FeePaymentStaffForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Payment processed.")
            return redirect("payment_list")
    else:
        form = FeePaymentStaffForm(instance=obj)

    return render(request, "portal/form.html", {"form": form, "title": "Process Payment"})

@login_required
def inquiry_list(request):
    staff = request.user.is_staff
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()

    if staff:
        qs = Inquiry.objects.select_related("student").all()
    else:
        profile = _profile_or_403(request.user)
        if not profile:
            return HttpResponseForbidden("Student profile not found.")
        qs = profile.inquiries.all()

    if status:
        qs = qs.filter(status=status)

    if q:
        qs = qs.filter(Q(subject__icontains=q) | Q(message__icontains=q) | Q(student__student_id__icontains=q))

    return render(request, "portal/inquiry_list.html", {"items": qs, "q": q, "status": status, "staff": staff})

@login_required
def inquiry_create(request):
    profile = _profile_or_403(request.user)
    if not profile:
        return HttpResponseForbidden("Student profile not found.")

    if request.method == "POST":
        form = InquiryForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.student = profile
            obj.save()
            messages.success(request, "Inquiry sent.")
            return redirect("inquiry_list")
    else:
        form = InquiryForm()

    return render(request, "portal/form.html", {"form": form, "title": "New Inquiry"})

@login_required
def inquiry_update(request, pk):
    profile = _profile_or_403(request.user)
    if not profile:
        return HttpResponseForbidden("Student profile not found.")

    obj = get_object_or_404(Inquiry, pk=pk, student=profile)
    if obj.status != "OPEN":
        return HttpResponseForbidden("Only open inquiries can be edited.")

    if request.method == "POST":
        form = InquiryForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Inquiry updated.")
            return redirect("inquiry_list")
    else:
        form = InquiryForm(instance=obj)

    return render(request, "portal/form.html", {"form": form, "title": "Edit Inquiry"})

@login_required
def inquiry_delete(request, pk):
    profile = _profile_or_403(request.user)
    if not profile:
        return HttpResponseForbidden("Student profile not found.")

    obj = get_object_or_404(Inquiry, pk=pk, student=profile)
    if obj.status != "OPEN":
        return HttpResponseForbidden("Only open inquiries can be deleted.")

    if request.method == "POST":
        obj.delete()
        messages.success(request, "Inquiry deleted.")
        return redirect("inquiry_list")

    return render(request, "portal/confirm_delete.html", {"obj": obj, "title": "Delete Inquiry"})

@user_passes_test(is_staff_user)
def inquiry_process(request, pk):
    obj = get_object_or_404(Inquiry, pk=pk)
    if request.method == "POST":
        form = InquiryStaffForm(request.POST, instance=obj)
        if form.is_valid():
            edited = form.save(commit=False)
            if edited.reply and edited.status in ["ANSWERED", "CLOSED"]:
                edited.replied_by = request.user
                edited.replied_at = timezone.now()
            edited.save()
            messages.success(request, "Inquiry processed.")
            return redirect("inquiry_list")
    else:
        form = InquiryStaffForm(instance=obj)

    return render(request, "portal/form.html", {"form": form, "title": "Reply / Update Inquiry"})
