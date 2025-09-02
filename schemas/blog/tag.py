from pydantic import BaseModel, Field, ConfigDict

class TagRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(nullable = True)
    name: str = Field(nullable = False)
    slug: str = Field(nullable = False)

class TagCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str = Field(nullable = False)
