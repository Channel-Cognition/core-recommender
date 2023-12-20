from pydantic import BaseModel, Field, ValidationError, model_validator

from typing import List

class Movie(BaseModel):
    title: str = Field(description="Name of the movie")
    year: int = Field(description="Year of the movie") # TODO: make string, though BE1 will be responsible for the movies table
    #year: int = Field(validators=[ValidRange(min=0, max=3000)])
    # genre: str = Field(description="Genre of movie")
    # summary: str = Field(description="Summary of movie")


class MovieInfo(BaseModel):
    movies: List[Movie] = Field(description="Each movie should be classified into a separate item in the list.")


class ItemSchema(BaseModel):
    item_type: str = Field(description="Example Movie")
    title: str = Field(description="Name of the movie")
    year: int = Field(description="Year of the movie")
    @model_validator(mode='before')
    @classmethod
    def validate_item_type(cls, values):
        item_type = values.get('item_type')
        if item_type:
            normalized_item_type = item_type.replace(' ', '_').lower()
            allowed_types = {"movie", "book", "tv_show"}
            if normalized_item_type not in allowed_types:
                raise ValueError('item_type must be one of "movie", "book", "tv_show"')
            values['item_type'] = normalized_item_type
        return values


class LLMResponseSchema(BaseModel):
    text: str
    new_items: List[ItemSchema]