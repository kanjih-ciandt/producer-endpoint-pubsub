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
import datetime
from random import randint

from protorpc import messages
from protorpc import remote
from google.cloud import pubsub


import os
import json
from json import JSONDecoder
from json import JSONEncoder

from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop

# [START NDB]
class MessageMock(ndb.Model):
    fromApp = ndb.StringProperty()
    messageType = ndb.StringProperty()
    jsonMsg = ndb.StringProperty()


# [END]


# [START messages]

class AddMessageMockRequest (messages.Message):
    fromApp = messages.StringField(1)
    messageType = messages.StringField(2)

class SendMessageRequest (messages.Message):
    topic = messages.StringField(1)
    numberOfMessage = messages.IntegerField(2)
    messageType = messages.StringField(3)

class DefaultResponse(messages.Message):
    content  = messages.StringField(1)

ADD_MSG_RESOURCE = endpoints.ResourceContainer(
    AddMessageMockRequest,
    jsonMessage = messages.StringField(2))

GET_MSG_RESOURCE = endpoints.ResourceContainer(
    messageType = messages.StringField(1))

SEND_MSG_RESOURCE = endpoints.ResourceContainer(SendMessageRequest)

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

        info = MessageMock(fromApp=request.fromApp, messageType=request.messageType, jsonMsg = request.jsonMessage)

        info.key = ndb.Key(MessageMock, request.messageType)
        info.put()

        output_content = request.jsonMessage
        return DefaultResponse(content=output_content)

    @endpoints.method(
        # This method takes an empty request body.
        GET_MSG_RESOURCE,
        # This method returns an Echo message.
        DefaultResponse,
        path='loadpubsub/getMock',
        http_method='GET',
        # Require auth tokens to have the following scopes to access this API.
        scopes=[endpoints.EMAIL_SCOPE],
        name='getMock')
    def getMock(self, request):
        user = endpoints.get_current_user()
        # If there's no user defined, the request was unauthenticated, so we
        # raise 401 Unauthorized.
        if not user:
            raise endpoints.UnauthorizedException

        query = ndb.Key(MessageMock, request.messageType).get()
        print query

        return DefaultResponse(content=query.jsonMsg)

    @endpoints.method(
        # This method takes an empty request body.
        SEND_MSG_RESOURCE,
        # This method returns an Echo message.
        DefaultResponse,
        path='loadpubsub/sendMessage',
        http_method='POST',
        # Require auth tokens to have the following scopes to access this API.
        scopes=[endpoints.EMAIL_SCOPE],
        name='sendMessage')
    def sendMessage(self, request):
        user = endpoints.get_current_user()
        # If there's no user defined, the request was unauthenticated, so we
        # raise 401 Unauthorized.
        if not user:
            raise endpoints.UnauthorizedException

        query = ndb.Key(MessageMock, request.messageType).get()
        publisher = pubsub.Client()
        topic = publisher.topic(request.topic)

        for x in xrange(request.numberOfMessage):
            msg = self._processDinamycFields(query.jsonMsg)

            print  msg

            topic.publish(msg)

        return DefaultResponse(content="Published messages.")



    def _processDinamycFields(self, jsonMsg):
        while jsonMsg.find('$RANDOM:DATE_GMT') > 0:
            t = datetime.datetime.today()
            data = "{} {}:{:0>2d}.{:0>4d} GMT".format(t.date(), t.hour, randint(0, t.minute), randint(0, 59),
                                                      randint(0, 3000))
            jsonMsg = jsonMsg.replace('$RANDOM:DATE_GMT', data, 1)

        while jsonMsg.find('$RANDOM:ID') > 0:
            t = datetime.datetime.today()
            data = "{:0>3d}".format(randint(0, 999))
            jsonMsg = jsonMsg.replace('$RANDOM:ID', data, 1)

        while jsonMsg.find('$RANDOM:NBR') > 0:
            t = datetime.datetime.today()
            data = "{:0>8d}".format(randint(0, 99999999))
            jsonMsg = jsonMsg.replace('$RANDOM:NBR', data, 1)

        while jsonMsg.find('$RANDOM:QTDY') > 0:
            t = datetime.datetime.today()
            data = "{:0>2d}".format(randint(0, 999))
            jsonMsg = jsonMsg.replace('$RANDOM:QTDY', data, 1)

        while jsonMsg.find('$RANDOM:DATE') > 0:
            t = datetime.datetime.today()
            data = "{} {}:{:0>2d}:{:0>2d}".format(t.date(), t.hour, randint(0, t.minute), randint(0, 59))
            jsonMsg = jsonMsg.replace('$RANDOM:DATE', data, 1)

        return jsonMsg


    @endpoints.method(
        # This method takes an empty request body.
        SEND_MSG_RESOURCE,
        # This method returns an Echo message.
        DefaultResponse,
        path='loadpubsub/break',
        http_method='POST',
        # Require auth tokens to have the following scopes to access this API.
        scopes=[endpoints.EMAIL_SCOPE],
        name='break')
    def breakMessage(self, request):
        user = endpoints.get_current_user()
        # If there's no user defined, the request was unauthenticated, so we
        # raise 401 Unauthorized.
        if not user:
            raise endpoints.UnauthorizedException

        query = ndb.Key(MessageMock, request.messageType).get()

        for x in xrange(request.numberOfMessage):
            xpto = query.jsonMsg

            print self._processDinamycFields(query.jsonMsg)





        return DefaultResponse(content="Done")

# [END echo_api]


# [START api_server]
api = endpoints.api_server([LoadPubSubApi])
# [END api_server]