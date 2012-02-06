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
#        create_api_key(User, instance=testapp, created=True)

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
#        create_api_key(User, instance=testapp, created=True)

        data = {"date" : "2012-02-05T10:10:10",
                "long_desc" : "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas vel dui mi, non ornare felis. Proin non urna libero. Ut nec enim elit. Integer iaculis, nisi ac sollicitudin tristique, augue justo adipiscing urna, ac venenatis quam eros sit amet nunc. Duis ultricies, erat at fringilla sollicitudin, libero eros adipiscing odio, ut vulputate velit sapien at nibh. Nullam imperdiet, felis eu egestas fringilla, est augue sodales nisl, non vehicula felis nisi sed ligula. Suspendisse potenti.Nullam at adipiscing neque. Morbi ornare, tortor non porttitor tincidunt, elit quam accumsan lectus, ut fringilla odio purus sed erat. Maecenas lacinia sagittis dignissim. In hac habitasse platea dictumst. Vestibulum cursus enim a neque malesuada vel mattis augue lacinia. Donec semper, lectus ut ornare porta, justo mauris vestibulum leo, et vehicula magna metus at magna. Nulla vel elit velit, vitae facilisis mauris. Fusce adipiscing tristique ligula, in ornare odio auctor eget. Vestibulum nec ante non turpis lobortis scelerisque.Aenean aliquet metus non quam egestas at sagittis felis eleifend. Quisque fringilla, leo sed lacinia hendrerit, eros lorem fringilla justo, in ultricies augue augue sed mauris. Donec eleifend massa vel ipsum convallis porttitor. Suspendisse sit amet ante neque, ac hendrerit nunc. Aenean bibendum, eros et laoreet commodo, nunc diam ornare velit, et bibendum dui ligula eu libero. Donec in lacus vitae mauris semper sollicitudin. Nullam pulvinar urna nec tellus facilisis dignissim. Praesent arcu leo, cursus et blandit vitae, luctus ac arcu. Quisque laoreet ipsum sit amet nulla accumsan sed mattis risus laoreet. Aliquam sed tincidunt diam. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Vivamus mattis mauris vitae mauris facilisis ac lobortis leo aliquam. Quisque interdum, quam sollicitudin vulputate pharetra, turpis metus venenatis justo, vitae tempus turpis tellus in velit. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Sed eget sapien et nisi dictum fringilla bibendum vitae quam.Sed luctus adipiscing lacus, in congue arcu fermentum vel. Aenean nisl orci, sagittis at facilisis vel, dictum vel dui. Cras venenatis erat in dui interdum molestie. Vestibulum auctor fringilla sapien, et egestas dui iaculis a. Ut sem quam, molestie sit amet suscipit ut, pharetra egestas felis. Ut pharetra elementum suscipit. Donec a ligula at orci dignissim dignissim. Sed sollicitudin ultrices velit. Nulla facilisi. Quisque in eros quam, ultrices fringilla nunc.Sed eu feugiat quam. Cras tortor leo, convallis nec elementum et, tincidunt venenatis purus. Aliquam erat volutpat. Ut eros nulla, fringilla et lobortis quis, faucibus et justo. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Fusce tempus nisl at purus malesuada porttitor. Sed eu ligula sapien, ac rutrum metus.",
                "short_desc" : "This is a short description",
                "user" : 2
                }


        print self.api_uri + testapp.api_key.key
        resp = self.client.post(self.api_uri + testapp.api_key.key, data)
        self.assertEqual(resp.status_code, 200)
        
