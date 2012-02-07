"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.conf import settings
from tastypie.api import Api
from django.contrib.auth.models import User, Permission
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import ApiKeyAuthentication
from tastypie.models import create_api_key, ApiKey
from log.models import LogMessage
import simplejson as json
from django.test import TestCase
from django.http import HttpRequest

class RestTest(TestCase):
    fixtures = ['auth.json']

    username = "testapp"
    api_uri = "/api/log/?username=" + username + "&api_key="
    api_key = ""
    

    def setUp(self):
        """
        Creates an api key for test user(from fixture) and sets permission to add logmessages
        """
        super(RestTest, self).setUp()
        ApiKey.objects.all().delete()        
        create_api_key(User, instance=User.objects.get(username='testapp'), created=True)
        add_logmessage = Permission.objects.get(codename='add_logmessage')
        User.objects.get(username='testapp').user_permissions.add(add_logmessage)
    

    def test_auth(self):
        """
        Tests user authentication using APIKEY and username
        """
        auth = ApiKeyAuthentication()
        request = HttpRequest()

        testapp = User.objects.get(username='testapp')

        request.GET['username'] = 'testapp'
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
        data = {"severity": 0 , "datetime" : "2012-10-10T10:10:10" } #wellformed data
        resp = self.client.post("/api/log/", data)
        self.assertEqual(resp.status_code, 401) #Unauthorized
            
    def test_post(self):
        """
        Tests various types of content we're trying to submit. 
        """
        testapp = User.objects.get(username='testapp')

        # Missing datetime
        data = {"severity": 0}
        resp = self.client.post(self.api_uri + testapp.api_key.key, json.dumps(data), content_type='application/json')
        self.assertNotEqual(resp.status_code, 201)
        
        # Datetime malformed. 
        data = {"severity": 0,
                "datetime" : "2",
                "long_desc" : "data",
                "short_desc" : "This is a short description"}
        resp = self.client.post(self.api_uri + testapp.api_key.key, json.dumps(data), content_type='application/json')
        self.assertNotEqual(resp.status_code, 201)

        # Severity out of scope
        data = {"severity": 15,
                "datetime" : "2012-02-05T10:10:10",
                "long_desc" : "data",
                "short_desc" : "This is a short description"}
        resp = self.client.post(self.api_uri + testapp.api_key.key, json.dumps(data), content_type='application/json')
        self.assertNotEqual(resp.status_code, 201) # Internal server error

        # long_desc or short_desc is possible to be without
        data = {"severity": 0,
                "datetime" : "2012-02-05T10:10:10"} 
        resp = self.client.post(self.api_uri + testapp.api_key.key, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 201) # CREATED

        # Successful post and wellformed post
        data = {"severity": 0,
                "datetime" : "2012-02-05T10:10:10",
                "long_desc" : "This is a long description",
                "short_desc" : "This is a short description"}

        resp = self.client.post(self.api_uri + testapp.api_key.key, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 201) #201=CREATED

