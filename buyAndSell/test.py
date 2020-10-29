from .models import Post
import random
import sys

limit = sys.argv[1]
allTexts = [post.content for post in Post.objects.all()]
allImages = [post.image for post in Post.objects.all()]

for i in range(0, limit):
  post = Post.objects.create(content = allTexts[random.randint(0, len(allTexts) - 1)], image = allImages[random.randint(0, len(allImages) - 1)], poster = User.objects.exclude(username = 'admin')[random.randint(0, len(User.objects.all() - 2))])
  post.save()

print('done')
  
