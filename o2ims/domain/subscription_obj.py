# Copyright (C) 2021 Wind River Systems, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import annotations
from enum import Enum
from dataclasses import dataclass

from o2common.domain.base import AgRoot, Serializer


class Subscription(AgRoot, Serializer):
    def __init__(self, id: str, callback: str, consumersubid: str = '',
                 filter: str = '') -> None:
        super().__init__()
        self.subscriptionId = id
        self.callback = callback
        self.consumerSubscriptionId = consumersubid
        self.filter = filter

        self.version_number = 0


class NotificationEventEnum(str, Enum):
    CREATE = 0
    MODIFY = 1
    DELETE = 2


class Message2SMO(Serializer):
    def __init__(self, eventtype: NotificationEventEnum,
                 id: str, ref: str, updatetime: str) -> None:
        self.notificationEventType = eventtype
        self.objectRef = ref
        self.id = id
        self.updatetime = updatetime


class RegistrationMessage(Serializer):
    def __init__(self, eventtype: NotificationEventEnum, id: str = '',
                 updatetime: str = '') -> None:
        self.notificationEventType = eventtype
        self.id = id
        self.updatetime = updatetime


@dataclass
class EventState():
    Initial = 0
    # NotInstalled = 1
    Installing = 2
    Installed = 3
    Updating = 4
    Uninstalling = 5
    Abnormal = 6
    Deleting = 7
