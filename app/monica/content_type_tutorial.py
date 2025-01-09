restaurant = Restaurant.objects.first()

comment = Comment.objects.create(text='This is a comment', content_object=restaurant) 15:28


class Comment(models.Model):
    text = models.TestField()
    content_type = ForeignKey(ContentType, on_delete=models.CASCADE)

 
from swn.models import User
user = User.objects.get(pk=9)

site.user = user
site.name = "test_site 2"
site.latitude = 50.1
site.longitude = 12.1
site.altitude = 50
site.slope = 0
site.n_deposition = 11
site.soil_profile = soil
site.save()

