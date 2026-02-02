from rest_framework import serializers

from .roles import can_view_financial, resolve_user_role

from .models import (
    UserProfile,
    AccountPlanTemplateHeader,
    AccountPlanTemplateItem,
    Certification,
    Client,
    ClientContact,
    Company,
    Supplier,
    AccountsPayable,
    AccountsReceivable,
    Competency,
    Consultant,
    DeploymentTemplate,
    DeploymentTemplateHeader,
    Module,
    Phase,
    Project,
    ProjectActivity,
    ProjectAttachment,
    Product,
    Submodule,
    ActivityBillingType,
    UserRole,
)


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class AccountsPayableSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountsPayable
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class AccountsReceivableSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountsReceivable
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ConsultantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultant
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ClientContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientContact
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class CompetencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Competency
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class PhaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phase
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class SubmoduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submodule
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class DeploymentTemplateHeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeploymentTemplateHeader
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class DeploymentTemplateItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeploymentTemplate
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class AccountPlanTemplateHeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountPlanTemplateHeader
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class AccountPlanTemplateItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountPlanTemplateItem
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "contracted_hours",
            "available_hours",
            "available_value",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        if request and not can_view_financial(request.user):
            for field in ("total_value", "hourly_rate", "available_value"):
                data.pop(field, None)
        return data


class ProjectAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectAttachment
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ProjectActivitySerializer(serializers.ModelSerializer):
    subactivities = serializers.SerializerMethodField()

    class Meta:
        model = ProjectActivity
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def get_subactivities(self, instance):
        return [
            item.description
            for item in instance.subactivity_items.all()
            if item.description
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        role = resolve_user_role(request.user) if request else None
        data["hours_available"] = str(instance.hours_available())
        data["hours_contingency"] = str(instance.hours_contingency())
        if role == UserRole.CLIENT:
            data.pop("hours", None)
            data.pop("days", None)
            data.pop("hours_available", None)
            data.pop("hours_contingency", None)
        elif role in {UserRole.CONSULTANT, UserRole.GP_EXTERNAL}:
            data.pop("hours", None)
            data.pop("hours_contingency", None)
        return data

    def validate(self, attrs):
        attrs = super().validate(attrs)
        billing_type = attrs.get(
            "billing_type",
            getattr(self.instance, "billing_type", None),
        )
        assumed_reason = attrs.get(
            "assumed_reason",
            getattr(self.instance, "assumed_reason", ""),
        )
        if billing_type == ActivityBillingType.ASSUMED_COMPANY:
            if not assumed_reason:
                raise serializers.ValidationError(
                    {"assumed_reason": "Informe o motivo das horas assumidas."}
                )
        else:
            attrs["assumed_reason"] = ""
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
