from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .forms import TodoForm
from .models import Todo


def home(request):
    return render(request=request,
                  template_name='todo/home.html')


def signupuser(request):
    if request.method == 'GET':
        return render(request=request,
                      template_name='todo/signupuser.html',
                      context={'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(username=request.POST['username'],
                                                password=request.POST['password1'])
                user.set_password(request.POST['password1'])
                user.save()
                login(request=request, user=user)
                return redirect(to="currenttodos")
            except IntegrityError:
                return render(request=request,
                              template_name='todo/signupuser.html',
                              context={'form': UserCreationForm(), 'error': "That username is already been taken."})
        else:
            return render(request=request,
                          template_name='todo/signupuser.html',
                          context={'form': UserCreationForm(), 'error': "Your passwords did not match."})


def loginuser(request):
    if request.method == 'GET':
        return render(request=request,
                      template_name='todo/loginuser.html',
                      context={'form': AuthenticationForm()})
    else:
        user = authenticate(request=request,
                            username=request.POST['username'],
                            password=request.POST['password'])
        if user is None:
            return render(request=request,
                          template_name='todo/loginuser.html',
                          context={'form': AuthenticationForm(),
                                   'error': "Your username and password did not match"})
        else:
            login(request=request, user=user)
            return redirect(to="currenttodos")


def currenttodos(request):
    todos = Todo.objects.filter(user=request.user, date_completed__isnull=True)
    return render(request=request,
                  template_name='todo/currenttodos.html',
                  context={'todos': todos})


@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect(to='home')


@login_required
def createtodo(request):
    if request.method == 'GET':
        return render(request=request,
                      template_name='todo/createtodo.html',
                      context={'form': TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect(to='currenttodos')
        except ValueError:
            return render(request=request,
                          template_name='todo/createtodo.html',
                          context={'form': TodoForm(), 'error': 'This Input is not accepted'})


@login_required
def viewtodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request=request,
                      template_name='todo/viewtodo.html',
                      context={'todo': todo, 'form': form})
    else:
        form = None
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect(to='currenttodos')
        except ValueError:
            return render(request=request,
                          template_name='todo/viewtodo.html',
                          context={'todo': todo, 'form': form, 'error': "Bad Input Please try again."})


@login_required
def completetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.date_completed = timezone.now()
        todo.save()
        return redirect(to='currenttodos')


@login_required
def deletetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect(to='currenttodos')


@login_required
def completedtodos(request):
    todos = Todo.objects.filter(user=request.user, date_completed__isnull=False).order_by('-date_completed')
    return render(request=request,
                  template_name='todo/completedtodos.html',
                  context={'todos': todos})
