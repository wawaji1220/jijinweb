"""
URL配置 for funds app
"""
from django.urls import path
from . import views

app_name = 'funds'

urlpatterns = [
    path('', views.index, name='index'),
    path('fund/<str:fund_code>/', views.fund_detail, name='fund_detail'),
    path('search/', views.search, name='search'),
    path('api/realtime/', views.api_fund_realtime, name='api_realtime'),
    path('api/history/', views.api_fund_history, name='api_history'),
    path('api/search/', views.api_fund_search, name='api_search'),
    path('api/info/', views.api_fund_info, name='api_fund_info'),
    path('api/add/', views.api_add_fund, name='api_add_fund'),
    path('api/delete/', views.api_delete_fund, name='api_delete_fund'),
    path('api/settings/', views.api_settings_get, name='api_settings_get'),
    path('api/settings/update/', views.api_settings_update, name='api_settings_update'),
    path('api/reorder/', views.api_reorder_funds, name='api_reorder_funds'),
]
