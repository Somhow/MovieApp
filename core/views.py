from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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

def index(request):
    from .models import BlogEntry
    from django.contrib.auth.models import User

    posts = BlogEntry.objects.order_by("-created_at").all()
    top_rated_posts = BlogEntry.objects.order_by("-rating").all()

    if request.method == "POST":
        email = request.POST.get("email")
        print(email)
        if email:
            user = User.objects.filter(email=email).first()
            if user:
                profile = user.profile
                profile.newsletter_subscription = True
                profile.save()
                
                messages.success(request, "Subscription successful")
                return redirect("home")
            else:
                messages.error(request, "User not found!")
                return redirect("registration")
        else:
            messages.error(request, "Email is invalid!")
            return redirect("registration")


    return render(
        request,
        "index.html",
        context={"posts": posts[0:4], "top_rated_posts": top_rated_posts[0:4]},
    )


def all_blog_entries(request):
    from .models import BlogEntry, Category

    category_name = request.GET.get("category")
    print("Filter category: ", category_name)

    if category_name:
        posts = (
            BlogEntry.objects.filter(category__title=category_name)
            .order_by("-created_at")
            .all()
        )
    else:
        posts = BlogEntry.objects.order_by("-created_at").all()

    categories = Category.objects.all()

    return render(
        request,
        "blog_entries_list.html",
        context={"posts": posts, "categories": categories},
    )


@login_required
def blog_entry_details(request, blog_id):
    from django.shortcuts import get_object_or_404
    from .models import BlogEntry, Category, Comment
    from .forms import CommentForm
    from django.contrib import messages

    from django.db.models import Avg

    post = get_object_or_404(BlogEntry, id=blog_id)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.blog_entry = post
            comment.save()

            post.rating = post.comments.aggregate(Avg("stars"))["stars__avg"]
            post.save()

            messages.success(request, "Comment created successfully!")

            form = CommentForm()
    else:
        form = CommentForm()

    categories = Category.objects.all()
    comments = Comment.objects.filter(blog_entry=post).all()

    recommended_posts = (
        BlogEntry.objects.filter(category=post.category)
        .exclude(id=post.id)
        .order_by("-created_at")[:4]
    )

    is_post_saved = post.savers.filter(user=request.user).exists()

    return render(
        request,
        "blog_entry_details.html",
        context={
            "post": post,
            "categories": categories,
            "form": form,
            "recommended_posts": recommended_posts,
            "comments": comments,
            "is_post_saved": is_post_saved
        },
    )


@login_required
def create_blog_entry(request):
    from .forms import BlogEntryForm
    from django.contrib.auth.models import User
    from django.template.loader import render_to_string
    from users.models import Profile
    from django.urls import reverse
    from django.contrib import messages
    form = BlogEntryForm()

    if request.method == "POST":
        form = BlogEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()

            form = BlogEntryForm()
            messages.success(request, "Blog Successfully created!")

            absolute_url = f"http://127.0.0.1:8000{reverse("blog_entry_details", kwargs={"blog_id": entry.id})}"

            html_message = render_to_string(
                "emails/new_blog_entry.html",
                context={"post": entry, "absolute_url": absolute_url},
            )

            subscribers = Profile.objects.filter(newsletter_subscription=True).all()
            recipient_list = [sub.user.email for sub in subscribers if sub.user.email]
            send_email(
                request,
                "Blog App: New Blog!",
                "New entry f{entry.title}",
                html_message,
                recipient_list,
            )

    return render(request, "create_blog_entry.html", {"form": form, "update_entry": False, "title": "Create_entry"})
    

def blog_entry_delete(request, blog_id):
    from core.models import BlogEntry
    from django.shortcuts import get_object_or_404

    post = get_object_or_404(BlogEntry, id=blog_id)

    if request.method == "POST":
        post.delete()
        messages.success(request, "Blog deleted succesfully")

    return redirect("profile")


@login_required
def edit_blog_entry(request, blog_id):
    from .forms import BlogEntryForm
    from .models import BlogEntry
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib.auth.models import User
    from django.template.loader import render_to_string
    from users.models import Profile
    from django.urls import reverse
    from django.contrib import messages

    post = get_object_or_404(BlogEntry, id=blog_id)

    if request.user != post.user:
        messages.error(request, "You don't have permission to edit this entry")
        return redirect("home")
    
    if request.method == "POST":
        form = BlogEntryForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Blog successfully updated!")
    else:
        form = BlogEntryForm(instance=post)

    return render(request, "create_blog_entry.html", {"form": form, "update_entry": True, "title": "Update_entry", "post": post})         

    