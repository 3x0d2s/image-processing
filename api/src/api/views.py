import datetime
import io
from typing import Annotated

from PIL import Image
from fastapi import APIRouter, Depends, status, Query, File, UploadFile, HTTPException, Path
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.crud import ImageCrud
from src.database.db import get_db_session
from src.services.redis_client import redis_client
from src.api.schemas import ImageRead
from src.core.config import config

router = APIRouter(tags=['Images'])


@router.post("/images",
             summary="Upload image",
             responses={
                 status.HTTP_201_CREATED: {"description": "Image successfully uploaded"},
                 status.HTTP_400_BAD_REQUEST: {"description": "Invalid image"},
             })
async def upload_image(file: Annotated[UploadFile, File(description='The image must be in JPEG format')],
                       description: Annotated[str, Query(max_length=200, title="Image description",)]
                       ):
    if file.content_type != "image/jpeg":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="File type must be JPEG")
    image_data = await file.read()

    try:
        image = Image.open(io.BytesIO(image_data))
        image_width, image_height = image.size
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid image")

    if not -100 <= image_width - 640 <= 100 or not -100 <= image_height - 480 <= 100:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Image size must be 640x480px (+-100px)")

    data = {
        'image': image_data,
        'description': description,
        'dt': datetime.datetime.utcnow().timestamp()
    }
    await redis_client.add_to_stream(data)

    return JSONResponse(status_code=status.HTTP_201_CREATED,
                        content={"message": "Image successfully uploaded"})


@router.get('/images',
            summary='Get all images',
            response_model=list[ImageRead],
            responses={
                status.HTTP_200_OK: {"description": "Images successfully uploaded"},
            }
            )
async def get_images(db: Annotated[AsyncSession, Depends(get_db_session)],
                     limit: Annotated[int, Query(gt=0)] = None,
                     offset: Annotated[int, Query(gt=0)] = None
                     ):
    img_crud = ImageCrud(db=db)
    imgs = await img_crud.get_images(limit, offset)
    return imgs


@router.get('/images/{image_id}',
            summary='Get a specific image',
            response_class=FileResponse,
            responses={
                status.HTTP_200_OK: {"description": "Image found"},
                status.HTTP_404_NOT_FOUND: {"description": "Image not found"},
            }
            )
async def get_image(image_id: Annotated[int, Path(gt=0, description='Image ID')],
                    db: Annotated[AsyncSession, Depends(get_db_session)]
                    ):
    img_crud = ImageCrud(db=db)
    img = await img_crud.get_image(image_id)
    if img is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail="Image not found")
    return FileResponse(path=f"{config.MEDIA_ROOT}/{img.file_path}")

