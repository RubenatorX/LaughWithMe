from django.db import models
from django.db.models import Manager
from django.db.models.query import QuerySet

# Create your models here.
class UserData(models.Model):
    email = models.CharField(max_length=254, validators=[validate_email])
    screenname = models.CharField(max_length=25, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    objects = CaseInsensitiveManager(['screenname','email'])
class Posts(models.Model):
    title = models.CharField(max_length=50, validators=[MinLengthValidator(1)])
    text = models.TextField(validators=[MaxLengthValidator(2000)])
    #image = None ###
class Favorites(models.Model):
    user = models.ForeignKey(Users) ##need to find out what Users actually should be called
    favorite = models.ForeignKey(User) ##
class Notifications(models.Model):
    user = models.ForeignKey(Users) ##
    activity = models.ForeignKey(Comments)
class Comments(models.Model):
    user = models.ForeignKey(Users) ##
    text = models.TextField(validators=[MaxLengthValidator(500)])
    ###type = 
class Tags(models.Model):
    tag = models.CharField(max_length=40, unique=True, validators=[MinLengthValidator(1),
            RegexValidator(
                r'^[a-zA-Z][a-zA-Z0-9]*',
                'Must be a letter followed by letters and numbers.',
                'Invalid Hashtag'
            )])
    objects = CaseInsensitiveManager(['tag'])




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
        return TagCaseInsensitiveQuerySet(self.model, fieldnames)
'''
#example
class Tags(models.Model):
  tag = models.CharField(max_length=50, unique=True)
  objects = CaseInsensitiveManager()
  def __str__(self):
    return self.name  
'''
