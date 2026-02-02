from rest_framework.routers import DefaultRouter

from .views import (
    AccountPlanTemplateHeaderViewSet,
    AccountPlanTemplateItemViewSet,
    CertificationViewSet,
    ClientContactViewSet,
    ClientViewSet,
    CompanyViewSet,
    SupplierViewSet,
    AccountsPayableViewSet,
    AccountsReceivableViewSet,
    CompetencyViewSet,
    ConsultantViewSet,
    DeploymentTemplateHeaderViewSet,
    DeploymentTemplateItemViewSet,
    ProjectActivityViewSet,
    ModuleViewSet,
    PhaseViewSet,
    ProjectAttachmentViewSet,
    ProjectViewSet,
    ProductViewSet,
    SubmoduleViewSet,
)

router = DefaultRouter()
router.register("empresas", CompanyViewSet, basename="empresa")
router.register("fornecedores", SupplierViewSet, basename="fornecedor")
router.register("contas-pagar", AccountsPayableViewSet, basename="conta_pagar")
router.register("contas-receber", AccountsReceivableViewSet, basename="conta_receber")
router.register("clientes", ClientViewSet, basename="cliente")
router.register("contatos", ClientContactViewSet, basename="contato")
router.register("consultores", ConsultantViewSet, basename="consultor")
router.register("competencias", CompetencyViewSet, basename="competencia")
router.register("certificacoes", CertificationViewSet, basename="certificacao")
router.register("fases", PhaseViewSet, basename="fase")
router.register("produtos", ProductViewSet, basename="produto")
router.register("modulos", ModuleViewSet, basename="modulo")
router.register("submodulos", SubmoduleViewSet, basename="submodulo")
router.register(
    "templates-implantacao",
    DeploymentTemplateHeaderViewSet,
    basename="template_implantacao",
)
router.register(
    "templates-implantacao-itens",
    DeploymentTemplateItemViewSet,
    basename="template_implantacao_item",
)
router.register(
    "modelos-plano-contas",
    AccountPlanTemplateHeaderViewSet,
    basename="modelo_plano_contas",
)
router.register(
    "modelos-plano-contas-itens",
    AccountPlanTemplateItemViewSet,
    basename="modelo_plano_contas_item",
)
router.register("projetos", ProjectViewSet, basename="projeto")
router.register("arquivos-projeto", ProjectAttachmentViewSet, basename="arquivo_projeto")
router.register("atividades-projeto", ProjectActivityViewSet, basename="atividade_projeto")

urlpatterns = router.urls
