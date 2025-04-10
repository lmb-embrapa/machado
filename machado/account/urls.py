# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""URLs."""

from django.urls import path

from machado.account import views as userViews


urlpatterns = [
    # PublicUserActions para criação de conta e login (não exige autenticação)
    path("login", userViews.PublicUserActions.as_view({'post': 'login'}), name="user_login"),
    
    # AuthenticatedUserActions para logout (exige autenticação)
    path("logout", userViews.AuthenticatedUserActions.as_view({'post': 'logout'}), name="user_logout"),

    #AdminUserActions para deletar usuário (exige autenticação e que o usuário seja admin)
    path("", userViews.AdminUserActions.as_view({'post': 'create', 'get': 'list'}), name="user_get_create"),
    path("<int:id>", userViews.AdminUserActions.as_view({'delete': 'delete', 'put': 'update', 'get': 'listUserById'}), name="user_delete_update_list"),
    path("username/<str:username>", userViews.AdminUserActions.as_view({'get': 'listUserByUsername'}), name="user_list_by_username"),
]