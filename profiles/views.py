from django.shortcuts import render,redirect
from django.conf import settings
from django.urls import reverse, reverse_lazy
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_str as force_text
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model



# Create your views here.

from django.contrib.auth import logout
from .forms import ProfileForm, InvitationForm
from .models import Profile, Invitation

from users.tokens import account_activation_token

def send_invitation(request, id):
    try:
        invitation = Invitation.objects.get(id=id, user=request.user)
    except Invitation.DoesNotExist:
        invitation = None
    if invitation:
        current_site = get_current_site(request)
        data = {
            'email': invitation.email,
            'user': invitation.user.email,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(invitation.pk)),
            'token': account_activation_token.make_token(invitation),
        }
        msg_plain = render_to_string('invitation.txt', data)
        msg_html = render_to_string('invitation.html', data)
        send_mail(
            'email title',
            msg_plain,
            'some@sender.com',
            ['some@receiver.com'],
            html_message=msg_html,
        )
        return redirect(reverse_lazy('invitation-list'))
    else:
        logout(request)
        return redirect(settings.LOGOUT_REDIRECT_URL)


def remove_invitation(request, id):
    User = get_user_model()
    try:
        invitation = Invitation.objects.get(id=id, profile=request.user.profile)
    except Invitation.DoesNotExist:
        invitation = None
    if invitation:
        try:
            user = User.objects.get(email=invitation.email)
        except User.DoesNotExist:
            user = None
        if user:
            return redirect(reverse_lazy('invitation-list'))
    else:
        logout(request)
        return redirect(settings.LOGOUT_REDIRECT_URL)


def activate_invite(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        invitation = Invitation.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Invitation.DoesNotExist):
        invitation = None

    if invitation is not None and account_activation_token.check_token(invitation, token):
        request.session['email'] = invitation.email
        return redirect('signup')
    else:
        return render(request, 'invitation_invalid.html')


class ProtectProfile:
    def dispatch(self, *args, **kwargs):
        if self.request.user.profile.pk != self.get_object().pk:
            raise PermissionDenied()
        return super().dispatch(*args, **kwargs)


class ProfileDetailView(ProtectProfile, LoginRequiredMixin, DetailView):
    model = Profile

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        uuid = urlsafe_base64_encode(force_bytes(self.get_object().pk))
        token = default_token_generator.make_token(self.get_object().user)
        url = self.request.build_absolute_uri(reverse(
                        "password_reset_confirm",
                        kwargs={"uidb64": uuid, "token": token}))
        context['password_url'] = url
        return context


class ProfileUpdateView(ProtectProfile, LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'profiles/profile_form.html'

    def get_success_url(self, **kwargs):
        return reverse_lazy('profile-detail',
                            kwargs={'pk': self.get_object().pk})


class ProfileDeleteView(ProtectProfile, LoginRequiredMixin, DeleteView):
    model = Profile
    template_name = 'profiles/profile_confirm_delete.html'

    def get_success_url(self, **kwargs):
        return reverse_lazy('profile-detail',
                            kwargs={'pk': self.get_object().pk})



class InvitationListView(LoginRequiredMixin, ListView):
    model = Invitation
    paginate_by = settings.PAGINATION_ITEMS
    queryset = Invitation.objects.select_related('user')

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user).order_by('-pk')
        return queryset


class InvitationDetailView(LoginRequiredMixin, DetailView):
    model = Invitation
    queryset = Invitation.objects.select_related('user')

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user).order_by('-pk')
        return queryset


class InvitationCreateView(LoginRequiredMixin, CreateView):
    model = Invitation
    form_class = InvitationForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()
        send_invitation(self.request, form.instance.pk)
        return super().form_valid(form)


class InvitationUpdateView(LoginRequiredMixin, UpdateView):
    model = Invitation
    form_class = InvitationForm
    queryset = Invitation.objects.select_related('user')

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user).order_by('-pk')
        return queryset


class InvitationDeleteView(LoginRequiredMixin, DeleteView):
    model = Invitation
    queryset = Invitation.objects.select_related('user')

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user).order_by('-pk')
        return queryset