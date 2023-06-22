from django.urls import path
from . import views


urlpatterns = [
    # paths for user managing and authentication
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("register/", views.register_user, name="register"),
    path("update-user/", views.update_user, name="update-user"),
    # path for main page
    path("", views.home, name="home"),
    path("profile/<int:pk>/", views.UserProfile, name="user-profile"),
    # paths for rooms CRUD
    path("room/<int:pk>/", views.room, name="room"),
    path("create-room/", views.create_room, name="create-room"),
    path("update-room/<int:pk>/", views.update_room, name="update-room"),
    path("delete-room/<int:pk>/", views.delete_room, name="delete-room"),
    path("delete-message/<int:pk>/", views.delete_message, name="delete-message"),


    path("topics/", views.topics_page, name="topics-page"),
    path("activity/", views.activity_page, name="activity-page"),
]   
