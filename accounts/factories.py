import factory
from django.contrib.auth.models import User
from .models import UserProfile

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('user_name')
    email = factory.Faker('email')

    @factory.post_generation
    def set_password(obj, create, extracted, **kwargs):
        # Set password (default or extracted)
        password = extracted or 'defaultpassword'
        obj.set_password(password)
        if create:
            obj.save()


# class UserProfileFactory(factory.django.DjangoModelFactory):
#     class Meta:
#         model = UserProfile

#     user = factory.SubFactory(UserFactory)
#     public_name = factory.Faker('name')
#     public_status = factory.Faker('text')
#     public_bio = factory.Faker('text')
