from django.db import models
from django.db.models import Manager
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.validators import MinLengthValidator
from django.core.validators import MaxLengthValidator
from django.core.validators import RegexValidator
import uuid


'''
#needs testing
class CaseInsensitiveQuerySet(QuerySet, fieldnames):
    def _filter_or_exclude(self, mapper, *args, **kwargs):
        for fieldname in fieldnames:
            if fieldname in kwargs:
                kwargs[fieldname + '__iexact'] = kwargs[fieldname]
                del kwargs[fieldname]
        return super(CaseInsensitiveQuerySet, self)._filter_or_exclude(mapper, *args, **kwargs)
class CaseInsensitiveManager(Manager, fieldnames):
    def get_query_set(self):
        return CaseInsensitiveQuerySet(self.model, fieldnames)
'''

DEFAULT_FAVORITES = 'Fav'
DEFAULT_MYPOSTS = 'MP'
DEFAULT_TRENDING = 'Trd'
DEFAULT_MATCHES = 'Mtch'
def defaultChoices():
    return (
        (DEFAULT_MYPOSTS, 'My Posts'),
        (DEFAULT_TRENDING, 'Trending'),
        (DEFAULT_FAVORITES, 'Favorites'),
        #(DEFAULT_MATCHES, 'Matches'),
    )

TEMPLATE_LARGE = 'LG'
TEMPLATE_SMALL = 'SM'
def templateChoices():
    return (
        (TEMPLATE_LARGE, 'Large Image'),
        (TEMPLATE_SMALL, 'Small Image'),
    )

# Create your models here.
class UserData(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    screenname = models.CharField(max_length=25, unique=True, validators=[
            RegexValidator(
                r'^[a-zA-Z0-9-_]*',
                "Screen name must contain only letters, numbers, hyphens and underscores.",
                'Invalid Screen Name'
            )]
    )
    favorites = models.ManyToManyField('self', through='Favorite', 
                                           symmetrical=False, 
                                           related_name='userFavorites')
    DEFAULT_VIEW_CHOICES = (
        (DEFAULT_MYPOSTS, 'My Posts'),
        (DEFAULT_TRENDING, 'Trending'),
        (DEFAULT_FAVORITES, 'Favorites'),
        #(DEFAULT_MATCHES, 'Matches'),
    )
    defaultview = models.CharField(max_length=5,
                                      choices=defaultChoices(),
                                      default=DEFAULT_TRENDING)
    def addFavorite(self, target):
        created = Favorite.objects.get_or_create(
            user=self,
            favorite=target)
        #Sanity Check?
        return created
    def delFavorite(self, target):
        toDelete = Favorite.objects.filter(
            user=self,
            favorite=target)
        #Sanity Check?
        toDelete.delete()
        return
    def getFavorites(self):
        return Favorite.objects.all().filter(
            user=self).prefetch_related('favorite__user')
    def hasFavorite(self, target):
        return len(Favorite.objects.all().filter(user=self, favorite=target)) ==1
    @property
    def notifications(self):
        n = Notification.objects.all().filter(
            user=self)
        l = len(n)
        print "l=%d" %l
        if l == 0:
            return None
        else:
            return l
    def __unicode__(self):
        return self.screenname
class Tag(models.Model):
    tag = models.CharField(max_length=40, unique=True, validators=[MinLengthValidator(1),
            RegexValidator(
                r'^[a-zA-Z][a-zA-Z0-9]*$',
                'Must be a letter followed by letters and numbers.',
                'Invalid Hashtag'
            )])
    count = models.IntegerField()
    #duplicate
    #add
    #remove
class Post(models.Model):
    user = models.ForeignKey(UserData)
    title = models.CharField(max_length=50, validators=[MinLengthValidator(1)])
    text = models.TextField(validators=[MaxLengthValidator(2000)])
    def imagepath(self, originalFilename):
        ext = originalFilename.split('.')[-1]
        filename = '{}.{}'.format(uuid.uuid4().hex, ext)
        print "image %s detected. Saving to %s" % (originalFilename, filename)
        return filename
    image = models.ImageField(upload_to=imagepath)
    tags = models.ManyToManyField(Tag)
    date = models.DateTimeField(auto_now_add=True)
    template = models.CharField(max_length=5,
                                      choices=templateChoices(),
                                      default=TEMPLATE_LARGE)
    def hasNotification(self, user):
        try:
            Notification.objects.get(user=user, activity=self)
            return True
        except:
            return False
    def notify(self):
        print "post notify self"
        created = Notification.objects.get_or_create(
            user=self.user,
            activity=self
            )
        print created
        return created
    def seen(self):
        try:
            toDelete = Notification.objects.get(
                user=self.user,
                activity=self
                )
            toDelete.delete()
            return
        except:
            return
    class Meta:
        ordering = ['-date']
    def addTag(self, tagtext):
        try:
            t = Tag.objects.get(tag__iexact=tagtext)
            t.count = int(t.count)+1
            t.save()
            self.tags.add(t)
        except:
            t = Tag(tag=tagtext, count=1)
            t.save()
            self.tags.add(t)
class Favorite(models.Model):
    user = models.ForeignKey(UserData, related_name='favoriter')
    favorite = models.ForeignKey(UserData, related_name='favoritee')
    class Meta:
        ordering = ['favorite__screenname']
class Comment(models.Model):
    post = models.ForeignKey(Post)
    commenter = models.ForeignKey(UserData)
    text = models.TextField(validators=[MaxLengthValidator(500)])
    date = models.DateTimeField(auto_now_add=True)

    COMMENT_NONE = 0,
    COMMENT_LAUGHWITH = 1,
    COMMENT_PITY = 2,
    COMMENT_TYPE_CHOICES = (
        (COMMENT_NONE, 'None'),
        (COMMENT_LAUGHWITH, 'LaughWith'),
        (COMMENT_PITY, 'Pity')
    )
    type = models.IntegerField(default=0)
    def notify(self):
        print "comment notify self"
        self.post.notify()
    @property
    def typename(self):
        if self.type == 1:
            typename = 'LaughWith'
        elif self.type == 2:
            typename = 'Pity'
        else :
            typename = None
        return typename
        #Sanity Check?
        return created
    class Meta:
        ordering = ['-date']
        
class Notification(models.Model):
    user = models.ForeignKey(UserData)
    activity = models.ForeignKey(Post)





'''
#example
class Tags(models.Model):
  tag = models.CharField(max_length=50, unique=True)
  objects = CaseInsensitiveManager()
  def __str__(self):
    return self.name  
'''
