from fastapi import APIRouter, Depends, HTTPException
from services.calendar_service import CalendarService
from core.security import get_current_user
from models.calendar_event import CalendarEvent

router = APIRouter()

@router.post("/sync")
async def sync_calendar(current_user: dict = Depends(get_current_user)):
    service = CalendarService()
    await service.sync_google_calendar(current_user['id'], current_user['access_token'])
    return {"message": "Calendar synced successfully"}

@router.get("/events")
async def get_events(current_user: dict = Depends(get_current_user)):
    service = CalendarService()
    events = await service.get_user_events(current_user['id'])
    return events

@router.post("/webhook")
async def calendar_webhook(event_data: dict):
    service = CalendarService()
    await service.handle_webhook_update(event_data)
    return {"message": "Webhook processed successfully"}