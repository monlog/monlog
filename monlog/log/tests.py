"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.conf import settings
from tastypie.api import Api
from django.contrib.auth.models import User, Permission
from tastypie.authorization import DjangoAuthorization
from monlog.log.api.authentication import MonlogAuthentication
from tastypie.models import create_api_key, ApiKey
from monlog.log.models import LogMessage,Label
from monlog.log.api.validation import LogValidation
import simplejson as json
from django.test import TestCase
from django.test.client import RequestFactory
from django.http import HttpRequest,HttpResponse,HttpResponseBadRequest
from tastypie.authentication import Authentication
from monlog.log.views import save_label
import logging

class MonlogTestCase(TestCase):
    fixtures = ['auth.json']

    username = "testapp"
    userpass = "test"

class ModelTest(MonlogTestCase):

    def setUp(self):
        login = self.client.login(username=self.username, password=self.userpass)
        if not login:
            print "Couldn't log in!"

    def test_save_label(self):
        """ Testing if label saving works """

        # Check for HttpResponseBadRequest if `name` or `query_string` not provided.
        data = {}
        response = self.client.post("/label/save", data)
        self.assertEqual(response.status_code, 400)

        # Valid post should work correctly.
        data['name']="validname"
        data['query_string']="severity__in=0" # also valid
        response = self.client.post("/label/save", data)
        self.assertEqual(response.status_code, 200)

class RestTest(MonlogTestCase):
    api_uri = "/api/log/?api_key="

    logmessages_uri = "/api/logmessages/"

    def setUp(self):
        """
        Creates an api key for test user(from fixture) and sets permission to add logmessages
        """
        super(RestTest, self).setUp()
        ApiKey.objects.all().delete()
        create_api_key(User, instance=User.objects.get(username=self.username), created=True)
        add_logmessage = Permission.objects.get(codename='add_logmessage')
        User.objects.get(username=self.username).user_permissions.add(add_logmessage)


    def test_auth(self):
        """
        Tests user authentication using APIKEY and username
        """
        auth = MonlogAuthentication()
        request = HttpRequest()

        testapp = User.objects.get(username=self.username) #API key created in setUp()
        request.GET['api_key'] = testapp.api_key.key 

        self.assertEqual(auth.is_authenticated(request), True)

    def test_get_from_rest(self):
        """
        Testing if we can use GET-method from the rest api. This should not be possible.
        """
        response = self.client.get("/api/log/")
        self.assertEqual(response.status_code, 405) #Method not allowed


    def test_unauth_post(self):
        """
        Tests if we can post without api key and user.
        """
        data = {"severity": 0 , "timestamp" : "1335169880" } #wellformed data
        resp = self.client.post("/api/log/", data)
        self.assertEqual(resp.status_code, 401) #Unauthorized
            
    def test_post(self):
        """
        Tests various types of content we're trying to submit. 
        """
        testapp = User.objects.get(username=self.username)

        # Missing timestamp
        data = {"severity": 0}
        resp = self.client.post(self.api_uri + testapp.api_key.key, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        
        # Datetime malformed, missing lots of stuff
        data = {"severity": 0,
                "timestamp" : "2001-02-22T12:12:12Z"}
        resp = self.client.post(self.api_uri + testapp.api_key.key, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 400)


        # Severity out of scope
        data = {"severity": 15,
                "timestamp" : "1335169880",
                "long_desc" : "data",
                "short_desc" : "This is a short description"}
        resp = self.client.post(self.api_uri + testapp.api_key.key, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 400)

        # long_desc or short_desc is possible to be without
        data = {"severity": 0,
                "timestamp" : "1335169660"} 
        resp = self.client.post(self.api_uri + testapp.api_key.key, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 201) # CREATED

        # Successful post and wellformed post
        data = {"severity": 0,
                "timestamp" : "1335169880",
                "long_desc" : "This is a long description",
                "short_desc" : "This is a short description"}

        resp = self.client.post(self.api_uri + testapp.api_key.key, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 201) #201=CREATED

