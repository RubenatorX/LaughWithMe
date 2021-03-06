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
import re
# Create your views here.

def summarizeComments(post):
    summary = ""
    for comment in post.comment_set.all():
        if comment.text == u"":
            continue
        summary += comment.commenter.screenname
        if comment.typename != None:
            summary += "- " + comment.typename
        summary += ": " + comment.text[:47]
        if len(comment.text) > 47:
            summary += "..."
        summary += "\n"
    if summary == "":
        post.hasComment = False
    else:
        post.hasComment = True
    return summary
def processPosts(posts, request):
    COMMENT_PITY = 2
    COMMENT_LAUGHWITH = 1
    for post in posts:
        if post.user.pk == request.user.pk:
            post.candelete = True
            for comment in post.comment_set.all():
                comment.candelete = True
        else:
            for comment in post.comment_set.all():
                if comment.commenter.pk == request.user.pk:
                    comment.candelete = True
        for comment in post.comment_set.all():
                if comment.text!=u'':
                    comment.notempty = True
                    post.hasComments = True
        post.hasNotification = post.hasNotification(request.user.userdata)
        post.tagList = []
        for tag in post.tags.all()[:5]:
            post.tagList.append(tag.tag)
        #print post.tagList
        post.commentSummary = summarizeComments(post)
        post.commentcount = len(post.comment_set.exclude(text=u''))
        post.pitycount = len(post.comment_set.filter(type=COMMENT_PITY))
        post.laughcount = len(post.comment_set.filter(type=COMMENT_LAUGHWITH))
    return posts

def WelcomeView(request):
    if request.user.is_authenticated():
        # Do something for authenticated users.
        return DefaultView(request)
    else:
        # Do something for anonymous users.
        return render(request, 'mainsite/welcome.html',{'loginform': LoginForm()})
def DefaultView(request):
    ignore = 'NULL'
    if request.user.is_authenticated():
        v = request.user.userdata.defaultview
        if v == DEFAULT_MYPOSTS:
            return MyPostsView(request, ignore)
        elif v == DEFAULT_TRENDING:
            return TrendingView(request, ignore)
        elif v == DEFAUL_FAVORITES:
            return FavoritesView(request, ignore)
        #elif v == DEFAULT_MATCHES:
            #return MyPostsView(request, ignore)###
        else:            
            return MyPostsView(request, ignore)##
    else:
        return redirect('/')
def AboutView(request, ignore):
    ##What do we do if they are logged in and go to the About page? (specifically with the sign in bar?)
    return render(request, 'mainsite/about.html',{'loginform': LoginForm()})
def MyPostsView(request, ignore): ## incomplete
        if request.user.is_authenticated():
            if request.method == 'POST': # Modify
                '''form = Form(request.POST)
                if form.is_valid():
                    pass #process stuff
                else:
                    pass #bad error'''
                pass
            pass #return normal stuff
        
           
            posts = Post.objects.all().filter(user=request.user).prefetch_related('user', 'comment_set__commenter', 'tags')

            posts = processPosts(posts, request)
            
            
            templates = [i[0] for i in templateChoices()]

            
            return render(request, 'mainsite/myPosts.html', {'posts':posts, 'userdata':request.user.userdata, 'templates':templates})
        else:
            return redirect('/')
def NewPostView(request, ignore):
    if request.user.is_authenticated():
        choices = templateChoices()
        tlist = [i[0] for i in choices]
        if request.method == 'POST': # If the form has been submitted...
            form = NewPostForm(request.POST, request.FILES)
            if form.is_valid():                
                templateType = choices[0][0]
                if 'templateType' in request.POST and request.POST['templateType'] in tlist:
                    templateType = request.POST['templateType']
                post = Post(user=request.user.userdata,
                            image=form.cleaned_data['image'],
                            title=form.cleaned_data["postTitle"],
                            text=form.cleaned_data["post"],
                            template=templateType
                )
                post.save()
                for t in form.cleaned_data["tags"]:
                    post.addTag(t)
                
                return redirect('/post/' + str(post.pk))
            else:
                #return form with errors
                return render(request, 'mainsite/newPost.html', {'userdata':request.user.userdata, 'form':form, 'templateChoices':tlist})
        else:
            #return empty form

            return render(request, 'mainsite/newPost.html', {'userdata':request.user.userdata, 'form':NewPostForm(), 'templateChoices':tlist})
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

def PersonView(request, username): #testing
    if request.user.is_authenticated():
        try:
            user = UserData.objects.all().get(screenname=username)
        except:
            user = None
        if 'searchBox' in request.POST and request.method == 'POST' and user is None: #search result
            return redirect("/user/"+request.POST['searchBox'].lstrip().split(" ")[0])
        if user == None: #the user isn't in the system
            return render(request, 'mainsite/message.html', {'message':"No Search Results", 'userdata':request.user.userdata})
            

        if request.user.pk == user.pk:
            return redirect('/myposts')
        if request.method == 'POST': # Modify
            if user != None and 'favoriteID' in request.POST and int(request.POST['favoriteID'])==user.pk and user.pk != request.user.pk:
                request.user.userdata.addFavorite(user)
                request.user.userdata.save()
                return redirect("/user/"+username)
            else:
                print "user=%s" % user
                print "'favoriteID' in request.POST=%s"% ('favoriteID' in request.POST)
                print "post=%s" % request.POST
                print "request.POST['favoriteID']==user.pk=%s" % request.POST['favoriteID']==user.pk
                
        else:
            pass #return normal stuff
            ##sanatize the screenname if necessary here
            pass
            COMMENT_PITY = 2
            COMMENT_LAUGHWITH = 1
            if user != None:
                posts = Post.objects.all().filter(user=user).prefetch_related('user', 'comment_set__commenter', 'tags')
                post = processPosts(posts,request)
                favorited=request.user.userdata.hasFavorite(user)
                                
                #print 'favorited=request.user.userdata.hasFavorite(user)=%s' % favorited
                return render(request, 'mainsite/personPage.html', {'posts':posts, 'userdata':request.user.userdata, 'favorited':favorited, 'viewuser':user})
            else:
                pass
                message = "username not found" #temp
                return render(request, 'mainsite/message.html', {'message':message}) #temp
                ##run some sort of search
    else:
        return redirect('/')
    
    return render(request, 'mainsite/myPosts.html')

def SettingsView(request, ignore): #testing
    if request.user.is_authenticated():
        message = None
        passwordmessage=None
        passwordForm = ResetPasswordForm(request.user)
        if request.method == 'POST': # Modify
            #print request.POST
            if 'defaultviewchoice' in request.POST:
                if request.POST['defaultviewchoice'] in [i[0] for i in defaultChoices()]:
                    user = request.user.userdata
                    user.defaultview = request.POST['defaultviewchoice']
                    user.save()
                    message = "Saved"
                else:
                    #print  "2 %s not in %s" % (request.POST['defaultviewchoice'], [i[0] for i in defaultChoices()])
                    pass #invalid form field
            elif 'favID' in request.POST:
                try:
                    f = Favorite.objects.filter(user=request.user, favorite=request.POST['favID'])
                    f.delete()
                except:
                    pass
            else:
                passwordForm = ResetPasswordForm(request.user, request.POST)
                if passwordForm.is_valid():
                    user = request.user
                    user.set_password(passwordForm.cleaned_data['password'])
                    user.save()
                    passwordForm = ResetPasswordForm(request.user)
                    passwordmessage = "Password Reset Successfully"
                pass
            '''form = Form(request.POST)
            if form.is_valid():
                pass #process stuff
            else:
                pass #bad error'''
        else:
            passwordForm = ResetPasswordForm(request.user)
            pass #return normal stuff
        userdata = request.user.userdata
        user = request.user
        favorites = userdata.getFavorites()
        #for favorite in favorites:
            #print favorite.favorite.screenname
        return render(request, 'mainsite/settings.html', {'user':user, 'userdata':userdata, 'choices':defaultChoices(), 'message':message, 'passwordmessage':passwordmessage, 'favorites':favorites, 'passwordForm':passwordForm, 'hasFavorites':len(favorites)>0,})
    else:
        return redirect('/')
    
    return render(request, 'mainsite/myPosts.html')

def PostView(request, postid):
    if request.user.is_authenticated():        
        posts = Post.objects.all().filter(pk=int(postid)).prefetch_related('comment_set__commenter', 'tags')

        if "noticicationID" in request.POST:
            print "notificationID found"
            posts[0].seen()
            return HttpResponse()
        
        form = CommentForm(request.POST)
        
        if len(posts) == 0:
            pass
            message = "post not found " + postid #temp
            return render(request, 'mainsite/message.html', {'message':message}) #temp
                ##run some sort of search
        
        elif "postID" in request.POST:
            post = posts[0]
            if post.user.pk == request.user.pk:
                #go for it
                if post.image:
                    post.image.delete()
                post.delete()
            else:
                #you aren't the user, no permission
                pass
            return redirect("/myposts")
        
        elif "commentID" in request.POST:
            comment = None
            try:
                comment = Comment.objects.get(pk = int(request.POST['commentID'])) 
            except:
                pass #no comment was found
            if posts[0].user.pk == request.user.pk:
                #go for it
                comment.delete()
            else:
                if comment.commenter.pk == request.user.pk:
                    #go for it
                    comment.delete()
                else:
                    # bad permission
                    pass
            return redirect('/post/' + str(posts[0].pk))
                    
        
        elif request.method == 'POST': # Modify
            if form.is_valid():
                #process stuff
                if form.cleaned_data['pity']:
                    type = 2
                elif form.cleaned_data['laughWith']:
                    type = 1
                else:
                    type = 0
                        
                
                comment = Comment(post = posts[0],
                    commenter = request.user.userdata,
                    text = form.cleaned_data['comment'],
                    type = type
                )
                
                comment.save()
                print "comment.post.user.pk=%d and request.user.pk=%d" % (comment.post.user.pk, request.user.pk)
                if comment.post.user.pk != request.user.pk:
                    comment.notify()
                form = CommentForm()
                
                return redirect('/post/' + str(posts[0].pk))
                 
            else:
                pass #bad error'''
            pass
        else:
            pass #return normal stuff
            ##sanatize the postid if necessary here
            pass
            form = CommentForm()

        '''for comment in post.comment_set.all():
            if comment.type == 1:
                comment.typename = 'LaughWith'
            elif comment.type == 2:
                comment.typename = 'Pity'
            else :
                comment.typename = 'NOTHING'
        '''

        posts = processPosts(posts,request)
        for post in posts:
            if request.user.pk == post.user.pk:
                post.seen()
       
              
        templates = [i[0] for i in templateChoices()]
        return render(request, 'mainsite/post.html', {'post':posts[0], 'form':form, 'userdata':request.user.userdata, 'templates':templates})
    else:
        return redirect('/')
    return render(request, 'mainsite/myPosts.html')

def FavoritesView(request, ignore):
    if request.user.is_authenticated():
        if request.method == 'POST': # Modify
            '''form = Form(request.POST)
            if form.is_valid():
                pass #process stuff
            else:
                pass #bad error'''
            pass
        pass #return normal stuff

        favoriteUsers = [i.favorite for i in request.user.userdata.getFavorites()]
        posts = Post.objects.all().filter(user__in=favoriteUsers).prefetch_related('user', 'comment_set__commenter', 'tags')

        print request.user.userdata.getFavorites()
        print posts
        
        posts = processPosts(posts, request)
            
            
        templates = [i[0] for i in templateChoices()]

            
        return render(request, 'mainsite/favorites.html', {'posts':posts, 'userdata':request.user.userdata, 'templates':templates})
    else:
        return redirect('/')
def TrendingView(request, ignore):
    if request.user.is_authenticated():
        if request.method == 'POST': # Modify
            '''form = Form(request.POST)
            if form.is_valid():
                pass #process stuff
            else:
                pass #bad error'''
            pass
        pass #return normal stuff
        
           
        posts = Post.objects.all().order_by('-date')[:25].prefetch_related('user', 'comment_set__commenter', 'tags')

        posts = processPosts(posts, request)
            
            
        templates = [i[0] for i in templateChoices()]

            
        return render(request, 'mainsite/trending.html', {'posts':posts, 'userdata':request.user.userdata, 'templates':templates})
    else:
        return redirect('/')

def MyActivityView(request, ignore):
    if request.user.is_authenticated():
        if request.method == 'POST': # Modify
            '''form = Form(request.POST)
            if form.is_valid():
                pass #process stuff
            else:
                pass #bad error'''
            pass
        pass #return normal stuff
        
           
        favoriteUsers = [i.favorite for i in request.user.userdata.getFavorites()]

        c = Comment.objects.all().filter(commenter=request.user)
        mycomments = [i.pk for i in c]
        
        posts = Post.objects.all().filter(comment__pk__in=mycomments).prefetch_related('user', 'comment_set__commenter', 'tags')
        posts = processPosts(posts, request)
            
            
        templates = [i[0] for i in templateChoices()]

            
        return render(request, 'mainsite/myactivity.html', {'posts':posts, 'userdata':request.user.userdata, 'templates':templates})
    else:
        return redirect('/')

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
                'id':'emailField',
            }
        )
    )
    screenname = forms.CharField(min_length=5, max_length=25,
        widget=forms.TextInput(
            attrs={
                'placeholder':'Screen Name',
                'class':'form-control',
                'id':'snField',
            }
        )
    )
    password = forms.CharField(max_length=32,
        widget=forms.PasswordInput(
            render_value=True,
            attrs={
                'placeholder':'password',
                'class':'form-control',
                'id':'passField',
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
                return form_data
        else :
            self._errors["password"]= "These fields are required"
            return form_data
        if not re.match(r'^(?=.*[a-zA-Z])(?=.*\d).+$', self.cleaned_data['password']):
            self._errors['password']= 'Password must contain letters and a numbers.'
            return form_data
        return form_data
    def clean_screenname(self):
        form_data = self.cleaned_data
        if 'screenname' in self.cleaned_data:
            name = self.cleaned_data['screenname']
            if len(UserData.objects.filter(screenname__iexact=name)) > 0:
                self._errors['screenname']= 'This Screenname is already taken, try another.'
                return form_data['screenname']
            if not re.match(r'^[a-zA-Z0-9]', self.cleaned_data['screenname']):
                self._errors['screenname']= "Screen Name must start with a letter or number"
                return form_data['screenname']
            if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9-_]*$', self.cleaned_data['screenname']):
                self._errors['screenname']= "Screen Name must only contain letters, numbers, hyphens, and underscores."
                return form_data['screenname']
            #profanity filter goes here
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

class NewPostForm(forms.Form):
    postTitle = forms.CharField(max_length=50, min_length=1,
        widget=forms.TextInput(
            attrs={
                'placeholder':'Title',
                'class':'form-control',
                'id':'title',
            }
        )
    )
    
    image = forms.ImageField(required=False,
        widget=forms.ClearableFileInput(
            attrs={
                'class':'form-control',
                'id':'image',
                'onchange':'toggleTemplates()',
            }
        )
    )
    
    post = forms.CharField(required=False, max_length=2000,
        widget=forms.Textarea(
            attrs={
                'placeholder':'Write your story...',
                'class':'form-control',
                'id':'post',
            }
        )
    )
    tags = forms.CharField(required=False, max_length=500,
        widget=forms.TextInput(
            attrs={
                'placeholder':'Add tags...',
                'class':'form-control',
                'id':'tags',
            }
        )
    )
    def clean_tags(self):
        form_data = self.cleaned_data
        if 'tags' in self.cleaned_data:
            t = [x.strip() for x in self.cleaned_data['tags'].split(',')]
            l = list(set(i.lower() for i in t))
            tags=[]
            for i in t:
                lc = i.lower()
                if lc in l and lc != "" and lc != " ":
                    l.remove(lc)
                    tags.append(i)
            cleanedTags = []
            for tag in tags:
                if tag[0] == '#':
                    tag = tag[1:]
                if re.match(r'^[a-zA-Z][a-zA-Z0-9]*$', tag):
                    cleanedTags.append(tag)
            #self._errors["tags"] = "Old Password incorrect"
            form_data['tags'] = cleanedTags
        return form_data['tags']
    
class CommentForm(forms.Form):
    pity = forms.BooleanField(initial=False, required=False,
        widget=forms.CheckboxInput(
            attrs={
                'class':'form-control',
                'id':'pity',
                'onclick':'checkPityBox()',
            }
        )
    )
    
    laughWith = forms.BooleanField(initial=False, required=False,
        widget=forms.CheckboxInput(
            attrs={
                'class':'form-control',
                'id':'laughWith',
                'onclick':'checkLaughWithBox()',
            }
        )
    )
    
    comment = forms.CharField(required=False, max_length=500,
        widget=forms.Textarea(
            attrs={
                'placeholder':'Make a comment...',
                'class':'form-control',
                'id':'commentArea',
                'style':'display:none;',
                'rows': '5', 
            }
        )
    )
    tags = forms.CharField(required=False, max_length=50,
        widget=forms.TextInput(
            attrs={
                'placeholder':'Add tags...',
                'class':'form-control',
                'id':'tags',
            }
        )
    )

class ResetPasswordForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ResetPasswordForm, self).__init__(*args, **kwargs)
    oldpassword = forms.CharField(max_length=32,
        widget=forms.PasswordInput(
            render_value=True,
            attrs={
                'placeholder':'old password',
                'class':'form-control',
                'id':'oldPassField',
            }
        )
    )
    password = forms.CharField(max_length=32,
        widget=forms.PasswordInput(
            render_value=True,
            attrs={
                'placeholder':'new password',
                'class':'form-control',
                'id':'passField',
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
                self._errors["password"]= "Passwords do not match"
                del form_data['password']
                return form_data
        else :
            self._errors["password"]= "These fields are required"
            return form_data
        if not re.match(r'^(?=.*[a-zA-Z])(?=.*\d).+$', self.cleaned_data['password']):
            self._errors['password']= 'Password must contain letters and a numbers.'
            return form_data
        return form_data
    def clean_oldpassword(self):
        form_data = self.cleaned_data
        if 'oldpassword' in self.cleaned_data:
            pwd = self.cleaned_data['oldpassword']
            user = authenticate(username=self.user.username, password=form_data['oldpassword'])
            if user is None:
                self._errors["oldpassword"] = "Old Password incorrect"                
        else:
            self._errors["oldpassword"]= "Old Password is required."
        return form_data['oldpassword']


             
    
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
