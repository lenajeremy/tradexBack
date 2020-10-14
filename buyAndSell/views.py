import json
from django.shortcuts import render, reverse, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, Http404
from django.contrib.auth import login, logout
from .models import User, Post, Store, Product, Cart, Account, Like
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import os

# Create your views here.
@login_required
def index(request):
  return render(request, 'buyAndSell/index.html', context={'allPosts':Post.objects.all().order_by('-dateCreated'), 'len': len(request.user.getProducts())})

@csrf_exempt
def new_post(request):
  if request.method == 'POST':
    content = request.POST['content']
    image = request.FILES['imageUrl']
    id = request.POST['user_id']
    try:
      poster = get_object_or_404(User, id = id)
      post = Post.objects.create(content = content, poster = poster, image = image)
      post.save()
    except Http404:
      return JsonResponse({'message': 'You have to login', 'errors': ['You need to login to create posts'], 'status': 403})
    return JsonResponse({'message': 'Your post has been successfully uploaded', 'status': 200, 'post_details': post.serialize()})
  
  return JsonResponse({'message': "Post request required", 'status': 403})

@login_required
def new_product(request):
  if request.method == 'POST':
    if request.user.userType == 'buyer':
      return JsonResponse({'message': "Operation DisAllowed, User is not a seller", 'status': 403})
    else:  
      data_sent = json.loads(request.body)
      print(data_sent)
      name = data_sent['name']
      description = data_sent['description']
      price = data_sent['price']
      imageUrl = data_sent['imageUrl']
      store = request.user.getCart()
      Product.objects.create(name = name, description = description ,price = price, imageUrl = imageUrl, store = store)
  
      return JsonResponse({'message': 'Product has been added to your store', 'status': 200})
  return JsonResponse({'message': "Post Request Required", 'status': 403})

def get_user(request, user_id):
  try:
    return JsonResponse({'user': get_object_or_404(User, id = user_id).serialize(), 'status': 200})
  except Http404 as e:
    return JsonResponse({'message': e.__str__(), 'status': 404})

def get_all_users(request):
  return JsonResponse({'users': [user.serialize() for user in User.objects.exclude(username = 'admin')], 'status': 200})

def get_all_posts(request):
  print(int(request.GET.get('start')))
  print(int(request.GET.get('end')))
  start = Post.objects.count() - int(request.GET.get('start'))
  end = Post.objects.count() - int(request.GET.get('end'))
  valid_posts = []
  
  for post in Post.objects.order_by('-dateCreated'):
    if post.test(start, end):
      valid_posts.append(post)
      
  return JsonResponse({'posts': [post.serialize() for post in valid_posts]})

def get_post(request, post_id):
  try:
    return JsonResponse(get_object_or_404(Post, id = post_id).serialize())
  except Http404 as e:
    return JsonResponse({'message': e.__str__(), 'status': 404})


def get_store(request, owner_id):
  user = User.objects.get(id = owner_id)
  store = user.store.get()
  start = store.products.count() - int(request.GET.get('start'))
  end = store.products.count() - int(request.GET.get('end'))
  valid_posts = []
  
  for product in store.products.order_by('-dateCreated'):
    if product.test(start, end):
      valid_posts.append(product)
  
  return JsonResponse({'products': [product.serialize() for product in valid_posts], 'status': 200})

@csrf_exempt
def post_operation(request, operation, post_id):
  
  if request.method == "PUT":
    try:
      post = get_object_or_404(Post, id = post_id)
      if operation == 'like':
        information_sent = json.loads(request.body)
        liker = User.objects.get(id = information_sent['user_id'])
        if Like.objects.filter(post = post, liker = liker).count() == 0:
          Like.objects.create(post = post, liker = liker)
        else:
          like = Like.objects.get(post = post, liker = liker)
          like.delete()
          
        return JsonResponse({'message': 'Operation has been carried out', 'newLikeCount': Like.objects.filter(post = post).count(), 'status': 200})
      
      elif operation == 'remove':
        # do another thing
        post.delete()
        return JsonResponse({'message': "Post has been deleted", 'status': 200})
      
      elif operation == 'edit':
        newText = information_sent['new_text']
        post.content = newText
        post.save()
        
      else:
        return JsonResponse({'message': "Invalid operation", 'status': 403})
      
    except Http404:
      return JsonResponse({'message': 'Post with that id not found', 'status': 404})
    
    # if there is a get request
  return JsonResponse({'message': "POST or PUT request is required",'status': 403})


@csrf_exempt
def edit_user_profile(request, user_id, operation):
  user = User.objects.get(id = user_id)
  if request.method == 'POST' and operation == 'edit':
    bio = request.POST['bio']
    status = request.POST['status']
    userProfile = user.profile
    userProfile.bio=bio
    userProfile.status = status
    userProfile.save()
    try:
      new_profile_image = request.FILES['profile_image']
      user.profile_picture = new_profile_image
      user.save()
    except Exception as e:
      print(e)
    return JsonResponse({'message': "User profile has been updated", "status": 200})
  return JsonResponse({'message': "Post or PUT request required", "status": 400})