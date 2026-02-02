from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView

from .forms import CandidateApplicationForm, ProposalRequestForm
from .models import CandidateApplication, ProposalRequest


class PublicFormBaseView(CreateView):
    template_name = "public_form.html"
    page_eyebrow = "Kuiper"
    page_title = ""
    page_description = ""
    form_title = ""
    form_badge = ""
    submit_label = "Enviar"
    success_message = "Solicitacao enviada com sucesso."
    form_columns = 2
    full_width_fields: tuple[str, ...] = ()

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cancel_url = f"{reverse('home')}#conexoes"
        context.update(
            {
                "page_eyebrow": self.page_eyebrow,
                "page_title": self.page_title,
                "page_description": self.page_description,
                "form_title": self.form_title,
                "form_badge": self.form_badge,
                "submit_label": self.submit_label,
                "cancel_url": cancel_url,
                "form_columns": self.form_columns,
                "full_width_fields": self.full_width_fields,
            }
        )
        return context


class CandidateApplicationCreateView(PublicFormBaseView):
    model = CandidateApplication
    form_class = CandidateApplicationForm
    success_url = reverse_lazy("candidate_application")
    page_eyebrow = "Trabalhe conosco"
    page_title = "Candidatura Kuiper"
    page_description = "Conte sobre seu perfil e envie seu curriculo para avaliacao."
    form_title = "Inscricao de consultores"
    form_badge = "Candidatura"
    submit_label = "Enviar candidatura"
    success_message = "Candidatura enviada com sucesso."
    full_width_fields = ("experience_summary", "resume")


class ProposalRequestCreateView(PublicFormBaseView):
    model = ProposalRequest
    form_class = ProposalRequestForm
    success_url = reverse_lazy("proposal_request")
    page_eyebrow = "Contato comercial"
    page_title = "Solicitar proposta"
    page_description = "Compartilhe o escopo e receba retorno do nosso time."
    form_title = "Solicitacao de proposta"
    form_badge = "Clientes"
    submit_label = "Enviar solicitacao"
    success_message = "Solicitacao enviada com sucesso."
    full_width_fields = ("project_summary", "additional_notes")
