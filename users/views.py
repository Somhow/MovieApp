from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def send_email(request, subject, message, html_content, recipient_list):
    from django.core.mail import EmailMultiAlternatives
    from django.conf import settings

    msg = EmailMultiAlternatives(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        recipient_list,
    )

    msg.attach_alternative(html_content, "text/html")
    msg.send()


# Create your views here.
def registration(request):
    from .forms import RegistrationForm
    from django.template.loader import render_to_string
    from .token import account_activation_token
    from django.utils.http import urlsafe_base64_encode
    from django.utils.encoding import force_bytes
    from .models import Profile

    form = RegistrationForm()
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            profile = Profile.objects.create(user=user)
            profile.save()

            user_token = account_activation_token.make_token(user)
            print("User token:", user_token)
            uid =   urlsafe_base64_encode(force_bytes(user.pk))
            print("UID", uid)

            html_message = render_to_string(
                "emails/registration_confirm.html",
                context={"user": user, "uid": uid, "token": user_token},
            )

            send_email(
                request,
                "BlogApp: Registration Confirm",
                "Confirm your registration",
                html_message,
                [user.email],
            )

            return redirect("login")

    return render(request, "registration.html", {"form": form})


def login(request):
    from .forms import LoginForm
    from django.contrib.auth import login

    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data["user"]
            print("User data:", user)
            login(request, user)

            messages.success(request, f"Welcome, {user.username}!")

            return redirect("home")

    return render(request, "login.html", {"form": form})

@login_required
def logout(request):
    from django.contrib.auth import logout

    logout()

    return redirect("home")


def activate(request, uid, token):
    from django.utils.http import urlsafe_base64_decode
    from .token import account_activation_token
    from django.utils.encoding import force_str
    from django.shortcuts import get_object_or_404
    from django.contrib.auth.models import User

    user_id = force_str(urlsafe_base64_decode(uid))
    user = get_object_or_404(User, pk=user_id)

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, "Account succesfully activated!")
        return redirect("login")
    else:
        messages.error(request, "Activation link is invalid")
        return redirect("registration")

@login_required
def profile(request, username=None):
    from core.models import BlogEntry
    from .models import SavedPosts
    from django.shortcuts import get_object_or_404
    from django.contrib.auth.models import User

    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user

    posts = BlogEntry.objects.filter(user=user).all()
    saved_posts = SavedPosts.objects.filter(user=user).all()


    return render(request, "profile.html", {"user": user,"posts": posts, "saved_posts": saved_posts})

@login_required
def toggle_save_post(request, blog_id):
    from django.http import JsonResponse
    from core.models import BlogEntry
    from .models import SavedPosts
    from django.shortcuts import get_object_or_404

    if request.method=="POST":
        post=get_object_or_404(BlogEntry, id=blog_id)
        saved_post, created=SavedPosts.objects.get_or_create(
            user=request.user, post=post
        )
        if not created:
            saved_post.delete()
            is_saved = False
            message = "Post removed from saved!"
        else:
            is_saved = True
            message  = "Post saved successfully!"

        return JsonResponse(
                {"isSaved": is_saved, "message": message, "savedCount": post.savers.count()}
            )

    return JsonResponse({"error": "Invalid method!"}, status=405)

@login_required
def get_saved_posts(request):
    saved_posts=profile.user


@login_required
def update_profile(request):
    from django.http import JsonResponse
    from django.contrib.auth.models import User
    import json
    from django.core.validators import validate_email

    if request.method=="POST":
        try:
            user = request.user
            data = json.loads(request.body)

            print("Update profile data:", data)
            
            # -- U S E R N A M E --
            
            new_username=data.get("username", "")

            if len(new_username) < 3:
                return JsonResponse({
                    "success": False,
                    "error": "Invalid username, must be at least 3 characters long"
                    },
                    status=400)
            

            if User.objects.filter(username=new_username).exclude(id=user.id).exists():
                return JsonResponse({
                    "success": False,
                    "error": "Username already in use"
                    },
                    status=400)
            
            user.username=new_username

            # -- E M A I L --

            new_email=data.get("email", "").strip()

            try:
                validate_email(new_email)
            except ValueError:
                return JsonResponse(
                    {
                        "success": False,
                        "error": "Invalid email adress format!",
                    },
                    status=400)
            
            user.email = new_email

            # -- F I R S T / L A S T   N A M E

            user.first_name = data.get("firstName", "").strip()
            user.last_name = data.get("lastName", "").strip()

            # -- B I O G R A P H Y --
            profile=user.profile
            profile.bio=data.get("bio", "").strip()

            profile.save()
            user.save()

            return JsonResponse({
                "success": True,
                "message":"Profile updated successfully!",
                "user": {
                        "username": user.username,
                        "email": user.email,
                        "firstName": user.first_name,
                        "lastName": user.last_name,
                        "bio": profile.bio
                }                
            })
        

        except json.JSONDecodeError:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Invalid JSON data!",
                },
                status=400,
            )
        
        except Exception as e:
            return JsonResponse(
                {
                    "success": False,
                    "error": f"An error: {str(e)}",
                },
                status=500,
            )

