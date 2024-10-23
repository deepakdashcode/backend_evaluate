from pydantic import BaseModel
from typing import List

class MyModel(BaseModel):
    items: List[str]

# Example usage
data = MyModel(items=["apple", "banana", "cherry"])
print(data)
