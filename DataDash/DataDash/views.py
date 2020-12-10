from django.http import HttpResponse
from django.shortcuts import render


def hello(request):
    # return render(request, 'index.html')
    return render(request, 'index.html')


def runoob(request):
    context = {}
    context['hello'] = 'Hello MB!'
    return render(request, 'runoob.html', context)

def runooblist(request):
    context = ['one','cao','bi']
    return render(request, 'runoob.html', {'fuck':context,'name':'picture'})