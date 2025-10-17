from pydantic import BaseModel, Field

class CreateChatRequest(BaseModel):
    pdf_id:int = Field(..., description="The ID of the PDF associated with the chat")



class AgentMessageRequest(BaseModel):
    content: str = Field(..., description="The message from the user to the agent")