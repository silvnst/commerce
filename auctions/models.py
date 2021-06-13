from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import fields
from django.db.models.base import Model
from django.db.models.deletion import CASCADE, DO_NOTHING, SET_NULL
from django.db.models.fields import CharField
from django import forms
from django.core.validators import MinValueValidator
from django.forms import widgets

class User(AbstractUser):
    pass

class Category(models.Model):
    category_name = models.CharField(max_length=64)
    
    def __str__(self):
        return f'{self.id}: {self.category_name}'

class Listing(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=64)
    desc = models.CharField(max_length=512)
    starting_bid = models.FloatField(validators=[MinValueValidator(0)])
    url = models.URLField(blank=True)
    category = models.ManyToManyField(Category, related_name="category_items" , blank=True)
    active = models.BooleanField(default=True)
    watchlist = models.ManyToManyField(User, related_name="watch_list", blank=True)

    def watch_count(self):
        return self.watchlist.count()
    
    def unique_categories(self):
        a = Listing.objects.filter(active=True).all()
        al = [l.category for l in a]
        return al.unique()

    def __str__(self):
        return f'{self.title} by {self.creator}'

class ListingForm(forms.ModelForm):
        
    class Meta:
        model = Listing
        fields = ['title', 'desc', 'starting_bid', 'url', 'category']

    category = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )


class Bid(models.Model):
    article = models.ForeignKey(Listing, on_delete=CASCADE, related_name="all_bids")
    user = models.ForeignKey(User, on_delete=CASCADE)
    time = models.DateTimeField(auto_now=True)
    value = models.FloatField()

    def __str__(self):
        return f'{self.user.username} for {self.article.title} at {self.value}'

class BidForm(forms.ModelForm):
        
    class Meta:
        model = Bid
        fields = ['value']

class Comment(models.Model):
    article = models.ForeignKey(Listing, on_delete=CASCADE, related_name="all_comments")
    user = models.ForeignKey(User, on_delete=CASCADE)
    time = models.DateTimeField(auto_now=True)
    text = models.TextField()

    def __str__(self):
        return f'{self.user.username} for {self.article.title} at {self.value}'

class CommentForm(forms.ModelForm):
        
    class Meta:
        model = Comment
        fields = ['text']