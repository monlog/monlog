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
        super(RestTest, self).setUp()
        ApiKey.objects.all().delete()        
        create_api_key(User, instance=User.objects.get(username='testapp'), created=True)
        add_logmessage = Permission.objects.get(codename='add_logmessage')
        User.objects.get(username='testapp').user_permissions.add(add_logmessage)
    

    def test_auth(self):
        auth = ApiKeyAuthentication()
        request = HttpRequest()

        testapp = User.objects.get(username='testapp')

        request.GET['username'] = 'testapp'
        request.GET['api_key'] = testapp.api_key.key
        
        self.assertEqual(auth.is_authenticated(request), True)
                

    def test_get_from_rest(self):
        """
        Testing if we can get from the rest api. This should not be possible.
        """
        response = self.client.get("/api/log/")
        self.assertEqual(response.status_code, 405)


    def test_unauth_post(self):
        """
        Tests if we can post without api key and user.
        """
        data = {}
        resp = self.client.post("/api/log/", data)
        self.assertEqual(resp.status_code, 401)
        

    def test_success_post(self):
        auth = ApiKeyAuthentication()

        testapp = User.objects.get(username='testapp')

        data = {"severity": 0,
                "server_ip" : "192.168.0.1",
                "application": "1" ,
                "datetime" : "2012-02-05T10:10:10",
                "long_desc" : "data",
                "short_desc" : "This is a short description"}

        resp = self.client.post(self.api_uri + testapp.api_key.key, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 201) #201=CREATED
        
