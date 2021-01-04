import json

from django.contrib.auth import authenticate, login
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import user_passes_test

from app.models import Movie, Seat, Ticket


def list_movies(request):
    return render(request, 'app/movies.html', {
        'movies': Movie.objects.all()
    })


def list_seats(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    seats = Seat.objects.exclude(ticket__movie_id=movie_id)

    return render(request, 'app/seats.html', {
        'movie': movie,
        'seats': seats
    })


def reserve_seat(request, movie_id, seat_id):
    if request.user.is_authenticated:
        movie_obj = Movie.objects.filter(pk=movie_id).first()
        seat_obj = Seat.objects.filter(pk=seat_id).first()
        ticket_obj = Ticket.objects.create(movie=movie_obj, seat=seat_obj, user=request.user)
        ticket_obj.save()
        return redirect('list_seats', movie_id=movie_id)

    return redirect('login')


@user_passes_test(lambda u: u.is_superuser)
def stats(request):
    seats = Seat.objects.filter(ticket__isnull=False).annotate(c_count=Count('ticket'))
    res = list()
    for seat in seats:
        seat_result = dict()
        seat_result['seat__number'] = seat.id
        seat_result['total'] = seat.c_count
        res.append(seat_result)

    return JsonResponse(res, safe=False)


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            new_user = authenticate(username=username, password=password)
            login(request, new_user)
            return redirect('list_movies')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})
