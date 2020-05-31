import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from flask import session
from urllib import  parse
import re
#from firebase_admin import auth
import pyrebase
import json

# Inicializate firebase conecction with .json credentials

cred = credentials.Certificate('skop-project-firebase-adminsdk-s2om4-43b7edc9ef.json')
firebase_admin.initialize_app(cred)

# Get Firestore database reference
db = firestore.client()

config = {
  "apiKey": "SECRET",
  "authDomain": "skop-project.firebaseapp.com",
  "databaseURL": "https://skop-project.firebaseio.com",
  "storageBucket": "skop-project.appspot.com",
  "serviceAccount": "skop-project-firebase-adminsdk-s2om4-43b7edc9ef.json",
  "messagingSenderId": "518648299242",
  "projectId": "skop-project"
}

# Make initialize Auth object and initialize the Storage object
auth_pyrebase = pyrebase.initialize_app(config)
auth = auth_pyrebase.auth()

storage = auth_pyrebase.storage()


# Class for handle users
class Person:
    def __init__(self, email, phone_number, password, display_name, photo_url):
        self.email = email
        self.phone_number = phone_number
        self.password = password
        self.display_name = display_name
        self.photo_url = photo_url

# Print user uid by uid
def checkUserById(uid):
    user = auth.get_user(uid)
    print('Successfully fetched user data: {0}'.format(user.uid))


# Print user uid by email
def checkUserByEmail(email):
    user = auth.get_user_by_email(email)
    print('Successfully fetched user data: {0}'.format(user.uid))


# Create a new user in Firebase Auth with user credentials.
def createUser(userCredentials):
    user = auth.create_user(
        email=userCredentials.email,
        email_verified=userCredentials.email_verified,
        phone_number=userCredentials.phone_number,
        password=userCredentials.password,
        display_name=userCredentials.display_name,
        photo_url=userCredentials.photo_url,
        disabled=userCredentials.disabled)

    print('Successfully created new user: {0}'.format(user.uid))


# Update user data in Firebase Auth.
def updateUser(userCredentials):
    user = auth.update_user(email=userCredentials.email,
                            email_verified=userCredentials.email_verified,
                            phone_number=userCredentials.phone_number,
                            password=userCredentials.password,
                            display_name=userCredentials.display_name,
                            photo_url=userCredentials.photo_url,
                            disabled=userCredentials.disabled)

    print('Successfully updated the new user: {0}'.format(user.uid))


# Delete a user from Firebase Auth.
def deleteUserById(uid):
    auth.delete_user(uid)
    print('Successfully deleted user')


# Prints all user in Firebase Auth.
def printAllUsers():
    # Start listing users from the beginning, 1000 at a time.
    page = auth.list_users()
    while page:
        for user in page.users:
            print('User: ' + user.uid)
        # Get next batch of users.
        page = page.get_next_page()

    # Iterate through all users. This will still retrieve users in batches,
    # buffering no more than 1000 users in memory at a time.
    for user in auth.list_users().iterate_all():
        print('User: ' + user.uid)


# Register user. Create a Firebase Auth user with email and password and
# saves a document with the firstname and lastname in the Users collection with
# the userId as document name.
def registerUser(email, password, firstname, lastname):

    response = []
    try:
        user = auth.create_user_with_email_and_password(email, password)
        data = {
            u'firstname': firstname,
            u'lastname': lastname,
        }
        db.collection(u'users').document(user['localId']).set(data)

        data = {
            u'links': []
        }
        db.collection(u'videos').document(user['localId']).set(data)

        text = "Successfully created user " + str(email) + " redirectered to login page."
        response.append(True)
        response.append(text)
    except Exception as error:
        response.append(False)
        response.append(error)
    return response


# Login user. Validate the user email and password with Firebase Auth
# and saves the returned userId in the session.

# If the validation goes wrong, print the error.
def login_user(email, password):
    session["userId"] = None
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        user_id = user['localId']
        session["userId"] = user_id
        response = "Successfully user login: " + str(user['localId'])
    except Exception as e:
        print(e)
        if hasattr(e, 'message'):
            response = e.message
        else:
            response = "Unknown error."
    print(response)
    return session["userId"]

# Logout user. Removes userId from the current session.
def logout_user():
    user_id = session["userId"]
    session["userId"] = None
    response = "User " + str(user_id) + " log out successfully"
    print(response)
    return response

# Get all video documents with a specific category.
# Return an array of videos.
def get_videos_by_category(category):
    existing_videos = db.collection(u'videos').where(u'category', u'==', category).stream()
    videos = []
    for post in existing_videos:
        videos.append(post.to_dict())
    return videos

# Get all video documents with a specific userId.
# Return an array of videos.
def get_videos_by_userId(userId):

    existing_videos = db.collection(u'videos').where(u'userId', u'==', userId).stream()
    videos = []
    for post in existing_videos:
        videos.append(post.to_dict())
    return videos

# Delete a video from Storage and the video document of Firestore
def deleteVideoFromUrl(link):
    path = urlToBucketPath(link)[1]
    storage.child(path).delete(path)
    print("deleting db")
    a = db.collection(u'videos').where(u'link', u'==', link).stream()
    for docs in a:
        docs.reference.delete()

    print("db delete")

def urlToBucketPath (url):
    """Convert a Firebase HTTP URL to a (bucket, path) tuple,
    Firebase's `refFromURL`.
    """
    bucket_domain = '([A-Za-z0-9.\\-]+)'
    is_http = not url.startswith('gs://')

    if is_http:
        path = '(/([^?#]*).*)?$'
        version =  'v[A-Za-z0-9_]+'
        rex = (
            '^https?://firebasestorage\\.googleapis\\.com/' +
            version + '/b/' + bucket_domain + '/o' + path)
    else:
        gs_path = '(/(.*))?$'
        rex = '^gs://' + bucket_domain + gs_path

    matches = re.match(rex, url, re.I)
    if not matches:
        raise Exception('URL does not match a bucket: %s' % url)

    bucket, _, path = matches.groups()

    if is_http:
        path = parse.unquote(path)

    return (bucket, path)
