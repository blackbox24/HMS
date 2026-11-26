"""Lockout response for django-axes.

Renders the branded locked page; for HTMX requests returns an HX-Redirect so
the lockout page isn't swapped inside the login form.
"""
import logging

from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse

logger = logging.getLogger(__name__)


def lockout_response(request, original_response=None, credentials=None):
    credentials = credentials or {}
    username = credentials.get('username') or request.POST.get('username', '')
    request.session['locked_username'] = username
    logger.warning('Account locked out: %s from %s', username,
                   request.META.get('REMOTE_ADDR'))

    if request.headers.get('HX-Request') == 'true':
        response = HttpResponse(status=200)
        response['HX-Redirect'] = reverse('accounts:locked')
        return response
    return render(request, 'accounts/locked.html', {
        'username': username,
        'locked_at': None,
    })


def locked(request):
    return render(request, 'accounts/locked.html', {
        'username': request.session.pop('locked_username', ''),
        'locked_at': None,
    })


def session_ended(request):
    return render(request, 'accounts/session_ended.html', {
        'username': request.session.pop('ended_username', ''),
    })
