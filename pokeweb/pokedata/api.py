from django.http import HttpResponse
from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models      import Pokemon
from .serializers import PokemonSerializer

@api_view(['GET', 'POST'])
def pokemon_list(request):
    """
    GET  /api/pokemon       → list all Pokémon
    POST /api/pokemon       → create a new Pokémon
    """
    if request.method == 'POST':
        serializer = PokemonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # GET
    qs = Pokemon.objects.all()
    serializer = PokemonSerializer(qs, many=True)
    return Response(serializer.data)


@api_view(['GET', 'PUT', 'DELETE'])
def pokemon_detail(request, pk):
    """
    GET    /api/pokemon/<pk>   → retrieve one Pokémon
    PUT    /api/pokemon/<pk>   → update it
    DELETE /api/pokemon/<pk>   → delete it
    """
    try:
        pokemon = Pokemon.objects.get(pk=pk)
    except Pokemon.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PokemonSerializer(pokemon)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = PokemonSerializer(pokemon, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE
    pokemon.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def pokemon_by_generation(request, gen):
    """
    GET /api/pokemon/gen/<gen> → list all Pokémon in generation <gen>
    """
    qs = Pokemon.objects.filter(generation=gen)
    serializer = PokemonSerializer(qs, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def pokemon_legendary(request):
    """
    GET /api/pokemon/legendary → list all legendary Pokémon
    """
    qs = Pokemon.objects.filter(legendary=True)
    serializer = PokemonSerializer(qs, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def pokemon_by_type(request, type1, type2=None):
    """
    GET /api/pokemon/type/<type1>/
    GET /api/pokemon/type/<type1>/<type2>/

    - If only type1 → return ALL Pokémon where primary OR secondary == type1.
    - If type2 is provided → return only those where:
        (primary == type1 AND secondary == type2)
         OR
        (primary == type2 AND secondary == type1)
    """
    # start with an empty QuerySet
    qs = Pokemon.objects.none()

    if type2:
        # Case A: primary matches type1 AND secondary matches type2
        qs_a = Pokemon.objects.filter(
            pokemon_type1__iexact=type1,
            pokemon_type2__iexact=type2
        )

        # Case B: primary matches type2 AND secondary matches type1
        qs_b = Pokemon.objects.filter(
            pokemon_type1__iexact=type2,
            pokemon_type2__iexact=type1
        )

        # combine both cases
        qs = qs_a | qs_b

    else:
        # only one type → match either slot
        qs = Pokemon.objects.filter(
            Q(pokemon_type1__iexact=type1) |
            Q(pokemon_type2__iexact=type1)
        )

    serializer = PokemonSerializer(qs.distinct(), many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_pokemon(request):
    """
    POST /api/create_pokemon  → create a new Pokémon
    """
    serializer = PokemonSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



