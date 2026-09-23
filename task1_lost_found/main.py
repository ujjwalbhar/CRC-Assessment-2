from fastapi import FastAPI, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Optional
from enum import Enum


# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------

DATABASE_URL = "sqlite:///./lost_found.db"
engine = create_engine(DATABASE_URL, echo=True)


def create_db_tables():
    SQLModel.metadata.create_all(engine)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ItemStatus(str, Enum):
    lost = "Lost"
    found = "Found"
    returned = "Returned"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class ItemBase(SQLModel):
    title: str = Field(min_length=1, description="Name/title of the item")
    description: str = Field(min_length=3, description="Meaningful description of the item")
    category: str = Field(description="E.g. Electronics, Documents, Accessories")
    location: str = Field(description="Where the item was lost or found")
    reported_by: str = Field(description="Name of the person reporting")
    status: ItemStatus = Field(description="Lost, Found, or Returned")


class Item(ItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class ItemCreate(ItemBase):
    pass


class ItemUpdate(SQLModel):
    """All fields optional so the caller can update just what changed."""
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None
    reported_by: Optional[str] = None
    status: Optional[ItemStatus] = None


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Campus Lost & Found API",
    description="Report and manage lost/found items on campus",
    version="1.0.0",
)


@app.on_event("startup")
def on_startup():
    create_db_tables()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.post("/items", response_model=Item, status_code=201, tags=["Items"])
def create_item(item: ItemCreate):
    """Report a new lost or found item."""
    with Session(engine) as session:
        db_item = Item(**item.model_dump())
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
        return db_item


@app.get("/items", response_model=list[Item], tags=["Items"])
def get_all_items():
    """Return every reported item."""
    with Session(engine) as session:
        items = session.exec(select(Item)).all()
        return items


# NOTE: These two filtered routes are registered BEFORE /items/{item_id}
# so FastAPI matches them correctly before trying to cast the path segment as an int.

@app.get("/items/status/{status}", response_model=list[Item], tags=["Items"])
def get_items_by_status(status: ItemStatus):
    """Return all items matching a given status (Lost / Found / Returned)."""
    with Session(engine) as session:
        items = session.exec(select(Item).where(Item.status == status)).all()
        return items


@app.get("/items/category/{category}", response_model=list[Item], tags=["Items"])
def get_items_by_category(category: str):
    """Return all items belonging to a particular category."""
    with Session(engine) as session:
        items = session.exec(
            select(Item).where(Item.category == category)
        ).all()
        return items


@app.get("/items/{item_id}", response_model=Item, tags=["Items"])
def get_item(item_id: int):
    """Return a single item by its ID."""
    with Session(engine) as session:
        item = session.get(Item, item_id)
        if not item:
            raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found")
        return item


@app.put("/items/{item_id}", response_model=Item, tags=["Items"])
def update_item(item_id: int, item_data: ItemUpdate):
    """Update any field(s) of an existing item report."""
    with Session(engine) as session:
        item = session.get(Item, item_id)
        if not item:
            raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found")

        updates = item_data.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(item, field, value)

        session.add(item)
        session.commit()
        session.refresh(item)
        return item


@app.delete("/items/{item_id}", status_code=204, tags=["Items"])
def delete_item(item_id: int):
    """Delete an item report permanently."""
    with Session(engine) as session:
        item = session.get(Item, item_id)
        if not item:
            raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found")
        session.delete(item)
        session.commit()
