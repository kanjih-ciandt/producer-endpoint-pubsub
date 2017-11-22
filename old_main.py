#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import endpoints
from protorpc import message_types
from protorpc import messages
from protorpc import remote
import json
from json import JSONDecoder
from json import JSONEncoder

from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop

# [START NDB]
class MessagesJson(ndb.Model):
    name = ndb.StringProperty()
    msg = ndb.JsonProperty()
    value = ndb.StringProperty()


# [START NDB]
class MessageMock(ndb.Model):
    name = ndb.StringProperty()
    msg = ndb.StringProperty()


# [END]


# [START messages]

class EchoRequest(messages.Message):
    content = messages.StringField(1)


class MetaRequest(messages.Message):
    createDateTime = messages.StringField(1)
    fromApp = messages.StringField(2)
    messageType = messages.StringField(3)


class AddMessageMockRequest (messages.Message):
    fromApp = messages.StringField(1)
    messageType =  messages.StringField(2)
    messageFieldParent = messages.StringField(3)
    message = messages.StringField(4,repeated=True)



class InventoryMessageRequest (messages.Message):
    storeId = messages.StringField(1)
    skuNbr = messages.StringField(2)
    eventDateTime = messages.StringField(3)
    sfQtdy = messages.StringField(4)
    srQtdy = messages.StringField(5)
    siQtdy = messages.StringField(6)


class InventoryRequest (messages.Message):
    meta = messages.MessageField(MetaRequest,1)
    message = messages.MessageField(InventoryMessageRequest,2)
    messages = messages.MessageField(InventoryMessageRequest,3, repeated=True)

LOAD_INVENTORY_RESOURCE = endpoints.ResourceContainer(InventoryRequest)



class LoadPubSubRequest(messages.Message):
    number_of_msgs = messages.IntegerField(1)
    number_of_record_per_msg = messages.IntegerField(2)
    message_types = messages.IntegerField(3)




class DefaultResponse(messages.Message):
    content  = messages.StringField(1)

class EchoResponse(messages.Message):
    """A proto Message that contains a simple string field."""
    content = messages.StringField(1)



ECHO_RESOURCE = endpoints.ResourceContainer(
    EchoRequest,
    n=messages.IntegerField(2, default=1))


LOAD_PUBSUB_RESOURCE = endpoints.ResourceContainer(LoadPubSubRequest)

ADD_MSG_RESOURCE = endpoints.ResourceContainer(AddMessageMockRequest)




# [END messages]


# [START echo_api]
@endpoints.api(name='loadpubsub', version='v1')
class LoadPubSubApi(remote.Service):

    @endpoints.method(
        # This method takes a ResourceContainer defined above.
        ADD_MSG_RESOURCE,
        # This method returns an Echo message.
        DefaultResponse,
        path='addMessageMock',
        http_method='POST',
        scopes=[endpoints.EMAIL_SCOPE],
        name='addMessageMock')
    def addMessageMock(self, request):
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException




        output_content = "xpto"
        return DefaultResponse(content=output_content)

    @endpoints.method(
        # This method takes a ResourceContainer defined above.
        LOAD_INVENTORY_RESOURCE,
        # This method returns an Echo message.
        DefaultResponse,
        path='loadInventorySnap',
        http_method='POST',
        scopes=[endpoints.EMAIL_SCOPE],
        name='loadInventorySnap')
    def loadInventorySnapshot(self, request):
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException

        jsonString = JSONEncoder().encode({
            "count": 222,
            "year": 2012
        })

        info = MessagesJson(name="xpto",msg=json.dumps(jsonString), value = jsonString)
        key = request.meta.fromApp + request.meta.messageType
        print key
        info.key = ndb.Key('MessagesJson', key)
        info.put()

        output_content = "xpto"
        return DefaultResponse(content=output_content)

    @endpoints.method(
        # This method takes an empty request body.
        message_types.VoidMessage,
        # This method returns an Echo message.
        EchoResponse,
        path='loadpubsub/getAllMsg',
        http_method='GET',
        # Require auth tokens to have the following scopes to access this API.
        scopes=[endpoints.EMAIL_SCOPE],
        name = 'getAllMessages')
    def getAllMsg(self, request):
        user = endpoints.get_current_user()
        # If there's no user defined, the request was unauthenticated, so we
        # raise 401 Unauthorized.
        if not user:
            raise endpoints.UnauthorizedException


        query1 = ndb.Key(MessagesJson, 'GIVGIVInventorySnapshot').get()
        print query1



        return EchoResponse(content=query1.value)



    @endpoints.method(
        # This method takes a ResourceContainer defined above.
        ECHO_RESOURCE,
        # This method returns an Echo message.
        EchoResponse,
        path='xpto',
        http_method='POST',
        name='xpto')
    def echo(self, request):
        output_content = ' '.join([request.content] * request.n)
        return EchoResponse(content=output_content)

    @endpoints.method(
        # This method takes a ResourceContainer defined above.
        LOAD_PUBSUB_RESOURCE,
        # This method returns an Echo message.
        DefaultResponse,
        path='load',
        http_method='POST',
        scopes=[endpoints.EMAIL_SCOPE],
        name='load')
    def loadPubSub(self, request):
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException

        output_content = [request.content]
        return DefaultResponse(content=output_content)


    @endpoints.method(
        # This method takes an empty request body.
        message_types.VoidMessage,
        # This method returns an Echo message.
        EchoResponse,
        path='loadpubsub/getUserEmail',
        http_method='GET',
        # Require auth tokens to have the following scopes to access this API.
        scopes=[endpoints.EMAIL_SCOPE],
        # OAuth2 audiences allowed in incoming tokens.
        audiences=['your-oauth-client-id.com'])
    def get_user_email(self, request):
        user = endpoints.get_current_user()
        # If there's no user defined, the request was unauthenticated, so we
        # raise 401 Unauthorized.
        if not user:
            raise endpoints.UnauthorizedException
        return EchoResponse(content=user.email())
# [END echo_api]


# [START api_server]
api = endpoints.api_server([LoadPubSubApi])
# [END api_server]