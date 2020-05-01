from django.shortcuts import render, HttpResponse
from compounds.models import CompoundType, Compound


def compound_view(request):
    compound_types = CompoundType.objects.values('id', 'type', 'description')

    for compound_type in compound_types:
        compounds = {}
        compounds_temp = list(Compound.objects.filter(compound_type=compound_type['id']).values_list('id', flat=True))
        print(compounds_temp)
        for compound in compounds_temp:
            if compound not in compounds.keys():
                compounds[compound] = list(Compound.objects.filter(pk=compound).values('id', 'compound', 'photo', 'description'))[0]
        compound_type['compounds'] = compounds

    compound_types = list(compound_types)
    print(compound_types)

    return render(request, 'compounds.html', {
        'compound_types': compound_types,
        'compounds': compounds
    })


def compound(request):

    compound = request.GET.get('compound')
    compound_inst = Compound.objects.filter(compound=compound)
    compound_dict = compound_inst.values()[0]
    print(compound_dict)
    return render(request, 'compound.html', compound_dict)

