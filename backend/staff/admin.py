from django.contrib import admin
from django import forms
from .models import CustomAdmin, Supplier, Client
from django.contrib.admin import ModelAdmin

class CustomAdminCreateForm(forms.ModelForm):
    class Meta:
        model = CustomAdmin
        fields = ("email", "first_name", "last_name", "phone_number")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_unusable_password() 
        if commit:
            user.save()
        return user


class CustomAdminAdmin(ModelAdmin):
    model = CustomAdmin
    add_form = CustomAdminCreateForm
    form = CustomAdminCreateForm

    list_display = ("email", "first_name", "last_name", "phone_number", "is_staff", "is_active")
    search_fields = ("email", "first_name", "last_name", "phone_number")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email",)}),
        ("Personal info", {"fields": ("first_name", "last_name", "phone_number")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("OTP / Security", {"fields": ("otp_locked_until",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "phone_number"),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        """
        Force the admin to use our custom form
        """
        if obj is None:
            kwargs["form"] = self.add_form
        return super().get_form(request, obj, **kwargs)


admin.site.register(CustomAdmin, CustomAdminAdmin)
admin.site.register(Supplier)
admin.site.register(Client)
