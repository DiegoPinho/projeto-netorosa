import os
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        abstract = True


class StatusChoices(models.TextChoices):
    ACTIVE = "active", "Ativo"
    INACTIVE = "inactive", "Inativo"
    PENDING = "pending", "Pendente"


class UserRole(models.TextChoices):
    ADMIN = "admin", "Admin"
    GP_INTERNAL = "gp_internal", "GP interno"
    GP_EXTERNAL = "gp_external", "GP externo"
    CONSULTANT = "consultant", "Consultor"
    CLIENT = "client", "Cliente"


class CompanyType(models.TextChoices):
    PRIMARY = "primary", "Empresa principal"
    BRANCH = "branch", "Filial"
    CLIENT = "client", "Cliente"


class BillingCycle(models.TextChoices):
    MONTHLY = "monthly", "Mensal"
    BIWEEKLY = "biweekly", "Quinzenal"
    WEEKLY = "weekly", "Semanal"
    ON_DEMAND = "on_demand", "Sob demanda"


class ConsultantType(models.TextChoices):
    PJ = "pj", "PJ"
    PF = "pf", "PF"


class SupplierPersonType(models.TextChoices):
    PF = "pf", "Pessoa fisica"
    PJ = "pj", "Pessoa juridica"


class BankAccountType(models.TextChoices):
    PF = "pf", "Pessoa fisica"
    PJ = "pj", "Pessoa juridica"


class BankMovementDirection(models.TextChoices):
    CREDIT = "credit", "Credito"
    DEBIT = "debit", "Debito"


class BankMovementSource(models.TextChoices):
    MANUAL = "manual", "Manual"
    OFX = "ofx", "Importado OFX"


class ProjectStatus(models.TextChoices):
    BUDGET = "budget", "Orcamento"
    IMPLEMENTATION = "implementation", "Em Implantacao"
    PAUSED = "paused", "Paralizado"
    CANCELED = "canceled", "Cancelado"
    COMPLETED = "completed", "Finalizado"


class ProjectType(models.TextChoices):
    BILLABLE = "billable", "Faturavel"
    INTERNAL = "internal", "Projeto interno"


class ProjectContractType(models.TextChoices):
    FIXED_HOURS = "fixed_hours", "Pacote fechado por hora"
    FIXED_VALUE = "fixed_value", "Pacote fechado por valor"
    HOURLY_PROJECT = "hourly_project", "Projeto por horas"
    AD_HOC = "ad_hoc", "Demanda avulsa"


class DatabaseType(models.TextChoices):
    SQL_SERVER = "sql_server", "SQL Server"
    ORACLE = "oracle", "Oracle"


class ProjectCriticality(models.TextChoices):
    LOW = "low", "Baixa"
    MEDIUM = "medium", "Media"
    HIGH = "high", "Alta"
    CRITICAL = "critical", "Critico"


class ActivityStatus(models.TextChoices):
    IN_PROGRESS = "in_progress", "Pendente"
    PLANNED = "planned", "Planejada"
    RELEASED = "released", "Liberada"
    DONE = "done", "Concluida"
    BLOCKED = "blocked", "Paralizada"
    CANCELED = "canceled", "Cancelada"


class ActivityBillingType(models.TextChoices):
    BILLABLE = "billable", "Faturavel"
    ASSUMED_COMPANY = "assumed_company", "Horas Assumidas (empresa)"
    ASSUMED_CONSULTANT = "assumed_consultant", "Horas Assumidas (Consultor)"
    CLIENT_ASSIGNED = "client_assigned", "Atividade atribuida ao Cliente"


class ActivityAssumedReason(models.TextChoices):
    REWORK = "rework", "Retrabalho"
    UNPLANNED = "unplanned", "Nao Planejadas"
    COURTESY = "courtesy", "Cortezia"


class ActivityCriticality(models.TextChoices):
    LOW = "low", "Baixa"
    MEDIUM = "medium", "Media"
    HIGH = "high", "Alta"
    CRITICAL = "critical", "Critica"


class TimeEntryType(models.TextChoices):
    DAILY = "daily", "Diario"
    WEEKLY = "weekly", "Semanal"


class TimeEntryStatus(models.TextChoices):
    PENDING = "pending", "Pendente"
    APPROVED = "approved", "Aprovada"
    REJECTED = "rejected", "Reprovada"


class BillingPaymentStatus(models.TextChoices):
    UNPAID = "unpaid", "Nao pago"
    PAID = "paid", "Pago"


class FinancialStatus(models.TextChoices):
    OPEN = "open", "Aberto"
    OVERDUE = "overdue", "Atrasado"
    PAID = "paid", "Pago"
    CANCELED = "canceled", "Cancelado"


class PaymentMethod(models.TextChoices):
    PIX = "pix", "Pix"
    TRANSFER = "transfer", "Transferencia"
    BOLETO = "boleto", "Boleto"
    CARD = "card", "Cartao"
    CASH = "cash", "Dinheiro"
    OTHER = "other", "Outro"


class TicketStatus(models.TextChoices):
    OPEN = "open", "Aberto"
    CLOSED = "closed", "Encerrado"


class TicketType(models.TextChoices):
    QUESTION = "question", "Duvida"
    ERROR = "error", "Erro"
    IMPROVEMENT = "improvement", "Solicitacao de melhoria"


class TicketCriticality(models.TextChoices):
    LOW = "low", "Baixa"
    MEDIUM = "medium", "Media"
    HIGH = "high", "Alta"
    CRITICAL = "critical", "Critica"


class UserProfile(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Usuario",
    )
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CONSULTANT,
        verbose_name="Perfil",
    )
    whatsapp_phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Telefone WhatsApp",
        help_text="Recebe mensagens de WhatsApp do sistema.",
    )
    must_change_password = models.BooleanField(
        default=True,
        verbose_name="Trocar senha no primeiro acesso",
    )

    class Meta:
        verbose_name = "Perfil de usuario"
        verbose_name_plural = "Perfis de usuario"

    def __str__(self) -> str:
        return f"{self.user} ({self.get_role_display()})"


class AccountType(models.TextChoices):
    ASSET = "asset", "Ativo"
    LIABILITY = "liability", "Passivo"
    EQUITY = "equity", "Patrimonio liquido"
    REVENUE = "revenue", "Receita"
    COST = "cost", "Custo"
    EXPENSE = "expense", "Despesa"
    OTHER = "other", "Outro"


class AccountNature(models.TextChoices):
    DEBIT = "debit", "Debito"
    CREDIT = "credit", "Credito"


class DreSign(models.TextChoices):
    ADD = "add", "Somar"
    SUBTRACT = "subtract", "Subtrair"


class Company(TimeStampedModel):
    company_type = models.CharField(
        max_length=20,
        choices=CompanyType.choices,
        default=CompanyType.CLIENT,
        verbose_name="Tipo de empresa",
    )
    legal_name = models.CharField(max_length=200, verbose_name="Razao social")
    trade_name = models.CharField(max_length=200, blank=True, verbose_name="Nome fantasia")
    tax_id = models.CharField(max_length=32, unique=True, verbose_name="CNPJ")
    state_registration = models.CharField(
        max_length=40,
        blank=True,
        verbose_name="Inscricao estadual",
    )
    municipal_registration = models.CharField(
        max_length=40,
        blank=True,
        verbose_name="Inscricao municipal",
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
        verbose_name="Status",
    )
    billing_email = models.EmailField(blank=True, verbose_name="Email de faturamento")
    phone = models.CharField(max_length=30, blank=True, verbose_name="Telefone")
    address_line = models.CharField(max_length=255, blank=True, verbose_name="Endereco")
    city = models.CharField(max_length=100, blank=True, verbose_name="Cidade")
    state = models.CharField(max_length=100, blank=True, verbose_name="Estado")
    postal_code = models.CharField(max_length=20, blank=True, verbose_name="CEP")
    country = models.CharField(max_length=2, default="BR", verbose_name="Pais")
    notes = models.TextField(blank=True, verbose_name="Observacoes")

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"

    def __str__(self) -> str:
        return self.trade_name or self.legal_name


class Supplier(TimeStampedModel):
    person_type = models.CharField(
        max_length=2,
        choices=SupplierPersonType.choices,
        default=SupplierPersonType.PJ,
        verbose_name="Tipo",
    )
    document = models.CharField(max_length=32, unique=True, verbose_name="CPF/CNPJ")
    name = models.CharField(max_length=200, verbose_name="Nome/Razao social")
    trade_name = models.CharField(max_length=200, blank=True, verbose_name="Nome fantasia")
    email = models.EmailField(blank=True, verbose_name="Email")
    phone = models.CharField(max_length=30, blank=True, verbose_name="Telefone")
    address_line = models.CharField(max_length=255, blank=True, verbose_name="Endereco")
    city = models.CharField(max_length=100, blank=True, verbose_name="Cidade")
    state = models.CharField(max_length=100, blank=True, verbose_name="Estado")
    postal_code = models.CharField(max_length=20, blank=True, verbose_name="CEP")
    country = models.CharField(max_length=2, default="BR", verbose_name="Pais")
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
        verbose_name="Status",
    )
    notes = models.TextField(blank=True, verbose_name="Observacoes")

    class Meta:
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"

    def __str__(self) -> str:
        return self.trade_name or self.name


class Client(TimeStampedModel):
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="clients",
        verbose_name="Empresa",
    )
    name = models.CharField(max_length=200, verbose_name="Nome")
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
        verbose_name="Status",
    )
    billing_cycle = models.CharField(
        max_length=20,
        choices=BillingCycle.choices,
        default=BillingCycle.MONTHLY,
        verbose_name="Ciclo de faturamento",
    )
    payment_terms_days = models.PositiveSmallIntegerField(
        default=30,
        verbose_name="Prazo de pagamento (dias)",
    )
    contract_start = models.DateField(
        null=True,
        blank=True,
        verbose_name="Inicio do contrato",
    )
    contract_end = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fim do contrato",
    )
    commercial_notes = models.TextField(blank=True, verbose_name="Observacoes comerciais")

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self) -> str:
        return self.name


class FinancialEntry(TimeStampedModel):
    document_number = models.CharField(max_length=60, verbose_name="Numero do documento")
    description = models.CharField(max_length=200, verbose_name="Descricao")
    issue_date = models.DateField(
        default=timezone.localdate,
        verbose_name="Data de emissao",
    )
    due_date = models.DateField(verbose_name="Data de vencimento")
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Valor",
    )
    discount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Desconto",
    )
    interest = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Juros",
    )
    penalty = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Multa",
    )
    status = models.CharField(
        max_length=20,
        choices=FinancialStatus.choices,
        default=FinancialStatus.OPEN,
        verbose_name="Status",
    )
    settlement_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de liquidacao",
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        blank=True,
        verbose_name="Forma de pagamento",
    )
    notes = models.TextField(blank=True, verbose_name="Observacoes")

    class Meta:
        abstract = True

    def total_amount(self) -> Decimal:
        amount = self.amount or Decimal("0.00")
        discount = self.discount or Decimal("0.00")
        interest = self.interest or Decimal("0.00")
        penalty = self.penalty or Decimal("0.00")
        return (amount - discount + interest + penalty).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

    def clean(self) -> None:
        super().clean()
        errors = {}
        if self.amount is not None and self.amount < 0:
            errors["amount"] = "Valor nao pode ser negativo."
        if self.discount is not None and self.discount < 0:
            errors["discount"] = "Desconto nao pode ser negativo."
        if self.interest is not None and self.interest < 0:
            errors["interest"] = "Juros nao pode ser negativo."
        if self.penalty is not None and self.penalty < 0:
            errors["penalty"] = "Multa nao pode ser negativa."
        if self.amount is not None and self.discount is not None and self.discount > self.amount:
            errors["discount"] = "Desconto nao pode ser maior que o valor."
        if self.issue_date and self.due_date and self.due_date < self.issue_date:
            errors["due_date"] = "Vencimento nao pode ser anterior a emissao."
        if (
            self.settlement_date
            and self.issue_date
            and self.settlement_date < self.issue_date
        ):
            errors["settlement_date"] = "Liquidacao nao pode ser anterior a emissao."
        if self.status == FinancialStatus.PAID and not self.settlement_date:
            errors["settlement_date"] = "Informe a data de liquidacao para contas pagas."
        if self.status == FinancialStatus.CANCELED and self.settlement_date:
            errors["settlement_date"] = "Conta cancelada nao pode ter data de liquidacao."
        if errors:
            raise ValidationError(errors)

    def _sync_status(self) -> None:
        if self.status == FinancialStatus.CANCELED:
            return
        if self.settlement_date:
            self.status = FinancialStatus.PAID
            return
        if self.due_date and self.due_date < timezone.localdate():
            self.status = FinancialStatus.OVERDUE
        elif self.status == FinancialStatus.OVERDUE:
            self.status = FinancialStatus.OPEN

    def save(self, *args, **kwargs) -> None:
        self._sync_status()
        super().save(*args, **kwargs)


class AccountsPayable(FinancialEntry):
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="accounts_payable",
        verbose_name="Fornecedor",
    )
    consultant = models.ForeignKey(
        "Consultant",
        on_delete=models.SET_NULL,
        related_name="accounts_payable_titles",
        null=True,
        blank=True,
        verbose_name="Consultor",
    )
    billing_invoice = models.ForeignKey(
        "BillingInvoice",
        on_delete=models.PROTECT,
        related_name="accounts_payable_titles",
        null=True,
        blank=True,
        verbose_name="Fatura",
    )
    account_plan_item = models.ForeignKey(
        "AccountPlanTemplateItem",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="accounts_payable_entries",
        verbose_name="Conta do plano de contas",
    )

    class Meta:
        verbose_name = "Conta a pagar"
        verbose_name_plural = "Contas a pagar"
        ordering = ("due_date", "id")
        constraints = [
            models.UniqueConstraint(
                fields=["supplier", "document_number"],
                name="unique_payable_document_per_supplier",
            )
        ]

    def __str__(self) -> str:
        return f"{self.document_number} - {self.supplier}"


def _accounts_payable_attachment_path(
    instance: "AccountsPayableAttachment", filename: str
) -> str:
    safe_name = os.path.basename(filename)
    payable_id = instance.payable_id or "temp"
    return f"accounts-payable/{payable_id}/attachments/{safe_name}"


class AccountsPayableAttachment(TimeStampedModel):
    payable = models.ForeignKey(
        AccountsPayable,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="Conta a pagar",
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Descricao",
    )
    file = models.FileField(
        upload_to=_accounts_payable_attachment_path,
        verbose_name="Arquivo",
    )

    class Meta:
        verbose_name = "Anexo da conta a pagar"
        verbose_name_plural = "Anexos das contas a pagar"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        if self.description:
            return self.description
        return os.path.basename(self.file.name) if self.file else "Anexo"


class AccountsReceivable(FinancialEntry):
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name="accounts_receivable",
        verbose_name="Cliente",
    )
    billing_invoice = models.ForeignKey(
        "BillingInvoice",
        on_delete=models.PROTECT,
        related_name="accounts_receivable_titles",
        null=True,
        blank=True,
        verbose_name="Fatura",
    )
    account_plan_item = models.ForeignKey(
        "AccountPlanTemplateItem",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="accounts_receivable_entries",
        verbose_name="Conta do plano de contas",
    )

    class Meta:
        verbose_name = "Conta a receber"
        verbose_name_plural = "Contas a receber"
        ordering = ("due_date", "id")
        constraints = [
            models.UniqueConstraint(
                fields=["client", "document_number"],
                name="unique_receivable_document_per_client",
            )
        ]

    def __str__(self) -> str:
        return f"{self.document_number} - {self.client}"

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        self._sync_invoice_payment_status()

    def _sync_invoice_payment_status(self) -> None:
        invoice = self.billing_invoice
        if not invoice:
            return
        receivables = invoice.accounts_receivable_titles.all()
        if not receivables.exists():
            new_status = BillingPaymentStatus.UNPAID
        else:
            unpaid_exists = receivables.exclude(status=FinancialStatus.PAID).exists()
            new_status = (
                BillingPaymentStatus.UNPAID
                if unpaid_exists
                else BillingPaymentStatus.PAID
            )
        if invoice.payment_status != new_status:
            invoice.payment_status = new_status
            invoice.save(update_fields=["payment_status"])


class ClientContact(TimeStampedModel):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="contacts",
        verbose_name="Cliente",
    )
    name = models.CharField(max_length=150, verbose_name="Nome")
    role = models.CharField(max_length=120, blank=True, verbose_name="Cargo")
    email = models.EmailField(blank=True, verbose_name="Email")
    phone = models.CharField(max_length=30, blank=True, verbose_name="Telefone")
    is_primary = models.BooleanField(default=False, verbose_name="Contato principal")
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
        verbose_name="Status",
    )

    class Meta:
        verbose_name = "Contato do cliente"
        verbose_name_plural = "Contatos do cliente"
        constraints = [
            models.UniqueConstraint(
                fields=["client"],
                condition=Q(is_primary=True),
                name="unique_primary_contact_per_client",
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.client})"


class Competency(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True, verbose_name="Nome")
    description = models.TextField(blank=True, verbose_name="Descricao")
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
        verbose_name="Status",
    )

    class Meta:
        verbose_name = "Competencia"
        verbose_name_plural = "Competencias"

    def __str__(self) -> str:
        return self.name


class Certification(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True, verbose_name="Nome")
    issuer = models.CharField(max_length=120, blank=True, verbose_name="Emissor")
    description = models.TextField(blank=True, verbose_name="Descricao")
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
        verbose_name="Status",
    )

    class Meta:
        verbose_name = "Certificacao"
        verbose_name_plural = "Certificacoes"

    def __str__(self) -> str:
        return self.name


class Phase(TimeStampedModel):
    description = models.CharField(max_length=200, verbose_name="Descricao")
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
        verbose_name="Situacao",
    )

    class Meta:
        verbose_name = "Fase"
        verbose_name_plural = "Fases"

    def __str__(self) -> str:
        return self.description


class Product(TimeStampedModel):
    description = models.CharField(max_length=200, verbose_name="Descricao")
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
        verbose_name="Situacao",
    )

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"

    def __str__(self) -> str:
        return self.description


class Module(TimeStampedModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="modules",
        verbose_name="Produto",
    )
    description = models.CharField(max_length=200, verbose_name="Descricao")
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
        verbose_name="Situacao",
    )

    class Meta:
        verbose_name = "Modulo"
        verbose_name_plural = "Modulos"

    def __str__(self) -> str:
        return f"{self.product} - {self.description}"


class Submodule(TimeStampedModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="submodules",
        verbose_name="Produto",
    )
    module = models.ForeignKey(
        Module,
        on_delete=models.PROTECT,
        related_name="submodules",
        verbose_name="Modulo",
    )
    description = models.CharField(max_length=200, verbose_name="Descricao")
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
        verbose_name="Situacao",
    )

    class Meta:
        verbose_name = "Submodulo"
        verbose_name_plural = "Submodulos"

    def clean(self) -> None:
        super().clean()
        if self.product_id and self.module_id and self.module.product_id != self.product_id:
            raise ValidationError(
                {"module": "Modulo nao pertence ao produto selecionado."}
            )

    def __str__(self) -> str:
        return f"{self.module} - {self.description}"


def _project_attachment_path(instance: "ProjectAttachment", filename: str) -> str:
    safe_name = os.path.basename(filename)
    project_id = instance.project_id or "temp"
    return f"projects/{project_id}/attachments/{safe_name}"

def _project_occurrence_attachment_path(
    instance: "ProjectOccurrenceAttachment", filename: str
) -> str:
    safe_name = os.path.basename(filename)
    project_id = (
        instance.occurrence.project_id
        if instance.occurrence_id and instance.occurrence
        else "temp"
    )
    occurrence_id = instance.occurrence_id or "temp"
    return f"projects/{project_id}/occurrences/{occurrence_id}/attachments/{safe_name}"


def _candidate_resume_path(instance: "CandidateApplication", filename: str) -> str:
    safe_name = os.path.basename(filename)
    date = timezone.localdate().strftime("%Y%m%d")
    return f"public/candidates/{date}/{safe_name}"


def _time_entry_attachment_path(instance: "TimeEntryAttachment", filename: str) -> str:
    safe_name = os.path.basename(filename)
    entry_id = instance.time_entry_id or "temp"
    return f"time-entries/{entry_id}/attachments/{safe_name}"

def _ticket_attachment_path(instance: "TicketAttachment", filename: str) -> str:
    safe_name = os.path.basename(filename)
    ticket_id = instance.ticket_id or "temp"
    return f"tickets/{ticket_id}/attachments/{safe_name}"


def _ticket_reply_attachment_path(instance: "TicketReplyAttachment", filename: str) -> str:
    safe_name = os.path.basename(filename)
    ticket_id = instance.reply.ticket_id if instance.reply_id else "temp"
    reply_id = instance.reply_id or "temp"
    return f"tickets/{ticket_id}/replies/{reply_id}/{safe_name}"


class Project(TimeStampedModel):
    billing_client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name="billing_projects",
        verbose_name="Cliente de faturamento",
    )
    project_client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name="projects",
        verbose_name="Cliente do projeto",
    )
    description = models.CharField(max_length=200, verbose_name="Descricao do projeto")
    cloud_environment = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Ambiente cloud do cliente",
    )
    database_type = models.CharField(
        max_length=20,
        choices=DatabaseType.choices,
        blank=True,
        default="",
        verbose_name="Banco de dados",
    )
    hml_url = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Endereco HML",
    )
    prd_url = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Endereco PRD",
    )
    senior_client_code = models.CharField(
        max_length=60,
        blank=True,
        default="",
        verbose_name="Codigo do cliente na Senior",
    )
    senior_project_code = models.CharField(
        max_length=60,
        blank=True,
        default="",
        verbose_name="Codigo do projeto na Senior",
    )
    received_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de recebimento",
    )
    planned_go_live_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Go live planejado",
    )
    cutover_planned_start = models.DateField(
        null=True,
        blank=True,
        verbose_name="Inicio planejado do cutover",
    )
    cutover_planned_end = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fim planejado do cutover",
    )
    explanation = models.TextField(
        blank=True,
        default="",
        verbose_name="Explicacao do projeto",
    )
    project_type = models.CharField(
        max_length=20,
        choices=ProjectType.choices,
        default=ProjectType.BILLABLE,
        verbose_name="Tipo de projeto",
    )
    contract_type = models.CharField(
        max_length=20,
        choices=ProjectContractType.choices,
        default=ProjectContractType.FIXED_VALUE,
        verbose_name="Classificacao do projeto",
    )
    criticality = models.CharField(
        max_length=20,
        choices=ProjectCriticality.choices,
        default=ProjectCriticality.MEDIUM,
        verbose_name="Criticidade",
    )
    status = models.CharField(
        max_length=20,
        choices=ProjectStatus.choices,
        default=ProjectStatus.BUDGET,
        verbose_name="Status",
    )
    total_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Valor total contratado (R$)",
    )
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor hora (R$)",
    )
    contracted_hours = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Horas contratadas",
    )
    contingency_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Contingencia (%)",
    )
    available_hours = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Horas disponiveis",
    )
    available_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Valor disponivel (R$)",
    )
    internal_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects_internal",
        verbose_name="GP interno",
    )
    external_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects_external",
        verbose_name="GP externo",
    )
    client_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects_client_user",
        verbose_name="Usuario do cliente",
    )

    class Meta:
        verbose_name = "Projeto"
        verbose_name_plural = "Projetos"

    def clean(self) -> None:
        super().clean()
        errors = {}
        if self.contingency_percent < 0 or self.contingency_percent > 100:
            errors["contingency_percent"] = "Contingencia deve estar entre 0 e 100."
        if self.hourly_rate <= 0:
            errors["hourly_rate"] = "Valor hora deve ser maior que zero."
        contract_type = self.contract_type or ProjectContractType.FIXED_VALUE
        if contract_type == ProjectContractType.FIXED_VALUE:
            if self.total_value <= 0:
                errors["total_value"] = "Valor total contratado deve ser maior que zero."
        else:
            if self.contracted_hours <= 0:
                errors["contracted_hours"] = "Horas contratadas devem ser maiores que zero."
        if self.total_value < 0:
            errors["total_value"] = "Valor total contratado nao pode ser negativo."
        if (
            self.cutover_planned_start
            and self.cutover_planned_end
            and self.cutover_planned_end < self.cutover_planned_start
        ):
            errors["cutover_planned_end"] = (
                "Fim planejado do cutover deve ser maior ou igual ao inicio planejado."
            )
        if errors:
            raise ValidationError(errors)

    def _calculate_metrics(self) -> tuple[Decimal, Decimal, Decimal, Decimal]:
        total_value = self.total_value or Decimal("0.00")
        hourly_rate = self.hourly_rate or Decimal("0.00")
        contracted = self.contracted_hours or Decimal("0.00")
        contract_type = self.contract_type or ProjectContractType.FIXED_VALUE
        if contract_type == ProjectContractType.FIXED_VALUE:
            if hourly_rate > 0:
                contracted = (total_value / hourly_rate).quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP,
                )
            else:
                contracted = Decimal("0.00")
        else:
            if hourly_rate > 0:
                total_value = (contracted * hourly_rate).quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP,
                )
            else:
                total_value = Decimal("0.00")
        factor = Decimal("1.00") - (self.contingency_percent / Decimal("100.00"))
        if factor < 0:
            factor = Decimal("0.00")
        available_hours = (contracted * factor).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
        available_value = (total_value * factor).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
        return total_value, contracted, available_hours, available_value

    def save(self, *args, **kwargs) -> None:
        total_value, contracted, available_hours, available_value = self._calculate_metrics()
        self.total_value = total_value
        self.contracted_hours = contracted
        self.available_hours = available_hours
        self.available_value = available_value
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.description


class ProjectRole(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True, verbose_name="Papel")
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
        verbose_name="Situacao",
    )

    class Meta:
        verbose_name = "Papel de projeto"
        verbose_name_plural = "Papeis de projeto"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class ProjectContact(TimeStampedModel):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="contacts",
        verbose_name="Projeto",
    )
    name = models.CharField(max_length=150, verbose_name="Nome")
    phone = models.CharField(max_length=30, blank=True, verbose_name="Telefone")
    function = models.CharField(max_length=120, blank=True, verbose_name="Funcao")
    email = models.EmailField(blank=True, verbose_name="Email")
    role = models.ForeignKey(
        ProjectRole,
        on_delete=models.PROTECT,
        related_name="project_contacts",
        verbose_name="Papel",
    )
    receives_status_report = models.BooleanField(
        default=False,
        verbose_name="Rec status report",
    )
    receives_delay_email = models.BooleanField(
        default=False,
        verbose_name="Rec e-mail atrasos",
    )

    class Meta:
        verbose_name = "Pessoa do projeto"
        verbose_name_plural = "Pessoas do projeto"
        ordering = ("project", "name")

    def __str__(self) -> str:
        return f"{self.name} - {self.project}"


class ProjectObservationType(models.TextChoices):
    MANUAL = "manual", "Manual"
    AUTO = "auto", "Automatica"
    CHANGE = "change", "Alteracao"


class ProjectVisibility(models.TextChoices):
    ALL = "all", "Todos"
    MANAGEMENT = "management", "Gestao"
    TEAM = "team", "Equipe"
    EXTERNAL_TEAM = "external_team", "Equipe Externa"
    PRIVATE = "private", "Privada"


class GoNoGoResult(models.TextChoices):
    OK = "ok", "OK"
    NO = "no", "Nao"
    PENDING = "pending", "Pendente"


class ProjectObservation(TimeStampedModel):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="observations",
        verbose_name="Projeto",
    )
    observation_type = models.CharField(
        max_length=20,
        choices=ProjectObservationType.choices,
        default=ProjectObservationType.MANUAL,
        verbose_name="Tipo",
    )
    note = models.TextField(blank=True, verbose_name="Observacao")
    changes = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Alteracoes",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="project_observations",
        verbose_name="Registrado por",
    )

    class Meta:
        verbose_name = "Observacao do projeto"
        verbose_name_plural = "Observacoes do projeto"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.project} - {self.get_observation_type_display()}"


class ProjectGoNoGoChecklistItem(TimeStampedModel):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="go_no_go_items",
        verbose_name="Projeto",
    )
    criterion = models.CharField(max_length=255, verbose_name="Criterio")
    category = models.CharField(
        max_length=120,
        blank=True,
        default="",
        verbose_name="Categoria",
    )
    required_evidence = models.TextField(
        blank=True,
        verbose_name="Evidencias obrigatorias",
    )
    approver = models.CharField(
        max_length=120,
        blank=True,
        default="",
        verbose_name="Aprovador",
    )
    result = models.CharField(
        max_length=10,
        choices=GoNoGoResult.choices,
        default=GoNoGoResult.PENDING,
        verbose_name="Resultado",
    )
    observation = models.TextField(blank=True, verbose_name="Observacao")
    visibility = models.CharField(
        max_length=20,
        choices=ProjectVisibility.choices,
        default=ProjectVisibility.ALL,
        verbose_name="Visibilidade",
    )

    class Meta:
        verbose_name = "Checklist Go/No-Go"
        verbose_name_plural = "Checklists Go/No-Go"
        ordering = ("project", "id")

    def __str__(self) -> str:
        return f"{self.project} - {self.criterion}"


class ProjectAttachmentType(models.TextChoices):
    SCOPE = "scope", "Escopo"
    OTHER = "other", "Outro"


class ProjectAttachment(TimeStampedModel):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="Projeto",
    )
    attachment_type = models.CharField(
        max_length=20,
        choices=ProjectAttachmentType.choices,
        default=ProjectAttachmentType.OTHER,
        verbose_name="Tipo",
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Descricao do arquivo",
    )
    file = models.FileField(upload_to=_project_attachment_path, verbose_name="Arquivo")

    class Meta:
        verbose_name = "Arquivo do projeto"
        verbose_name_plural = "Arquivos do projeto"

    def __str__(self) -> str:
        return self.description or os.path.basename(self.file.name)


class ProjectOccurrence(TimeStampedModel):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="occurrences",
        verbose_name="Projeto",
    )
    title = models.CharField(max_length=200, verbose_name="Ocorrencia")
    description = models.TextField(blank=True, verbose_name="Descricao")
    visibility = models.CharField(
        max_length=20,
        choices=ProjectVisibility.choices,
        default=ProjectVisibility.ALL,
        verbose_name="Visibilidade",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="project_occurrences",
        verbose_name="Registrado por",
    )

    class Meta:
        verbose_name = "Ocorrencia do projeto"
        verbose_name_plural = "Ocorrencias do projeto"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.project} - {self.title}"


class ProjectOccurrenceAttachment(TimeStampedModel):
    occurrence = models.ForeignKey(
        ProjectOccurrence,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="Ocorrencia",
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Descricao do anexo",
    )
    file = models.FileField(
        upload_to=_project_occurrence_attachment_path,
        verbose_name="Arquivo",
    )

    class Meta:
        verbose_name = "Anexo da ocorrencia"
        verbose_name_plural = "Anexos da ocorrencia"

    def __str__(self) -> str:
        return self.description or os.path.basename(self.file.name)


class CandidateApplication(TimeStampedModel):
    full_name = models.CharField(max_length=150, verbose_name="Nome completo")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=30, blank=True, verbose_name="Telefone")
    location = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Cidade/Estado",
    )
    role_interest = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Area de interesse",
    )
    linkedin_url = models.URLField(blank=True, verbose_name="Linkedin")
    availability = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Disponibilidade",
    )
    experience_summary = models.TextField(
        blank=True,
        verbose_name="Resumo profissional",
    )
    resume = models.FileField(
        upload_to=_candidate_resume_path,
        verbose_name="Curriculo",
    )

    class Meta:
        verbose_name = "Candidatura"
        verbose_name_plural = "Candidaturas"

    def __str__(self) -> str:
        return f"{self.full_name} - {self.email}"


class ProposalRequest(TimeStampedModel):
    company_name = models.CharField(max_length=200, verbose_name="Empresa")
    contact_name = models.CharField(max_length=150, verbose_name="Contato")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=30, blank=True, verbose_name="Telefone")
    project_summary = models.TextField(verbose_name="Resumo do projeto")
    estimated_start = models.DateField(
        null=True,
        blank=True,
        verbose_name="Inicio desejado",
    )
    budget_range = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Faixa de investimento",
    )
    additional_notes = models.TextField(
        blank=True,
        verbose_name="Observacoes",
    )

    class Meta:
        verbose_name = "Solicitacao de proposta"
        verbose_name_plural = "Solicitacoes de proposta"

    def __str__(self) -> str:
        return f"{self.company_name} - {self.contact_name}"


class ProjectActivity(TimeStampedModel):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="activities",
        verbose_name="Projeto",
    )
    template_item = models.ForeignKey(
        "DeploymentTemplate",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="project_activities",
        verbose_name="Item do template",
    )
    seq = models.PositiveSmallIntegerField(verbose_name="Seq")
    seq_predecessor = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Seq predecessora",
    )
    predecessors = models.ManyToManyField(
        "self",
        symmetrical=False,
        blank=True,
        related_name="successors",
        verbose_name="Predecessoras",
    )
    phase = models.ForeignKey(
        Phase,
        on_delete=models.PROTECT,
        related_name="project_activities",
        verbose_name="Fase",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="project_activities",
        verbose_name="Produto",
    )
    module = models.ForeignKey(
        Module,
        on_delete=models.PROTECT,
        related_name="project_activities",
        verbose_name="Modulo",
    )
    submodule = models.ForeignKey(
        Submodule,
        on_delete=models.PROTECT,
        related_name="project_activities",
        verbose_name="Submodulo",
    )
    activity = models.CharField(max_length=200, verbose_name="Atividade")
    subactivity = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Subatividade",
    )
    days = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Dias")
    hours = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Horas")
    criticality = models.CharField(
        max_length=20,
        choices=ActivityCriticality.choices,
        default=ActivityCriticality.MEDIUM,
        verbose_name="Criticidade",
    )
    billing_type = models.CharField(
        max_length=20,
        choices=ActivityBillingType.choices,
        default=ActivityBillingType.BILLABLE,
        verbose_name="Classificacao de horas",
    )
    assumed_reason = models.CharField(
        max_length=20,
        choices=ActivityAssumedReason.choices,
        blank=True,
        default="",
        verbose_name="Motivo",
    )
    consultant_hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Valor hora consultor (R$)",
    )
    account_plan_item = models.ForeignKey(
        "AccountPlanTemplateItem",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="project_activities",
        verbose_name="Conta do plano de contas",
    )
    planned_start = models.DateField(
        null=True,
        blank=True,
        verbose_name="Inicio previsto",
    )
    planned_end = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fim previsto",
    )
    actual_start = models.DateField(
        null=True,
        blank=True,
        verbose_name="Inicio real",
    )
    actual_end = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fim real",
    )
    status = models.CharField(
        max_length=20,
        choices=ActivityStatus.choices,
        default=ActivityStatus.PLANNED,
        verbose_name="Status",
    )
    consultants = models.ManyToManyField(
        "Consultant",
        blank=True,
        related_name="project_activities",
        verbose_name="Consultores",
    )
    client_visible = models.BooleanField(default=False, verbose_name="Visivel ao cliente")
    client_completed = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Concluida pelo cliente",
    )
    client_comment = models.TextField(blank=True, verbose_name="Comentario do cliente")
    client_feedback_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="client_activity_feedbacks",
        verbose_name="Feedback por",
    )
    client_feedback_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Feedback em",
    )

    class Meta:
        verbose_name = "Atividade do projeto"
        verbose_name_plural = "Atividades do projeto"
        ordering = ("project", "seq")
        constraints = [
            models.UniqueConstraint(
                fields=["project", "seq"],
                name="unique_project_activity_seq",
            )
        ]

    def clean(self) -> None:
        super().clean()
        errors = {}
        if self.consultant_hourly_rate is not None and self.consultant_hourly_rate < 0:
            errors["consultant_hourly_rate"] = "Valor hora consultor nao pode ser negativo."
        if self.module_id and self.product_id and self.module.product_id != self.product_id:
            errors["module"] = "Modulo nao pertence ao produto selecionado."
        if self.submodule_id and self.module_id and self.submodule.module_id != self.module_id:
            errors["submodule"] = "Submodulo nao pertence ao modulo selecionado."
        if self.submodule_id and self.product_id and self.submodule.product_id != self.product_id:
            errors["submodule"] = "Submodulo nao pertence ao produto selecionado."
        if self.planned_start and self.planned_end and self.planned_end < self.planned_start:
            errors["planned_end"] = "Fim previsto deve ser maior ou igual ao inicio previsto."
        if self.actual_start and self.actual_end and self.actual_end < self.actual_start:
            errors["actual_end"] = "Fim real deve ser maior ou igual ao inicio real."
        if self.billing_type != ActivityBillingType.ASSUMED_COMPANY and self.assumed_reason:
            self.assumed_reason = ""
        if self.billing_type == ActivityBillingType.ASSUMED_COMPANY and not self.assumed_reason:
            errors["assumed_reason"] = "Informe o motivo das horas assumidas."
        if errors:
            raise ValidationError(errors)

    def _contingency_factor(self) -> Decimal:
        percent = self.project.contingency_percent or Decimal("0.00")
        factor = Decimal("1.00") - (percent / Decimal("100.00"))
        if factor < 0:
            factor = Decimal("0.00")
        return factor

    def hours_available(self) -> Decimal:
        return (self.hours * self._contingency_factor()).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

    def hours_contingency(self) -> Decimal:
        return (self.hours - self.hours_available()).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

    def __str__(self) -> str:
        return f"{self.project} - {self.activity}"

    def billing_type_label(self) -> str:
        label = self.get_billing_type_display()
        if (
            self.billing_type == ActivityBillingType.ASSUMED_COMPANY
            and self.assumed_reason
        ):
            reason_label = self.get_assumed_reason_display()
            if reason_label:
                return f"{label} - {reason_label}"
        return label

    def schedule_state(self, today=None) -> str | None:
        target = today or timezone.localdate()
        if not self.planned_start and not self.planned_end:
            return None
        planned_start = self.planned_start
        planned_end = self.planned_end or planned_start
        if self.actual_end and planned_end:
            return "late" if self.actual_end > planned_end else "on_time"
        if self.actual_start and planned_end:
            return "late" if target > planned_end else "on_time"
        if planned_start and target < planned_start:
            return "not_started"
        if planned_end and target > planned_end:
            return "late"
        return "on_time"

    def schedule_label(self, today=None) -> str:
        mapping = {
            "late": "Atrasada",
            "on_time": "No prazo",
            "not_started": "Nao iniciada",
        }
        return mapping.get(self.schedule_state(today), "-")

    def subactivities_label(self) -> str:
        items = [
            item.description
            for item in self.subactivity_items.all()
            if item.description
        ]
        if not items and self.subactivity:
            items = [self.subactivity]
        return ", ".join(items)


class ProjectActivitySubactivity(TimeStampedModel):
    activity = models.ForeignKey(
        ProjectActivity,
        on_delete=models.CASCADE,
        related_name="subactivity_items",
        verbose_name="Atividade do projeto",
    )
    description = models.CharField(max_length=200, verbose_name="Subatividade")
    order = models.PositiveSmallIntegerField(default=1, verbose_name="Ordem")

    class Meta:
        verbose_name = "Subatividade do projeto"
        verbose_name_plural = "Subatividades do projeto"
        ordering = ("activity", "order", "id")
        constraints = [
            models.UniqueConstraint(
                fields=["activity", "order"],
                name="unique_project_activity_subactivity_order",
            )
        ]

    def __str__(self) -> str:
        return f"{self.activity} - {self.description}"


class TimeEntry(TimeStampedModel):
    activity = models.ForeignKey(
        ProjectActivity,
        on_delete=models.CASCADE,
        related_name="time_entries",
        verbose_name="Atividade",
    )
    consultant = models.ForeignKey(
        "Consultant",
        on_delete=models.PROTECT,
        related_name="time_entries",
        verbose_name="Consultor",
    )
    entry_type = models.CharField(
        max_length=10,
        choices=TimeEntryType.choices,
        default=TimeEntryType.DAILY,
        verbose_name="Tipo de apontamento",
    )
    status = models.CharField(
        max_length=10,
        choices=TimeEntryStatus.choices,
        default=TimeEntryStatus.PENDING,
        verbose_name="Status",
    )
    start_date = models.DateField(verbose_name="Data inicial")
    end_date = models.DateField(verbose_name="Data final")
    hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Horas (total)",
    )
    hours_monday = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Horas segunda",
    )
    hours_tuesday = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Horas terca",
    )
    hours_wednesday = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Horas quarta",
    )
    hours_thursday = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Horas quinta",
    )
    hours_friday = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Horas sexta",
    )
    hours_saturday = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Horas sabado",
    )
    hours_sunday = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Horas domingo",
    )
    total_hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Horas totais",
    )
    description = models.TextField(blank=True, verbose_name="Descricao do servico")
    rejection_reason = models.TextField(
        blank=True,
        verbose_name="Motivo da reprovacao",
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="time_entries_reviewed",
        verbose_name="Revisado por",
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Revisado em",
    )
    billing_invoice = models.ForeignKey(
        "BillingInvoice",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="time_entries",
        verbose_name="Fatura",
    )
    billing_invoice_number = models.CharField(
        max_length=40,
        blank=True,
        default="",
        db_index=True,
        verbose_name="Numero da fatura",
    )

    class Meta:
        verbose_name = "Apontamento"
        verbose_name_plural = "Apontamentos"
        ordering = ("-created_at",)
        constraints = [
            models.CheckConstraint(
                check=Q(end_date__gte=F("start_date")),
                name="time_entry_end_date_gte_start_date",
            )
        ]

    def _calculate_total_hours(self) -> Decimal:
        if self.entry_type == TimeEntryType.WEEKLY:
            values = [
                self.hours_monday,
                self.hours_tuesday,
                self.hours_wednesday,
                self.hours_thursday,
                self.hours_friday,
                self.hours_saturday,
                self.hours_sunday,
            ]
            total = sum((value or Decimal("0.00") for value in values), Decimal("0.00"))
        else:
            total = self.hours or Decimal("0.00")
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def clean(self) -> None:
        super().clean()
        errors = {}
        if self.activity_id and self.activity.status != ActivityStatus.RELEASED:
            errors["activity"] = "Apontamento permitido apenas para atividades liberadas."
        if self.start_date and self.end_date and self.end_date < self.start_date:
            errors["end_date"] = "Data final deve ser maior ou igual a data inicial."
        if self.entry_type == TimeEntryType.DAILY:
            if self.hours is None or self.hours <= 0:
                errors["hours"] = "Informe a quantidade de horas apontadas."
        if self.entry_type == TimeEntryType.WEEKLY:
            total = self._calculate_total_hours()
            if total <= 0:
                errors["hours_monday"] = "Informe horas em pelo menos um dia."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs) -> None:
        self.total_hours = self._calculate_total_hours()
        if self.billing_invoice and self.billing_invoice_number != self.billing_invoice.number:
            self.billing_invoice_number = self.billing_invoice.number
        should_sync_start = self.activity_id and not self.activity.actual_start
        super().save(*args, **kwargs)
        if should_sync_start:
            self._sync_activity_start()
        if self.status == TimeEntryStatus.APPROVED:
            self._sync_activity_completion()

    def _sync_activity_start(self) -> None:
        activity = self.activity
        if activity.actual_start:
            return
        first_start = (
            activity.time_entries.order_by("start_date")
            .values_list("start_date", flat=True)
            .first()
        )
        if not first_start:
            return
        ProjectActivity.objects.filter(
            pk=activity.pk,
            actual_start__isnull=True,
        ).update(actual_start=first_start)

    def _sync_activity_completion(self) -> None:
        activity = self.activity
        total_hours = activity.hours or Decimal("0.00")
        if total_hours <= 0:
            return
        approved_entries = activity.time_entries.filter(
            status=TimeEntryStatus.APPROVED
        ).only("start_date", "end_date", "total_hours")
        approved_total = sum(
            (entry.total_hours or Decimal("0.00") for entry in approved_entries),
            Decimal("0.00"),
        )
        if approved_total < total_hours:
            return
        last_end = None
        for entry in approved_entries:
            end_date = entry.end_date or entry.start_date
            if end_date and (last_end is None or end_date > last_end):
                last_end = end_date
        update_fields = []
        if activity.status != ActivityStatus.DONE:
            activity.status = ActivityStatus.DONE
            update_fields.append("status")
        if last_end and activity.actual_end != last_end:
            activity.actual_end = last_end
            update_fields.append("actual_end")
        if update_fields:
            activity.save(update_fields=update_fields)

    def __str__(self) -> str:
        return f"{self.activity} - {self.consultant}"


class TimeEntryAttachment(TimeStampedModel):
    time_entry = models.ForeignKey(
        TimeEntry,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="Apontamento",
    )
    file = models.FileField(
        upload_to=_time_entry_attachment_path,
        verbose_name="Arquivo",
    )

    class Meta:
        verbose_name = "Anexo do apontamento"
        verbose_name_plural = "Anexos do apontamento"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return os.path.basename(self.file.name) if self.file else "Anexo"


class BillingInvoice(TimeStampedModel):
    number = models.CharField(max_length=40, unique=True, verbose_name="Numero da fatura")
    billing_client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name="billing_invoices",
        verbose_name="Cliente de faturamento",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="billing_invoices",
        verbose_name="Projeto",
    )
    period_start = models.DateField(verbose_name="Periodo inicial")
    period_end = models.DateField(verbose_name="Periodo final")
    total_hours = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Horas totais",
    )
    total_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Valor total (R$)",
    )
    payment_status = models.CharField(
        max_length=10,
        choices=BillingPaymentStatus.choices,
        default=BillingPaymentStatus.UNPAID,
        verbose_name="Status de pagamento",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="billing_invoices_created",
        verbose_name="Criado por",
    )

    class Meta:
        verbose_name = "Fatura"
        verbose_name_plural = "Faturas"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.number


class BillingInvoiceItem(TimeStampedModel):
    invoice = models.ForeignKey(
        BillingInvoice,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Fatura",
    )
    consultant = models.ForeignKey(
        "Consultant",
        on_delete=models.PROTECT,
        related_name="billing_items",
        verbose_name="Consultor",
    )
    hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Horas",
    )
    rate = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Tarifa",
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Total",
    )

    class Meta:
        verbose_name = "Item de fatura"
        verbose_name_plural = "Itens de fatura"
        ordering = ("consultant", "id")

    def __str__(self) -> str:
        return f"{self.invoice} - {self.consultant}"


class Ticket(TimeStampedModel):
    title = models.CharField(max_length=200, verbose_name="Titulo")
    description = models.TextField(blank=True, verbose_name="Descricao")
    ticket_type = models.CharField(
        max_length=20,
        choices=TicketType.choices,
        default=TicketType.QUESTION,
        verbose_name="Tipo de chamado",
    )
    criticality = models.CharField(
        max_length=20,
        choices=TicketCriticality.choices,
        default=TicketCriticality.MEDIUM,
        verbose_name="Criticidade",
    )
    status = models.CharField(
        max_length=10,
        choices=TicketStatus.choices,
        default=TicketStatus.OPEN,
        verbose_name="Status",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        related_name="tickets",
        verbose_name="Projeto",
    )
    activity = models.ForeignKey(
        ProjectActivity,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets",
        verbose_name="Atividade",
    )
    project_role = models.ForeignKey(
        ProjectRole,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets",
        verbose_name="Papel",
    )
    consultant_responsible = models.ForeignKey(
        "Consultant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets_responsible",
        verbose_name="Consultor responsavel",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets_created",
        verbose_name="Criado por",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets_assigned",
        verbose_name="Direcionado para",
    )
    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Encerrado em",
    )
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets_closed",
        verbose_name="Encerrado por",
    )

    class Meta:
        verbose_name = "Chamado"
        verbose_name_plural = "Chamados"
        ordering = ("-updated_at", "-created_at")

    def clean(self) -> None:
        super().clean()
        errors = {}
        if self.activity_id and self.project_id:
            if self.activity.project_id != self.project_id:
                errors["activity"] = "Atividade nao pertence ao projeto selecionado."
        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return self.title


class TicketAttachment(TimeStampedModel):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="Chamado",
    )
    file = models.FileField(
        upload_to=_ticket_attachment_path,
        verbose_name="Arquivo",
    )

    class Meta:
        verbose_name = "Anexo do chamado"
        verbose_name_plural = "Anexos do chamado"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return os.path.basename(self.file.name) if self.file else "Anexo"


class TicketReply(TimeStampedModel):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="replies",
        verbose_name="Chamado",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ticket_replies",
        verbose_name="Autor",
    )
    message = models.TextField(verbose_name="Mensagem")

    class Meta:
        verbose_name = "Resposta do chamado"
        verbose_name_plural = "Respostas do chamado"
        ordering = ("created_at",)

    def __str__(self) -> str:
        return f"{self.ticket} - {self.author or 'Usuario'}"


class TicketReplyAttachment(TimeStampedModel):
    reply = models.ForeignKey(
        TicketReply,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="Resposta",
    )
    file = models.FileField(
        upload_to=_ticket_reply_attachment_path,
        verbose_name="Arquivo",
    )

    class Meta:
        verbose_name = "Anexo da resposta"
        verbose_name_plural = "Anexos da resposta"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return os.path.basename(self.file.name) if self.file else "Anexo"


class KnowledgeCategory(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True, verbose_name="Categoria")
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
        verbose_name="Status",
    )

    class Meta:
        verbose_name = "Categoria de conhecimento"
        verbose_name_plural = "Categorias de conhecimento"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class KnowledgePost(TimeStampedModel):
    title = models.CharField(max_length=200, verbose_name="Titulo")
    content = models.TextField(verbose_name="Conteudo")
    category = models.ForeignKey(
        KnowledgeCategory,
        on_delete=models.PROTECT,
        related_name="posts",
        verbose_name="Categoria",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="knowledge_posts",
        verbose_name="Autor",
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
        verbose_name="Status",
    )

    class Meta:
        verbose_name = "Post de conhecimento"
        verbose_name_plural = "Posts de conhecimento"
        ordering = ("-updated_at", "-created_at")

    def __str__(self) -> str:
        return self.title


def _knowledge_attachment_path(instance: "KnowledgeAttachment", filename: str) -> str:
    safe_name = os.path.basename(filename)
    post_id = instance.post_id or "temp"
    return f"knowledge/{post_id}/attachments/{safe_name}"


class KnowledgeAttachment(TimeStampedModel):
    post = models.ForeignKey(
        KnowledgePost,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="Post",
    )
    file = models.FileField(
        upload_to=_knowledge_attachment_path,
        verbose_name="Arquivo",
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="knowledge_attachments",
        verbose_name="Enviado por",
    )

    class Meta:
        verbose_name = "Anexo de conhecimento"
        verbose_name_plural = "Anexos de conhecimento"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return os.path.basename(self.file.name) if self.file else "Anexo"


class DeploymentTemplateHeader(TimeStampedModel):
    name = models.CharField(max_length=200, unique=True, verbose_name="Nome do template")

    class Meta:
        verbose_name = "Template de implantacao"
        verbose_name_plural = "Templates de implantacao"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class DeploymentTemplate(TimeStampedModel):
    template = models.ForeignKey(
        DeploymentTemplateHeader,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Template",
    )
    seq = models.PositiveSmallIntegerField(verbose_name="Seq")
    seq_predecessor = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Seq predecessora",
    )
    phase = models.ForeignKey(
        Phase,
        on_delete=models.PROTECT,
        related_name="deployment_templates",
        verbose_name="Fase",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="deployment_templates",
        verbose_name="Produto",
    )
    module = models.ForeignKey(
        Module,
        on_delete=models.PROTECT,
        related_name="deployment_templates",
        verbose_name="Modulo",
    )
    submodule = models.ForeignKey(
        Submodule,
        on_delete=models.PROTECT,
        related_name="deployment_templates",
        verbose_name="Submodulo",
    )
    activity = models.CharField(max_length=200, verbose_name="Atividade")
    subactivity = models.CharField(max_length=200, verbose_name="Subatividade")
    days = models.PositiveSmallIntegerField(verbose_name="Dias")
    hours = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Horas")

    class Meta:
        verbose_name = "Item do template"
        verbose_name_plural = "Itens do template"
        ordering = ("template", "seq")

    def clean(self) -> None:
        super().clean()
        errors = {}
        if self.module_id and self.product_id and self.module.product_id != self.product_id:
            errors["module"] = "Modulo nao pertence ao produto selecionado."
        if self.submodule_id and self.module_id and self.submodule.module_id != self.module_id:
            errors["submodule"] = "Submodulo nao pertence ao modulo selecionado."
        if self.submodule_id and self.product_id and self.submodule.product_id != self.product_id:
            errors["submodule"] = "Submodulo nao pertence ao produto selecionado."
        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return f"{self.template} - {self.activity}"


class AccountPlanTemplateHeader(TimeStampedModel):
    name = models.CharField(max_length=200, unique=True, verbose_name="Nome do modelo")
    description = models.TextField(blank=True, verbose_name="Descricao")

    class Meta:
        verbose_name = "Modelo de plano de contas"
        verbose_name_plural = "Modelos de plano de contas"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class AccountPlanTemplateItem(TimeStampedModel):
    template = models.ForeignKey(
        AccountPlanTemplateHeader,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Modelo",
    )
    code = models.CharField(max_length=40, verbose_name="Codigo")
    description = models.CharField(max_length=200, verbose_name="Descricao")
    level = models.PositiveSmallIntegerField(verbose_name="Nivel")
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Conta pai",
    )
    account_type = models.CharField(
        max_length=20,
        choices=AccountType.choices,
        verbose_name="Tipo de conta",
    )
    nature = models.CharField(
        max_length=10,
        choices=AccountNature.choices,
        verbose_name="Natureza",
    )
    is_analytic = models.BooleanField(default=True, verbose_name="Analitica")
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
        verbose_name="Status",
    )
    dre_group = models.CharField(max_length=120, verbose_name="Grupo DRE")
    dre_subgroup = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Linha DRE",
    )
    dre_order = models.PositiveSmallIntegerField(verbose_name="Ordem DRE")
    dre_sign = models.CharField(
        max_length=10,
        choices=DreSign.choices,
        default=DreSign.ADD,
        verbose_name="Sinal DRE",
    )

    class Meta:
        verbose_name = "Conta do modelo"
        verbose_name_plural = "Contas do modelo"
        ordering = ("template", "code")
        constraints = [
            models.UniqueConstraint(
                fields=["template", "code"],
                name="unique_account_code_per_template",
            )
        ]

    def clean(self) -> None:
        super().clean()
        errors = {}
        if self.level is not None and self.level < 1:
            errors["level"] = "Nivel deve ser maior ou igual a 1."
        if self.parent_id:
            if self.template_id and self.parent.template_id != self.template_id:
                errors["parent"] = "Conta pai deve pertencer ao mesmo modelo."
            if self.level and self.parent.level and self.level <= self.parent.level:
                errors["level"] = "Nivel deve ser maior que o nivel da conta pai."
        else:
            if self.level and self.level != 1:
                errors["level"] = "Nivel deve ser 1 para contas sem conta pai."
        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return f"{self.code} - {self.description}"


class WhatsappSettings(TimeStampedModel):
    opportunities_numbers = models.TextField(
        blank=True,
        verbose_name="Numeros WhatsApp - oportunidades",
        help_text="Informe um numero por linha.",
    )
    financial_numbers = models.TextField(
        blank=True,
        verbose_name="Numeros WhatsApp - financeiro",
        help_text="Informe um numero por linha.",
    )
    zapi_base_url = models.CharField(
        max_length=200,
        blank=True,
        default="https://api.z-api.io",
        verbose_name="API base Z-API",
        help_text="Ex.: https://api.z-api.io",
    )
    zapi_instance_id = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Z-API Instance ID",
    )
    zapi_token = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Z-API Token",
    )
    zapi_client_token = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Z-API Client Token",
        help_text="Header exigido pela Z-API (client-token).",
    )
    daily_activities_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Horario atividades de hoje (consultor)",
        help_text="Formato HH:MM.",
    )
    daily_overdue_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Horario atividades em atraso (consultor)",
        help_text="Formato HH:MM.",
    )
    daily_admin_due_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Horario titulos vencendo hoje (admin)",
        help_text="Formato HH:MM.",
    )
    last_daily_activities_sent = models.DateField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="Ultimo envio atividades de hoje",
    )
    last_daily_overdue_sent = models.DateField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="Ultimo envio atividades em atraso",
    )
    last_daily_admin_due_sent = models.DateField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="Ultimo envio titulos vencendo hoje",
    )

    class Meta:
        verbose_name = "Parametrizacao WhatsApp"
        verbose_name_plural = "Parametrizacao WhatsApp"

    def __str__(self) -> str:
        return "Parametrizacao WhatsApp"


class ChatGPTSettings(TimeStampedModel):
    api_url = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="API URL",
        help_text="Ex.: https://api.openai.com/v1/chat/completions",
    )
    api_key = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="API Key",
        help_text="Chave de acesso da API.",
    )
    api_model = models.CharField(
        max_length=120,
        blank=True,
        default="",
        verbose_name="Modelo",
        help_text="Ex.: gpt-4o-mini",
    )
    request_timeout = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Timeout (segundos)",
        help_text="Tempo maximo de espera da requisicao.",
    )
    org_id = models.CharField(
        max_length=120,
        blank=True,
        default="",
        verbose_name="Organization ID",
        help_text="Header OpenAI-Organization (opcional).",
    )
    project_id = models.CharField(
        max_length=120,
        blank=True,
        default="",
        verbose_name="Project ID",
        help_text="Header OpenAI-Project (opcional).",
    )
    system_prompt = models.TextField(
        blank=True,
        verbose_name="Prompt do sistema",
        help_text="Mensagem base enviada como role system.",
    )
    analysis_prompt = models.TextField(
        blank=True,
        verbose_name="Prompt da analise",
        help_text=(
            "Use {{PROJECT_CONTEXT}} e {{DETAILS_JSON}} para inserir os dados do projeto."
        ),
    )

    class Meta:
        verbose_name = "Parametros ChatGPT"
        verbose_name_plural = "Parametros ChatGPT"

    def __str__(self) -> str:
        return "Parametros ChatGPT"


class Consultant(TimeStampedModel):
    full_name = models.CharField(max_length=200, verbose_name="Nome completo")
    email = models.EmailField(blank=True, verbose_name="Email")
    phone = models.CharField(max_length=30, blank=True, verbose_name="Telefone")
    whatsapp_phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Telefone WhatsApp financeiro",
        help_text=(
            "Recebe mensagens de WhatsApp sobre titulos criados, pagos, "
            "vencendo no dia e fechamentos."
        ),
    )
    contract_type = models.CharField(
        max_length=10,
        choices=ConsultantType.choices,
        default=ConsultantType.PJ,
        verbose_name="Tipo de contrato",
    )
    document = models.CharField(max_length=32, blank=True, verbose_name="Documento")
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de nascimento",
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        related_name="consultants",
        null=True,
        blank=True,
        verbose_name="Empresa",
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        related_name="consultants",
        null=True,
        blank=True,
        verbose_name="Fornecedor",
    )
    is_senior_accredited = models.BooleanField(
        default=False,
        verbose_name="Credenciado senior",
    )
    is_partner = models.BooleanField(default=False, verbose_name="Socio")
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="consultant_profile",
        null=True,
        blank=True,
        verbose_name="Usuario vinculado",
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
        verbose_name="Status",
    )
    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Inicio do contrato",
    )
    end_date = models.DateField(null=True, blank=True, verbose_name="Fim do contrato")
    notes = models.TextField(blank=True, verbose_name="Observacoes")
    competencies = models.ManyToManyField(
        Competency,
        blank=True,
        related_name="consultants",
        verbose_name="Competencias",
    )
    certifications = models.ManyToManyField(
        Certification,
        blank=True,
        related_name="consultants",
        verbose_name="Certificacoes",
    )

    class Meta:
        verbose_name = "Consultor"
        verbose_name_plural = "Consultores"

    def get_rate_for_date(self, date=None):
        if date is None:
            date = timezone.localdate()
        return (
            self.rates.filter(start_date__lte=date)
            .filter(Q(end_date__isnull=True) | Q(end_date__gte=date))
            .order_by("-start_date")
            .first()
        )

    def __str__(self) -> str:
        return self.full_name


def _consultant_attachment_path(instance: "ConsultantAttachment", filename: str) -> str:
    safe_name = os.path.basename(filename)
    consultant_id = instance.consultant_id or "temp"
    return f"consultants/{consultant_id}/attachments/{safe_name}"


class ConsultantAttachment(TimeStampedModel):
    consultant = models.ForeignKey(
        Consultant,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="Consultor",
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Descricao do arquivo",
    )
    file = models.FileField(upload_to=_consultant_attachment_path, verbose_name="Arquivo")

    class Meta:
        verbose_name = "Arquivo do consultor"
        verbose_name_plural = "Arquivos do consultor"

    def __str__(self) -> str:
        return self.description or os.path.basename(self.file.name)


class ConsultantRate(TimeStampedModel):
    consultant = models.ForeignKey(
        Consultant,
        on_delete=models.CASCADE,
        related_name="rates",
        verbose_name="Consultor",
    )
    rate = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Tarifa",
    )
    currency = models.CharField(max_length=3, default="BRL", verbose_name="Moeda")
    start_date = models.DateField(verbose_name="Inicio da vigencia")
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fim da vigencia",
    )
    notes = models.TextField(blank=True, verbose_name="Observacoes")

    class Meta:
        verbose_name = "Tarifa do consultor"
        verbose_name_plural = "Tarifas do consultor"
        constraints = [
            models.UniqueConstraint(
                fields=["consultant", "start_date"],
                name="unique_consultant_rate_start",
            ),
            models.CheckConstraint(
                check=Q(end_date__isnull=True) | Q(end_date__gte=F("start_date")),
                name="rate_end_date_gte_start_date",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.consultant} - {self.rate} {self.currency}"


class ConsultantBankAccount(TimeStampedModel):
    consultant = models.ForeignKey(
        Consultant,
        on_delete=models.CASCADE,
        related_name="bank_accounts",
        verbose_name="Consultor",
    )
    account_type = models.CharField(
        max_length=2,
        choices=BankAccountType.choices,
        default=BankAccountType.PF,
        verbose_name="Tipo de conta",
    )
    bank_name = models.CharField(max_length=120, verbose_name="Banco")
    agency = models.CharField(max_length=20, verbose_name="Agencia")
    account_number = models.CharField(max_length=30, verbose_name="Conta")
    account_digit = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Digito",
    )
    pix_keys = models.TextField(blank=True, verbose_name="Chaves Pix")

    class Meta:
        verbose_name = "Conta bancaria do consultor"
        verbose_name_plural = "Contas bancarias do consultor"

    def __str__(self) -> str:
        return f"{self.consultant} - {self.bank_name}"


class CompanyBankAccount(TimeStampedModel):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="bank_accounts",
        limit_choices_to={"company_type__in": [CompanyType.PRIMARY, CompanyType.BRANCH]},
        verbose_name="Empresa",
    )
    account_type = models.CharField(
        max_length=2,
        choices=BankAccountType.choices,
        default=BankAccountType.PJ,
        verbose_name="Tipo de conta",
    )
    bank_name = models.CharField(max_length=120, verbose_name="Banco")
    agency = models.CharField(max_length=20, verbose_name="Agencia")
    account_number = models.CharField(max_length=30, verbose_name="Conta")
    account_digit = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Digito",
    )
    initial_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Saldo inicial",
    )
    pix_keys = models.TextField(blank=True, verbose_name="Chaves Pix")

    class Meta:
        verbose_name = "Conta bancaria da consultoria"
        verbose_name_plural = "Contas bancarias da consultoria"

    def __str__(self) -> str:
        return f"{self.company} - {self.bank_name}"


def _bank_statement_import_path(instance: "BankStatementImport", filename: str) -> str:
    safe_name = os.path.basename(filename)
    account_id = instance.bank_account_id or "temp"
    return f"bank-statements/{account_id}/{safe_name}"


class BankStatementImport(TimeStampedModel):
    bank_account = models.ForeignKey(
        CompanyBankAccount,
        on_delete=models.CASCADE,
        related_name="statement_imports",
        verbose_name="Conta bancaria",
    )
    imported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bank_statement_imports",
        verbose_name="Importado por",
    )
    file = models.FileField(
        upload_to=_bank_statement_import_path,
        verbose_name="Arquivo OFX",
        blank=True,
        null=True,
    )
    original_filename = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Nome do arquivo",
    )
    statement_start = models.DateField(null=True, blank=True, verbose_name="Inicio do extrato")
    statement_end = models.DateField(null=True, blank=True, verbose_name="Fim do extrato")
    bank_id = models.CharField(max_length=60, blank=True, verbose_name="Banco OFX")
    account_number = models.CharField(max_length=60, blank=True, verbose_name="Conta OFX")

    class Meta:
        verbose_name = "Importacao OFX"
        verbose_name_plural = "Importacoes OFX"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.bank_account} - {self.original_filename or 'OFX'}"


class BankStatementEntry(TimeStampedModel):
    statement_import = models.ForeignKey(
        BankStatementImport,
        on_delete=models.CASCADE,
        related_name="entries",
        verbose_name="Importacao OFX",
    )
    bank_account = models.ForeignKey(
        CompanyBankAccount,
        on_delete=models.CASCADE,
        related_name="statement_entries",
        verbose_name="Conta bancaria",
    )
    posted_at = models.DateField(verbose_name="Data do movimento")
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Valor",
    )
    direction = models.CharField(
        max_length=10,
        choices=BankMovementDirection.choices,
        verbose_name="Direcao",
    )
    fit_id = models.CharField(max_length=120, blank=True, verbose_name="FITID")
    transaction_type = models.CharField(max_length=40, blank=True, verbose_name="Tipo OFX")
    name = models.CharField(max_length=120, blank=True, verbose_name="Nome")
    memo = models.CharField(max_length=200, blank=True, verbose_name="Historico")
    check_number = models.CharField(max_length=60, blank=True, verbose_name="Cheque")

    class Meta:
        verbose_name = "Movimento OFX"
        verbose_name_plural = "Movimentos OFX"
        ordering = ("-posted_at", "-created_at")
        indexes = [
            models.Index(fields=["bank_account", "posted_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.posted_at} - {self.memo or self.name or self.fit_id}"


class BankSystemMovement(TimeStampedModel):
    bank_account = models.ForeignKey(
        CompanyBankAccount,
        on_delete=models.CASCADE,
        related_name="system_movements",
        verbose_name="Conta bancaria",
    )
    account_plan_item = models.ForeignKey(
        "AccountPlanTemplateItem",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="bank_system_movements",
        verbose_name="Conta do plano de contas",
    )
    movement_date = models.DateField(verbose_name="Data do movimento")
    description = models.CharField(max_length=200, verbose_name="Descricao")
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Valor",
    )
    direction = models.CharField(
        max_length=10,
        choices=BankMovementDirection.choices,
        verbose_name="Direcao",
    )
    source = models.CharField(
        max_length=20,
        choices=BankMovementSource.choices,
        default=BankMovementSource.MANUAL,
        verbose_name="Origem",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bank_system_movements",
        verbose_name="Criado por",
    )
    notes = models.TextField(blank=True, verbose_name="Observacoes")

    class Meta:
        verbose_name = "Movimento bancario"
        verbose_name_plural = "Movimentos bancarios"
        ordering = ("-movement_date", "-created_at")
        indexes = [
            models.Index(fields=["bank_account", "movement_date"]),
        ]

    def __str__(self) -> str:
        return f"{self.bank_account} - {self.description}"


class BankReconciliation(TimeStampedModel):
    bank_account = models.ForeignKey(
        CompanyBankAccount,
        on_delete=models.CASCADE,
        related_name="reconciliations",
        verbose_name="Conta bancaria",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bank_reconciliations",
        verbose_name="Conciliado por",
    )
    total_system = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Total sistema",
    )
    total_ofx = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Total OFX",
    )
    difference = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Diferenca",
    )

    class Meta:
        verbose_name = "Conciliacao bancaria"
        verbose_name_plural = "Conciliacoes bancarias"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.bank_account} - {self.created_at:%d/%m/%Y}"


class BankReconciliationSystemItem(TimeStampedModel):
    reconciliation = models.ForeignKey(
        BankReconciliation,
        on_delete=models.CASCADE,
        related_name="system_items",
        verbose_name="Conciliacao",
    )
    receivable_payment = models.ForeignKey(
        "AccountsReceivablePayment",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reconciliation_items",
        verbose_name="Recebimento",
    )
    payable_payment = models.ForeignKey(
        "AccountsPayablePayment",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reconciliation_items",
        verbose_name="Pagamento",
    )
    system_movement = models.ForeignKey(
        BankSystemMovement,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reconciliation_items",
        verbose_name="Movimento",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Valor",
    )
    direction = models.CharField(
        max_length=10,
        choices=BankMovementDirection.choices,
        verbose_name="Direcao",
    )

    class Meta:
        verbose_name = "Conciliacao (sistema)"
        verbose_name_plural = "Conciliacoes (sistema)"
        constraints = [
            models.CheckConstraint(
                check=(
                    Q(receivable_payment__isnull=False)
                    | Q(payable_payment__isnull=False)
                    | Q(system_movement__isnull=False)
                ),
                name="bank_reconciliation_system_item_has_reference",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.reconciliation}"


class BankReconciliationOfxItem(TimeStampedModel):
    reconciliation = models.ForeignKey(
        BankReconciliation,
        on_delete=models.CASCADE,
        related_name="ofx_items",
        verbose_name="Conciliacao",
    )
    ofx_entry = models.ForeignKey(
        BankStatementEntry,
        on_delete=models.CASCADE,
        related_name="reconciliation_items",
        verbose_name="Movimento OFX",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Valor",
    )
    direction = models.CharField(
        max_length=10,
        choices=BankMovementDirection.choices,
        verbose_name="Direcao",
    )

    class Meta:
        verbose_name = "Conciliacao (OFX)"
        verbose_name_plural = "Conciliacoes (OFX)"
        constraints = [
            models.UniqueConstraint(
                fields=["reconciliation", "ofx_entry"],
                name="unique_reconciliation_ofx_entry",
            )
        ]

    def __str__(self) -> str:
        return f"{self.reconciliation}"


class AccountsPayablePayment(TimeStampedModel):
    payable = models.ForeignKey(
        AccountsPayable,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Conta a pagar",
    )
    bank_account = models.ForeignKey(
        CompanyBankAccount,
        on_delete=models.PROTECT,
        related_name="payable_payments",
        verbose_name="Conta bancaria",
    )
    payment_date = models.DateField(
        default=timezone.localdate,
        verbose_name="Data de pagamento",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Valor pago",
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        blank=True,
        verbose_name="Forma de pagamento",
    )
    notes = models.TextField(blank=True, verbose_name="Observacoes")

    class Meta:
        verbose_name = "Baixa conta a pagar"
        verbose_name_plural = "Baixas contas a pagar"
        ordering = ("-payment_date", "-created_at")
        indexes = [
            models.Index(fields=["bank_account", "payment_date"]),
        ]

    def __str__(self) -> str:
        return f"{self.payable} - {self.amount}"

    def clean(self) -> None:
        super().clean()
        if self.amount is not None and self.amount <= 0:
            raise ValidationError({"amount": "Valor pago deve ser maior que zero."})


class AccountsReceivablePayment(TimeStampedModel):
    receivable = models.ForeignKey(
        AccountsReceivable,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Conta a receber",
    )
    bank_account = models.ForeignKey(
        CompanyBankAccount,
        on_delete=models.PROTECT,
        related_name="receivable_payments",
        verbose_name="Conta bancaria",
    )
    payment_date = models.DateField(
        default=timezone.localdate,
        verbose_name="Data de recebimento",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Valor recebido",
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        blank=True,
        verbose_name="Forma de recebimento",
    )
    notes = models.TextField(blank=True, verbose_name="Observacoes")

    class Meta:
        verbose_name = "Baixa conta a receber"
        verbose_name_plural = "Baixas contas a receber"
        ordering = ("-payment_date", "-created_at")
        indexes = [
            models.Index(fields=["bank_account", "payment_date"]),
        ]

    def __str__(self) -> str:
        return f"{self.receivable} - {self.amount}"

    def clean(self) -> None:
        super().clean()
        if self.amount is not None and self.amount <= 0:
            raise ValidationError({"amount": "Valor recebido deve ser maior que zero."})
