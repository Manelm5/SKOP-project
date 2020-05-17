import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
#from firebase_admin import auth

import pyrebase

cred = credentials.Certificate('skop-project-firebase-adminsdk-s2om4-43b7edc9ef.json')
firebase_admin.initialize_app(cred)

db = firestore.client()
city_ref = db.collection(u'cities').document()

city_ref.set({
    u'capital': True
}, merge=True)

config = {
  "apiKey": "AIzaSyD6hkzuOIHHfIhgbduQxQPnQVnq2v-39wM",
  "authDomain": "skop-project.firebaseapp.com",
  "databaseURL": "https://skop-project.firebaseio.com",
  "storageBucket": "skop-project.appspot.com",
  "serviceAccount": "skop-project-firebase-adminsdk-s2om4-43b7edc9ef.json",
  "messagingSenderId": "518648299242",
  "projectId": "skop-project"
}
pyrebase = pyrebase.initialize_app(config)
auth = pyrebase.auth()

storage = pyrebase.storage()

#auth.create_user_with_email_and_password(email="danielcruanyes@gmail.com", password="xxxxxx")

# Log the user in
user = auth.sign_in_with_email_and_password(email="danielcruanyes@gmail.com", password="xxxxxx")
#auth.send_email_verification(user['idToken'])

print (auth.get_account_info(user['idToken']))






# p1 = Person('example@example.com', +34689876876, 'secretPassword', 'John Doe',
# 'http://www.example.com/12345678/photo.png')
class Person:
    def __init__(self, email, phone_number, password, display_name, photo_url):
        self.email = email
        self.phone_number = phone_number
        self.password = password
        self.display_name = display_name
        self.photo_url = photo_url


def checkUserById(uid):
    user = auth.get_user(uid)
    print('Successfully fetched user data: {0}'.format(user.uid))


def checkUserByEmail(email):
    user = auth.get_user_by_email(email)
    print('Successfully fetched user data: {0}'.format(user.uid))


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


def updateUser(userCredentials):
    user = auth.update_user(email=userCredentials.email,
                            email_verified=userCredentials.email_verified,
                            phone_number=userCredentials.phone_number,
                            password=userCredentials.password,
                            display_name=userCredentials.display_name,
                            photo_url=userCredentials.photo_url,
                            disabled=userCredentials.disabled)

    print('Successfully updated the new user: {0}'.format(user.uid))


def deleteUserById(uid):
    auth.delete_user(uid)
    print('Successfully deleted user')


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


