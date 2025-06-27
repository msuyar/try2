from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q


from .forms import PokemonForm
from .models import Pokemon, Generation, PokemonType


def paginate_master(request, per_page=15, page_kwarg="sidebar_page"):
    all_qs    = Pokemon.objects.all()
    paginator = Paginator(all_qs, per_page)
    page_num  = request.GET.get(page_kwarg)
    try:
        page = paginator.page(page_num)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    return page

class SidebarMixin:
    sidebar_per_page   = 15
    sidebar_page_kwarg = "sidebar_page"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        page = paginate_master(
            self.request,
            per_page=self.sidebar_per_page,
            page_kwarg=self.sidebar_page_kwarg
        )
        ctx["master_pokemons"] = page
        # this gives you e.g. [1, '…', 4, 5, 6, '…', 20]
        ctx["sidebar_pages"] = page.paginator.get_elided_page_range(
            page.number,
            on_each_side=2,
            on_ends=1
        )
        return ctx

def pokemon_by_generation(request, gen):
    pokemons     = Pokemon.objects.filter(generation=gen)
    page         = paginate_master(request)
    sidebar_pages = page.paginator.get_elided_page_range(
        number=page.number,
        on_each_side=2,
        on_ends=1,
    )
    return render(request, 'pokedata/list.html', {
        'master_pokemons': page,     
        'sidebar_pages':  sidebar_pages,
        'pokemons':        pokemons,
        'current_generation': gen,
    })

def pokemon_legendary(request):
    pokemons     = Pokemon.objects.filter(legendary=True)
    page         = paginate_master(request)
    sidebar_pages = page.paginator.get_elided_page_range(
        number=page.number,
        on_each_side=2,
        on_ends=1,
    )
    return render(request, 'pokedata/list.html', {
        'master_pokemons': page,
        'sidebar_pages':  sidebar_pages,
        'pokemons':        pokemons,
    })

def pokemon_by_type(request, type1, type2=None):
    if type2:
        qs = (
            Pokemon.objects.filter(pokemon_type1__iexact=type1,
                                   pokemon_type2__iexact=type2)
            | 
            Pokemon.objects.filter(pokemon_type1__iexact=type2,
                                   pokemon_type2__iexact=type1)
        )
        title = f"{type1.title()} / {type2.title()}"
    else:
        qs = Pokemon.objects.filter(
            Q(pokemon_type1__iexact=type1) |
            Q(pokemon_type2__iexact=type1)
        )
        title = type1.title()

    # paginate the sidebar
    page = paginate_master(request)
    sidebar_pages = page.paginator.get_elided_page_range(
        number=page.number, on_each_side=2, on_ends=1
    )

    return render(request, 'pokedata/list.html', {
        'master_pokemons': page,
        'sidebar_pages':   sidebar_pages,
        'pokemons':        qs.distinct(),
        'type':            title,
    })

class PokemonDetail(SidebarMixin, DetailView):
    model               = Pokemon
    context_object_name = 'pokemon'
    template_name       = 'pokedata/pokemon.html'

    # you can delete this override if SidebarMixin already adds master_pokemons & sidebar_pages
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        page = paginate_master(self.request)
        ctx['master_pokemons'] = page
        ctx['sidebar_pages'] = page.paginator.get_elided_page_range(
            number=page.number, on_each_side=2, on_ends=1
        )
        return ctx
    
class PokemonList(SidebarMixin, ListView):
    model = Pokemon
    paginate_by = 15
    context_object_name = 'pokemons'  

    def get_queryset(self):
        qs = super().get_queryset()
        # apply GET filters, e.g.: ?generation=3&type=Fire
        gen = self.request.GET.get('generation')
        t   = self.request.GET.get('type')
        legendary = self.request.GET.get('legendary')
        if gen:
            qs = qs.filter(generation=gen)
        if t:
            qs = qs.filter(
                Q(pokemon_type1__iexact=t) |
                Q(pokemon_type2__iexact=t)
            )
        if legendary == 'true':
            qs = qs.filter(is_legendary=True)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Pass back selected values so the form can re-populate
        ctx['selected_gen']  = self.request.GET.get('generation', '')
        ctx['selected_type'] = self.request.GET.get('type', '')

        # Here’s where your choices come in:
        ctx['gen_choices']  = Generation.choices        # [(1,"Generation I"),(2,"Generation II"),...]
        ctx['type_choices'] = PokemonType.choices       # [("Normal","Normal"),("Fire","Fire"),...]

        return ctx

    def get_template_names(self):
        if self.request.GET.get('type'):
            return ['pokedata/list.html']
        return ['pokedata/index.html']
    

class PokemonCreate(SidebarMixin, CreateView):
    model         = Pokemon
    form_class    = PokemonForm
    template_name = "pokedata/create_pokemon.html"
    success_url   = reverse_lazy('pokemon_list')


class PokemonUpdate(SidebarMixin, UpdateView):
    model         = Pokemon
    form_class    = PokemonForm
    template_name_suffix = "_update_form"
    success_url   = reverse_lazy('pokemon_list')

class PokemonDelete(SidebarMixin, DeleteView):
    model         = Pokemon
    template_name = "pokedata/pokemon_confirm_delete.html"
    success_url   = reverse_lazy('pokemon_list')


def api_home(request):
    return render(request, 'pokedata/api_home.html', {
        'gen_choices': Generation.choices,
        'type_choices': PokemonType.choices,
    })