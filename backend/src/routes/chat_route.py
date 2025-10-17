from fastapi import APIRouter,Request
from ..models.db_models import UserModel,ChatModel,MessageModel
from ..models.db_schemes import Chat,Message,User
from .route_schemes import CreateChatRequest,AgentMessageRequest
from datetime import datetime, timezone
from ..config import RedisClient, RedisMetaSessionSchema, RedisMessageSchema
from ..models.enums.role import Role

router = APIRouter(
    tags=["chats"],
)

@router.post("/users/{user_id}/chats")
async def create_user_chat(user_id: int,chat_request: CreateChatRequest):
    chat_model = ChatModel()
    user_model = UserModel()
    try:
        user = await user_model.get_user_by_id(user_id)
        if user is None:
            return {"error": "User not found"}
    except Exception as e:
        return {"error": str(e)}
    
    # check the pdf exis
    try:
        pdfs = await user_model.get_user_pdfs(user_id)
        print(pdfs)
        # find the pdf once (handles empty lists too)
        for pdf in pdfs:
            print("Checking PDF:", pdf.id)
        
        pdf = next((p for p in pdfs if getattr(p, "id", None) == chat_request.pdf_id), None)
        if pdf is None:
            return {"error": "PDF not found for this user"}
        print("PDF found:", pdf)
    except Exception as e:
        return {"error": str(e)}
    
    # create the chat
    try:
        title = f"Chat for PDF {pdf.filename} at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
        chat_object = Chat(user_id=user_id, pdf_id=chat_request.pdf_id, title=title)
        created_chat = await chat_model.create_chat(chat_object)
    except Exception as e:
        return {"error": str(e)}
    
    return created_chat



@router.get("/users/{user_id}/chats/{chat_id}")
async def get_user_chat(user_id: int, chat_id: int):
    chat_model = ChatModel()
    user_model = UserModel()
    try:
        user = await user_model.get_user_by_id(user_id)
        if user is None:
            return {"error": "User not found"}
    except Exception as e:
        return {"error": str(e)}
    
    try:
        chat =  await chat_model.get_chat_by_id(chat_id)
        if chat is None or chat.user_id != user_id:
            return {"error": "Chat not found for this user"}
    except Exception as e:
        return {"error": str(e)}
    
    return chat


@router.delete("/users/{user_id}/chats/{chat_id}")
async def delete_user_chat(user_id: int, chat_id: int):
    chat_model = ChatModel()
    user_model = UserModel()
    try:
        user = await user_model.get_user_by_id(user_id)
        if user is None:
            return {"error": "User not found"}
    except Exception as e:
        return {"error": str(e)}
    
    try:
        chat =  await chat_model.get_chat_by_id(chat_id)
        if chat is None or chat.user_id != user_id:
            return {"error": "Chat not found for this user"}
        
        deleted = await chat_model.delete_chat_by_id(chat_id)
        if not deleted:
            return {"error": "Failed to delete chat"}
    except Exception as e:
        return {"error": str(e)}
    
    return {"detail": "Chat deleted successfully"}


@router.get("/users/{user_id}/chats/{chat_id}/messages")
async def get_chat_messages(user_id: int, chat_id: int):
    chat_model = ChatModel()
    user_model = UserModel()
    try:
        user = await user_model.get_user_by_id(user_id)
        if user is None:
            return {"error": "User not found"}
    except Exception as e:
        return {"error": str(e)}
    
    try:
        chat =  await chat_model.get_chat_by_id(chat_id)
        if chat is None or chat.user_id != user_id:
            return {"error": "Chat not found for this user"}
    except Exception as e:
        return {"error": str(e)}
    
    try:
        messages = await chat_model.get_chat_history(chat_id)
    except Exception as e:
        return {"error": str(e)}
    
    return messages


@router.post("/users/{user_id}/chats/{chat_id}/messages")
async def add_chat_message(user_id: int, chat_id: int, message_content: AgentMessageRequest, request: Request):
    chat_model = ChatModel()
    user_model = UserModel()
    message_model = MessageModel()
    redis_client: RedisClient = request.app.state.redis_client

    # validate user and chat
    try:
        user = await user_model.get_user_by_id(user_id)
        if user is None:
            return {"error": "User not found"}
    except Exception as e:
        return {"error": str(e)}
    
    try:
        chat =  await chat_model.get_chat_by_id(chat_id)
        if chat is None or chat.user_id != user_id:
            return {"error": "Chat not found for this user"}
    except Exception as e:
        return {"error": str(e)}


    # get or create redis session
    try:
        # get or create redis session
        redis_session: RedisMetaSessionSchema | None = await redis_client.get_session(user_id)
        if redis_session is None:
            redis_session = RedisMetaSessionSchema(
                user_id=user_id,
                chat_id=chat_id,
                created_at=datetime.utcnow().isoformat(),
                updated_at=datetime.utcnow().isoformat(),
            )
            await redis_client.create_session(redis_session)

    except Exception as e:
        return {"error": str(e)}
    
    # add the user message and agent response to the redis
    # get agent response
    try:
        agent_response = f"Simulated response for chat {message_content.content}."
        history = await redis_client.get_messages(user_id, limit=10)
        print("Chat history from Redis:", history)
        
        user_message = RedisMessageSchema(role=Role.USER, content=message_content.content)
        agent_message = RedisMessageSchema(role=Role.ASSISTANT, content=agent_response)

        await redis_client.append_message(user_id=user_id, msg=user_message)
        await redis_client.append_message(user_id=user_id, msg=agent_message)



    except Exception as e:
        return {"error": str(e)}
    
    return {
        "user_message": user_message,
        "agent_message": agent_message
    }
    