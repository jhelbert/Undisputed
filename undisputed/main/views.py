# Create your views here.
import twilio.twiml

from django.template import Context, loader
from django.http import HttpResponse
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from django import forms
from django.template import RequestContext

from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate,login, logout
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.core.exceptions import ValidationError

from django.core.files.base import ContentFile
from django.core.mail import send_mail
import base64
import hmac, sha
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F
from django.contrib import auth
from django.core.mail import send_mail
from django.core.mail import EmailMessage

from subprocess import *
from datetime import *


from random import choice

import os
import cgi
import hashlib
import urllib2
import json
import base64
import hmac
import settings


def incoming_text(request):
	return HttpResponse("aaa")