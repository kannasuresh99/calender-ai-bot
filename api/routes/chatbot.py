from fastapi import APIRouter, Depends
from services.chatbot_service import ChatbotService
from core.security import get_current_user

router = APIRouter()

@router.post("/query")
async def chatbot_query(query: str, current_user: dict = Depends(get_current_user)):
    service = ChatbotService()
    response = await service.process_query(current_user['id'], query)
    return {"response": response}