from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .models import Profile
from .models import Post,Like,Comment,Follow,SavedPost,Notification
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator

# Create your views here.


def signup(request):
    if request.method=='GET':
        return render(request,'signup.html')
    if request.method == 'POST':
        username=request.POST.get('username')
        email=request.POST.get('email')
        password=request.POST.get('password')
        confirm_password=request.POST.get('confirm_password')
        if password != confirm_password:
            messages.error(request, 'Invalid passward.')
            return redirect('signup')
        if User.objects.filter(username=username).exists():
            messages.error(request,'Username already exists.')
            return redirect('signup')
        if User.objects.filter(email=email).exists():
            messages.error(request,'email already exists.')
            return redirect('signup')
        print("POST DATA=", request.POST)
        print("USERNAME=", username)
        print("EMAIL=", email)
        user=User.objects.create_user(username=username, email=email, password=password)
        profile=Profile.objects.create(user=user)
        messages.success(request, 'Account created successfully!')
        
    return redirect('loginn')


def loginn(request):
    if request.method=='GET':
        return render(request, 'loginn.html')
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        user = authenticate(
            request,
            username=username,
            password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('home')
        
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('loginn')




@login_required
def logoutt(request):
    logout(request)
    messages.success(request,'Logged out successfully!')
    return redirect('loginn')

@login_required
def edit_profile(request):
    user=request.user
    profile=request.user.profile
    if request.method=='GET':
        context={'user': user, 'profile':profile}
        return render(request, 'edit_profile.html',context)
    if request.method=='POST':
        username=request.POST.get('username', '').strip()
        bio=request.POST.get('bio', '').strip()
        profile_picture=request.FILES.get('profile_picture')

        #USERNAME VALIDATION
        if not username:
            messages.error(request, 'Username cannot be empty.')
            return redirect('edit_profile')
        if User.objects.filter(username=username).exclude(id=user.id).exists():
            messages.error(request, 'Username already exists.')
            return redirect('edit_profile')
        
        #UPDATE USER AND PROFILE
        user.username=username
        profile.bio=bio

        #PROFILE PICTURE VALIDATION
        if profile_picture:
            profile.profile_picture=profile_picture
            user.save()
            profile.save()
            messages.success(request, 'Profile update successfully.')
    return redirect('profile', user.id)

    

@login_required
def delete_post(request, post_id):
    post=Post.objects.get(id=post_id)
    if post.user != request.user:
        return redirect('home')
    post.delete()
    messages.success(request, 'Post deleted successfully.')
    return redirect('home')



@login_required
def like_post(request,post_id):
    post=Post.objects.get(id=post_id)
    if Like.objects.filter(user=request.user, post=post).exists():
        Like.objects.filter(user=request.user, post=post).delete()
    else:
        Like.objects.create(user=request.user,post=post)
        if request.user != post.user:
            Notification.objects.create(sender=request.user, receiver=post.user, post=post, notification_type='like')
    return redirect('home')


@login_required
def create_comment(request, post_id):
    if request.method=='GET':
        return redirect('home')
    if request.method=='POST':
        post=Post.objects.get(id=post_id)
        user=request.user
        content=request.POST.get('content').strip()
        if content:
            Comment.objects.create(user=user, post=post, content=content)
            messages.success(request, 'Comment added successfully!')
            if request.user != post.user:
                Notification.objects.create(sender=request.user, receiver=post.user, notification_type='comment')
            return redirect('home')
        else:
            messages.error(request, 'Comment box is empty add comment')
            return redirect('home')

@login_required
def delete_comment(request, comment_id):
    if request.method=='POST':
        comment=get_object_or_404(Comment, id=comment_id)
        if request.user==comment.user or request.user==comment.post.user:
            comment.delete()
            return redirect('home')

@login_required
def Profilee(request,user_id):
    # profile=request.user.profile
    profile_user= get_object_or_404(User, id=user_id)
    profile=profile_user.profile
    is_following=Follow.objects.filter(follower=request.user, following=profile_user).exists()
    follower_count=Follow.objects.filter(following=profile_user).count()
    following_count=Follow.objects.filter(follower=profile_user).count()
    context={ 'profile_user':profile_user, 'is_following': is_following, 'user_id': user_id, 'profile' : profile, 'follower_count' : follower_count, 'following_count' : following_count}
    return render(request, 'profile.html', context)

@login_required
def follow(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    if request.method=='GET':
        return redirect( 'profile')
    if request.method=='POST':
        follower=request.user
        following=get_object_or_404(User, id=user_id)
        if follower==following:
            messages.error(request, 'You cannot follow your own account.')
            return redirect('home')
        is_following= Follow.objects.filter(follower=follower, following=following).exists()
        if is_following:
            Follow.objects.get(follower=request.user, following=following).delete()
            return redirect('profile', user_id=user_id)
        else:
            Follow.objects.create(follower=request.user, following=following)
            Notification.objects.create(sender=request.user, receiver= user_to_follow, notification_type= 'follow')
        return redirect('profile', user_id=user_id)

@login_required
def home(request):
    # Post.objects.filter(user=request.user)
    # posts = Post.objects.order_by('-created_at')
    query=request.GET.get('q', "").strip()
    if query != "":
        users=User.objects.filter(username__icontains=query)
    else:
        users=User.objects.none()
    searched_performed= bool(query)
    # ------------------HOMEFEED FEATURE--------
    
    following_ids = set(
    Follow.objects.filter(
        follower=request.user
    ).values_list('following', flat=True)
) 
    # if following_ids:
    #     posts=Post.objects.filter (Q(user=request.user) | Q(user__in = following_ids)).order_by('-created_at') 
    # else:
    #     posts=Post.objects.order_by('-created_at')
    posts = Post.objects.order_by('-created_at')

    for post in posts:
        post.is_following = post.user.id in following_ids

    paginator= Paginator(posts, 10)
    page_number=request.GET.get('page')
    page_obj= paginator.get_page(page_number)

    saved_post_ids=SavedPost.objects.filter(user=request.user).values_list('post', flat=True)
    context={

        'query': query,
        'users': users,
        'searched_performed': searched_performed,
        'saved_post_ids': saved_post_ids,
        'following_ids': following_ids,
        'page_obj': page_obj
    }
    return render(request, 'home.html', context)

@login_required
def create_post(request):
    if request.method == 'GET':
        return render(request, 'create_post.html')

    if request.method == 'POST':
        image=request.FILES.get('image')
        content = request.POST.get('content', '').strip()
        # if image:
        #     pass
        if not image:
            messages.error(request, 'Image is required!')
            return render(request, 'create_post.html')

        if not content:
            messages.error(request, 'Caption is required.')
            return render(request, 'create_post.html')

        if len(content) > 1000:
            messages.error(request, 'Post cannot exceed 1000 characters.')
            return render(request, 'create_post.html')

        Post.objects.create(
            user=request.user,
            content=content,
            image=image
        )

        messages.success(request, 'Post uploaded successfully.')
        return redirect('home')
    



@login_required
def edit_post(request, post_id):
    post = Post.objects.get(id=post_id)

    # Authorization Check
    if post.user != request.user:
        messages.error(request, "You are not allowed to edit this post.")
        return redirect('home')

    if request.method == 'GET':
        context = {'post': post}
        return render(request, 'edit_post.html', context)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        image= request.FILES.get('image')

        if not content:
            messages.error(request, "Content cannot be empty.")
            return redirect('edit-post', post_id=post.id)

        post.content = content
        post.image = image
        post.save()

        messages.success(request, "Post updated successfully.")
        return redirect('home')


@login_required
def save_post(request, post_id):
    post=Post.objects.get(id=post_id)
    saved_post=SavedPost.objects.filter(user=request.user, post=post)
    if saved_post.exists():
        saved_post.delete()
    else:
        SavedPost.objects.create(user=request.user, post=post)
    return redirect('home')


@login_required
def savedpost(request):
    savedpost_ids= SavedPost.objects.filter(user=request.user).values_list('post_id',flat=True)
    posts=Post.objects.filter(id__in = savedpost_ids).order_by('-created_at')
    context= {
        'posts': posts
    }
    return render(request, 'saved-post.html', context)



@login_required
def Notifications(request):
    notifications=Notification.objects.filter(receiver=request.user).order_by('-created_at')
    context={'notifications': notifications}
    return render(request, 'notification.html', context)
