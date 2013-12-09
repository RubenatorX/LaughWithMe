from django.db import models
from django.db.models import Manager
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.validators import MinLengthValidator
from django.core.validators import MaxLengthValidator
from django.core.validators import RegexValidator


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

# Create your models here.
class UserData(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    screenname = models.CharField(max_length=25, unique=True)
    favorites = models.ManyToManyField('self', through='Favorite', 
                                           symmetrical=False, 
                                           related_name='userFavorites')
    #objects = CaseInsensitiveManager(['screenname'])
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
        return self.userFavorites.filter(
            favoritee__favoriter=self)
class Tag(models.Model):
    tag = models.CharField(max_length=40, unique=True, validators=[MinLengthValidator(1),
            RegexValidator(
                r'^[a-zA-Z][a-zA-Z0-9]*',
                'Must be a letter followed by letters and numbers.',
                'Invalid Hashtag'
            )])
    count = models.IntegerField()
    #objects = CaseInsensitiveManager(['tag'])
    #duplicate
    #add
    #remove
class Post(models.Model):
    user = models.ForeignKey(UserData)
    title = models.CharField(max_length=50, validators=[MinLengthValidator(1)])
    text = models.TextField(validators=[MaxLengthValidator(2000)])
    #image = None ###
    tags = models.ManyToManyField(Tag)
    date = models.DateTimeField(auto_now_add=True)
class Favorite(models.Model):
    user = models.ForeignKey(UserData, related_name='favoriter')
    favorite = models.ForeignKey(UserData, related_name='favoritee')
class Comment(models.Model):
    post = models.ForeignKey(Post)
    commenter = models.ForeignKey(UserData)
    text = models.TextField(validators=[MaxLengthValidator(500)])
    date = models.DateTimeField(auto_now_add=True)
    ###type = 
class Notification(models.Model):
    user = models.ForeignKey(UserData)
    activity = models.ForeignKey(Comment)





'''
#example
class Tags(models.Model):
  tag = models.CharField(max_length=50, unique=True)
  objects = CaseInsensitiveManager()
  def __str__(self):
    return self.name  
'''
