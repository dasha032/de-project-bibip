from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel


class CarStatus(StrEnum):
    available = "available"
    reserve = "reserve"
    sold = "sold"
    delivery = "delivery"


class Car(BaseModel):
    vin: str
    model: int
    price: Decimal
    date_start: datetime
    status: CarStatus
    
    def index(self) -> str:
        return self.vin
    
    def to_string(self):
        return f"{self.vin}; {self.model}; {self.price}; {self.date_start.isoformat()}; {self.status}"
    
    
class Model(BaseModel):
    id: int
    name: str
    brand: str

    def index(self) -> str:
        return str(self.id)
    
    def to_string(self):
        return f"{self.id}; {self.name}; {self.brand}"


class Sale(BaseModel):
    sales_number: str
    car_vin: str
    sales_date: datetime
    cost: Decimal

    def index(self) -> str:
        return self.car_vin
    
    def to_string(self):
        return f"{self.sales_number}; {self.car_vin}; {self.sales_date.isoformat()}; {self.cost}"


class CarFullInfo(BaseModel):
    vin: str
    car_model_name: str
    car_model_brand: str
    price: Decimal
    date_start: datetime
    status: CarStatus
    sales_date: datetime | None
    sales_cost: Decimal | None


class ModelSaleStats(BaseModel):
    car_model_name: str
    brand: str
    sales_number: int
