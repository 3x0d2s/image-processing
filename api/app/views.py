import datetime
import io
from typing import Annotated
from fastapi import APIRouter, Depends, status, Form, Query, Body, File, UploadFile, HTTPException
from PIL import Image

from app.redis_client import redis_client

router = APIRouter()


@router.post("/images",
             summary="Upload image",
             responses={
                 status.HTTP_201_CREATED: {"description": "Image successfully uploaded"},
             })
async def upload_image(file: Annotated[UploadFile, File()],
                       description: Annotated[str, Form(max_length=200)]
                       ):
    if file.content_type != "image/jpeg":
        raise HTTPException(status_code=400, detail="File type must be JPEG")
    image_data = await file.read()

    try:
        image = Image.open(io.BytesIO(image_data))
        image_width, image_height = image.size
        if not -100 <= image_width - 640 <= 100 or not -100 <= image_height - 480 <= 100:
            raise HTTPException(status_code=400, detail="Image size must be 640x480px (+-100px)")
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid image")

    data = {
        'image': image_data,
        'description': description,
        'dt': datetime.datetime.utcnow().timestamp()
    }
    await redis_client.add_to_stream(data)

    return {"message": "Image successfully uploaded"}
