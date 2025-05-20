from django.shortcuts import render,redirect

def sending(response):
    return render(response, 'index.html')


def about(response):
    return render(response, 'about.html')