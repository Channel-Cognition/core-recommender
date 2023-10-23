from pydantic import BaseModel, Field
from typing import List
from guardrails.validators import ValidRange


class Movie(BaseModel):
    title: str = Field(description="Name of the movie")
    year: int = Field(validators=[ValidRange(min=0, max=3000)])
    # genre: str = Field(description="Genre of movie")
    # summary: str = Field(description="Summary of movie")


class MovieInfo(BaseModel):
    movies: List[Movie] = Field(description="Each movie should be classified into a separate item in the list.")