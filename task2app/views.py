from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import User, Organisation
from .utils import generateOrgID, parseData
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate




# Create your views here

# Index view
@api_view(['GET'])
@permission_classes([AllowAny])
def index(request):
    data = {
        'greetings': "Hello & welcome to my backend task 2 @HNG",
        'track': "backend track",
        'name': "Paulson Bosah",
        'slackId': "Paulson'sLegacy",
        'slackEmail': "paulsonbosah@gmail.com",
        'message': f"pytest filenames follow *_test.py, test_*.py formats hence the naming of my test file",
        'testFilePath': "task2pp/tests/auth_spec_test.py",
        'tokenLifetime': "30min"
    }
    return Response(data, status=status.HTTP_200_OK)


# Register view
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    try:
        # Parse and validate data using the serializer
        serializer = UserRegistrationSerializer(data=parseData(request.data))
        
        if serializer.is_valid():
            # Save user using the validated data
            user = serializer.save()
            # Refreshing user token
            refresh = RefreshToken.for_user(user)
            # Return successful response
            return Response({
                'status': 'success',
                'message': 'Registration successful',
                'data': {
                    'accessToken': str(refresh.access_token),
                    'user': UserSerializer(user).data
                }
            }, status=status.HTTP_201_CREATED)
        else:
            message = "Validation error"
            for key, value in serializer.errors.items():
                field = key
                if isinstance(value, list) and value:
                    message = value[0]
            response = {
                "errors": [
                    {
                    "field": field,
                    "message": message
                    },
                ]
            }
            print(response)
            # Return validation errors with 422 status code
            return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    except Exception:
        return Response({
            'status': 'Bad request',
            'message': 'Registration unsuccessful',
        }, status=status.HTTP_400_BAD_REQUEST)


# Login view
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    data = request.data
    user = authenticate(email=data['email'], password=data['password'])
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'status': 'success',
            'message': 'Login successful',
            'data': {
                'accessToken': str(refresh.access_token),
                'user': UserSerializer(user).data
            }
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'status': 'Bad request',
            'message': 'Authentication failed',
            'statusCode': 401
        }, status=status.HTTP_401_UNAUTHORIZED)
    

# User view
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user(request, userId):
    user = request.user

    if user:
        return Response({
            "status": "success",
            "message": "Auth user details",
            "data": UserSerializer(user).data
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'status': 'Bad request',
            'message': 'Authentication failed',
            'statusCode': 401
        }, status=status.HTTP_401_UNAUTHORIZED)


# Organisations view
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def organisations(request):
    user = request.user

    if request.method == 'GET': # If GET request then fetch auth user organisations
        # Get all organisations connected to the user
        organisations = user.organisations.all()
        serializer = OrganisationSerializer(organisations, many=True)

        if user:
            return Response({
                "status": "success",
                "message": "Auth user organisations",
                "data": {
                    "organisations": serializer.data
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'Bad request',
                'message': 'Authentication failed',
                'statusCode': 401
            }, status=status.HTTP_401_UNAUTHORIZED)
    else: # Else create new organistion for user 
        data =  parseData(request.body)
        organisation = Organisation.objects.create(
            orgId = generateOrgID(),
            name = data.get('name') or f"{user.firstName}'s Organisation",
            description = data.get('description', None)
        )
        organisation.users.add(user)
        return Response({
            "status": "success",
            "message": "Organisation created successfully",
            "data": OrganisationSerializer(organisation).data
        }, status=status.HTTP_201_CREATED)


# Single organisation view
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def organisation(request, orgId):
    try:
        organisation = Organisation.objects.get(orgId=orgId)

        if request.user in organisation.users.all():
            # Proceed with your logic if the user is part of the organisation
            return Response({
                "status": "success",
                "message": "Organisation detail",
                "data": OrganisationSerializer(organisation).data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "failed",
                "message": "Organisation not found",
            }, status=status.HTTP_404_NOT_FOUND)
    except Exception:
        return Response({
            "status": "failed",
            "message": "Organisation not found",
        }, status=status.HTTP_404_NOT_FOUND)


# Add User to Organisation view
@api_view(['POST'])
@permission_classes([AllowAny])
def addUserToOrg(request, orgId):
    try:
        data = parseData(request.body)
        user = User.objects.get(userId=data['userId'])
        organisation = Organisation.objects.get(orgId=orgId)
        organisation.users.add(user)

        return Response({
            "status": "success",
            "message": "User added to organisation successfully",
        }, status=status.HTTP_200_OK)
    except Exception:
        return Response({
            "status": "failed",
            "message": "User NOT added to organisation",
        }, status=status.HTTP_304_NOT_MODIFIED)