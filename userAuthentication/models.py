from django.db import models
from django.contrib.auth.models import AbstractUser
from django.http import HttpRequest
import json

# Create your models here.
class User(AbstractUser):
  USERTYPE_CHOICES = (
    ('buyer', 'Buyer'),
    ('seller', 'Seller')
  )
  userType = models.CharField(choices=USERTYPE_CHOICES, default='buyer', max_length=9)
  profile_picture = models.TextField(default = "https://img.icons8.com/bubbles/2x/user-male.png")
  cover_picture = models.TextField(default  = "https://graphicsfamily.com/wp-content/uploads/2020/10/Abstract-Facebook-Cover-Design-Presentation-scaled.jpg")
  paypal_email_address = models.EmailField()
  
  def getProducts(self):
    if self.userType == 'buyer':
      return self.cart.products.all()
    return self.store.products.all()

  def serialize(self, isSelf:bool, user_id:int):
    data_to_return = None
    if isSelf:
      data_to_return = {'id': self.id, 'userName': self.username, 'firstName': self.first_name, 'lastName': self.last_name, 'profilePicture': self.profile_picture, 'postsMade': [post.serialize(self) for post in self.posts.order_by('-dateCreated')], 'userType': self.userType, 'accountDetails': self.account.serialize(), 'emailAddress': self.email, 'paypalEmail': self.paypal_email_address, 'profile': self.profile.serialize(), 'coverPicture': self.cover_picture, 'latestMessages': [conversation.messages.last().serialize(user_id = user_id) for conversation in self.conversation.order_by('-last_modified')]}
      if self.userType == 'buyer':
        data_to_return['cart'] = self.cart.serialize()
      else:
        data_to_return['products'] = self.store.serialize()
    else:
      data_to_return = {'id': self.id, 'userName': self.username,'firstName': self.first_name, 'lastName': self.last_name, 'profilePicture': self.profile_picture, 'postsMade': [post.serialize(self) for post in self.posts.order_by('-dateCreated')], 'userType': self.userType, 'profile': self.profile.serialize(), 'coverPicture': self.cover_picture}
      
    return data_to_return
  
  def __str__(self):
      return self.username
    

class User_profile(models.Model):
  user = models.OneToOneField(User, on_delete = models.CASCADE, related_name = 'profile')
  bio = models.CharField(max_length = 200, default='A short introduction about yourself')
  status = models.CharField(max_length = 60, default = 'Currently Available')
  
  def __str__(self):
    return f"{self.user} {self.status}"
  
  def serialize(self):
    return {'bio': self.bio,'status': self.status}