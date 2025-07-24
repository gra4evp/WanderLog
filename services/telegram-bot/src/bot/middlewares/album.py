import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message


class AlbumMiddleware(BaseMiddleware):
    """Middleware for collecting and processing media group (album) messages in Aiogram."""

    def __init__(self, latency: int | float = 0.1):
        """
        Initialize the AlbumMiddleware.

        Args:
        ----
            latency (int | float, optional): Time in seconds to wait for collecting album messages. Defaults to 0.1.

        """
        self.latency = latency
        self.album_data: dict[str, dict[str, list[Message]]] = {}

    def collect_album_messages(self, event: Message):
        """
        Collects messages that belong to the same media group (album).

        Args:
        ----
            event (Message): The incoming message event to collect.

        Returns:
        -------
            int: The total number of messages collected for the media group so far.

        """
        # Check if media_group_id exists in album_data
        if event.media_group_id not in self.album_data:
            self.album_data[event.media_group_id] = {'messages': []}

        self.album_data[event.media_group_id]['messages'].append(event)

        return len(self.album_data[event.media_group_id]['messages'])

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any]
    ) -> Any:
        """
        Middleware entry point for processing incoming messages.

        Collects album messages and passes them to the handler when the album is complete.

        Args:
        ----
            handler (Callable): The next handler to process the message.
            event (Message): The incoming message event.
            data (dict): Additional data/context for the handler.

        Returns:
        -------
            Any: The result of the handler call, or None if the message is not yet ready to be processed as part of an album.

        """
        if event.media_group_id is None:
            return await handler(event, data)

        # Collect message of the same media group
        total_before = self.collect_album_messages(event)
        print(f"total_before: {total_before}")

        #Wait for a specified
        await asyncio.sleep(self.latency)

        total_after = len(self.album_data[event.media_group_id]['messages'])

        # If new messages were added during the latency, exit
        if total_before != total_after:
            return

        # Sort the album messages by message_id and add to data
        album_messages = self.album_data[event.media_group_id]['messages']
        album_messages.sort(key=lambda m: m.message_id)
        data['album'] = album_messages

        # Call the original event handler
        await handler(event,  data)

        # Remove the media group from tracking to free up memory
        del self.album_data[event.media_group_id]
