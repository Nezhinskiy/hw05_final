from django.urls import reverse_lazy
from django.views.generic import CreateView

from posts.urls import INDEX
from users.forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy(INDEX)
    template_name = 'users/signup.html'
