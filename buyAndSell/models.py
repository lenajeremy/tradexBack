from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from userAuthentication.models import User, User_profile
import random, json

# Create your models here.
class Store(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name = 'store')
  
  def serialize(self):
    data_to_return = {'id': self.id, 'owner': self.user.first_name, 'user_id': self.user.id, 'products': [product.serialize() for product in self.products.order_by('-dateCreated')]}
    return data_to_return
  
  def __str__(self):
    return f"{self.user} {len(self.products.all())}"


class Product(models.Model):
  name = models.CharField(max_length=100)
  description = models.CharField(max_length=200)
  price = models.IntegerField()
  image = models.ImageField(upload_to = 'product_images')
  watchers = models.ManyToManyField(User, related_name='watched_products', blank = True)
  store = models.ForeignKey(Store, on_delete = models.CASCADE, related_name = 'products')
  isAvailable = models.BooleanField(default = True)
  availableStock = models.IntegerField(default = 1)
  initialStock = models.IntegerField(default = 1)
  isDelivered = models.BooleanField(default = False)
  dateCreated = models.DateTimeField(auto_now_add=True)
  
  def test(self, start, end):
    index = list(Product.objects.all()).index(self)
    if index <= start and index >= end:
      return self
  
  def serialize(self):
    data_to_return = {'id': self.id, 'name': self.name, 'description': self.description, 'price': self.price, 'initialStock': self.initialStock, 'currentStock': self.availableStock, 'image': self.image.url, 'isAvailable': self.isAvailable, 'dateCreated': self.dateCreated.timestamp(), 'owner': {'id': self.store.user.id, 'username': self.store.user.username}}
    return data_to_return
  
  def __str__(self):
      return f"{self.name} {self.price}"

class Cart(models.Model):
  user = models.OneToOneField(User, on_delete = models.CASCADE, related_name = 'cart')
  # products = models.ManyToManyField(Product, related_name='cart')
  
  def serialize(self):
    data_to_return = {'id': self.id, 'user': {'id': self.user.id, 'username': self.user.username}, 'products': [order.serialize() for order in self.orders.order_by('-dateCreated')]}
    return data_to_return
  
  def __str__(self):
    return f"{self.user} {len(self.orders.all())}"
  
  
class Post(models.Model):
  content = models.TextField()
  poster = models.ForeignKey(User, on_delete= models.DO_NOTHING, related_name='posts')
  image = models.ImageField(upload_to = 'post_images')
  dateCreated = models.DateTimeField(auto_now_add = True)
  
  def serialize(self, user):
    data_to_return = {'id': self.id, "content": self.content,'posterId': self.poster.id, "poster": self.poster.username, 'image': self.image.url, 'dateCreated': self.dateCreated.timestamp(), 'number_of_likes': len(self.likes.all()), 'posterPicture': self.poster.profile_picture.url}
    data_to_return['isLiked'] = user in [like.liker for like in self.likes.all()]
    return data_to_return
  
  def test(self, start, end):
    index = list(Post.objects.all()).index(self)
    if index <= start and index >= end:
      return self
    
  def __str__(self):
      return f"{self.content[:25]}..."
  
class Account(models.Model):
  owner = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'account')
  number = models.IntegerField(default = random.randint(9999999, 99999999), unique = True)
  amount = models.IntegerField(default = 0)
  
  def serialize(self):
    data_to_return = {'id': self.id, "owner": self.owner.username, 'number': self.number, 'accountName': f"{self.owner.first_name} {self.owner.last_name}", 'balance': f"${self.amount}"}
    return data_to_return
    
  def __str__(self):
    return f"NAME: {self.owner.first_name} {self.owner.last_name} NUMBER: {str(self.number)}"
  
class Like(models.Model):
  post = models.ForeignKey(Post, on_delete = models.CASCADE, related_name='likes')
  liker = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'likes')
  
  def __str__(self):
    return f"{self.liker} liked {self.post}"
  
  def serialize(self):
    data_to_return = {'id': self.id, 'post_id': self.post.id, 'liker_id': self.liker.id, 'post_content_shortened': self.post.__str__()}
    return data_to_return

class Comment(models.Model):
  text = models.CharField(max_length = 300)
  post = models.ForeignKey(Post, on_delete = models.CASCADE, related_name = 'comments')
  commenter = models.ForeignKey(User, on_delete = models.DO_NOTHING, related_name = 'comments')
  
  def __str__(self):
    return f"{self.text} {self.post}"
  
  def serialize(self):
    data_to_return = {'id': self.id, 'post_id': self.post.id, 'commenter': self.commenter.__str__(), 'post_content_shortened': self.post.__str__()}
    return data_to_return

class Order(models.Model):
  product = models.ForeignKey(Product, on_delete = models.CASCADE, related_name = 'orders')
  cart = models.ForeignKey(Cart, on_delete = models.CASCADE, related_name = 'orders')
  number = models.IntegerField(default = 1)
  dateCreated = models.DateTimeField(auto_now = True)

  def __str__(self):
    return f"{self.product.name} {self.number}"
  
  def serialize(self):
    useless_keys = ['initialStock', 'currentStock', 'isAvailable']
    data_to_return = {}
    for key in self.product.serialize().keys():
      if key not in useless_keys:
        data_to_return[key] = self.product.serialize()[key]
    data_to_return['currentStock'] = self.number
    return data_to_return


class Notification(models.Model):
  notification_type = (
    ('new_post', 'NEW_POST'),
    ('update_profile', 'UPDATE_PROFILE'),
    ('user_update_profile', 'USER_UPDATE_PROFILE'),
    ('view_store', 'VIEW_STORE'),
    ('from_store_to_cart', 'PLUS_STC'),
    ('to_store_from_cart', "MINUS_STC"),
    ('followed', 'FOLLOW'),
    ('new_product', 'NEW_PRODUCT')
  )
  text = models.CharField(max_length = 200)
  owner = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'notifications')
  related_user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'notification_related')
  notification_type = models.CharField(choices = notification_type, default = 'admin', max_length = 20)
  dateCreated = models.DateTimeField(auto_now = True)

  def __str__(self):
    return self.text

  def serialize(self):
    data_to_return = {'text': self.text, 'owner': self.owner.username, 'related_user': self.related_user, 'notification_type': self.notification_type, 'dateCreated': self.dateCreated}