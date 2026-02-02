from django.contrib import admin

from .observations import (
    create_project_change_observation,
    create_project_receipt_observation,
)
from .models import (
    AccountPlanTemplateHeader,
    AccountPlanTemplateItem,
    Certification,
    CandidateApplication,
    BillingInvoice,
    BillingInvoiceItem,
    Client,
    ClientContact,
    Company,
    CompanyBankAccount,
    Supplier,
    AccountsPayable,
    AccountsPayablePayment,
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
    ProjectActivitySubactivity,
    ProjectAttachment,
    ProjectGoNoGoChecklistItem,
    ProjectContractType,
    ProjectContact,
    ProjectObservation,
    ProjectOccurrence,
    ProjectOccurrenceAttachment,
    ProjectRole,
    Product,
    ProposalRequest,
    Submodule,
    KnowledgeAttachment,
    KnowledgeCategory,
    KnowledgePost,
    TimeEntry,
    TimeEntryAttachment,
    Ticket,
    TicketAttachment,
    TicketReply,
    TicketReplyAttachment,
    TicketStatus,
    UserProfile,
    WhatsappSettings,
)
from .whatsapp_notifications import notify_ticket_closed, notify_ticket_updated


class ClientContactInline(admin.TabularInline):
    model = ClientContact
    extra = 0


class ConsultantRateInline(admin.TabularInline):
    model = ConsultantRate
    extra = 0


class ConsultantAttachmentInline(admin.TabularInline):
    model = ConsultantAttachment
    extra = 0


class ConsultantBankAccountInline(admin.TabularInline):
    model = ConsultantBankAccount
    extra = 0


class CompanyBankAccountInline(admin.TabularInline):
    model = CompanyBankAccount
    extra = 0


class ProjectAttachmentInline(admin.TabularInline):
    model = ProjectAttachment
    extra = 0


class ProjectContactInline(admin.TabularInline):
    model = ProjectContact
    extra = 0


class ProjectActivityInline(admin.TabularInline):
    model = ProjectActivity
    extra = 0


class ProjectActivitySubactivityInline(admin.TabularInline):
    model = ProjectActivitySubactivity
    extra = 0


class DeploymentTemplateItemInline(admin.TabularInline):
    model = DeploymentTemplate
    extra = 0


class TimeEntryAttachmentInline(admin.TabularInline):
    model = TimeEntryAttachment
    extra = 0


class TicketAttachmentInline(admin.TabularInline):
    model = TicketAttachment
    extra = 0


class TicketReplyInline(admin.TabularInline):
    model = TicketReply
    extra = 0


class TicketReplyAttachmentInline(admin.TabularInline):
    model = TicketReplyAttachment
    extra = 0


class AccountPlanTemplateItemInline(admin.TabularInline):
    model = AccountPlanTemplateItem
    extra = 0


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("legal_name", "trade_name", "company_type", "tax_id", "status")
    search_fields = ("legal_name", "trade_name", "tax_id")
    list_filter = ("company_type", "status")
    inlines = [CompanyBankAccountInline]


@admin.register(CompanyBankAccount)
class CompanyBankAccountAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "bank_name",
        "agency",
        "account_number",
        "account_digit",
        "initial_balance",
    )
    search_fields = (
        "company__legal_name",
        "company__trade_name",
        "bank_name",
        "agency",
        "account_number",
        "pix_keys",
    )
    list_filter = ("account_type", "bank_name")


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "trade_name", "person_type", "document", "status")
    search_fields = ("name", "trade_name", "document", "email")
    list_filter = ("person_type", "status")


@admin.register(AccountsPayable)
class AccountsPayableAdmin(admin.ModelAdmin):
    list_display = (
        "supplier",
        "consultant",
        "billing_invoice",
        "document_number",
        "due_date",
        "amount",
        "status",
        "settlement_date",
    )
    search_fields = (
        "document_number",
        "description",
        "supplier__name",
        "supplier__trade_name",
        "consultant__full_name",
        "billing_invoice__number",
    )
    list_filter = ("status", "due_date", "supplier")


@admin.register(AccountsPayablePayment)
class AccountsPayablePaymentAdmin(admin.ModelAdmin):
    list_display = (
        "payable",
        "bank_account",
        "payment_date",
        "amount",
        "payment_method",
    )
    search_fields = (
        "payable__document_number",
        "payable__description",
        "bank_account__bank_name",
        "bank_account__company__legal_name",
    )
    list_filter = ("payment_date", "payment_method", "bank_account")


@admin.register(AccountsReceivable)
class AccountsReceivableAdmin(admin.ModelAdmin):
    list_display = (
        "client",
        "billing_invoice",
        "document_number",
        "due_date",
        "amount",
        "status",
        "settlement_date",
    )
    search_fields = (
        "document_number",
        "description",
        "client__name",
        "client__company__legal_name",
        "client__company__trade_name",
        "billing_invoice__number",
    )
    list_filter = ("status", "due_date", "client")


@admin.register(AccountsReceivablePayment)
class AccountsReceivablePaymentAdmin(admin.ModelAdmin):
    list_display = (
        "receivable",
        "bank_account",
        "payment_date",
        "amount",
        "payment_method",
    )
    search_fields = (
        "receivable__document_number",
        "receivable__description",
        "bank_account__bank_name",
        "bank_account__company__legal_name",
    )
    list_filter = ("payment_date", "payment_method", "bank_account")


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "billing_cycle", "payment_terms_days", "status")
    search_fields = ("name", "company__legal_name", "company__trade_name")
    list_filter = ("billing_cycle", "status")
    inlines = [ClientContactInline]


@admin.register(ClientContact)
class ClientContactAdmin(admin.ModelAdmin):
    list_display = ("name", "client", "role", "email", "is_primary", "status")
    search_fields = ("name", "client__name", "email")
    list_filter = ("status", "is_primary")


@admin.register(Competency)
class CompetencyAdmin(admin.ModelAdmin):
    list_display = ("name", "status")
    search_fields = ("name",)
    list_filter = ("status",)


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ("name", "issuer", "status")
    search_fields = ("name", "issuer")
    list_filter = ("status",)


@admin.register(Phase)
class PhaseAdmin(admin.ModelAdmin):
    list_display = ("description", "status")
    search_fields = ("description",)
    list_filter = ("status",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("description", "status")
    search_fields = ("description",)
    list_filter = ("status",)


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("description", "product", "status")
    search_fields = ("description", "product__description")
    list_filter = ("status", "product")


@admin.register(Submodule)
class SubmoduleAdmin(admin.ModelAdmin):
    list_display = ("description", "product", "module", "status")
    search_fields = ("description", "product__description", "module__description")
    list_filter = ("status", "product", "module")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "description",
        "received_date",
        "planned_go_live_date",
        "cutover_planned_start",
        "cutover_planned_end",
        "billing_client",
        "project_client",
        "contract_type",
        "status",
        "total_value",
        "hourly_rate",
        "contracted_hours",
        "contingency_percent",
        "available_hours",
        "available_value",
    )
    search_fields = ("description",)
    list_filter = ("status", "contract_type", "billing_client", "project_client")
    readonly_fields = ("available_hours", "available_value")
    inlines = [ProjectContactInline, ProjectAttachmentInline, ProjectActivityInline]

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if obj and obj.contract_type == ProjectContractType.FIXED_VALUE:
            fields.append("contracted_hours")
        return tuple(fields)

    def save_model(self, request, obj, form, change):
        before = None
        if change and obj.pk:
            before = Project.objects.get(pk=obj.pk)
        super().save_model(request, obj, form, change)
        if before:
            create_project_change_observation(before, obj, request.user)
            if before.received_date != obj.received_date:
                create_project_receipt_observation(
                    obj,
                    request.user,
                    previous_date=before.received_date,
                )
        else:
            create_project_receipt_observation(obj, request.user)


@admin.register(ProjectAttachment)
class ProjectAttachmentAdmin(admin.ModelAdmin):
    list_display = ("project", "attachment_type", "description", "file", "created_at")
    search_fields = ("description", "project__description")
    list_filter = ("attachment_type", "project")


@admin.register(ProjectObservation)
class ProjectObservationAdmin(admin.ModelAdmin):
    list_display = (
        "project",
        "observation_type",
        "created_by",
        "created_at",
    )
    search_fields = ("project__description", "note")
    list_filter = ("observation_type", "created_at")


@admin.register(ProjectGoNoGoChecklistItem)
class ProjectGoNoGoChecklistItemAdmin(admin.ModelAdmin):
    list_display = (
        "project",
        "criterion",
        "category",
        "result",
        "visibility",
        "created_at",
    )
    search_fields = ("project__description", "criterion", "category", "approver")
    list_filter = ("result", "visibility", "project")


@admin.register(ProjectOccurrence)
class ProjectOccurrenceAdmin(admin.ModelAdmin):
    list_display = ("project", "title", "visibility", "created_by", "created_at")
    search_fields = ("project__description", "title", "description")
    list_filter = ("visibility", "created_at")


@admin.register(ProjectOccurrenceAttachment)
class ProjectOccurrenceAttachmentAdmin(admin.ModelAdmin):
    list_display = ("occurrence", "description", "file", "created_at")
    search_fields = ("occurrence__title", "description")


@admin.register(ProjectRole)
class ProjectRoleAdmin(admin.ModelAdmin):
    list_display = ("name", "status")
    search_fields = ("name",)
    list_filter = ("status",)


@admin.register(ProjectContact)
class ProjectContactAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "project",
        "role",
        "phone",
        "email",
        "receives_status_report",
        "receives_delay_email",
    )
    search_fields = ("name", "project__description", "email")
    list_filter = ("role", "receives_status_report", "receives_delay_email")


@admin.register(CandidateApplication)
class CandidateApplicationAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "phone", "role_interest", "created_at")
    search_fields = ("full_name", "email", "role_interest")
    list_filter = ("created_at",)


@admin.register(ProposalRequest)
class ProposalRequestAdmin(admin.ModelAdmin):
    list_display = (
        "company_name",
        "contact_name",
        "email",
        "estimated_start",
        "created_at",
    )
    search_fields = ("company_name", "contact_name", "email")
    list_filter = ("estimated_start", "created_at")


@admin.register(KnowledgeCategory)
class KnowledgeCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "created_at", "updated_at")
    search_fields = ("name",)
    list_filter = ("status",)


@admin.register(KnowledgePost)
class KnowledgePostAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "author", "status", "updated_at")
    search_fields = ("title", "content", "author__username", "author__email")
    list_filter = ("status", "category")


@admin.register(KnowledgeAttachment)
class KnowledgeAttachmentAdmin(admin.ModelAdmin):
    list_display = ("post", "file", "uploaded_by", "created_at")
    search_fields = ("post__title", "file")
    list_filter = ("created_at",)


@admin.register(DeploymentTemplateHeader)
class DeploymentTemplateHeaderAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    inlines = [DeploymentTemplateItemInline]


@admin.register(DeploymentTemplate)
class DeploymentTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "template",
        "seq",
        "phase",
        "product",
        "module",
        "submodule",
    )
    search_fields = ("template__name", "activity", "subactivity")
    list_filter = ("template", "phase", "product", "module", "submodule")


@admin.register(AccountPlanTemplateHeader)
class AccountPlanTemplateHeaderAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    inlines = [AccountPlanTemplateItemInline]


@admin.register(AccountPlanTemplateItem)
class AccountPlanTemplateItemAdmin(admin.ModelAdmin):
    list_display = (
        "template",
        "code",
        "description",
        "level",
        "parent",
        "account_type",
        "nature",
        "status",
    )
    search_fields = ("template__name", "code", "description")
    list_filter = ("template", "account_type", "nature", "status")


@admin.register(WhatsappSettings)
class WhatsappSettingsAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "updated_at")


@admin.register(Consultant)
class ConsultantAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "user",
        "contract_type",
        "company",
        "supplier",
        "birth_date",
        "status",
    )
    search_fields = (
        "full_name",
        "email",
        "document",
        "user__username",
        "supplier__name",
        "supplier__trade_name",
        "supplier__document",
    )
    list_filter = ("contract_type", "status")
    inlines = [ConsultantRateInline, ConsultantAttachmentInline, ConsultantBankAccountInline]
    filter_horizontal = ("competencies", "certifications")


@admin.register(ConsultantRate)
class ConsultantRateAdmin(admin.ModelAdmin):
    list_display = ("consultant", "rate", "currency", "start_date", "end_date")
    search_fields = ("consultant__full_name",)
    list_filter = ("currency",)


@admin.register(ConsultantBankAccount)
class ConsultantBankAccountAdmin(admin.ModelAdmin):
    list_display = (
        "consultant",
        "bank_name",
        "account_type",
        "agency",
        "account_number",
        "account_digit",
    )
    search_fields = ("consultant__full_name", "bank_name", "agency", "account_number")
    list_filter = ("account_type",)


@admin.register(ConsultantAttachment)
class ConsultantAttachmentAdmin(admin.ModelAdmin):
    list_display = ("consultant", "description", "file", "created_at")
    search_fields = ("description", "consultant__full_name")
    list_filter = ("consultant",)


@admin.register(ProjectActivity)
class ProjectActivityAdmin(admin.ModelAdmin):
    list_display = (
        "project",
        "seq",
        "phase",
        "product",
        "module",
        "submodule",
        "account_plan_item",
        "planned_start",
        "planned_end",
        "actual_start",
        "actual_end",
        "status",
        "billing_type",
        "client_visible",
    )
    search_fields = (
        "project__description",
        "activity",
        "subactivity",
        "subactivity_items__description",
    )
    list_filter = (
        "project",
        "phase",
        "product",
        "module",
        "submodule",
        "status",
        "billing_type",
    )
    inlines = [ProjectActivitySubactivityInline]
    filter_horizontal = ("consultants",)


@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = (
        "activity",
        "consultant",
        "entry_type",
        "status",
        "billing_invoice_number",
        "start_date",
        "end_date",
        "total_hours",
    )
    search_fields = (
        "activity__project__description",
        "activity__activity",
        "activity__subactivity",
        "activity__subactivity_items__description",
        "consultant__full_name",
    )
    list_filter = ("entry_type", "status", "consultant", "activity__project")
    inlines = [TimeEntryAttachmentInline]


@admin.register(BillingInvoice)
class BillingInvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "number",
        "billing_client",
        "project",
        "period_start",
        "period_end",
        "total_hours",
        "total_value",
        "payment_status",
    )
    search_fields = ("number", "billing_client__name", "project__description")
    list_filter = ("payment_status", "billing_client", "project")


@admin.register(BillingInvoiceItem)
class BillingInvoiceItemAdmin(admin.ModelAdmin):
    list_display = ("invoice", "consultant", "hours", "rate", "total")
    search_fields = ("invoice__number", "consultant__full_name")
    list_filter = ("invoice", "consultant")


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "project",
        "ticket_type",
        "criticality",
        "status",
        "assigned_to",
        "consultant_responsible",
        "created_by",
        "created_at",
        "closed_at",
    )
    search_fields = ("title", "description", "project__description")
    list_filter = (
        "status",
        "ticket_type",
        "criticality",
        "project",
        "consultant_responsible",
    )
    inlines = [TicketAttachmentInline, TicketReplyInline]

    def save_model(self, request, obj, form, change):
        previous_status = None
        if change and obj.pk:
            previous_status = Ticket.objects.filter(pk=obj.pk).values_list(
                "status", flat=True
            ).first()
        super().save_model(request, obj, form, change)
        if not change or not form.changed_data:
            return
        if obj.status == TicketStatus.CLOSED and previous_status != TicketStatus.CLOSED:
            notify_ticket_closed(obj)
            return
        notify_ticket_updated(obj)


@admin.register(TicketAttachment)
class TicketAttachmentAdmin(admin.ModelAdmin):
    list_display = ("ticket", "file", "created_at")
    search_fields = ("ticket__title", "ticket__project__description")
    list_filter = ("created_at",)


@admin.register(TicketReply)
class TicketReplyAdmin(admin.ModelAdmin):
    list_display = ("ticket", "author", "created_at")
    search_fields = ("ticket__title", "message", "author__username")
    list_filter = ("created_at",)
    inlines = [TicketReplyAttachmentInline]


@admin.register(TicketReplyAttachment)
class TicketReplyAttachmentAdmin(admin.ModelAdmin):
    list_display = ("reply", "file", "created_at")
    search_fields = ("reply__ticket__title",)
    list_filter = ("created_at",)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "whatsapp_phone", "created_at", "updated_at")
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "whatsapp_phone",
    )
    list_filter = ("role",)
