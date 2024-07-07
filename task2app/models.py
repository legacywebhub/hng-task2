from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from .utils import generateUserID, generateOrgID



# Create your models here.

# Manager class for custom user
class UserManager(BaseUserManager):
    # Determines how to create our user model and validations
    def create_user(self, firstName, lastName, email, password=None):
        # Use this check for as many field you want
        if not email:
            raise ValueError("email is required")
        if not firstName:
            raise ValueError("provide a first name")
        if not lastName:
            raise ValueError("provide a last name")


        user = self.model(
            # normalize_email ensures our email is properly formatted
            email = self.normalize_email(email),
            firstName = firstName,
            lastName = lastName,
        )
        # Setting password for user
        user.set_password(password)
        # Saving user to database
        user.save(using=self._db)
        # Return user after saving
        return user

    # Determines how to create superuser
    def create_superuser(self, email, firstName, lastName, password=None):
        user = self.create_user(
            email = self.normalize_email(email),
            firstName = firstName,
            lastName = lastName,
            password = password
        )
        # Granting permissions to the super user
        user.is_staff = True
        user.is_superuser = True
        # Saving user to database
        user.save(using=self._db)
        # Return user after saving
        return user

    '''
    Make sure to set this manager as the manager in your custom model
    objects = MyUserManager()
    '''



# Custom user model class
class User(AbstractBaseUser, PermissionsMixin):
    userId = models.CharField(max_length=100, unique=True)
    firstName = models.CharField(verbose_name="first name", max_length=60, null=False, blank=False)
    lastName = models.CharField(verbose_name="last name", max_length=60, null=False, blank=False)
    email = models.EmailField(verbose_name="email address", max_length=60, unique=True, null=False, blank=False)
    phone = models.CharField(verbose_name="phone number", max_length=15, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    @property
    def fullName(self):
        return f'{self.firstName} {self.lastName}'

    # Default setting to determine what field to show on our database
    def __str__(self):
        return self.fullName

    # Setting to determing what field to use as login parameter
    USERNAME_FIELD = "email"

    # Setting to set required fields
    REQUIRED_FIELDS = ["firstName", "lastName"]

    # Setting a manager for this custom user model
    objects = UserManager()

    # Determines if signup user has permissions
    def has_perm(self, perm, obj=None):
        return True

    # Determines if the signed up user will have acccess to other models
    # In our app or project
    def has_module_perms(self, app_label):
        return True
    
    # Triggers during saving
    def save(self, *args, **kwargs):
        # If userId not set before saving
        if not self.userId:
            self.userId = generateUserID()
        super().save(*args, **kwargs) # Save user first to generate ID if necessary
        
        # Creating an organisation for created user
        organisation, created = Organisation.objects.get_or_create(
            orgId=generateOrgID(),
            name=f"{self.firstName}'s Organisation"
        )
        organisation.users.add(self)

        

    '''
    Make sure to set this custom model as our user model in settings.py
    AUTH_USER_MODEL = "App.CustomUserModel"
    Make sure to delete previous migration files incase of errors
    Then make migrations
    '''



class Organisation(models.Model):
    orgId = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    users = models.ManyToManyField(User, related_name='organisations')
    
    def __str__(self):
        return self.name
