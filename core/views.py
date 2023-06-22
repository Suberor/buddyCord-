from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ""   #gets the query from the URL 

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    rooms_count = rooms.count()
    topics = Topic.objects.all()[0:5]
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    context = {"rooms": rooms, "topics":topics, "rooms_count":rooms_count, "room_messages": room_messages}

    return render(request, "core/home.html", context)


# views for user login/logut/register

def login_user(request):
    page = "login"

    if request.user.is_authenticated:   # if the user is already logged in he can't acccess to login view
        return redirect("home")
    
    if request.method == "POST":
        username = request.POST.get("username").lower()
        password = request.POST.get("password")
        
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "User does not exist")
            return render(request, "core/login_register.html")
        
        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "incorrect username or password")
            
        
    context = {"page":page}
    return render(request, "core/login_register.html", context)


def register_user(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect("home")

        else:
            messages.error(request, "An error ocurred during registration.")
            
    context = {"form":form}
    return render(request, "core/login_register.html", context)


def logout_user(request):
    logout(request)
    messages.success(request, "logged out.")
    return redirect("login")


def room(request, pk):  
    room = Room.objects.get(id=pk)
    messgs = room.message_set.all()   # get all the messages for this room. This way you can access information from a child class
    participants = room.participants.all()

    if request.method == "POST":
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get("body")
        )
        room.participants.add(request.user)
        return redirect("room", pk=room.id)
    
    context = {"room": room, "messgs":messgs, "participants":participants}

    return render(request, "core/room.html", context)


def UserProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()   # getting all the user's rooms 
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {"user":user, "rooms":rooms, "room_messages": room_messages, "topics": topics}

    return render(request, "core/profile.html", context)



# views for CRUD of rooms 

@login_required(login_url="login")
def create_room(request):
    form = RoomForm()       # shows the empty form
    topics = Topic.objects.all()
    if request.method == "POST":         # If the user is posting information into the form 
        form = RoomForm(request.POST)
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get("name"),
            description=request.POST.get("description"),
        )

        return redirect("home") 
        
    context = {"form":form, "topics":topics}

    return render(request, "core/create_room.html", context)


@login_required(login_url="login")
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse("You are not allowed to update another host's room")

    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)
        
        room.name = request.POST.get("name")
        room.description = request.POST.get("description")
        room.topic = topic
        room.save()

        return redirect("home")
    
    context = {"form":form, "topics":topics, "room":room}
    return render(request, "core/create_room.html",context)


@login_required(login_url="login")
def delete_room(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("You are not allowed to delete another host's room")

    if request.method == "POST":
        room.delete()
        #messages.success(request, "Room deleted successfully")
        return redirect("home")
    
    context = {"obj":room, "word":"room"}
    return render(request, "core/delete_room.html", context)


@login_required(login_url="login")
def delete_message(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse("You are not allowed to delete another host's message")

    if request.method == "POST":
        message.delete()
        return redirect("home")
    
    context = {"obj":message, "word":"message"}
    return render(request, "core/delete_room.html", context)


@login_required(login_url="login")
def update_user(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == "POST":
        form = UserForm(request.POST, instance=user)

        if form.is_valid():
            form.save()
            return redirect("user-profile", pk=user.id)
        
    context = {"form":form}

    return render(request, "core/update_user.html", context)


def topics_page(request):
    q = request.GET.get("q") if request.GET.get("q") != None else "" #pass the q value if there is any
    topics = Topic.objects.filter(name__icontains=q)
    context = {"topics":topics}

    return render(request, "core/topics.html", context)


def activity_page(request):
    room_messages = Message.objects.all()
    context = {"room_messages":room_messages}

    return render(request, "core/activity.html", context)