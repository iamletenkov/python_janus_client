import unittest
import logging
import asyncio
import os

from aiortc.contrib.media import MediaPlayer, MediaRecorder

from janus_client import (
    JanusTransport,
    JanusSession,
    JanusVideoRoomPlugin,
)
from test.util import async_test

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
logger = logging.getLogger()


class BaseTestClass:
    class TestClass(unittest.TestCase):
        server_url: str

        async def asyncSetUp(self) -> None:
            self.transport = JanusTransport.create_transport(base_url=self.server_url)
            await self.transport.connect()

        async def asyncTearDown(self) -> None:
            await self.transport.disconnect()
            # https://docs.aiohttp.org/en/stable/client_advanced.html#graceful-shutdown
            # Working around to avoid "Exception ignored in: <function _ProactorBasePipeTransport.__del__ at 0x0000024A04C60280>"
            await asyncio.sleep(0.250)

        @async_test
        async def test_create_edit_destroy(self):
            await self.asyncSetUp()

            session = JanusSession(transport=self.transport)

            plugin = JanusVideoRoomPlugin()

            await plugin.attach(session=session)

            room_id = 123

            response = await plugin.destroy_room(room_id)
            self.assertFalse(response)

            response = await plugin.edit(room_id)
            self.assertFalse(response)

            response = await plugin.create_room(room_id)
            self.assertTrue(response)

            response = await plugin.edit(room_id)
            self.assertTrue(response)

            response = await plugin.destroy_room(room_id)
            self.assertTrue(response)

            await session.destroy()

            await self.asyncTearDown()

        @async_test
        async def test_exists(self):
            await self.asyncSetUp()

            session = JanusSession(transport=self.transport)

            plugin = JanusVideoRoomPlugin()

            await plugin.attach(session=session)

            room_id = 123

            response = await plugin.exists(room_id)
            self.assertFalse(response)

            response = await plugin.destroy_room(room_id)
            self.assertFalse(response)

            response = await plugin.create_room(room_id)
            self.assertTrue(response)

            response = await plugin.exists(room_id)
            self.assertTrue(response)

            response = await plugin.destroy_room(room_id)
            self.assertTrue(response)

            await session.destroy()

            await self.asyncTearDown()

        @async_test
        async def test_allowed(self):
            """Test "allowed" API.

            This is a dummy test to increase coverage.
            """
            await self.asyncSetUp()

            session = JanusSession(transport=self.transport)

            plugin = JanusVideoRoomPlugin()

            await plugin.attach(session=session)

            room_id = 123

            response = await plugin.create_room(room_id)
            self.assertTrue(response)

            response = await plugin.allowed(room_id)
            self.assertTrue(response)

            response = await plugin.destroy_room(room_id)
            self.assertTrue(response)

            await session.destroy()

            await self.asyncTearDown()

        @async_test
        async def test_kick(self):
            """Test "kick" API."""
            await self.asyncSetUp()

            session = JanusSession(transport=self.transport)

            plugin = JanusVideoRoomPlugin()

            await plugin.attach(session=session)

            room_id = 123

            response = await plugin.create_room(room_id)
            self.assertTrue(response)

            response = await plugin.kick(room_id=room_id, id=22222)
            self.assertFalse(response)

            response = await plugin.destroy_room(room_id)
            self.assertTrue(response)

            await session.destroy()

            await self.asyncTearDown()

        @async_test
        async def test_moderate(self):
            """Test "kick" API."""
            await self.asyncSetUp()

            session = JanusSession(transport=self.transport)

            plugin = JanusVideoRoomPlugin()

            await plugin.attach(session=session)

            room_id = 123

            response = await plugin.create_room(room_id)
            self.assertTrue(response)

            response = await plugin.moderate(
                room_id=room_id, id=22222, mid="0", mute=True
            )
            self.assertFalse(response)

            response = await plugin.destroy_room(room_id)
            self.assertTrue(response)

            await session.destroy()

            await self.asyncTearDown()

        @async_test
        async def test_list_room(self):
            """Test "list" API."""
            await self.asyncSetUp()

            session = JanusSession(transport=self.transport)

            plugin = JanusVideoRoomPlugin()

            await plugin.attach(session=session)

            room_id = 123

            response = await plugin.create_room(room_id)
            self.assertTrue(response)

            room_list = await plugin.list_room()
            self.assertTrue(
                len(list(filter(lambda room: room["room"] == room_id, room_list))) > 0
            )

            response = await plugin.destroy_room(room_id)
            self.assertTrue(response)

            await session.destroy()

            await self.asyncTearDown()

        @async_test
        async def test_list_participants(self):
            """Test "listparticipants" API."""
            await self.asyncSetUp()

            session = JanusSession(transport=self.transport)

            plugin = JanusVideoRoomPlugin()

            await plugin.attach(session=session)

            room_id = 123

            response = await plugin.create_room(room_id)
            self.assertTrue(response)

            room_list = await plugin.list_participants(room_id=room_id)
            self.assertListEqual(room_list, [])

            response = await plugin.destroy_room(room_id)
            self.assertTrue(response)

            await session.destroy()

            await self.asyncTearDown()

        @async_test
        async def test_join_and_leave(self):
            """Test "listparticipants" API."""
            await self.asyncSetUp()

            session = JanusSession(transport=self.transport)

            plugin = JanusVideoRoomPlugin()

            await plugin.attach(session=session)

            room_id = 123

            response = await plugin.create_room(room_id)
            self.assertTrue(response)

            response = await plugin.join(room_id=room_id)
            self.assertTrue(response)

            response = await plugin.leave()
            self.assertTrue(response)

            response = await plugin.destroy_room(room_id)
            self.assertTrue(response)

            await session.destroy()

            await self.asyncTearDown()

        @async_test
        async def test_publish_and_unpublish(self):
            """Test "listparticipants" API."""
            await self.asyncSetUp()

            session = JanusSession(transport=self.transport)

            plugin = JanusVideoRoomPlugin()

            await plugin.attach(session=session)

            room_id = 12345

            response = await plugin.destroy_room(room_id)
            self.assertFalse(response)

            response = await plugin.create_room(room_id)
            self.assertTrue(response)

            response = await plugin.join(
                room_id=room_id, display_name="Test video room"
            )
            self.assertTrue(response)

            # player = MediaPlayer(
            #     "http://download.tsi.telecom-paristech.fr/gpac/dataset/dash/uhd/mux_sources/hevcds_720p30_2M.mp4"
            # )
            player = MediaPlayer("./Into.the.Wild.2007.mp4")
            response = await plugin.publish(player=player)
            self.assertTrue(response)

            await asyncio.sleep(15)

            response = await plugin.unpublish()
            self.assertTrue(response)

            response = await plugin.leave()
            self.assertTrue(response)

            response = await plugin.destroy_room(room_id)
            self.assertTrue(response)

            await session.destroy()

            await self.asyncTearDown()

        @async_test
        async def test_publish_and_subscribe(self):
            """Test "listparticipants" API."""
            await self.asyncSetUp()

            session = JanusSession(transport=self.transport)

            plugin_publish = JanusVideoRoomPlugin()
            plugin_subscribe = JanusVideoRoomPlugin()

            await asyncio.gather(
                plugin_publish.attach(session=session),
                plugin_subscribe.attach(session=session),
            )

            room_id = 12345

            response = await plugin_publish.destroy_room(room_id)
            self.assertFalse(response)

            response = await plugin_publish.create_room(room_id)
            self.assertTrue(response)

            response = await plugin_publish.join(
                room_id=room_id, display_name="Test video room publish"
            )
            self.assertTrue(response)

            # response = await plugin_subscribe.join(
            #     room_id=room_id, display_name="Test video room subscribe"
            # )
            # self.assertTrue(response)

            # player = MediaPlayer(
            #     "http://download.tsi.telecom-paristech.fr/gpac/dataset/dash/uhd/mux_sources/hevcds_720p30_2M.mp4"
            # )
            player = MediaPlayer("./Into.the.Wild.2007.mp4")
            response = await plugin_publish.publish(player=player)
            self.assertTrue(response)

            await asyncio.sleep(10)

            participants = await plugin_subscribe.list_participants(room_id=room_id)
            self.assertEqual(len(participants), 1)

            output_filename_out = "./video_room_record_out.mp4"
            if os.path.exists(output_filename_out):
                os.remove(output_filename_out)
            recorder = MediaRecorder(output_filename_out)
            response = await plugin_subscribe.subscribe_and_start(
                room_id=room_id,
                recorder=recorder,
                stream={"feed": participants[0]["id"]},
            )
            self.assertTrue(response)

            await asyncio.sleep(30)

            response = await plugin_subscribe.unsubscribe()
            self.assertTrue(response)

            response = await plugin_publish.unpublish()
            self.assertTrue(response)

            response = await plugin_publish.leave()
            self.assertTrue(response)

            response = await plugin_publish.destroy_room(room_id)
            self.assertTrue(response)

            await session.destroy()

            await self.asyncTearDown()


# class TestTransportHttps(BaseTestClass.TestClass):
#     server_url = "https://janusmy.josephgetmyip.com/janusbase/janus"


class TestTransportWebsocketSecure(BaseTestClass.TestClass):
    server_url = "wss://janusmy.josephgetmyip.com/janusbasews/janus"
