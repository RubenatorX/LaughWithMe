from django.shortcuts import render
from django.shortcuts import render_to_response
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect

# Create your views here.


def WelcomeView(request):
    if request.user.is_authenticated():
        # Do something for authenticated users.
        return render(request, 'mainsite/temploggedin.html', {'user':request.user})
    else:
        # Do something for anonymous users.
        form = LoginForm()
        return render(request, 'mainsite/welcome.html',{'form': form})
def AboutView(request, ignore):
    form = LoginForm()
    return render(request, 'mainsite/about.html',{'form': form})
def LoginView(request, ignore):
    if request.method == 'POST': # If the form has been submitted...
        form = LoginForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            user = authenticate(username=form.cleaned_data['email'], password=form.cleaned_data['password'])
            if user is not None:
                if user.is_active:
                    #Successful login
                    login(request, user)
                    return redirect('/')
                else:
                    # Account Disabled
                    return render(request, 'mainsite/login.html', {
                        'form': form,
                        })
        #bad login
        loginError = "The username and/or password was incorrect. Please try again."
        return render(request, 'mainsite/login.html', {
                'form': form,
                'loginError' : loginError,
                })
            
    else:
        form = LoginForm() # An unbound form

    return render(request, 'mainsite/login.html', {
        'form': form,
    })


'''def RegistrationView(request, ignore):
    return render_to_response('mainsite/registration.html')'''
def RegistrationView(request, ignore):
    if request.method == 'POST': # If the form has been submitted...
        form = RegistrationForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            ## check for duplicate Names etc.

            # Process the data in form.cleaned_data
            # ...
            user = User.objects.create_user(username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'])
            #user.save()
            #user = authenticate(username=form.cleaned_data['email'], password=form.cleaned_data['password'])
            #Sanity Check?

            #login(request, user)
            
            ##Do other stuff (like save screenname)
            return redirect('/') # Redirect after POST
    else:
        form = RegistrationForm() # An unbound form

    return render(request, 'mainsite/registration.html', {
        'form': form,
    })

class LoginForm(forms.Form):
    email = forms.email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                'placeholder':'Email',
                'class':'form-control',
            }
        )
    )
    password = forms.CharField(max_length=32,
        widget=forms.PasswordInput(
            render_value=True,
            attrs={
                'placeholder':'password',
                'class':'form-control',
            }
        )
    )
class RegistrationForm(forms.Form):
    email = forms.EmailField(max_length=30, min_length=7,
        widget=forms.TextInput(
            attrs={
                'placeholder':'Email',
                'class':'form-control',
            }
        )
    )
    screenname = forms.CharField(min_length=5, max_length=25,
        widget=forms.TextInput(
            attrs={
                'placeholder':'Screen Name',
                'class':'form-control',
            }
        )
    )
    password = forms.CharField(max_length=32,
        widget=forms.PasswordInput(
            render_value=True,
            attrs={
                'placeholder':'password',
                'class':'form-control',
            }
        )
    )
    passwordconfirm = forms.CharField(max_length=32,
        widget=forms.PasswordInput(
            render_value=True,
            attrs={
                'placeholder':'confirm password',
                'class':'form-control',
            }
        )
    )
    def clean(self):
        form_data = self.cleaned_data
        if 'password' in form_data and 'passwordconfirm' in form_data:
            if form_data['password'] != form_data['passwordconfirm']:
                self._errors["password"] = "Passwords do not match" 
                #raise forms.ValidationError()
                del form_data['password']
        else :
            self._errors["password"] = "These fields are required" 
        return form_data
    

'''from django.shortcuts import render,get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.http import Http404
from polls.models import Poll, Choice
from django.views import generic

class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_poll_list'

    def get_queryset(self):
        """Return the last five published polls."""
        return Poll.objects.order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Poll
    template_name = 'polls/detail.html'


class ResultsView(generic.DetailView):
    model = Poll
    template_name = 'polls/results.html'

def vote(request, poll_id):
    p = get_object_or_404(Poll, pk=poll_id)
    try:
        selected_choice = p.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the poll voting form.
        return render(request, 'polls/detail.html', {
            'poll': p,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(p.id,)))
'''
