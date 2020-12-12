import json
from django.shortcuts import render, reverse, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, Http404, HttpResponse
from django.contrib.auth import login, logout
from .models import User, Post, Store, Product, Cart, Account, Like, Order, Notification, Conversation, Message
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import os

# Create your views here.
class Console:
  def log(self, stuff):
    print(stuff)
console = Console()

@login_required
def index(request):
  return render(request, 'buyAndSell/index.html', context={'allPosts':Post.objects.all().order_by('-dateCreated'), 'len': len(request.user.getProducts())})

@csrf_exempt
def new_post(request):
  if request.method == 'POST':
    content = request.POST['content']
    try:
      image = request.FILES['imageUrl']
    except Exception as e:
      image = None
    id = request.POST['user_id']
    try:
      poster = get_object_or_404(User, id = id)
      if image:
        post = Post.objects.create(content = content, poster = poster, image = image)
      else:
        post = Post.objects.create(content = content, poster = poster)
      post.save()
      return JsonResponse({'message': 'Your post has been successfully uploaded', 'status': 200, 'post_details': post.serialize(poster)})
    except Http404:
      return JsonResponse({'message': 'You have to login', 'errors': ['You need to login to create posts'], 'status': 403})
  
  return JsonResponse({'message': "Post request required", 'status': 403})

@csrf_exempt 
def new_product(request):
  if request.method == 'POST':
    user = User.objects.get(id = request.POST['user_id'])
    if user.userType == 'buyer':
      return JsonResponse({'message': "Operation DisAllowed, User is not a seller", 'status': 403})
    else:  
      name = request.POST['name']
      description = request.POST['description']
      price = float(request.POST['price'])
      imageUrl = request.FILES['imageUrl']
      availableStock = request.POST['availableQuantity']
      product = Product.objects.create(name = name, description = description ,price = price, initialStock = availableStock, image = imageUrl, store = user.store, availableStock = availableStock)
      return JsonResponse({'message': 'Product has been added to your store', 'status': 200, 'details': product.serialize()})
  return JsonResponse({'message': "Post Request Required", 'status': 403})

def get_user(request, user_id):
  try:
    isSelf = request.GET.get('self')
    if isSelf == 'false':
      isSelf = False
    else:
      isSelf = True
    user = get_object_or_404(User, id = user_id)
    details = user.serialize(isSelf)
    if isSelf:
      details['notifications'] = [notification.serialize() for notification in Notification.objects.order_by('-dateCreated').filter(owner = user)]
    return JsonResponse({'user': details, 'status': 200})
  except Http404 as e:
    return JsonResponse({'message': e.__str__(), 'status': 404})


def get_all_posts(request):
  user = None
  try:
    user = User.objects.get(id = request.GET.get('user'))
  except User.DoesNotExist:
    pass
  print(request.GET.get('start'))
  start = int(request.GET.get('start')) - 1
  end = int(request.GET.get('end'))
  valid_posts = list(Post.objects.order_by('-dateCreated')[start:end])
  print(valid_posts)
  return JsonResponse({'posts': [post.serialize(user) for post in valid_posts], 'status': 200})

def get_post(request, post_id):
  try:
    return JsonResponse(get_object_or_404(Post, id = post_id).serialize())
  except Http404 as e:
    return JsonResponse({'message': e.__str__(), 'status': 404})


def get_store(request):
  user = User.objects.get(username = request.GET.get('owner_username'))
  return JsonResponse({'products': [product.serialize() for product in user.store.products.order_by('-dateCreated')], 'status': 200, 'owner': user.first_name})

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
          if post.poster != liker:
            Notification.objects.create(owner = post.poster, related_user = liker, text = f"{liker.username} liked your post...", notification_type = 'like_post')
          liked = True
        else:
          like = Like.objects.get(post = post, liker = liker)
          liked = False
          like.delete()
          
        return JsonResponse({'message': 'Operation has been carried out', 'newLikeCount': Like.objects.filter(post = post).count(), 'status': 200, 'liked': liked})
      
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
  edited = None
  if request.method == 'POST' and operation == 'edit':
    field = request.POST['field']
    if field == 'profile_image':
      user.profile_picture = request.FILES['profile_image']
      user.save()
      edited = user.profile_picture.url
    elif field == 'cover_image':
      user.cover_picture = request.FILES['cover_image']
      user.save()
      edited = user.cover_picture.url
    else:      
      userProfile = user.profile
      userProfile.bio=request.POST['status']
      userProfile.status = request.POST['bio']
      edited = {'bio': request.POST['bio'], 'status': request.POST['status']}
      userProfile.save()
    print(edited)
    return JsonResponse({'message': "User profile has been updated", 'edited': edited,  "status": 200})
  return JsonResponse({'message': "Post or PUT request required", "status": 400})

@csrf_exempt
def remove_product(request, product_id):
  user = User.objects.get(id = int(request.GET.get('user_id')))
  if user.userType == 'seller':
    try:
      product = get_object_or_404(Product, id = product_id)
      product.delete()
      return JsonResponse({'message': "Product has been removed from store", 'status': 200})
    except Http404:
      return JsonResponse({'message': "Product with that id not found", 'status': 404})
  return JsonResponse({'message': 'Forbidden operation', 'status': 400})

@csrf_exempt
def add_to_cart(request):
  try:
    cart = User.objects.get(id = json.loads(request.body)['user_id']).cart
    product = Product.objects.get(id = json.loads(request.body)['product_id'])
    operation = json.loads(request.body)['operation']
    quantity = json.loads(request.body)['quantity']
    if operation == 'add_to_cart' and not product in [order.product for order in cart.orders.all()]:
      Notification.objects.create(text = f"{cart.user.username} added your product {product.name} to cart", owner = product.store.user, related_user = cart.user, notification_type = 'from_store_to_cart')
      order = Order.objects.create(product = product, number = quantity, cart = cart);product.availableStock-=quantity
    elif operation == 'remove_from_cart':
      Notification.objects.create(text = f"{cart.user.username} has removed your product {product.name} from his cart. Message him to know why.", notification_type = 'to_store_from_cart', owner = product.store.user, related_user = cart.user)
      order = cart.orders.get(product = product)
      product.availableStock+=order.number;order.delete()
    elif operation == 'increase' and product.availableStock - quantity >= 0:
      order = cart.orders.get(product = product)
      order.number+=quantity;product.availableStock-=quantity;order.save()
    elif operation == 'decrease' and product.availableStock + quantity <= product.initialStock:
      order = cart.orders.get(product = product)
      if order.number - quantity <= 0:
        Notification.objects.create(text = f"{cart.user.username} has removed your product {product.name} from his cart. Message him to know why.", notification_type = 'to_store_from_cart', owner = product.store.user, related_user = cart.user)
        details = order.serialize();product.availableStock+=quantity;order.delete()
        return JsonResponse({'message': f"Product has been deleted", 'status': 200, 'details': details})
      else:
        order.number-=quantity;product.availableStock+=quantity;order.save()

    product.save();cart.save()
    return JsonResponse({'message': f"Product has been {operation}", 'status': 200, 'details': cart.orders.get(product = product).serialize()})
  except User.DoesNotExist:
    return JsonResponse({'message': "cart with that credential does not exist", 'status': 404})
  except Product.DoesNotExist:
    return JsonResponse({'message': "product with that id does not exist", 'status': 404})
  except Order.DoesNotExist:
    return JsonResponse({'message': 'that order does not exist', 'status': 404})

def get_product(request):
  try:
    product = Product.objects.get(id = request.GET.get('id'))
    return JsonResponse({'details': product.serialize(), 'status': 200})
  except Product.DoesNotExist:
    return JsonResponse({'details': None, 'status': 404, 'message': "Product was not found"})
  
@csrf_exempt
def messages_view(request):
  operation = request.GET.get('operation')
  user_id = int(request.GET.get('ref_id'))
  chat_id = int(request.GET.get('chat_id'))
  if request.method == 'GET':
    if operation == 'get_last_messages_for_each_messaged':
      last_messages = [message.serialize() for message in [chat.messages_sent.last() for chat in Conversation.objects.filter(chatter = User.objects.get(id = user_id)).order_by('-last_modified')]]
      return JsonResponse({'messages': last_messages, 'status': 200})
    elif operation == 'get_chat_messages':
      step = int(request.GET.get('step'))
      conversation = Conversation.objects.get(id = chat_id)
      messages = list(conversation.messages.order_by('-date_sent')[step * 15 : (step + 1) * 15])
      print(messages)
      messages.reverse()
      if User.objects.get(id = user_id) in conversation.users.all():
        return JsonResponse({'messages': [message.serialize() for message in messages], 'status': 200, 'users': [{'firstName': user.first_name, 'lastName': user.last_name, 'picture': user.profile_picture.url, 'id': user.id} for user in conversation.users.exclude(id = user_id)]})
      else:
        return JsonResponse({'message': "You are not permitted to view this information", 'status': 403})
  else:
    if operation == 'send_message':
      undecided = request.GET.get('undecided');
      message = None
      if undecided == 'false':
        chatter_with = Conversation.objects.get(id = chat_id).users.exclude(id = user_id).get()
      else:
        # the id of the user to chat with is given as the chat id if the message is from the profile
        chatter_with = User.objects.get(id = chat_id)
      chatter = User.objects.get(id = user_id)
      content = request.POST['content']

      try:
        conversation = Conversation.objects.filter(users = chatter).filter(users = chatter_with).get()
        message = Message.objects.create(conversation = conversation, content = content, sender = chatter, receiver = chatter_with)
        message.conversation.save()
      except Conversation.DoesNotExist:
        conversation = Conversation.objects.create()
        [conversation.users.add(user) for user in [chatter, chatter_with]]
        message = Message.objects.create(conversation = conversation, content = content, sender = chatter, receiver = chatter_with)
      return JsonResponse({'status': 200, 'message': message.serialize()})
    return JsonResponse({'message': 'Invalid Operation', 'status': 403})
        
      
                       

def checkout(request):
  response = HttpResponse('this is the http response')
  print(request.headers)
  response.set_cookie(key = 'csrftoken', value = 'cool stuff')
  return response