from fastapi import APIRouter, Depends, HTTPException

from app.crud.crud_out_of_stock_item import out_of_stock_item as out_of_stock_items
from app.dependencies import get_db
from app.schemas import out_of_stock_item as out_of_stock_item_schema


router = APIRouter()


@router.get("/buy/", response_model=list[out_of_stock_item_schema.OutOfStockItem], response_model_exclude_none=True)
async def read_out_of_stock_items_buy(db=Depends(get_db)) -> list:
    return out_of_stock_items.query(db, limit=None, buy_or_sell=True)


@router.get("/sell/", response_model=list[out_of_stock_item_schema.OutOfStockItem], response_model_exclude_none=True)
async def read_out_of_stock_items_sell(db=Depends(get_db)) -> list:
    return out_of_stock_items.query(db, limit=None, buy_or_sell=False)


@router.get("/{out_of_stock_item_id}", response_model=out_of_stock_item_schema.OutOfStockItem, response_model_exclude_none=True)
async def read_out_of_stock_item(out_of_stock_item_id: int, db=Depends(get_db)) -> dict:
    out_of_stock_item = out_of_stock_items.read(db, out_of_stock_item_id)
    if out_of_stock_item is None:
        raise HTTPException(
            status_code=404, detail="Out of stock item not found")
    return out_of_stock_item


@router.post("/", response_model=out_of_stock_item_schema.OutOfStockItem, response_model_exclude_none=True)
async def create_out_of_stock_item(out_of_stock_item: out_of_stock_item_schema.OutOfStockItemBase, db=Depends(get_db)) -> dict:
    test = out_of_stock_items.query(
        db, limit=1, name=out_of_stock_item.name, buy_or_sell=out_of_stock_item.sell_price is None)
    if len(test) > 0:
        raise HTTPException(
            status_code=400, detail="Out of stock item already exists")

    saved_model = out_of_stock_item_schema.OutOfStockItemCreate(
        **out_of_stock_item.dict(), buy_or_sell=out_of_stock_item.sell_price is None)
    return out_of_stock_items.create(db, obj_in=saved_model.dict(by_alias=False))


@router.put("/{out_of_stock_item_id}", response_model=out_of_stock_item_schema.OutOfStockItem, response_model_exclude_none=True)
async def update_out_of_stock_item_buy(out_of_stock_item_id: int, out_of_stock_item: out_of_stock_item_schema.OutOfStockItemBase, db=Depends(get_db)):
    test = out_of_stock_items.query(
        db, limit=1, name=out_of_stock_item.name, buy_or_sell=out_of_stock_item.sell_price is None)
    old_out_of_stock_item = out_of_stock_items.read(db, out_of_stock_item_id)
    if old_out_of_stock_item is None:
        raise HTTPException(
            status_code=404, detail="Out of stock item not found")
    if len(test) and test[0].id != old_out_of_stock_item.id:
        raise HTTPException(
            status_code=400, detail="Out of stock item already exists")

    saved_model = out_of_stock_item_schema.OutOfStockItemUpdate(
        **out_of_stock_item.dict(), buy_or_sell=out_of_stock_item.sell_price is None)
    return out_of_stock_items.update(db, db_obj=old_out_of_stock_item, obj_in=saved_model)


@router.delete("/{out_of_stock_item_id}", response_model=out_of_stock_item_schema.OutOfStockItem, response_model_exclude_none=True)
async def delete_out_of_stock_item_buy(out_of_stock_item_id: int, db=Depends(get_db)):
    out_of_stock_item = out_of_stock_items.read(db, out_of_stock_item_id)
    if out_of_stock_item is None:
        raise HTTPException(
            status_code=404, detail="Out of stock item not found")
    return out_of_stock_items.delete(db, id=out_of_stock_item_id)
