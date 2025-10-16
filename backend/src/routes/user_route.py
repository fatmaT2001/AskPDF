from fastapi import APIRouter
from src.models.db_models import UserModel
from src.models.db_schemes import User
from .route_schemes import CreateUserScheme


router = APIRouter(
    tags=["users"],
)

@router.post("/users/")
async def create_user(create_user: CreateUserScheme):
    user_model = UserModel()
    try:
        new_user = User(name=create_user.username)
        created_user = await user_model.create_user(new_user)
    except Exception as e:
        return {"error": str(e)}
    return created_user


@router.get("/users/{user_id}")
async def get_user(user_id: int):
    user_model = UserModel()

    try:
        user = await user_model.get_user_by_id(user_id)
        if user is None:
            return {"error": "User not found"}
    except Exception as e:
        return {"error": str(e)}
     
    return user


@router.delete("/users/{user_id}")
async def delete_user(user_id: int):
    user_model = UserModel()
    try:
        user = await user_model.delete_user(user_id)
    except Exception as e:
        return {"error": str(e)}

    return user


@router.get("/users/{user_id}/chats")
async def get_user_chats(user_id: int):
    user_model = UserModel()
    try:
        chats = await user_model.get_user_chats(user_id)
    except Exception as e:
        return {"error": str(e)}    
    if chats is None:
        return []
    return chats


@router.get("/users/{user_id}/pdfs")
async def get_user_pdfs(user_id: int):
    user_model = UserModel()
    try:
        pdfs = await user_model.get_user_pdfs(user_id)
    except Exception as e:
        return {"error": str(e)}
    if pdfs is None:
        return []
    return pdfs



@router.get("/users/")
async def list_users(skip: int = 0, limit: int = 100):
    user_model = UserModel()
    try:
        users = await user_model.list_users(skip=skip, limit=limit)
    except Exception as e:
        return {"error": str(e)}
    return users