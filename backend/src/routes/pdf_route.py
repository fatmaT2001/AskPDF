from fastapi import APIRouter
from src.models.db_models import PDFModel, UserModel
from src.models.db_schemes import PDF
from fastapi import UploadFile, File, HTTPException
from typing import List
import os
router = APIRouter(
    tags=["pdfs"],
)

@router.post("/users/{user_id}/pdfs")
async def create_user_pdf(user_id: int, pdf: UploadFile = File(...)):
    pdf_model = PDFModel()
    user_model = UserModel()
    try:
        user = await user_model.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    #save the file locally
    try:
        base_dir = os.path.dirname(__file__)         
        assets_dir = os.path.join(base_dir, "..", "assets")  
        file_location = os.path.join(assets_dir, pdf.filename)
        with open(file_location, "wb+") as file_object:
            file_object.write(pdf.file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # save the pdf record in the database
    try:
        pdf_object = PDF(user_id=user_id, filename=pdf.filename, filepath=file_location)
        created_pdf = await pdf_model.save_pdf(pdf_object)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return created_pdf


@router.get("/users/{user_id}/pdfs/{pdf_id}")
async def get_user_pdf(user_id: int, pdf_id: int):
    pdf_model = PDFModel()
    user_model = UserModel()
    try:
        user = await user_model.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    try:
        pdf = await pdf_model.get_pdf_by_id(pdf_id)
        if pdf is None or pdf.user_id != user_id:
            raise HTTPException(status_code=404, detail="PDF not found for this user")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return pdf


@router.delete("/users/{user_id}/pdfs/{pdf_id}")
async def delete_user_pdf(user_id: int, pdf_id: int):
    pdf_model = PDFModel()
    user_model = UserModel()
    try:
        user = await user_model.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    try:
        pdf = await pdf_model.get_pdf_by_id(pdf_id)
        if pdf is None or pdf.user_id != user_id:
            raise HTTPException(status_code=404, detail="PDF not found for this user")
        
        # delete the file locally
        if os.path.exists(pdf.filepath):
            os.remove(pdf.filepath)
        
        deleted = await pdf_model.delete_pdf_by_id(pdf_id)
        if not deleted:
            raise HTTPException(status_code=500, detail="Failed to delete PDF")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return {"detail": "PDF deleted successfully"}


