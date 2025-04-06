from flask import Blueprint, jsonify, request, send_file
from io import BytesIO
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from config import db
# from Models.User_moel import User, Complaints, Images  # Corrected import statement
from datetime import timedelta
from email_verification.send_email import send_email
import bcrypt
import re
from firebase_admin.auth import InvalidIdTokenError, EmailAlreadyExistsError
from firebase_admin import auth, firestore
from config import firebaseDataStore, firebaseAuth
from Azure.azureBlobStorage import uploadImagesToContainer, DeleteImagesFromContainer, createContainer
from Routes.Firebase_register import google_auth

from GCP.CloudStorageBucket import upload_images_to_bucket, delete_image_from_bucket, create_bucket 

from Azure.AIModel import AIMLForComplaints

user_route = Blueprint('user_route', __name__)

@user_route.route("/login", methods=["POST"])
def login():
    user_email = request.json.get("user_email")
    user_password = request.json.get("user_password")
    # print(user_email, user_password)
    if not user_email or not user_password:
        return jsonify({'message': 'please fill all the fields'}), 401

    try:
        checkFirebaseUser = firebaseAuth.sign_in_with_email_and_password(user_email, user_password)
        # print(checkFirebaseUser)

        # Fetch the user data from Firebase
        firebase_user = auth.get_user(checkFirebaseUser['localId'])

        # Check if the user's email is verified
        if not firebase_user.email_verified:
            # Send verification email
            email_verification_link = auth.generate_email_verification_link(user_email)
            send_email(firebase_user.display_name or "User", user_email, email_verification_link)
            return jsonify({'message': 'Email not verified. Verification email sent.'}), 400

        access_token = create_access_token(identity=checkFirebaseUser['localId'], expires_delta=timedelta(days=7), additional_claims={"token_type": "access_token"})
        refresh_token = create_refresh_token(identity=checkFirebaseUser['localId'], expires_delta=timedelta(days=14), additional_claims={"token_type": "refresh_token"})
        return jsonify({'message': 'login success', 'access_token': access_token, 'refresh_token': refresh_token}), 200

    except InvalidIdTokenError:
        return jsonify({'message': 'invalid credentials'}), 401
    except Exception as e:
        # print(e)
        return jsonify({'message': str(e)}), 401

@user_route.route("/google-auth", methods=["POST"])
def google_auth_route():
    try:
        # print("google auth")
        get_data = request.json
        # print(get_data)
        email = get_data.get("user_email")
        display_name = get_data.get("user_name")
        photo_url = get_data.get("photoURL")
        uId = get_data.get("user_firebase_uid")
        last_login_at = get_data.get("last_login")
        last_sign_in_at = get_data.get("last_SigIn_Time")
        creation_time = get_data.get("created_at")
        email_verified = get_data.get("email_verified")
        user_password = get_data.get("user_password")
        isLogin = get_data.get("isLogin")
        isUId = get_data.get("isUId")

        # print("email", email, "display_name", display_name, "photo_url", photo_url, "uId", uId, "last_login_at", last_login_at, "last_sign_in_at", last_sign_in_at, "creation_time", creation_time, "email_verified", email_verified)
        authStatus = google_auth(email, display_name, photo_url, uId, last_login_at, last_sign_in_at, creation_time, email_verified, isLogin, isUId)
        # print(authStatus)
        # print(isLogin, isUId)
        return authStatus

    except Exception as e:
        # print(e)
        return jsonify({'message': str(e)}), 401

@user_route.route("/register", methods=["POST"])
def register():
    get_data = request.json
    user_email = get_data.get("user_email")
    user_name = get_data.get("user_name")
    user_password = get_data.get("user_password")
    user_password_retype = get_data.get("user_password_retype")
    # print(user_email, user_password)
    if not user_email or not user_password or not user_name:
        # print('please fill all the fields')
        return jsonify({'message': 'please fill all the fields'}), 401
    if user_password != user_password_retype:
        # print('passwords are not matching!')
        return jsonify({'message': 'passwords are not matching!'}), 401

    if not re.match(r"[^@]+@[^@]+\.[^@]+", user_email):
        return jsonify({'message': 'invalid email'}), 401
    if len(user_password) < 6:
        return jsonify({'message': 'password must be 6 characters or more'}), 401
    if len(user_name) < 6:
        return jsonify({'message': 'username must be 6 characters or more'}), 401

    # Initialize firebase new user
    try:
        newFireBaseUser = auth.create_user(email=user_email, password=user_password, display_name=user_name)

        # Add user to firestore
        # print(newFireBaseUser)
   
        # newPSQLUser = User(user_email=user_email, user_name=user_name, user_email_verified=False, user_phone_verified=False, firebase_uid=newFireBaseUser.uid, user_id=newFireBaseUser.uid)
        # print(newPSQLUser)

        # db.session.add(newPSQLUser)
        # db.session.commit()
        # print(newPSQLUser.user_id)
        newUser = firebaseDataStore.collection('users').document(newFireBaseUser.uid).set(
            {"user_email": newFireBaseUser.email, "user_firebase_auth_id": newFireBaseUser.uid}
        )
        emailVerificationLink = auth.generate_email_verification_link(newFireBaseUser.email, action_code_settings=None)
        send_email(newFireBaseUser.display_name or "User", newFireBaseUser.email, emailVerificationLink)

        access_token = create_access_token(identity=newFireBaseUser.uid, expires_delta=timedelta(days=1), additional_claims={"user_id": newFireBaseUser.uid, "user_email": user_email, "token_type": "access"})
        refresh_token = create_refresh_token(identity=newFireBaseUser.uid, expires_delta=timedelta(days=1), additional_claims={"user_id": newFireBaseUser.uid, "user_email": user_email, "token_type": "refresh"})

        return jsonify({'message': 'user registered successfully', 'access_token': access_token, 'refresh_token': refresh_token}), 200

    except EmailAlreadyExistsError:
        return jsonify({'message': 'email already exists'}), 401
    except InvalidIdTokenError:
        return jsonify({'message': 'invalid email or password'}), 401
    except Exception as e:
        # print(e)
        return jsonify({'message': str(e), "error": str(e)}), 401

@user_route.route("/get_user", methods=["GET"])
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({'message': 'You are not authorized to use this function'}), 401

    user = firebaseDataStore.collection('users').document(user_id).get().to_dict()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    userFirebase = firebaseDataStore.collection("complaints")
    query = userFirebase.where('user_id', '==', user_id).stream()
    complaints_data = []
    for complaint in query:
        complaint_dict = complaint.to_dict()
        complaint_dict['images'] = {image['index']: image['imageURL'] for image in complaint_dict.get('images', [])}
        complaints_data.append(complaint_dict)

    user['complaints'] = complaints_data

    return jsonify({'user_data': user, 'message': "Welcome to profile page"}), 200

@user_route.route("/update_user", methods=["PUT"])
@jwt_required()
def update_user():
    user_id = get_jwt_identity()  # Firebase UID
    if not user_id:
        return jsonify({'message': 'You are not authorized to use this function'}), 401

    user_ref = firebaseDataStore.collection('users').document(user_id)
    user_data = user_ref.get().to_dict()

    if not user_data:
        return jsonify({'message': 'User not found'}), 404

    get_data = request.json
    user_name = get_data.get("user_name")
    user_email = get_data.get("user_email")
    user_phone = get_data.get("user_phone")

    if not user_name and not user_email and not user_phone:
        return jsonify({'message': 'Please provide at least one field to update'}), 400

    updated_fields = {}

    if user_name:
        updated_fields["user_name"] = user_name
    if user_email:
        updated_fields["user_email"] = user_email
    if user_phone:
        updated_fields["user_phone"] = user_phone

    try:
        user_ref.update(updated_fields)
        return jsonify({'message': 'User updated successfully'}), 200
    except Exception as e:
        # print(e)
        return jsonify({'message': f'Error updating user: {e}'}), 500

@user_route.route("/add_image", methods=["POST"])
@jwt_required()
def add_image():
    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({'message': 'You are not authorized to use this function'}), 401

    try:
        print(request.form)
        # Add complaint to Firebase
        complaint_ref = firebaseDataStore.collection('complaints').document()
        complaint_ref.set({
            "complaint_status": False,
            "complaint_closed_by": None,
            "complaint_closed_reason": None,
            "complaint_closed_comment": None,
            "complaint_banned": False,
            "complaint_closed_rating": None,
            "user_id": user_id,
            "latitude": request.form.get("latitude"),
            "longitude": request.form.get("longitude"),
            "upload_time": firestore.SERVER_TIMESTAMP,
            "street_Address" : request.form.get("street_Address"),
            "city": request.form.get("city"),
            "state": request.form.get("state"),
            "pincode" : request.form.get("pincode"),
            "complaint_description": request.form.get("complaint_description"),
            "rating": request.form.get("rating"),
            "path_type": request.form.get("path_type"),
            'analysisDate': firestore.SERVER_TIMESTAMP,
            

            
        })
      

        # Handle image upload
        images = request.files.getlist('images')
        if not images:
            return jsonify({'message': 'No images provided'}), 400

        # print(len(images))

        count = 0
        images_array = []
        Aidata = []
        for img in images:
            try:
                new_image_in_azureStorage = uploadImagesToContainer(container="complaints", image=img, userId=user_id + complaint_ref.id + f"{count}")
                print(f"Image added to Azure Storage: {new_image_in_azureStorage}")
                # print(f"Image added to GCP Storage: {new_image_in_gcp_storage}")
                images_array.append({
                    "imageURL": new_image_in_azureStorage,
                    "index": count
                })
                # AiResult = AIMLForComplaints(new_image_in_gcp_storage)
                AiResult = AIMLForComplaints(new_image_in_azureStorage)
                # print(f"AI Result: {AiResult}")
                Aidata.extend(AiResult)  # Flatten the AI results
                count += 1
                # print(count)
            except Exception as e:
                # print(f"ResourceNotFoundError: {e}")
                return jsonify({'message': str(e)}), 500
            # print("ai data", Aidata)
        complaint_ref.update({
            "images": images_array,
            "AiData": Aidata
        })
        # print(f"Images added to Firebase: {images_array} , {complaint_ref.id}")

        return jsonify({'message': 'Image and complaint added successfully'}), 200

    except Exception as e:
        # print(e)
        return jsonify({'message': str(e)}), 500
    
    
@user_route.route("/get_images", methods=["GET"])
@jwt_required()
def get_images():
    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({'message': 'You are not authorized to use this function'}), 401



    # images = Images.query.filter_by(user_id=user_id).all()
    # if not images:
    #     return jsonify({'message': 'No images found'}), 401
    # image_data = []
    # for image in images:
    #     image_data.append({
    #         "image_id": image.image_id,
    #         "image_name": image.image_name,
    #         "mimetype": image.mimetype,
    #         "longitude": image.longitude,
    #         "latitude": image.latitude,
    #         "problem": image.problem,
    #         "stars": image.stars
    #     })
    # return jsonify({'image_data': image_data, 'message': "Images found"}), 200


