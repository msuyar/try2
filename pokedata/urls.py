from django.urls import include, path
from . import views
from . import api


urlpatterns = [

    path('', views.api_home, name='api_home'),

    path('pokemon/', views.PokemonList.as_view(), name='pokemon_list'),
    path('pokemon/', views.PokemonList.as_view(),   name='pokemon-index'),
    path('type/<str:type>', views.PokemonList.as_view(), name='pokemon_list_by_type'),

    # Detail & CRUD views
    path('create_pokemon/', views.PokemonCreate.as_view(), name='pokemon_create'),
    path('update/<int:pk>/', views.PokemonUpdate.as_view(), name='pokemon_update'),
    path('delete/<int:pk>/', views.PokemonDelete.as_view(), name='pokemon_delete'),
    path('pokemon/gen/<int:gen>/', views.pokemon_by_generation, name='pokemon_by_generation'),
    path('pokemon/legendary/', views.pokemon_legendary, name='pokemon_legendary'),
    path('pokemon/type/<str:type1>/<str:type2>/', views.pokemon_by_type, name='api_pokemon_by_type_one'),
    path('pokemon/type/<str:type1>/', views.pokemon_by_type, name='api_pokemon_by_type_one'),
    path('pokemon/<int:pk>/', views.PokemonDetail.as_view(), name='pokemon-detail'),
    

    #  DRF API 
    path('api/pokemon/', api.pokemon_list, name='api_pokemon-list-api'),
    path('api/pokemon/<int:pk>/', api.pokemon_detail, name='api_pokemon-detail-api'),
    path('api/create_pokemon/', api.create_pokemon, name='api_create-pokemon'),
    path('api/pokemon/gen/<int:gen>/', api.pokemon_by_generation, name='api_pokemon_by_generation'),
    path('api/pokemon/legendary/', api.pokemon_legendary, name='api_pokemon_legendary'),
    path('api/pokemon/type/<str:type1>/<str:type2>/', api.pokemon_by_type, name='api_pokemon_by_type_one'),
    path('api/pokemon/type/<str:type1>/', api.pokemon_by_type, name='api_pokemon_by_type_one'),
    path('pokemon/type/<str:type1>/<str:type2>', api.pokemon_by_type, name='pokemon_by_type_two'),
]
