from repositories.calendar_repository import CalendarRepository
from utils.google_calendar_api import fetch_google_calendar_events
from models.calendar_event import CalendarEvent

class CalendarService:
    def __init__(self):
        self.repository = CalendarRepository()

    async def sync_google_calendar(self, user_id: str, access_token: str):
        google_events = await fetch_google_calendar_events(access_token)
        for event in google_events:
            calendar_event = CalendarEvent(
                id=event['id'],
                user_id=user_id,
                title=event['summary'],
                start_time=event['start']['dateTime'],
                end_time=event['end']['dateTime'],
                description=event.get('description', '')
            )
            await self.repository.add_event(calendar_event)

    async def get_user_events(self, user_id: str):
        return await self.repository.get_events(user_id)

    async def handle_webhook_update(self, event_data: dict):
        # Process the webhook data and update the database
        event = CalendarEvent(**event_data)
        await self.repository.update_event(event)