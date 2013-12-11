from django.shortcuts import render
from django.shortcuts import render_to_response
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.forms.util import ErrorList
from models import *
from django.contrib.auth import logout
from captcha.fields import ReCaptchaField

# Create your views here.


def WelcomeView(request):
    if request.user.is_authenticated():
        # Do something for authenticated users.
        return DefaultView(request)
    else:
        # Do something for anonymous users.
        return render(request, 'mainsite/welcome.html',{'loginform': LoginForm()})
def DefaultView(request):
    if request.user.is_authenticated():
        pass
        #handle request.user.userdata.defaultview
        return render(request, 'mainsite/base-loggedin.html', {'userdata':request.user.userdata}) #temp
    else:
        return redirect('/')
def AboutView(request, ignore):
    ##What do we do if they are logged in and go to the About page? (specifically with the sign in bar?)
    return render(request, 'mainsite/about.html',{'loginform': LoginForm()})
def MyPostsView(request, ignore): ## incomplete
        if request.user.is_authenticated():
            if request.method == 'POST': # Modify
                form = NewPostForm(request.POST)
                if form.is_valid():
                    pass #process stuff
                else:
                    pass #bad error
            pass #return normal stuff
            posts = Post.objects.all().filter(user=request.user).prefetch_related('user', 'comment_set__commenter', 'tags')
            
            return render(request, 'mainsite/myPosts.html', {'posts':posts})
        else:
            return redirect('/')    
def NewPostView(request, ignore):
    if request.user.is_authenticated():
        if request.method == 'POST': # If the form has been submitted...
            #form = NewPostForm(request.POST)
            if True:#'''form.is_valid():'''
                pass
                #process stuff
            else:
                #return form with errors
                return render(request, 'mainsite/newPost.html', {'userdata':request.user.userdata})#''',{'form':form}''')
        else:
            #return empty form
            return render(request, 'mainsite/newPost.html', {'userdata':request.user.userdata})#''',{'form':NewPostForm()}''')
    else:
        return redirect('/')
def LoginView(request, ignore):
    if request.method == 'POST': # If the form has been submitted...
        loginform = LoginForm(request.POST) # A form bound to the POST data
        if loginform.is_valid(): # All validation rules pass
            user = authenticate(username=loginform.cleaned_data['email'], password=loginform.cleaned_data['password'])
            if user is not None:
                if user.is_active:
                    #Successful login
                    login(request, user)
                    return redirect('/')
                else:
                    # Account Disabled
                    loginError = "Your account has been disabled"
                    return render(request, 'mainsite/login.html', {
                        'loginform': loginform,
                        'loginError' : loginError,
                        })
        #Bad login
        loginError = "The username and/or password was incorrect. Please try again."
        return render(request, 'mainsite/login.html', {
                'loginform': loginform,
                'loginError' : loginError,
                })
            
    else:
        loginform = LoginForm() # An unbound form

    return render(request, 'mainsite/login.html', {
        'loginform': loginform,
    })
def LogoutView(request, ignore):
    logout(request)
    return redirect('/')


'''def RegistrationView(request, ignore):
    return render_to_response('mainsite/registration.html')'''
def RegistrationView(request, ignore):
    if request.method == 'POST': # If the form has been submitted...
        form = RegistrationForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass

            user = User.objects.create_user(username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'])
            user.save()
            user = authenticate(username=form.cleaned_data['email'], password=form.cleaned_data['password'])
            ##Sanity Check?

            login(request, user)
            
            ##Do other stuff (like save screenname)
            userdata = UserData(user=user, screenname=form.cleaned_data['screenname'])
            userdata.save()
            return redirect('/') # Redirect after POST
    else:
        form = RegistrationForm() # An unbound form

    return render(request, 'mainsite/registration.html', {
        'loginform': LoginForm(),
        'form':form,
    })

class LoginForm(forms.Form):
    email = forms.email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                'placeholder':'email',
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
    captcha = ReCaptchaField()
    
    def clean(self):
        form_data = self.cleaned_data
        if 'password' in form_data and 'passwordconfirm' in form_data:
            if form_data['password'] != form_data['passwordconfirm']:
                self._errors["password"]= "Passwords do not match"
                del form_data['password']
        else :
            self._errors["password"]= "These fields are required"
        return form_data
    def clean_screenname(self):
        form_data = self.cleaned_data
        if 'screenname' in self.cleaned_data:
            name = self.cleaned_data['screenname']
            if len(UserData.objects.filter(screenname__iexact=name)) > 0:
                self._errors['screenname']= 'This Screenname is already taken, try another.'
        else:
            self._errors["screenname"]= "A Screen Name is required"
        return form_data['screenname']
    def clean_email(self):
        form_data = self.cleaned_data
        if 'email' in self.cleaned_data:
            name = self.cleaned_data['email']
            if len(User.objects.filter(username__iexact=name)) > 0:
                self._errors['email']= "There is already an account associated with this email."
        else:
            self._errors["email"]= "An email is required."
        return form_data['email']
        
    
'''#File Upload example
def upload_file(request):
    if request.method == 'POST':
        form = ModelFormWithFileField(request.POST, request.FILES)
        if form.is_valid():
            # file is saved
            form.save()
            return HttpResponseRedirect('/success/url/')
    else:
        form = ModelFormWithFileField()
    return render(request, 'upload.html', {'form': form})
'''
