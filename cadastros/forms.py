import os
from decimal import Decimal, ROUND_HALF_UP

from django import forms
from django.contrib.auth import authenticate, get_user_model, password_validation
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.db.models import Q, Sum
from django.utils import timezone

from .models import (
    AccountPlanTemplateHeader,
    AccountPlanTemplateItem,
    AccountType,
    Certification,
    Client,
    ClientContact,
    CandidateApplication,
    Company,
    CompanyBankAccount,
    CompanyType,
    BillingCycle,
    Supplier,
    AccountsPayable,
    AccountsPayablePayment,
    AccountsPayableAttachment,
    AccountsReceivable,
    AccountsReceivablePayment,
    Competency,
    Consultant,
    ConsultantAttachment,
    ConsultantBankAccount,
    ConsultantRate,
    DeploymentTemplate,
    DeploymentTemplateHeader,
    Module,
    Phase,
    Project,
    ProjectActivity,
    ProjectAttachment,
    ProjectContractType,
    ProjectContact,
    ProjectGoNoGoChecklistItem,
    ProjectObservation,
    ProjectOccurrence,
    ProjectOccurrenceAttachment,
    ProjectRole,
    Product,
    StatusChoices,
    Submodule,
    TimeEntry,
    TimeEntryStatus,
    TimeEntryType,
    ProposalRequest,
    ActivityBillingType,
    ActivityStatus,
    UserProfile,
    UserRole,
    Ticket,
    TicketReply,
    WhatsappSettings,
    ChatGPTSettings,
    KnowledgeCategory,
    KnowledgePost,
)

User = get_user_model()

CHATGPT_MODEL_CHOICES = (
    ("gpt-5", "gpt-5"),
    ("gpt-5-mini", "gpt-5-mini"),
    ("gpt-5-nano", "gpt-5-nano"),
    ("gpt-4.1", "gpt-4.1"),
    ("gpt-4.1-mini", "gpt-4.1-mini"),
    ("gpt-4.1-nano", "gpt-4.1-nano"),
    ("gpt-4o", "gpt-4o"),
    ("gpt-4o-mini", "gpt-4o-mini"),
    ("o3-mini", "o3-mini"),
    ("o1", "o1"),
    ("o1-mini", "o1-mini"),
    ("gpt-4-turbo", "gpt-4-turbo"),
    ("gpt-4", "gpt-4"),
    ("gpt-3.5-turbo", "gpt-3.5-turbo"),
)


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            "company_type",
            "legal_name",
            "trade_name",
            "tax_id",
            "state_registration",
            "municipal_registration",
            "status",
            "billing_email",
            "phone",
            "address_line",
            "city",
            "state",
            "postal_code",
            "country",
            "notes",
        ]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class WhatsappSettingsForm(forms.ModelForm):
    class Meta:
        model = WhatsappSettings
        fields = [
            "opportunities_numbers",
            "financial_numbers",
            "zapi_base_url",
            "zapi_instance_id",
            "zapi_token",
            "zapi_client_token",
            "daily_activities_time",
            "daily_overdue_time",
            "daily_admin_due_time",
        ]
        widgets = {
            "opportunities_numbers": forms.Textarea(attrs={"rows": 4}),
            "financial_numbers": forms.Textarea(attrs={"rows": 4}),
            "zapi_base_url": forms.TextInput(attrs={"placeholder": "https://api.z-api.io"}),
            "zapi_instance_id": forms.TextInput(attrs={"placeholder": "Instance ID"}),
            "zapi_token": forms.PasswordInput(render_value=True),
            "zapi_client_token": forms.PasswordInput(render_value=True),
            "daily_activities_time": forms.TimeInput(attrs={"type": "time"}),
            "daily_overdue_time": forms.TimeInput(attrs={"type": "time"}),
            "daily_admin_due_time": forms.TimeInput(attrs={"type": "time"}),
        }


class ChatGPTSettingsForm(forms.ModelForm):
    api_model = forms.ChoiceField(
        choices=CHATGPT_MODEL_CHOICES,
        required=False,
        label="Modelo",
        help_text="Selecione o modelo do ChatGPT.",
    )

    class Meta:
        model = ChatGPTSettings
        fields = [
            "api_url",
            "api_key",
            "api_model",
            "request_timeout",
            "org_id",
            "project_id",
            "system_prompt",
            "analysis_prompt",
        ]
        widgets = {
            "api_url": forms.TextInput(
                attrs={"placeholder": "https://api.openai.com/v1/chat/completions"}
            ),
            "api_key": forms.PasswordInput(render_value=True),
            "request_timeout": forms.NumberInput(attrs={"min": 1}),
            "org_id": forms.TextInput(attrs={"placeholder": "org_xxxxx"}),
            "project_id": forms.TextInput(attrs={"placeholder": "proj_xxxxx"}),
            "system_prompt": forms.Textarea(attrs={"rows": 10}),
            "analysis_prompt": forms.Textarea(attrs={"rows": 18}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current = ""
        if self.instance and self.instance.api_model:
            current = self.instance.api_model
        elif self.initial.get("api_model"):
            current = self.initial["api_model"]
        if current:
            choice_values = {value for value, _ in self.fields["api_model"].choices}
            if current not in choice_values:
                self.fields["api_model"].choices = (
                    (current, f"{current} (personalizado)"),
                ) + tuple(self.fields["api_model"].choices)


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = [
            "person_type",
            "document",
            "name",
            "trade_name",
            "email",
            "phone",
            "address_line",
            "city",
            "state",
            "postal_code",
            "country",
            "status",
            "notes",
        ]
        widgets = {
            "document": forms.TextInput(
                attrs={"placeholder": "CPF ou CNPJ", "inputmode": "numeric"}
            ),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
        help_texts = {
            "document": "Informe CPF ou CNPJ.",
        }


class AccountsPayableForm(forms.ModelForm):
    recurrence_interval_days = forms.IntegerField(
        required=False,
        min_value=1,
        label="Intervalo de vencimento (dias)",
        help_text="Ex.: 10 para cada 10 dias, 30 para mensal.",
        widget=forms.NumberInput(attrs={"placeholder": "Ex.: 10"}),
    )
    recurrence_count = forms.IntegerField(
        required=False,
        min_value=1,
        label="Quantidade de titulos",
        help_text="Total de titulos a gerar, incluindo o primeiro.",
        widget=forms.NumberInput(attrs={"placeholder": "Ex.: 3"}),
    )

    class Meta:
        model = AccountsPayable
        fields = [
            "supplier",
            "consultant",
            "billing_invoice",
            "account_plan_item",
            "document_number",
            "description",
            "issue_date",
            "due_date",
            "amount",
            "discount",
            "interest",
            "penalty",
            "status",
            "settlement_date",
            "payment_method",
            "notes",
        ]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
            "document_number": forms.TextInput(attrs={"placeholder": "Numero da nota ou fatura"}),
        }
        help_texts = {
            "status": "Atualizado automaticamente por vencimento e liquidacao.",
            "payment_method": "Opcional. Informe ao liquidar.",
            "billing_invoice": "Opcional. Vincule a fatura de origem.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["settlement_date"].label = "Data de pagamento"
        self.fields["payment_method"].label = "Forma de pagamento"
        if self.instance and self.instance.pk:
            self.fields.pop("recurrence_interval_days", None)
            self.fields.pop("recurrence_count", None)
        else:
            self.fields["due_date"].label = "1o vencimento"
            self.fields["document_number"].help_text = (
                "Para recorrencias, os titulos adicionais recebem sufixo automatico."
            )
            self.order_fields(
                [
                    "supplier",
                    "consultant",
                    "billing_invoice",
                    "account_plan_item",
                    "document_number",
                    "description",
                    "issue_date",
                    "due_date",
                    "recurrence_interval_days",
                    "recurrence_count",
                    "amount",
                    "discount",
                    "interest",
                    "penalty",
                    "status",
                    "settlement_date",
                    "payment_method",
                    "notes",
                ]
            )
        _apply_br_date_field(self.fields.get("issue_date"))
        _apply_br_date_field(self.fields.get("due_date"))
        _apply_br_date_field(self.fields.get("settlement_date"))
        _localize_decimal_field(self.fields.get("amount"))
        _localize_decimal_field(self.fields.get("discount"))
        _localize_decimal_field(self.fields.get("interest"))
        _localize_decimal_field(self.fields.get("penalty"))
        account_field = self.fields.get("account_plan_item")
        if account_field:
            queryset = AccountPlanTemplateItem.objects.filter(
                account_type__in=[AccountType.EXPENSE, AccountType.COST],
                status=StatusChoices.ACTIVE,
                is_analytic=True,
            ).order_by("code")
            if self.instance and self.instance.account_plan_item_id:
                queryset = AccountPlanTemplateItem.objects.filter(
                    Q(pk=self.instance.account_plan_item_id) | Q(pk__in=queryset)
                ).order_by("code")
            account_field.queryset = queryset

    def clean(self):
        cleaned_data = super().clean()
        if self.instance and self.instance.pk:
            return cleaned_data
        interval = cleaned_data.get("recurrence_interval_days")
        count = cleaned_data.get("recurrence_count")
        if interval and not count:
            self.add_error("recurrence_count", "Informe a quantidade de titulos.")
        if count and count > 1 and not interval:
            self.add_error("recurrence_interval_days", "Informe o intervalo em dias.")
        return cleaned_data


class AccountsReceivableForm(forms.ModelForm):
    class Meta:
        model = AccountsReceivable
        fields = [
            "client",
            "billing_invoice",
            "account_plan_item",
            "document_number",
            "description",
            "issue_date",
            "due_date",
            "amount",
            "discount",
            "interest",
            "penalty",
            "status",
            "settlement_date",
            "payment_method",
            "notes",
        ]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
            "document_number": forms.TextInput(attrs={"placeholder": "Numero da nota ou fatura"}),
        }
        help_texts = {
            "status": "Atualizado automaticamente por vencimento e liquidacao.",
            "payment_method": "Opcional. Informe ao liquidar.",
            "billing_invoice": "Opcional. Vincule a fatura de origem.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["settlement_date"].label = "Data de recebimento"
        self.fields["payment_method"].label = "Forma de recebimento"
        _apply_br_date_field(self.fields.get("issue_date"))
        _apply_br_date_field(self.fields.get("due_date"))
        _apply_br_date_field(self.fields.get("settlement_date"))
        _localize_decimal_field(self.fields.get("amount"))
        _localize_decimal_field(self.fields.get("discount"))
        _localize_decimal_field(self.fields.get("interest"))
        _localize_decimal_field(self.fields.get("penalty"))
        account_field = self.fields.get("account_plan_item")
        if account_field:
            queryset = AccountPlanTemplateItem.objects.filter(
                account_type=AccountType.REVENUE,
                status=StatusChoices.ACTIVE,
                is_analytic=True,
            ).order_by("code")
            if self.instance and self.instance.account_plan_item_id:
                queryset = AccountPlanTemplateItem.objects.filter(
                    Q(pk=self.instance.account_plan_item_id) | Q(pk__in=queryset)
                ).order_by("code")
            account_field.queryset = queryset


class AccountsPayablePaymentForm(forms.ModelForm):
    class Meta:
        model = AccountsPayablePayment
        fields = [
            "payable",
            "bank_account",
            "payment_date",
            "amount",
            "payment_method",
            "notes",
        ]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
        help_texts = {
            "payment_method": "Opcional. Informe a forma de pagamento.",
        }

    def __init__(self, *args, **kwargs):
        self.payable = kwargs.pop("payable", None)
        super().__init__(*args, **kwargs)
        if self.payable:
            self.fields["payable"].initial = self.payable.pk
            self.fields["payable"].widget = forms.HiddenInput()
        if "bank_account" in self.fields:
            self.fields["bank_account"].queryset = CompanyBankAccount.objects.select_related(
                "company"
            ).order_by("company__legal_name", "bank_name", "agency", "account_number")
        _apply_br_date_field(self.fields.get("payment_date"))
        _localize_decimal_field(self.fields.get("amount"))

    def clean(self):
        cleaned_data = super().clean()
        payable = cleaned_data.get("payable") or self.payable
        amount = cleaned_data.get("amount")
        if payable and amount is not None:
            paid_total = (
                payable.payments.aggregate(total=Sum("amount")).get("total")
                or Decimal("0.00")
            )
            if self.instance.pk:
                paid_total -= self.instance.amount or Decimal("0.00")
            remaining = payable.total_amount() - paid_total
            if amount > remaining:
                self.add_error(
                    "amount",
                    "Valor pago nao pode ser maior que o saldo em aberto.",
                )
        return cleaned_data


class AccountsPayableAttachmentForm(forms.ModelForm):
    class Meta:
        model = AccountsPayableAttachment
        fields = ["payable", "description", "file"]

    def __init__(self, *args, **kwargs):
        self.payable = kwargs.pop("payable", None)
        super().__init__(*args, **kwargs)
        if self.payable:
            self.fields["payable"].initial = self.payable.pk
            self.fields["payable"].widget = forms.HiddenInput()


class AccountsReceivablePaymentForm(forms.ModelForm):
    class Meta:
        model = AccountsReceivablePayment
        fields = [
            "receivable",
            "bank_account",
            "payment_date",
            "amount",
            "payment_method",
            "notes",
        ]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
        help_texts = {
            "payment_method": "Opcional. Informe a forma de recebimento.",
        }

    def __init__(self, *args, **kwargs):
        self.receivable = kwargs.pop("receivable", None)
        super().__init__(*args, **kwargs)
        if self.receivable:
            self.fields["receivable"].initial = self.receivable.pk
            self.fields["receivable"].widget = forms.HiddenInput()
        if "bank_account" in self.fields:
            self.fields["bank_account"].queryset = CompanyBankAccount.objects.select_related(
                "company"
            ).order_by("company__legal_name", "bank_name", "agency", "account_number")
        _apply_br_date_field(self.fields.get("payment_date"))
        _localize_decimal_field(self.fields.get("amount"))

    def clean(self):
        cleaned_data = super().clean()
        receivable = cleaned_data.get("receivable") or self.receivable
        amount = cleaned_data.get("amount")
        if receivable and amount is not None:
            paid_total = (
                receivable.payments.aggregate(total=Sum("amount")).get("total")
                or Decimal("0.00")
            )
            if self.instance.pk:
                paid_total -= self.instance.amount or Decimal("0.00")
            remaining = receivable.total_amount() - paid_total
            if amount > remaining:
                self.add_error(
                    "amount",
                    "Valor recebido nao pode ser maior que o saldo em aberto.",
                )
        return cleaned_data


class TravelReimbursementForm(forms.Form):
    consultant = forms.ModelChoiceField(
        queryset=Consultant.objects.none(),
        label="Consultor",
    )
    document_number = forms.CharField(
        max_length=AccountsPayable._meta.get_field("document_number").max_length,
        label="Numero do documento",
        help_text="Informe o numero do comprovante enviado pela Senior.",
        widget=forms.TextInput(attrs={"placeholder": "Ex.: REEMB-2026-001"}),
    )
    description = forms.CharField(
        max_length=AccountsPayable._meta.get_field("description").max_length,
        label="Descricao",
        help_text="Descreva o reembolso de viagem.",
    )
    issue_date = forms.DateField(label="Data de emissao")
    due_date = forms.DateField(label="Data de vencimento")
    amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
        label="Valor",
    )
    notes = forms.CharField(
        label="Observacoes",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )
    confirmation_file = forms.FileField(
        label="Confirmacao da Senior (PDF ou imagem)",
        help_text="Arquivo obrigatorio. Aceita PDF, JPG ou PNG.",
        widget=forms.ClearableFileInput(attrs={"accept": ".pdf,.jpg,.jpeg,.png"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        consultant_field = self.fields.get("consultant")
        if consultant_field:
            consultant_field.queryset = Consultant.objects.filter(
                status=StatusChoices.ACTIVE
            ).order_by("full_name")
        self.fields["issue_date"].initial = timezone.localdate()
        self.fields["due_date"].initial = timezone.localdate()
        _apply_br_date_field(self.fields.get("issue_date"))
        _apply_br_date_field(self.fields.get("due_date"))
        _localize_decimal_field(self.fields.get("amount"))

    def clean_confirmation_file(self):
        uploaded = self.cleaned_data.get("confirmation_file")
        if not uploaded:
            return uploaded
        ext = os.path.splitext(uploaded.name)[1].lower()
        if ext not in {".pdf", ".jpg", ".jpeg", ".png"}:
            raise ValidationError("Arquivo deve ser PDF ou imagem (JPG/PNG).")
        return uploaded

    def clean(self):
        cleaned_data = super().clean()
        issue_date = cleaned_data.get("issue_date")
        due_date = cleaned_data.get("due_date")
        if issue_date and due_date and due_date < issue_date:
            self.add_error("due_date", "Vencimento nao pode ser anterior a emissao.")
        return cleaned_data


class ClientContactForm(forms.ModelForm):
    class Meta:
        model = ClientContact
        fields = [
            "client",
            "name",
            "role",
            "email",
            "phone",
            "is_primary",
            "status",
        ]


class CompetencyForm(forms.ModelForm):
    class Meta:
        model = Competency
        fields = ["name", "description", "status"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ["name", "issuer", "description", "status"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class PhaseForm(forms.ModelForm):
    class Meta:
        model = Phase
        fields = ["description", "status"]


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["description", "status"]


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ["product", "description", "status"]


class SubmoduleForm(forms.ModelForm):
    class Meta:
        model = Submodule
        fields = ["product", "module", "description", "status"]

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get("product")
        module = cleaned_data.get("module")
        if product and module and module.product_id != product.id:
            self.add_error("module", "Modulo nao pertence ao produto selecionado.")
        return cleaned_data


class AccountsCompensationForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
        label="Valor da compensacao",
    )
    payment_date = forms.DateField(
        label="Data da baixa",
        initial=timezone.localdate,
    )
    bank_account = forms.ModelChoiceField(
        queryset=CompanyBankAccount.objects.none(),
        label="Conta bancaria de registro",
    )
    notes = forms.CharField(
        label="Observacoes",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["bank_account"].queryset = CompanyBankAccount.objects.select_related(
            "company"
        ).order_by("company__legal_name", "bank_name", "agency", "account_number")
        _apply_br_date_field(self.fields.get("payment_date"))
        _localize_decimal_field(self.fields.get("amount"))


class SubmoduleBulkCreateForm(forms.Form):
    description = forms.CharField(
        label="Descricao do submodulo",
        max_length=200,
    )
    status = forms.ChoiceField(
        label="Situacao",
        choices=StatusChoices.choices,
        initial=StatusChoices.ACTIVE,
    )


class DeploymentTemplateHeaderForm(forms.ModelForm):
    class Meta:
        model = DeploymentTemplateHeader
        fields = ["name"]


class DeploymentTemplateItemForm(forms.ModelForm):
    class Meta:
        model = DeploymentTemplate
        fields = [
            "template",
            "seq",
            "seq_predecessor",
            "phase",
            "product",
            "module",
            "submodule",
            "activity",
            "subactivity",
            "days",
            "hours",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        hours_field = self.fields.get("hours")
        if hours_field:
            hours_field.localize = True
            hours_field.widget = forms.TextInput(attrs={"inputmode": "decimal", "placeholder": "0,00"})
            hours_field.widget.is_localized = True
            hours_field.widget.attrs.setdefault("inputmode", "decimal")

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get("product")
        module = cleaned_data.get("module")
        submodule = cleaned_data.get("submodule")
        if product and module and module.product_id != product.id:
            self.add_error("module", "Modulo nao pertence ao produto selecionado.")
        if submodule and module and submodule.module_id != module.id:
            self.add_error("submodule", "Submodulo nao pertence ao modulo selecionado.")
        if submodule and product and submodule.product_id != product.id:
            self.add_error("submodule", "Submodulo nao pertence ao produto selecionado.")
        return cleaned_data


class DeploymentTemplateMaintenanceForm(DeploymentTemplateItemForm):
    class Meta(DeploymentTemplateItemForm.Meta):
        fields = [
            "seq",
            "seq_predecessor",
            "phase",
            "product",
            "module",
            "submodule",
            "activity",
            "subactivity",
            "days",
            "hours",
        ]


class DeploymentTemplateImportForm(forms.Form):
    file = forms.FileField(
        label="Arquivo",
        help_text="Aceita .xlsx, .csv ou .xml (Microsoft Project).",
        widget=forms.ClearableFileInput(attrs={"accept": ".xlsx,.csv,.xml"}),
    )


class AccountPlanTemplateHeaderForm(forms.ModelForm):
    class Meta:
        model = AccountPlanTemplateHeader
        fields = ["name", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class AccountPlanTemplateItemForm(forms.ModelForm):
    class Meta:
        model = AccountPlanTemplateItem
        fields = [
            "template",
            "code",
            "description",
            "level",
            "parent",
            "account_type",
            "nature",
            "is_analytic",
            "status",
            "dre_group",
            "dre_subgroup",
            "dre_order",
            "dre_sign",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        parent_field = self.fields.get("parent")
        template_id = (
            self.data.get("template")
            or self.initial.get("template")
            or getattr(self.instance, "template_id", None)
        )
        if parent_field:
            queryset = AccountPlanTemplateItem.objects.all().order_by("code")
            if template_id:
                queryset = queryset.filter(template_id=template_id)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            parent_field.queryset = queryset


class AccountPlanTemplateImportForm(forms.Form):
    file = forms.FileField(
        label="Arquivo",
        help_text="Aceita .xlsx ou .csv.",
        widget=forms.ClearableFileInput(attrs={"accept": ".xlsx,.csv"}),
    )


class BrDateInput(forms.DateInput):
    input_type = "text"

    def __init__(self, **kwargs):
        kwargs.setdefault("format", "%d/%m/%Y")
        attrs = kwargs.setdefault("attrs", {})
        attrs.setdefault("placeholder", "dd/mm/aaaa")
        attrs.setdefault("inputmode", "numeric")
        super().__init__(**kwargs)


def _apply_br_date_field(field: forms.Field | None) -> None:
    if field is None:
        return
    field.widget = BrDateInput()
    field.input_formats = ["%d/%m/%Y"]


def _localize_decimal_field(field: forms.Field | None, placeholder: str = "0,00") -> None:
    if field is None:
        return
    field.localize = True
    field.widget = forms.TextInput(attrs={"inputmode": "decimal", "placeholder": placeholder})
    field.widget.is_localized = True


class MultiTextField(forms.Field):
    widget = forms.MultipleHiddenInput

    def to_python(self, value):
        if value in self.empty_values:
            return []
        if isinstance(value, (list, tuple)):
            items = [str(item).strip() for item in value if str(item).strip()]
        else:
            text = str(value).strip()
            items = [text] if text else []
        normalized = []
        seen = set()
        for item in items:
            key = item.lower()
            if key in seen:
                continue
            seen.add(key)
            normalized.append(item)
        return normalized


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "billing_client",
            "project_client",
            "description",
            "cloud_environment",
            "database_type",
            "hml_url",
            "prd_url",
            "senior_client_code",
            "senior_project_code",
            "received_date",
            "planned_go_live_date",
            "cutover_planned_start",
            "cutover_planned_end",
            "explanation",
            "project_type",
            "contract_type",
            "criticality",
            "status",
            "total_value",
            "hourly_rate",
            "contracted_hours",
            "contingency_percent",
            "available_hours",
            "available_value",
            "internal_manager",
            "external_manager",
            "client_user",
        ]
        widgets = {
            "explanation": forms.Textarea(attrs={"rows": 10}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        currency_fields = (
            "total_value",
            "hourly_rate",
            "contracted_hours",
            "contingency_percent",
            "available_hours",
            "available_value",
        )
        for field_name in currency_fields:
            _localize_decimal_field(self.fields.get(field_name))
        for field_name in ("contracted_hours", "available_hours", "available_value"):
            field = self.fields.get(field_name)
            if field:
                field.disabled = True
                field.required = False
        _apply_br_date_field(self.fields.get("received_date"))
        _apply_br_date_field(self.fields.get("planned_go_live_date"))
        _apply_br_date_field(self.fields.get("cutover_planned_start"))
        _apply_br_date_field(self.fields.get("cutover_planned_end"))
        contract_type = self._resolve_contract_type()
        self._apply_contract_rules(contract_type)

    def _resolve_contract_type(self) -> str:
        if self.data and self.data.get("contract_type"):
            return str(self.data.get("contract_type"))
        if self.initial and self.initial.get("contract_type"):
            return str(self.initial.get("contract_type"))
        if getattr(self.instance, "contract_type", None):
            return str(self.instance.contract_type)
        return ProjectContractType.FIXED_VALUE

    def _apply_contract_rules(self, contract_type: str) -> None:
        hourly_types = {
            ProjectContractType.FIXED_HOURS,
            ProjectContractType.HOURLY_PROJECT,
            ProjectContractType.AD_HOC,
        }
        total_value_field = self.fields.get("total_value")
        contracted_hours_field = self.fields.get("contracted_hours")
        if contract_type in hourly_types:
            if total_value_field:
                total_value_field.required = False
                total_value_field.disabled = True
            if contracted_hours_field:
                contracted_hours_field.required = True
                contracted_hours_field.disabled = False
        else:
            if total_value_field:
                total_value_field.required = True
                total_value_field.disabled = False
            if contracted_hours_field:
                contracted_hours_field.required = False
                contracted_hours_field.disabled = True

    def clean(self):
        cleaned_data = super().clean()
        contract_type = cleaned_data.get("contract_type") or self._resolve_contract_type()
        hourly_rate = cleaned_data.get("hourly_rate") or Decimal("0.00")
        total_value = cleaned_data.get("total_value") or Decimal("0.00")
        contracted_hours = cleaned_data.get("contracted_hours") or Decimal("0.00")
        def add_field_error(field: str, message: str) -> None:
            if field in self.fields:
                self.add_error(field, message)
            else:
                self.add_error(None, message)
        hourly_types = {
            ProjectContractType.FIXED_HOURS,
            ProjectContractType.HOURLY_PROJECT,
            ProjectContractType.AD_HOC,
        }
        if contract_type in hourly_types:
            if contracted_hours <= 0:
                add_field_error(
                    "contracted_hours",
                    "Informe a quantidade de horas contratadas.",
                )
            if hourly_rate <= 0:
                add_field_error("hourly_rate", "Informe o valor hora.")
            if contracted_hours > 0 and hourly_rate > 0:
                total_value = (contracted_hours * hourly_rate).quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP,
                )
                cleaned_data["total_value"] = total_value
                self.instance.total_value = total_value
        else:
            if total_value <= 0:
                add_field_error("total_value", "Informe o valor total do projeto.")
            if hourly_rate <= 0:
                add_field_error("hourly_rate", "Informe o valor hora.")
            if total_value > 0 and hourly_rate > 0:
                contracted_hours = (total_value / hourly_rate).quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP,
                )
                cleaned_data["contracted_hours"] = contracted_hours
                self.instance.contracted_hours = contracted_hours
        return cleaned_data


class ProjectRoleForm(forms.ModelForm):
    class Meta:
        model = ProjectRole
        fields = ["name", "status"]


class ProjectContactForm(forms.ModelForm):
    class Meta:
        model = ProjectContact
        fields = [
            "project",
            "name",
            "phone",
            "function",
            "email",
            "role",
            "receives_status_report",
            "receives_delay_email",
        ]


class ProjectAttachmentForm(forms.ModelForm):
    class Meta:
        model = ProjectAttachment
        fields = ["project", "attachment_type", "description", "file"]


class ProjectObservationForm(forms.ModelForm):
    class Meta:
        model = ProjectObservation
        fields = ["project", "note"]
        widgets = {
            "note": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        note_field = self.fields.get("note")
        if note_field:
            note_field.required = True


class ProjectGoNoGoChecklistItemForm(forms.ModelForm):
    class Meta:
        model = ProjectGoNoGoChecklistItem
        fields = [
            "project",
            "criterion",
            "category",
            "required_evidence",
            "approver",
            "result",
            "observation",
            "visibility",
        ]
        widgets = {
            "required_evidence": forms.Textarea(attrs={"rows": 3}),
            "observation": forms.Textarea(attrs={"rows": 3}),
        }


class ProjectOccurrenceForm(forms.ModelForm):
    class Meta:
        model = ProjectOccurrence
        fields = [
            "project",
            "title",
            "description",
            "visibility",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class ProjectOccurrenceAttachmentForm(forms.ModelForm):
    class Meta:
        model = ProjectOccurrenceAttachment
        fields = ["occurrence", "description", "file"]


class ProjectActivityForm(forms.ModelForm):
    subactivities = MultiTextField(
        required=False,
        label="Subatividades",
        help_text="Adicione uma ou mais subatividades.",
    )
    predecessors = forms.ModelMultipleChoiceField(
        queryset=ProjectActivity.objects.none(),
        required=False,
        label="Predecessoras",
        widget=forms.MultipleHiddenInput(),
    )

    class Meta:
        model = ProjectActivity
        fields = [
            "project",
            "seq",
            "predecessors",
            "phase",
            "product",
            "module",
            "submodule",
            "activity",
            "criticality",
            "days",
            "hours",
            "account_plan_item",
            "planned_start",
            "planned_end",
            "actual_start",
            "actual_end",
            "status",
            "billing_type",
            "assumed_reason",
            "consultants",
            "consultant_hourly_rate",
            "client_visible",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        seq_field = self.fields.get("seq")
        if seq_field:
            seq_field.required = bool(self.instance and self.instance.pk)
            if not seq_field.required and not seq_field.help_text:
                seq_field.help_text = "Sequencia sugerida automaticamente."
        subactivities_field = self.fields.get("subactivities")
        if subactivities_field and self.instance and self.instance.pk:
            subactivity_items = list(
                self.instance.subactivity_items.order_by("order", "id").values_list(
                    "description", flat=True
                )
            )
            if not subactivity_items:
                legacy_subactivity = (self.instance.subactivity or "").strip()
                if legacy_subactivity:
                    subactivity_items = [legacy_subactivity]
            if subactivity_items:
                self.initial["subactivities"] = subactivity_items
        _localize_decimal_field(self.fields.get("hours"))
        _localize_decimal_field(self.fields.get("days"))
        _localize_decimal_field(self.fields.get("consultant_hourly_rate"))
        _apply_br_date_field(self.fields.get("planned_start"))
        _apply_br_date_field(self.fields.get("planned_end"))
        _apply_br_date_field(self.fields.get("actual_start"))
        _apply_br_date_field(self.fields.get("actual_end"))
        account_field = self.fields.get("account_plan_item")
        if account_field:
            account_field.queryset = AccountPlanTemplateItem.objects.order_by("code")
        consultants_field = self.fields.get("consultants")
        if consultants_field:
            consultants_field.queryset = consultants_field.queryset.exclude(user__isnull=True)
        rate_field = self.fields.get("consultant_hourly_rate")
        if rate_field and not rate_field.help_text:
            rate_field.help_text = "Sugestao baseada nos consultores selecionados."
        project_id = (
            self.data.get("project")
            or self.initial.get("project")
            or getattr(self.instance, "project_id", None)
        )
        predecessors_field = self.fields.get("predecessors")
        if predecessors_field and project_id:
            queryset = (
                ProjectActivity.objects.filter(project_id=project_id)
                .prefetch_related("subactivity_items")
                .order_by("seq")
            )
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
                self.initial["predecessors"] = list(
                    self.instance.predecessors.values_list("id", flat=True)
                )
            predecessors_field.queryset = queryset
            predecessors_field.label_from_instance = self._label_predecessor

    def clean(self):
        cleaned_data = super().clean()
        subactivities = cleaned_data.get("subactivities") or []
        if not subactivities:
            self.add_error("subactivities", "Informe ao menos uma subatividade.")
        cleaned_data["subactivities_list"] = subactivities
        billing_type = cleaned_data.get("billing_type")
        assumed_reason = (cleaned_data.get("assumed_reason") or "").strip()
        if billing_type == ActivityBillingType.ASSUMED_COMPANY:
            if not assumed_reason:
                self.add_error("assumed_reason", "Informe o motivo das horas assumidas.")
        else:
            assumed_reason = ""
        cleaned_data["assumed_reason"] = assumed_reason
        return cleaned_data

    @staticmethod
    def _label_predecessor(obj: ProjectActivity) -> str:
        subactivities = [
            item.description for item in obj.subactivity_items.all() if item.description
        ]
        if not subactivities and obj.subactivity:
            subactivities = [obj.subactivity]
        suffix = f" / {', '.join(subactivities)}" if subactivities else ""
        return f"{obj.seq} - {obj.activity}{suffix}"


class ProjectActivityGenerateForm(forms.Form):
    project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        widget=forms.HiddenInput(),
    )
    template = forms.ModelChoiceField(
        queryset=DeploymentTemplateHeader.objects.all(),
        label="Template de implantacao",
    )
    replace_existing = forms.BooleanField(
        required=False,
        label="Substituir atividades existentes",
        help_text="Remove as atividades atuais antes de gerar novamente.",
    )


class ProjectActivityFeedbackForm(forms.ModelForm):
    class Meta:
        model = ProjectActivity
        fields = ["client_completed", "client_comment"]
        widgets = {
            "client_comment": forms.Textarea(attrs={"rows": 3}),
        }


class TimeEntryForm(forms.ModelForm):
    class Meta:
        model = TimeEntry
        fields = [
            "activity",
            "consultant",
            "start_date",
            "end_date",
            "hours",
            "description",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_br_date_field(self.fields.get("start_date"))
        _apply_br_date_field(self.fields.get("end_date"))
        _localize_decimal_field(self.fields.get("hours"))
        if self.instance and self.instance.pk and self.instance.entry_type == TimeEntryType.WEEKLY:
            self.initial.setdefault(
                "hours",
                self.instance.total_hours or Decimal("0.00"),
            )

    def clean(self):
        cleaned_data = super().clean()
        activity = cleaned_data.get("activity")
        total_hours = cleaned_data.get("hours") or Decimal("0.00")

        if activity and activity.status != ActivityStatus.RELEASED:
            self.add_error("activity", "Apontamento permitido apenas para atividades liberadas.")

        if total_hours <= 0:
            self.add_error("hours", "Informe a quantidade de horas apontadas.")

        if activity and total_hours > 0:
            existing = TimeEntry.objects.filter(activity=activity)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            approved = (
                existing.filter(status=TimeEntryStatus.APPROVED)
                .aggregate(total=Sum("total_hours"))
                .get("total")
                or Decimal("0.00")
            )
            pending = (
                existing.filter(status=TimeEntryStatus.PENDING)
                .aggregate(total=Sum("total_hours"))
                .get("total")
                or Decimal("0.00")
            )
            available = (activity.hours or Decimal("0.00")) - approved - pending
            if total_hours > available:
                self.add_error(
                    None,
                    "Horas informadas excedem o saldo disponivel da atividade.",
                )

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.entry_type = TimeEntryType.DAILY
        instance.hours_monday = None
        instance.hours_tuesday = None
        instance.hours_wednesday = None
        instance.hours_thursday = None
        instance.hours_friday = None
        instance.hours_saturday = None
        instance.hours_sunday = None
        if commit:
            instance.save()
        return instance


class TimeEntryReviewForm(forms.ModelForm):
    class Meta:
        model = TimeEntry
        fields = ["status", "rejection_reason"]
        widgets = {
            "rejection_reason": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        status_field = self.fields.get("status")
        if status_field:
            status_field.choices = [
                (TimeEntryStatus.APPROVED, TimeEntryStatus.APPROVED.label),
                (TimeEntryStatus.REJECTED, TimeEntryStatus.REJECTED.label),
            ]

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get("status")
        reason = cleaned_data.get("rejection_reason")
        if status == TimeEntryStatus.REJECTED and not reason:
            self.add_error("rejection_reason", "Informe o motivo da reprovacao.")
        return cleaned_data


class ConsultantAttachmentForm(forms.ModelForm):
    class Meta:
        model = ConsultantAttachment
        fields = ["consultant", "description", "file"]


class ConsultantBankAccountForm(forms.ModelForm):
    class Meta:
        model = ConsultantBankAccount
        fields = [
            "consultant",
            "account_type",
            "bank_name",
            "agency",
            "account_number",
            "account_digit",
            "pix_keys",
        ]
        widgets = {
            "pix_keys": forms.Textarea(attrs={"rows": 3}),
        }
        help_texts = {
            "pix_keys": "Informe uma chave por linha.",
        }


class CompanyBankAccountForm(forms.ModelForm):
    class Meta:
        model = CompanyBankAccount
        fields = [
            "company",
            "account_type",
            "bank_name",
            "agency",
            "account_number",
            "account_digit",
            "initial_balance",
            "pix_keys",
        ]
        widgets = {
            "pix_keys": forms.Textarea(attrs={"rows": 3}),
        }
        help_texts = {
            "initial_balance": "Saldo inicial da conta.",
            "pix_keys": "Informe uma chave por linha.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "company" in self.fields:
            self.fields["company"].queryset = Company.objects.filter(
                company_type__in=[CompanyType.PRIMARY, CompanyType.BRANCH]
            ).order_by("legal_name")
        _localize_decimal_field(self.fields.get("initial_balance"))


class ConsultantRateForm(forms.ModelForm):
    class Meta:
        model = ConsultantRate
        fields = ["consultant", "rate", "currency", "start_date", "end_date", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _localize_decimal_field(self.fields.get("rate"))
        _apply_br_date_field(self.fields.get("start_date"))
        _apply_br_date_field(self.fields.get("end_date"))

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        if start_date and end_date and end_date < start_date:
            self.add_error(
                "end_date",
                "Fim da vigencia deve ser igual ou maior que inicio da vigencia.",
            )
        return cleaned_data


class ConsultantForm(forms.ModelForm):
    class Meta:
        model = Consultant
        fields = [
            "full_name",
            "email",
            "phone",
            "whatsapp_phone",
            "contract_type",
            "document",
            "birth_date",
            "company",
            "supplier",
            "is_senior_accredited",
            "is_partner",
            "user",
            "status",
            "start_date",
            "end_date",
            "notes",
            "competencies",
            "certifications",
        ]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_br_date_field(self.fields.get("birth_date"))
        _apply_br_date_field(self.fields.get("start_date"))
        _apply_br_date_field(self.fields.get("end_date"))


class ClientForm(forms.ModelForm):
    document = forms.CharField(
        label="CNPJ",
        max_length=32,
        help_text="Informe o CNPJ.",
        widget=forms.TextInput(attrs={"placeholder": "CNPJ", "inputmode": "numeric"}),
    )
    trade_name = forms.CharField(
        label="Nome fantasia",
        required=False,
    )
    billing_email = forms.EmailField(
        label="Email de faturamento",
        required=False,
    )
    phone = forms.CharField(
        label="Telefone",
        required=False,
    )
    address_line = forms.CharField(
        label="Endereco",
        required=False,
    )
    city = forms.CharField(
        label="Cidade",
        required=False,
    )
    state = forms.CharField(
        label="Estado",
        required=False,
    )
    postal_code = forms.CharField(
        label="CEP",
        required=False,
    )
    country = forms.CharField(
        label="Pais",
        required=False,
        initial="BR",
    )

    class Meta:
        model = Client
        fields = [
            "name",
            "status",
            "billing_cycle",
            "payment_terms_days",
            "contract_start",
            "contract_end",
            "commercial_notes",
        ]
        widgets = {
            "commercial_notes": forms.Textarea(attrs={"rows": 3}),
        }
        labels = {
            "name": "Razao social",
            "commercial_notes": "Observacoes",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_br_date_field(self.fields.get("contract_start"))
        _apply_br_date_field(self.fields.get("contract_end"))
        if "billing_cycle" in self.fields:
            self.fields["billing_cycle"].required = False
        if "payment_terms_days" in self.fields:
            self.fields["payment_terms_days"].required = False

        company = getattr(self.instance, "company", None)
        if company:
            self.fields["document"].initial = company.tax_id
            self.fields["trade_name"].initial = company.trade_name
            self.fields["billing_email"].initial = company.billing_email
            self.fields["phone"].initial = company.phone
            self.fields["address_line"].initial = company.address_line
            self.fields["city"].initial = company.city
            self.fields["state"].initial = company.state
            self.fields["postal_code"].initial = company.postal_code
            self.fields["country"].initial = company.country

        self.order_fields(
            [
                "document",
                "name",
                "trade_name",
                "billing_email",
                "phone",
                "address_line",
                "city",
                "state",
                "postal_code",
                "country",
                "status",
                "billing_cycle",
                "payment_terms_days",
                "contract_start",
                "contract_end",
                "commercial_notes",
            ]
        )

    def save(self, commit=True):
        client = super().save(commit=False)
        cleaned = self.cleaned_data
        document = (cleaned.get("document") or "").strip()
        company = None
        if client.pk and client.company_id:
            company = client.company
        elif document:
            company = Company.objects.filter(tax_id=document).first()
        if company is None:
            company = Company(company_type=CompanyType.CLIENT)

        if cleaned.get("name"):
            company.legal_name = cleaned["name"]
        if document:
            company.tax_id = document
        trade_name = cleaned.get("trade_name")
        if trade_name:
            company.trade_name = trade_name
        billing_email = cleaned.get("billing_email")
        if billing_email:
            company.billing_email = billing_email
        phone = cleaned.get("phone")
        if phone:
            company.phone = phone
        address_line = cleaned.get("address_line")
        if address_line:
            company.address_line = address_line
        city = cleaned.get("city")
        if city:
            company.city = city
        state = cleaned.get("state")
        if state:
            company.state = state
        postal_code = cleaned.get("postal_code")
        if postal_code:
            company.postal_code = postal_code
        country = cleaned.get("country")
        if country:
            company.country = country
        status = cleaned.get("status")
        if status:
            company.status = status

        billing_cycle = cleaned.get("billing_cycle") or client.billing_cycle or BillingCycle.MONTHLY
        payment_terms = cleaned.get("payment_terms_days") or client.payment_terms_days or 30
        client.billing_cycle = billing_cycle
        client.payment_terms_days = payment_terms
        if status:
            client.status = status

        if commit:
            company.save()
            client.company = company
            client.save()
        return client


class CandidateApplicationForm(forms.ModelForm):
    class Meta:
        model = CandidateApplication
        fields = [
            "full_name",
            "email",
            "phone",
            "location",
            "role_interest",
            "linkedin_url",
            "availability",
            "experience_summary",
            "resume",
        ]
        widgets = {
            "experience_summary": forms.Textarea(attrs={"rows": 4}),
            "resume": forms.ClearableFileInput(attrs={"accept": ".pdf,.doc,.docx"}),
        }
        help_texts = {
            "resume": "Envie o curriculo em PDF ou DOC/DOCX.",
        }


class ProposalRequestForm(forms.ModelForm):
    class Meta:
        model = ProposalRequest
        fields = [
            "company_name",
            "contact_name",
            "email",
            "phone",
            "project_summary",
            "estimated_start",
            "budget_range",
            "additional_notes",
        ]
        widgets = {
            "project_summary": forms.Textarea(attrs={"rows": 4}),
            "additional_notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_br_date_field(self.fields.get("estimated_start"))


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["user", "role", "whatsapp_phone"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user_field = self.fields.get("user")
        if user_field:
            user_field.disabled = True
            user_field.help_text = "Usuario nao pode ser alterado nesta tela."
            if self.instance and self.instance.user_id:
                user_field.queryset = User.objects.filter(pk=self.instance.user_id)


class UserCreateForm(UserCreationForm):
    role = forms.ChoiceField(choices=UserRole.choices, label="Perfil")
    whatsapp_phone = forms.CharField(
        required=False,
        label="Telefone WhatsApp",
        help_text="Recebe mensagens de WhatsApp do sistema.",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email", "role")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "username" in self.fields:
            self.fields["username"].label = "Usuario"
        if "first_name" in self.fields:
            self.fields["first_name"].label = "Nome"
        if "last_name" in self.fields:
            self.fields["last_name"].label = "Sobrenome"
        if "email" in self.fields:
            self.fields["email"].label = "Email"
        if "password1" in self.fields:
            self.fields["password1"].label = "Senha"
        if "password2" in self.fields:
            self.fields["password2"].label = "Confirmar senha"
        if "role" in self.fields:
            self.fields["role"].help_text = "Define o perfil de acesso no sistema."
        self.order_fields(
            [
                "username",
                "first_name",
                "last_name",
                "email",
                "role",
                "whatsapp_phone",
                "password1",
                "password2",
            ]
        )

    def save(self, commit=True):
        user = super().save(commit=commit)
        role = self.cleaned_data.get("role")
        phone = self.cleaned_data.get("whatsapp_phone", "")
        if commit and role:
            UserProfile.objects.update_or_create(
                user=user,
                defaults={"role": role, "whatsapp_phone": phone},
            )
        return user


class PasswordChangeRequestForm(forms.Form):
    username = forms.CharField(label="Usuario")
    old_password = forms.CharField(
        label="Senha atual",
        widget=forms.PasswordInput,
    )
    new_password1 = forms.CharField(
        label="Nova senha",
        widget=forms.PasswordInput,
    )
    new_password2 = forms.CharField(
        label="Confirmar nova senha",
        widget=forms.PasswordInput,
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        old_password = cleaned_data.get("old_password")
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")

        if new_password1 and new_password2 and new_password1 != new_password2:
            self.add_error("new_password2", "As senhas nao conferem.")

        if username and old_password:
            user = authenticate(username=username, password=old_password)
            if not user:
                raise ValidationError("Usuario ou senha invalido.")
            if new_password1:
                try:
                    password_validation.validate_password(new_password1, user)
                except ValidationError as exc:
                    self.add_error("new_password1", exc)
            self.user = user
        return cleaned_data

    def save(self):
        user = getattr(self, "user", None)
        if not user:
            raise ValidationError("Usuario invalido.")
        user.set_password(self.cleaned_data["new_password1"])
        user.save(update_fields=["password"])
        return user


class KnowledgeCategoryForm(forms.ModelForm):
    class Meta:
        model = KnowledgeCategory
        fields = ["name", "status"]


class KnowledgePostForm(forms.ModelForm):
    class Meta:
        model = KnowledgePost
        fields = ["title", "category", "content"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 8}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        category_field = self.fields.get("category")
        if category_field:
            queryset = KnowledgeCategory.objects.filter(status=StatusChoices.ACTIVE)
            if self.instance and self.instance.pk and self.instance.category_id:
                queryset = KnowledgeCategory.objects.filter(
                    Q(status=StatusChoices.ACTIVE) | Q(id=self.instance.category_id)
                )
            category_field.queryset = queryset.order_by("name")


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = [
            "title",
            "project",
            "activity",
            "ticket_type",
            "criticality",
            "consultant_responsible",
            "assigned_to",
            "description",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        description_field = self.fields.get("description")
        if description_field:
            description_field.required = True
        assigned_field = self.fields.get("assigned_to")
        if assigned_field and not assigned_field.help_text:
            assigned_field.help_text = "Admins sao incluidos automaticamente."
        if assigned_field:
            assigned_field.required = True
        activity_field = self.fields.get("activity")
        if activity_field and not activity_field.help_text:
            activity_field.help_text = "Opcional. Use para detalhar o chamado."


class TicketReplyForm(forms.ModelForm):
    class Meta:
        model = TicketReply
        fields = ["message"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 4}),
        }
