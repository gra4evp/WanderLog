import asyncio
from typing import Any, Callable, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message


class AlbumMiddleware(BaseMiddleware):
    def __init__(self, latency: int | float = 0.1):
        self.latency = latency
        self.album_data: dict[str, dict[str, list[Message]]] = {}
    
    def collect_album_messages(self, event: Message):
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
