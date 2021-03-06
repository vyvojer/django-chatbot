import copy
from dataclasses import dataclass
from typing import List
from unittest import TestCase

from django.utils import timezone

from django_chatbot.telegram.types import CallbackQuery, Chat, Message, \
    TelegramType, Update, \
    User


class TelegramTypeTestCase(TestCase):
    def test_get_telegram_type__type(self):
        telegram_type = TelegramType._get_telegram_type(User)
        self.assertEqual(telegram_type, User)

        telegram_type = TelegramType._get_telegram_type(int)
        self.assertEqual(telegram_type, None)

    def test_get_telegram_type__str(self):
        telegram_type = TelegramType._get_telegram_type('User')
        self.assertEqual(telegram_type, User)
        telegram_type = TelegramType._get_telegram_type('int')
        self.assertEqual(telegram_type, None)

    def test_from_timestamp(self):
        timestamp = 1441645532
        dt = TelegramType._from_timestamp(timestamp)
        self.assertEqual(dt, timezone.datetime(
            2015, 9, 7, 17, 5, 32, tzinfo=timezone.utc))

    def test_from_dict(self):
        source_data = {
            "parent_p1": 1,
            "parent_p2": {
                "child_p1": [
                    {"grandchild_p1": 5, "grandchild_p2": ["a", "b"]},
                    {"grandchild_p1": 6, "grandchild_p2": ["c", "d"]},
                    {"grandchild_p1": 7, "grandchild_p2": ["e", "f"]},
                ],
                "child_p2": 2,
                "child_p3": [[
                    {"grandchild_p1": 5, "grandchild_p2": ["a", "b"]},
                    {"grandchild_p1": 6, "grandchild_p2": ["c", "d"]},
                    {"grandchild_p1": 7, "grandchild_p2": ["e", "f"]},
                ]],
            }
        }
        source = copy.deepcopy(source_data)

        @dataclass(frozen=True)
        class GrandChild(TelegramType):
            grandchild_p1: int
            grandchild_p2: List[str]

        @dataclass(frozen=True)
        class Child(TelegramType):
            child_p1: List[GrandChild]
            child_p2: int
            child_p3: List[List[GrandChild]]

        @dataclass(frozen=True)
        class Parent(TelegramType):
            parent_p1: int
            parent_p2: Child

        parent = Parent.from_dict(source=source)

        self.assertEqual(
            parent,
            Parent(
                parent_p1=1,
                parent_p2=Child(
                    child_p1=[
                        GrandChild(5, ["a", "b"]),
                        GrandChild(6, ["c", "d"]),
                        GrandChild(7, ["e", "f"]),
                    ],
                    child_p2=2,
                    child_p3=[[
                        GrandChild(5, ["a", "b"]),
                        GrandChild(6, ["c", "d"]),
                        GrandChild(7, ["e", "f"]),
                    ]],
                )
            )
        )
        self.assertEqual(source, source_data)

    def test_to_dict(self):
        @dataclass(frozen=True)
        class GrandChild(TelegramType):
            grandchild_p1: int
            grandchild_p2: List[str]

        @dataclass(frozen=True)
        class Child(TelegramType):
            child_p1: List[GrandChild]
            child_p2: int

        @dataclass(frozen=True)
        class Parent(TelegramType):
            parent_p1: int
            parent_p2: Child

        parent = Parent(
            parent_p1=1,
            parent_p2=Child(
                child_p1=[
                    GrandChild(5, ["a", "b"]),
                    GrandChild(6, ["c", "d"]),
                    GrandChild(7, ["e", "f"]),
                ],
                child_p2=2,
            )
        )

        as_dict = parent.to_dict()

        self.assertEqual(
            as_dict,
            {
                "parent_p1": 1,
                "parent_p2": {
                    "child_p1": [
                        {"grandchild_p1": 5, "grandchild_p2": ["a", "b"]},
                        {"grandchild_p1": 6, "grandchild_p2": ["c", "d"]},
                        {"grandchild_p1": 7, "grandchild_p2": ["e", "f"]},
                    ],
                    "child_p2": 2,
                }
            }
        )


class UpdateTestCase(TestCase):
    def test_init(self):
        source = {
            "update_id": 10000,
            "message": {
                "date": 1,
                "chat": {
                    "last_name": "Test Lastname",
                    "id": 1111111,
                    "type": "private",
                    "first_name": "Test Firstname",
                    "username": "Testusername"
                },
                "message_id": 1365,
                "from": {
                    "last_name": "Test Lastname",
                    "id": 1111111,
                    "is_bot": False,
                    "first_name": "Test Firstname",
                    "username": "Testusername"
                },
                "text": "/start"
            }
        }

        update = Update.from_dict(source)
        self.assertEqual(update.update_id, 10000)

    def test_effective_user__message(self):
        source = {
            "update_id": 10000,
            "message": {
                "date": 1441645532,
                "chat": {
                    "last_name": "Test Lastname",
                    "id": 1111111,
                    "type": "private",
                    "first_name": "Test Firstname",
                    "username": "Testusername"
                },
                "message_id": 1365,
                "from": {
                    "last_name": "Test Lastname",
                    "is_bot": False,
                    "id": 1111111,
                    "first_name": "Test Firstname",
                    "username": "Testusername"
                },
                'reply_to_message': {'message_id': 52,
                                     'from': {'id': 2222,
                                              'is_bot': False,
                                              'first_name': 'Fedor',
                                              'last_name': 'Sumkin',
                                              'username': 'fedor',
                                              'language_code': 'en'},
                                     'chat': {
                                         "last_name": "Test Lastname",
                                         "id": 1111111,
                                         "type": "private",
                                         "first_name": "Test Firstname",
                                         "username": "Testusername"
                                     },
                                     'date': 1441645532,
                                     'text': 'question'},
                "text": "/start"
            }
        }
        update = Update.from_dict(source)

        user = update.effective_user

        self.assertEqual(
            user,
            User(
                id=1111111,
                is_bot=False,
                username="Testusername",
                first_name="Test Firstname",
                last_name="Test Lastname",
            )
        )

    def test_effective_message(self):
        source = {
            "update_id": 10000,
            "message": {
                "date": 1441645532,
                "chat": {
                    "last_name": "Test Lastname",
                    "id": 1111111,
                    "type": "private",
                    "first_name": "Test Firstname",
                    "username": "Testusername"
                },
                "message_id": 1365,
                "from": {
                    "last_name": "Test Lastname",
                    "is_bot": False,
                    "id": 1111111,
                    "first_name": "Test Firstname",
                    "username": "Testusername"
                },
                "text": "/start"
            }
        }
        update = Update.from_dict(source)

        message = update.effective_message

        self.assertEqual(message.message_id, 1365)
        self.assertEqual(message.date, timezone.datetime(
            2015, 9, 7, 17, 5, 32, tzinfo=timezone.utc)
                         )
        self.assertEqual(message.text, '/start')


class UpdateFromDictTestCase(TestCase):
    """

    """

    def test_message_with_text(self):
        source = {
            "update_id": 10000,
            "message": {
                "date": 1441645532,
                "chat": {
                    "last_name": "Test Lastname",
                    "id": 1111111,
                    "type": "private",
                    "first_name": "Test Firstname",
                    "username": "Testusername"
                },
                "message_id": 1365,
                "from": {
                    "last_name": "Test Lastname",
                    "is_bot": False,
                    "id": 1111111,
                    "first_name": "Test Firstname",
                    "username": "Testusername"
                },
                "text": "/start"
            }
        }

        update = Update.from_dict(source=source)

        self.assertEqual(update.update_id, 10000)
        self.assertEqual(
            update,
            Update(
                update_id=10000,
                message=Message(
                    message_id=1365,
                    text="/start",
                    date=timezone.datetime(
                        2015, 9, 7, 17, 5, 32, tzinfo=timezone.utc
                    ),
                    chat=Chat(
                        id=1111111,
                        type="private",
                        username="Testusername",
                        first_name="Test Firstname",
                        last_name="Test Lastname",
                    ),
                    from_user=User(
                        id=1111111,
                        is_bot=False,
                        username="Testusername",
                        first_name="Test Firstname",
                        last_name="Test Lastname",
                    )
                )
            )
        )

    def test_callback_query(self):
        source = {
            "update_id": 10000,
            "callback_query": {
                "id": "4382bfdwdsb323b2d9",
                "chat_instance": "42a",
                "from": {
                    "last_name": "Test Lastname",
                    "is_bot": False,
                    "id": 1111111,
                    "first_name": "Test Firstname",
                    "username": "Testusername"
                },
                "data": "Data from button callback",
                "inline_message_id": "1234csdbsk4839"
            }
        }

        update = Update.from_dict(source=source)

        self.assertEqual(update.update_id, 10000)
        self.assertEqual(
            update,
            Update(
                update_id=10000,
                callback_query=CallbackQuery(
                    id="4382bfdwdsb323b2d9",
                    data="Data from button callback",
                    inline_message_id="1234csdbsk4839",
                    chat_instance="42a",
                    from_user=User(
                        id=1111111,
                        is_bot=False,
                        username="Testusername",
                        first_name="Test Firstname",
                        last_name="Test Lastname",
                    )
                )
            )
        )
