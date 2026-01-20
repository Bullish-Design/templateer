
from dataclasses import dataclass

@dataclass
class Person:
    name: str
    age: int
    def greet(self) -> str:
        return f'Hi, I am {self.name}'
