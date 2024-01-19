import logging

from fastapi import APIRouter, Depends, HTTPException, Security, status

from app.core.translation import Translator
from app.crud.crud_consumable import consumable as consumables
from app.crud.crud_consumable_item import consumable_item as consumable_items
from app.dependencies import get_current_active_account, get_db
from app.schemas import consumable_item as consumable_item_schema

router = APIRouter(tags=["consumable_item"], prefix="/consumable_item")
translator = Translator(element="consumable_item")

logger = logging.getLogger("app.api.v1.consumable_item")


@router.get(
    "/",
    response_model=list[consumable_item_schema.ConsumableItem],
    dependencies=[Security(get_current_active_account)],
)
async def read_consumable_items(db=Depends(get_db)):
    """
    Retrieve a list of all consumable items.
    """
    return await consumable_items.query(db, limit=None)


@router.post(
    "/",
    response_model=consumable_item_schema.ConsumableItem,
    dependencies=[Security(get_current_active_account)],
)
async def create_consumable_item(
    consumable_item: consumable_item_schema.ConsumableItemCreate, db=Depends(get_db)
):
    """
    Create a new consumable item.
    """
    if await consumable_items.query(db, name=consumable_item.name, limit=1):
        logger.debug(f"Consumable item {consumable_item.name} already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=translator.ELEMENT_ALREADY_EXISTS,
        )
    return await consumable_items.create(db, obj_in=consumable_item)


@router.get(
    "/{consumable_item_id}",
    response_model=consumable_item_schema.ConsumableItem,
    dependencies=[Security(get_current_active_account)],
)
async def read_consumable_item(consumable_item_id: int, db=Depends(get_db)):
    """
    Retrieve a specific consumable item by ID.
    """
    consumable_item = await consumable_items.read(db, consumable_item_id)
    if consumable_item is None:
        logger.debug(f"Consumable item {consumable_item_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=translator.ELEMENT_NOT_FOUND
        )
    return consumable_item


@router.put(
    "/{consumable_item_id}",
    response_model=consumable_item_schema.ConsumableItem,
    dependencies=[Security(get_current_active_account)],
)
async def update_consumable_item(
    consumable_item_id: int,
    consumable_item: consumable_item_schema.ConsumableItemUpdate,
    db=Depends(get_db),
):
    """
    Update a specific consumable item by ID.
    """
    old_consumable_item = await consumable_items.read(db, consumable_item_id)
    if old_consumable_item is None:
        logger.debug(f"Consumable item {consumable_item_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=translator.ELEMENT_NOT_FOUND
        )
    results = await consumable_items.query(db, name=consumable_item.name, limit=1)
    if results and results[0].id != old_consumable_item.id:
        logger.debug(f"Consumable item {consumable_item.name} already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=translator.ELEMENT_ALREADY_EXISTS,
        )
    return await consumable_items.update(
        db, db_obj=old_consumable_item, obj_in=consumable_item
    )


@router.delete(
    "/{consumable_item_id}",
    response_model=consumable_item_schema.ConsumableItem,
    dependencies=[Security(get_current_active_account)],
)
async def delete_consumable_item(consumable_item_id: int, db=Depends(get_db)):
    """
    Delete a specific consumable item by ID.
    """
    if await consumable_items.read(db, consumable_item_id) is None:
        logger.debug(f"Consumable item {consumable_item_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=translator.ELEMENT_NOT_FOUND
        )
    if await consumables.query(db, consumable_item_id=consumable_item_id, limit=1):
        logger.debug(f"Consumable item {consumable_item_id} is used")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=translator.DELETION_OF_USED_ELEMENT,
        )
    return await consumable_items.delete(db, id=consumable_item_id)
