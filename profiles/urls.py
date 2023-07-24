from django.urls import path


from . import views


urlpatterns = [
    path('activate/invitation/<str:uidb64>/<str:token>/', views.activate_invite, name='activate-invite'),
    path('invitation/send/<int:id>/', views.send_invitation, name='send-invitation'),
    path('invitation/remove/<int:id>/', views.remove_invitation, name='remove-invitation'),
    path('profile/detail/<int:pk>/', views.ProfileDetailView.as_view(), name='profile-detail'),
    path('profile/update/<int:pk>/', views.ProfileUpdateView.as_view(), name='profile-update'),
    path('profile/delete/<int:pk>/', views.ProfileDeleteView.as_view(), name='profile-delete'),

    path('invitations/', views.InvitationListView.as_view(), name='invitation-list'),
    path('invitations/create/', views.InvitationCreateView.as_view(), name='invitation-create'),
    path('invitation/detail/<int:pk>/', views.InvitationDetailView.as_view(), name='invitation-detail'),
    path('invitation/update/<int:pk>/', views.InvitationUpdateView.as_view(), name='invitation-update'),
    path('invitation/delete/<int:pk>/', views.InvitationDeleteView.as_view(), name='invitation-delete'),
]
