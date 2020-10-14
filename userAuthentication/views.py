from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password, ValidationError
from django.db import IntegrityError
from .models import User
from django.contrib.auth.hashers import PBKDF2SHA1PasswordHasher
from buyAndSell.models import Store, Account, Cart
from .models import User_profile
from django.views.decorators.csrf import csrf_exempt
import json


# Create your views here.
hasher = PBKDF2SHA1PasswordHasher()
@csrf_exempt
def register(request):
  if request.method == "POST":
    data_sent = json.loads(request.body)
    username = data_sent['username']
    password = data_sent['password']
    first_name = data_sent['first_name']
    last_name = data_sent['last_name']
    conf_password = data_sent['conf_password']
    user_type = data_sent['user_type']
    email = data_sent['email']
    paypayEmail = data_sent['paypalEmail']
    print(password)
    
    if password != '' and password == conf_password:
      hashedPassword = hasher.encode(password=password, salt=hasher.salt())
      # Create a testuser and save the user in memory
      testUser = User(username = username, password = hashedPassword, first_name= first_name, last_name = last_name, userType=user_type, email = email, paypal_email_address = paypayEmail)
      try:
        validate_password(password, testUser)
        # if the password validation is successful, save the user to the database and then redirect to the index route
        testUser.save()
        
        # create a store for the user if the user is a seller
        if testUser.userType == 'seller':
          Store.objects.create(user = testUser)
        else:
          Cart.objects.create(user = testUser)
        
        User_profile.objects.create(user = testUser)
        Account.objects.create(owner = testUser)
        login(request, testUser)
        
        return JsonResponse({'message': 'You have successfully registered and is logged in already', 'status': 200, 'id': testUser.id})
      
      except ValidationError as e:
        return JsonResponse({'message': 'There is an error in the registration process', 'status': 403, 'errors': e.messages})
      except IntegrityError as e:
        return JsonResponse({'message': 'A user with that username already exists', 'errors': ["A user with that username already exists"], 'status': 403})
    else:
        return JsonResponse({'message': 'Passwords do not match', 'errors': ["Passwords do not match"], 'status': 403})
      
      
  #send an error message is the request is not a post request
  return JsonResponse({'message': "Post request required", 'status': 403})


@csrf_exempt
def login_view(request):
  if request.method == 'POST':
    data_sent = json.loads(request.body)
    username = data_sent['username']
    password = data_sent['password']
    
    user = authenticate(username = username, password = password)
    if user is not None:
      login(request, user)
      return JsonResponse({'message': "You have successfully logged in", 'status': 200, 'id': user.id})
    else:
      return JsonResponse({'message': 'Invalid Login Credentials', "status": 403})
  
  return JsonResponse({'message': "Post request required", 'status': 403})

    
def logout_view(request):
  logout(request)
  return JsonResponse({'message':'You have been logged out', 'status': 200})