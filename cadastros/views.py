from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from .models import (
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
    UserRole,
)
from .serializers import (
    AccountPlanTemplateHeaderSerializer,
    AccountPlanTemplateItemSerializer,
    CertificationSerializer,
    ClientContactSerializer,
    ClientSerializer,
    CompanySerializer,
    SupplierSerializer,
    AccountsPayableSerializer,
    AccountsReceivableSerializer,
    CompetencySerializer,
    ConsultantSerializer,
    DeploymentTemplateHeaderSerializer,
    DeploymentTemplateItemSerializer,
    ModuleSerializer,
    PhaseSerializer,
    ProjectActivitySerializer,
    ProjectAttachmentSerializer,
    ProjectSerializer,
    ProductSerializer,
    SubmoduleSerializer,
)
from .observations import (
    create_project_change_observation,
    create_project_receipt_observation,
)
from .roles import (
    filter_activities_for_user,
    filter_projects_for_user,
    resolve_user_role,
)


def _parse_bool(value):
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes", "y", "sim"}:
        return True
    if normalized in {"false", "0", "no", "n", "nao"}:
        return False
    return None


class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    search_fields = ("legal_name", "trade_name", "tax_id", "billing_email", "city", "state")
    ordering_fields = ("legal_name", "trade_name", "tax_id", "status", "company_type", "created_at")
    ordering = ("legal_name",)

    def get_queryset(self):
        queryset = Company.objects.all()
        params = self.request.query_params
        status = params.get("status")
        company_type = params.get("company_type")
        tax_id = params.get("tax_id")
        city = params.get("city")
        state = params.get("state")
        if status:
            queryset = queryset.filter(status=status)
        if company_type:
            queryset = queryset.filter(company_type=company_type)
        if tax_id:
            queryset = queryset.filter(tax_id__icontains=tax_id)
        if city:
            queryset = queryset.filter(city__icontains=city)
        if state:
            queryset = queryset.filter(state__icontains=state)
        return queryset.order_by("legal_name")


class SupplierViewSet(viewsets.ModelViewSet):
    serializer_class = SupplierSerializer
    search_fields = ("name", "trade_name", "document", "email", "city", "state")
    ordering_fields = ("name", "trade_name", "document", "status", "person_type", "created_at")
    ordering = ("name",)

    def get_queryset(self):
        queryset = Supplier.objects.all()
        params = self.request.query_params
        status = params.get("status")
        person_type = params.get("person_type")
        document = params.get("document")
        city = params.get("city")
        state = params.get("state")
        if status:
            queryset = queryset.filter(status=status)
        if person_type:
            queryset = queryset.filter(person_type=person_type)
        if document:
            queryset = queryset.filter(document__icontains=document)
        if city:
            queryset = queryset.filter(city__icontains=city)
        if state:
            queryset = queryset.filter(state__icontains=state)
        return queryset.order_by("name")


class AccountsPayableViewSet(viewsets.ModelViewSet):
    serializer_class = AccountsPayableSerializer
    search_fields = (
        "document_number",
        "description",
        "supplier__name",
        "supplier__trade_name",
        "supplier__document",
        "consultant__full_name",
        "billing_invoice__number",
    )
    ordering_fields = ("due_date", "issue_date", "amount", "status", "created_at")
    ordering = ("due_date",)

    def _require_financial(self):
        role = resolve_user_role(self.request.user)
        if role != UserRole.ADMIN:
            raise PermissionDenied("Perfil sem permissao para contas a pagar.")

    def get_queryset(self):
        self._require_financial()
        queryset = AccountsPayable.objects.select_related(
            "supplier",
            "consultant",
            "billing_invoice",
        )
        params = self.request.query_params
        status = params.get("status")
        supplier_id = params.get("supplier_id")
        document_number = params.get("document_number")
        due_date = params.get("due_date")
        if status:
            queryset = queryset.filter(status=status)
        if supplier_id:
            queryset = queryset.filter(supplier_id=supplier_id)
        if document_number:
            queryset = queryset.filter(document_number__icontains=document_number)
        if due_date:
            queryset = queryset.filter(due_date=due_date)
        return queryset.order_by("due_date")

    def perform_create(self, serializer):
        self._require_financial()
        serializer.save()

    def perform_update(self, serializer):
        self._require_financial()
        serializer.save()

    def perform_destroy(self, instance):
        self._require_financial()
        instance.delete()


class AccountsReceivableViewSet(viewsets.ModelViewSet):
    serializer_class = AccountsReceivableSerializer
    search_fields = (
        "document_number",
        "description",
        "client__name",
        "client__company__legal_name",
        "client__company__trade_name",
        "billing_invoice__number",
    )
    ordering_fields = ("due_date", "issue_date", "amount", "status", "created_at")
    ordering = ("due_date",)

    def _require_financial(self):
        role = resolve_user_role(self.request.user)
        if role != UserRole.ADMIN:
            raise PermissionDenied("Perfil sem permissao para contas a receber.")

    def get_queryset(self):
        self._require_financial()
        queryset = AccountsReceivable.objects.select_related(
            "client",
            "client__company",
            "billing_invoice",
        )
        params = self.request.query_params
        status = params.get("status")
        client_id = params.get("client_id")
        document_number = params.get("document_number")
        due_date = params.get("due_date")
        if status:
            queryset = queryset.filter(status=status)
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        if document_number:
            queryset = queryset.filter(document_number__icontains=document_number)
        if due_date:
            queryset = queryset.filter(due_date=due_date)
        return queryset.order_by("due_date")

    def perform_create(self, serializer):
        self._require_financial()
        serializer.save()

    def perform_update(self, serializer):
        self._require_financial()
        serializer.save()

    def perform_destroy(self, instance):
        self._require_financial()
        instance.delete()


class ClientViewSet(viewsets.ModelViewSet):
    serializer_class = ClientSerializer
    search_fields = ("name", "company__legal_name", "company__trade_name")
    ordering_fields = ("name", "status", "billing_cycle", "payment_terms_days", "created_at")
    ordering = ("name",)

    def get_queryset(self):
        queryset = Client.objects.select_related("company")
        params = self.request.query_params
        status = params.get("status")
        company_id = params.get("company_id")
        billing_cycle = params.get("billing_cycle")
        payment_terms_days = params.get("payment_terms_days")
        if status:
            queryset = queryset.filter(status=status)
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        if billing_cycle:
            queryset = queryset.filter(billing_cycle=billing_cycle)
        if payment_terms_days:
            queryset = queryset.filter(payment_terms_days=payment_terms_days)
        return queryset.order_by("name")


class ClientContactViewSet(viewsets.ModelViewSet):
    serializer_class = ClientContactSerializer
    search_fields = ("name", "email", "role", "client__name")
    ordering_fields = ("name", "is_primary", "status", "created_at")
    ordering = ("client_id", "name")

    def get_queryset(self):
        queryset = ClientContact.objects.select_related("client")
        params = self.request.query_params
        status = params.get("status")
        client_id = params.get("client_id")
        is_primary = _parse_bool(params.get("is_primary"))
        if status:
            queryset = queryset.filter(status=status)
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        if is_primary is not None:
            queryset = queryset.filter(is_primary=is_primary)
        return queryset.order_by("client_id", "name")


class ConsultantViewSet(viewsets.ModelViewSet):
    serializer_class = ConsultantSerializer
    search_fields = (
        "full_name",
        "email",
        "document",
        "company__legal_name",
        "company__trade_name",
        "supplier__name",
        "supplier__trade_name",
        "supplier__document",
    )
    ordering_fields = ("full_name", "status", "contract_type", "created_at")
    ordering = ("full_name",)

    def get_queryset(self):
        queryset = Consultant.objects.select_related("company", "supplier").prefetch_related(
            "competencies",
            "certifications",
        )
        params = self.request.query_params
        status = params.get("status")
        contract_type = params.get("contract_type")
        company_id = params.get("company_id")
        competency_id = params.get("competency_id")
        certification_id = params.get("certification_id")
        requires_distinct = False
        if status:
            queryset = queryset.filter(status=status)
        if contract_type:
            queryset = queryset.filter(contract_type=contract_type)
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        if competency_id:
            queryset = queryset.filter(competencies__id=competency_id)
            requires_distinct = True
        if certification_id:
            queryset = queryset.filter(certifications__id=certification_id)
            requires_distinct = True
        if requires_distinct:
            queryset = queryset.distinct()
        return queryset.order_by("full_name")


class CompetencyViewSet(viewsets.ModelViewSet):
    serializer_class = CompetencySerializer
    search_fields = ("name", "description")
    ordering_fields = ("name", "status", "created_at")
    ordering = ("name",)

    def get_queryset(self):
        queryset = Competency.objects.all()
        status = self.request.query_params.get("status")
        if status:
            queryset = queryset.filter(status=status)
        return queryset.order_by("name")


class CertificationViewSet(viewsets.ModelViewSet):
    serializer_class = CertificationSerializer
    search_fields = ("name", "issuer", "description")
    ordering_fields = ("name", "issuer", "status", "created_at")
    ordering = ("name",)

    def get_queryset(self):
        queryset = Certification.objects.all()
        params = self.request.query_params
        status = params.get("status")
        issuer = params.get("issuer")
        if status:
            queryset = queryset.filter(status=status)
        if issuer:
            queryset = queryset.filter(issuer__icontains=issuer)
        return queryset.order_by("name")


class PhaseViewSet(viewsets.ModelViewSet):
    serializer_class = PhaseSerializer
    search_fields = ("description",)
    ordering_fields = ("description", "status", "created_at")
    ordering = ("description",)

    def get_queryset(self):
        queryset = Phase.objects.all()
        status = self.request.query_params.get("status")
        if status:
            queryset = queryset.filter(status=status)
        return queryset.order_by("description")


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    search_fields = ("description",)
    ordering_fields = ("description", "status", "created_at")
    ordering = ("description",)

    def get_queryset(self):
        queryset = Product.objects.all()
        status = self.request.query_params.get("status")
        if status:
            queryset = queryset.filter(status=status)
        return queryset.order_by("description")


class ModuleViewSet(viewsets.ModelViewSet):
    serializer_class = ModuleSerializer
    search_fields = ("description", "product__description")
    ordering_fields = ("description", "status", "created_at")
    ordering = ("description",)

    def get_queryset(self):
        queryset = Module.objects.select_related("product")
        params = self.request.query_params
        status = params.get("status")
        product_id = params.get("product_id")
        if status:
            queryset = queryset.filter(status=status)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset.order_by("description")


class SubmoduleViewSet(viewsets.ModelViewSet):
    serializer_class = SubmoduleSerializer
    search_fields = ("description", "product__description", "module__description")
    ordering_fields = ("description", "status", "created_at")
    ordering = ("description",)

    def get_queryset(self):
        queryset = Submodule.objects.select_related("product", "module")
        params = self.request.query_params
        status = params.get("status")
        product_id = params.get("product_id")
        module_id = params.get("module_id")
        if status:
            queryset = queryset.filter(status=status)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        if module_id:
            queryset = queryset.filter(module_id=module_id)
        return queryset.order_by("description")


class DeploymentTemplateHeaderViewSet(viewsets.ModelViewSet):
    serializer_class = DeploymentTemplateHeaderSerializer
    search_fields = ("name",)
    ordering_fields = ("name", "created_at")
    ordering = ("name",)

    def get_queryset(self):
        queryset = DeploymentTemplateHeader.objects.all()
        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset.order_by("name")


class DeploymentTemplateItemViewSet(viewsets.ModelViewSet):
    serializer_class = DeploymentTemplateItemSerializer
    search_fields = ("template__name", "activity", "subactivity")
    ordering_fields = ("template", "seq", "days", "hours")
    ordering = ("template", "seq")

    def get_queryset(self):
        queryset = DeploymentTemplate.objects.select_related(
            "template",
            "phase",
            "product",
            "module",
            "submodule",
        )
        params = self.request.query_params
        template_id = params.get("template_id")
        phase_id = params.get("phase_id")
        product_id = params.get("product_id")
        module_id = params.get("module_id")
        submodule_id = params.get("submodule_id")
        if template_id:
            queryset = queryset.filter(template_id=template_id)
        if phase_id:
            queryset = queryset.filter(phase_id=phase_id)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        if module_id:
            queryset = queryset.filter(module_id=module_id)
        if submodule_id:
            queryset = queryset.filter(submodule_id=submodule_id)
        return queryset.order_by("template_id", "seq")


class AccountPlanTemplateHeaderViewSet(viewsets.ModelViewSet):
    serializer_class = AccountPlanTemplateHeaderSerializer
    search_fields = ("name",)
    ordering_fields = ("name", "created_at")
    ordering = ("name",)

    def get_queryset(self):
        queryset = AccountPlanTemplateHeader.objects.all()
        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset.order_by("name")


class AccountPlanTemplateItemViewSet(viewsets.ModelViewSet):
    serializer_class = AccountPlanTemplateItemSerializer
    search_fields = ("template__name", "code", "description", "dre_group")
    ordering_fields = ("template", "code", "level", "dre_order")
    ordering = ("template", "code")

    def get_queryset(self):
        queryset = AccountPlanTemplateItem.objects.select_related("template", "parent")
        params = self.request.query_params
        template_id = params.get("template_id")
        parent_id = params.get("parent_id")
        account_type = params.get("account_type")
        nature = params.get("nature")
        status = params.get("status")
        dre_group = params.get("dre_group")
        if template_id:
            queryset = queryset.filter(template_id=template_id)
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        if account_type:
            queryset = queryset.filter(account_type=account_type)
        if nature:
            queryset = queryset.filter(nature=nature)
        if status:
            queryset = queryset.filter(status=status)
        if dre_group:
            queryset = queryset.filter(dre_group__icontains=dre_group)
        return queryset.order_by("template_id", "code")


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    search_fields = ("description",)
    ordering_fields = ("description", "status", "total_value", "hourly_rate", "created_at")
    ordering = ("description",)

    def _require_management_create(self):
        role = resolve_user_role(self.request.user)
        if role not in {
            UserRole.ADMIN,
            UserRole.GP_INTERNAL,
            UserRole.GP_EXTERNAL,
        }:
            raise PermissionDenied("Perfil sem permissao para alterar projetos.")

    def _require_management_edit(self):
        role = resolve_user_role(self.request.user)
        if role not in {UserRole.ADMIN, UserRole.GP_INTERNAL}:
            raise PermissionDenied("Perfil sem permissao para alterar projetos.")

    def get_queryset(self):
        queryset = Project.objects.select_related(
            "billing_client",
            "project_client",
            "internal_manager",
            "external_manager",
            "client_user",
        )
        queryset = filter_projects_for_user(queryset, self.request.user)
        params = self.request.query_params
        status = params.get("status")
        billing_client_id = params.get("billing_client_id")
        project_client_id = params.get("project_client_id")
        if status:
            queryset = queryset.filter(status=status)
        if billing_client_id:
            queryset = queryset.filter(billing_client_id=billing_client_id)
        if project_client_id:
            queryset = queryset.filter(project_client_id=project_client_id)
        return queryset.order_by("description")

    def perform_create(self, serializer):
        self._require_management_create()
        project = serializer.save()
        create_project_receipt_observation(project, self.request.user)

    def perform_update(self, serializer):
        self._require_management_edit()
        before = Project.objects.get(pk=serializer.instance.pk)
        project = serializer.save()
        create_project_change_observation(before, project, self.request.user)
        if before.received_date != project.received_date:
            create_project_receipt_observation(
                project,
                self.request.user,
                previous_date=before.received_date,
            )

    def perform_destroy(self, instance):
        self._require_management_edit()
        instance.delete()


class ProjectAttachmentViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectAttachmentSerializer
    search_fields = ("description", "project__description")
    ordering_fields = ("created_at",)
    ordering = ("-created_at",)

    def _require_management(self):
        role = resolve_user_role(self.request.user)
        if role not in {
            UserRole.ADMIN,
            UserRole.GP_INTERNAL,
            UserRole.GP_EXTERNAL,
        }:
            raise PermissionDenied("Perfil sem permissao para alterar arquivos.")

    def get_queryset(self):
        self._require_management()
        queryset = ProjectAttachment.objects.select_related("project")
        project_ids = filter_projects_for_user(
            Project.objects.all(), self.request.user
        ).values_list("id", flat=True)
        queryset = queryset.filter(project_id__in=project_ids)
        project_id = self.request.query_params.get("project_id")
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset.order_by("-created_at")

    def perform_create(self, serializer):
        self._require_management()
        serializer.save()

    def perform_update(self, serializer):
        self._require_management()
        serializer.save()

    def perform_destroy(self, instance):
        self._require_management()
        instance.delete()


class ProjectActivityViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectActivitySerializer
    search_fields = (
        "project__description",
        "activity",
        "subactivity",
        "subactivity_items__description",
    )
    ordering_fields = ("project", "seq", "status", "created_at")
    ordering = ("project", "seq")

    def get_queryset(self):
        queryset = ProjectActivity.objects.select_related(
            "project",
            "phase",
            "product",
            "module",
            "submodule",
        ).prefetch_related("consultants", "predecessors", "subactivity_items")
        queryset = filter_activities_for_user(queryset, self.request.user)
        params = self.request.query_params
        project_id = params.get("project_id")
        status = params.get("status")
        consultant_id = params.get("consultant_id")
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if status:
            queryset = queryset.filter(status=status)
        if consultant_id:
            queryset = queryset.filter(consultants__id=consultant_id)
        return queryset.order_by("project_id", "seq")

    def _require_management_create(self):
        role = resolve_user_role(self.request.user)
        if role not in {UserRole.ADMIN, UserRole.GP_INTERNAL}:
            raise PermissionDenied("Perfil sem permissao para alterar atividades.")

    def _require_management_edit(self):
        role = resolve_user_role(self.request.user)
        if role not in {UserRole.ADMIN, UserRole.GP_INTERNAL}:
            raise PermissionDenied("Perfil sem permissao para alterar atividades.")

    def perform_create(self, serializer):
        self._require_management_create()
        serializer.save()

    def perform_update(self, serializer):
        self._require_management_edit()
        serializer.save()

    def perform_destroy(self, instance):
        self._require_management_edit()
        instance.delete()
