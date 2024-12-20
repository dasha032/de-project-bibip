import os
from collections import defaultdict
from datetime import datetime
from decimal import Decimal

from models import Car, CarFullInfo, CarStatus, Model, ModelSaleStats, Sale


class CarService:
    cars_file = "cars.txt"
    cars_index_file = "cars_index.txt"
    models_file = "models.txt"
    models_index_file = "models_index.txt"
    sales_file = "sales.txt"
    sales_index_file = "sales_index.txt"
    FIXED_LINE_LENGTH = 500

    def __init__(self, root_directory_path: str) -> None:
        self.root_directory_path = root_directory_path

        for file in [
            self.models_file,
            self.models_index_file,
            self.cars_file,
            self.cars_index_file,
        ]:
            full_path = os.path.join(self.root_directory_path, file)
            if not os.path.exists(full_path):
                with open(full_path, "w") as f:
                    pass
        self.model_indices = self._read_index(
            os.path.join(self.root_directory_path, self.models_index_file)
        )
        self.car_indices = self._read_index(
            os.path.join(self.root_directory_path, self.cars_index_file)
        )
        self.sales_indices = self._read_index(
            os.path.join(self.root_directory_path, self.sales_index_file)
        )

    def _read_index(self, index_file):
        if os.path.exists(index_file):
            with open(index_file, "r") as file:
                return sorted(
                    [
                        tuple(map(int, line.strip().split(",")))
                        for line in file.readlines()
                        if line.strip()
                    ]
                )
        return []

    def _write_index(self, index_file, indices):
        with open(index_file, "w") as file:
            for idx, line_num in sorted(indices):
                file.write(f"{idx},{line_num}\n")

    def _write_fixed_length_line(self, file_path, content):
        formatted_line = content.ljust(self.FIXED_LINE_LENGTH) + "\n"
        with open(file_path, "a+") as file:
            file.seek(0, os.SEEK_END)
            line_number = file.tell() // (self.FIXED_LINE_LENGTH + 1)
            file.write(formatted_line)
        return line_number

    # Задание 1. Сохранение автомобилей и моделей
    def add_model(self, model: Model) -> Model:
        """Добавляет модели в базу данных"""
        models_file_path = os.path.join(self.root_directory_path, self.models_file)
        line_number = self._write_fixed_length_line(models_file_path, model.to_string())

        self.model_indices.append((model.id, line_number))
        self.model_indices.sort()
        self._write_index(
            os.path.join(self.root_directory_path, self.models_index_file),
            self.model_indices,
        )

        return model

    # Задание 1. Сохранение автомобилей и моделей
    def add_car(self, car: Car) -> Car:
        """Добавляет автомобили в базу данных"""
        cars_file_path = os.path.join(self.root_directory_path, self.cars_file)
        line_number = self._write_fixed_length_line(cars_file_path, car.to_string())

        self.car_indices.append((car.vin, line_number))
        self.car_indices.sort()
        self._write_index(
            os.path.join(self.root_directory_path, self.cars_index_file),
            self.car_indices,
        )

        return car

    # Задание 2. Сохранение продаж.
    def sell_car(self, sale: Sale) -> Car:
        """Записывает новую продажу в таблицу"""
        sales_file_path = os.path.join(self.root_directory_path, self.sales_file)
        line_number = self._write_fixed_length_line(sales_file_path, sale.to_string())

        self.sales_indices.append((sale.sales_number, line_number))
        self.sales_indices.sort()
        self._write_index(
            os.path.join(self.root_directory_path, self.sales_index_file),
            self.sales_indices,
        )

        updated_car = None
        car_file_path = os.path.join(self.root_directory_path, self.cars_file)
        for car_vin, car_line_number in self.car_indices:
            if car_vin == sale.car_vin:
                with open(car_file_path, "r+") as file:
                    file.seek(car_line_number * (self.FIXED_LINE_LENGTH + 1))
                    car_data = file.read(self.FIXED_LINE_LENGTH).strip()
                    car_parts = car_data.split("; ")

                    updated_car_data = "; ".join(car_parts[:4]) + "; sold".ljust(
                        self.FIXED_LINE_LENGTH - len(car_data)
                    )

                    file.seek(car_line_number * (self.FIXED_LINE_LENGTH + 1))
                    file.write(updated_car_data)
                    updated_car = Car(
                        vin=car_parts[0],
                        model=int(car_parts[1]),
                        price=Decimal(car_parts[2]),
                        date_start=datetime(
                            day=int(car_parts[3].split("T")[0].split("-")[2]),
                            month=int(car_parts[3].split("T")[0].split("-")[1]),
                            year=int(car_parts[3].split("T")[0].split("-")[0]),
                        ),
                        status=CarStatus(car_parts[4]),
                    )
        return updated_car

    # Задание 3. Доступные к продаже
    def get_cars(self, status: CarStatus) -> list[Car]:
        """Выводит список моделей, доступных к продаже"""
        cars_file_path = os.path.join(self.root_directory_path, self.cars_file)
        filtered_cars = []

        with open(cars_file_path, "r") as file:
            for line in file:
                car_data = line.strip().split("; ")
                print(car_data)

                if CarStatus(car_data[4]) == status:
                    filtered_cars.append(
                        Car(
                            vin=car_data[0],
                            model=int(car_data[1]),
                            price=Decimal(car_data[2]),
                            date_start=datetime(
                                day=int(car_data[3].split("T")[0].split("-")[2]),
                                month=int(car_data[3].split("T")[0].split("-")[1]),
                                year=int(car_data[3].split("T")[0].split("-")[0]),
                            ),
                            status=CarStatus(car_data[4]),
                        )
                    )

        return filtered_cars

    # Задание 4. Детальная информация
    def get_car_info(self, vin: str) -> CarFullInfo | None:
        """Выводит информацию о машине"""
        car_file_path = os.path.join(self.root_directory_path, self.cars_file)
        for car_vin, car_line_number in self.car_indices:
            if car_vin == vin:
                with open(car_file_path, "r") as file:
                    file.seek((car_line_number) * (self.FIXED_LINE_LENGTH + 1))
                    car_data = file.read(self.FIXED_LINE_LENGTH).strip().split("; ")
                    car_id = car_data[0]
                    model_id = int(car_data[1])
                    price = Decimal(car_data[2])
                    date_start = datetime(
                        day=int(car_data[3].split("T")[0].split("-")[2]),
                        month=int(car_data[3].split("T")[0].split("-")[1]),
                        year=int(car_data[3].split("T")[0].split("-")[0]),
                    )
                    status = CarStatus(car_data[4])

                    model_file_path = os.path.join(
                        self.root_directory_path, self.models_file
                    )
                    for model_id_key, model_line_number in self.model_indices:
                        if model_id_key == model_id:
                            with open(model_file_path, "r") as model_file:
                                model_file.seek(
                                    model_line_number * (self.FIXED_LINE_LENGTH + 1)
                                )
                                model_data = (
                                    model_file.read(self.FIXED_LINE_LENGTH)
                                    .strip()
                                    .split("; ")
                                )
                                model_name = model_data[1]
                                model_brand = model_data[2]
                                break
                    else:
                        raise ValueError(
                            f"Model with ID {
                                         model_id} not found."
                        )

                    sales_date = None
                    sales_cost = None
                    if status == "sold":
                        sales_file_path = os.path.join(
                            self.root_directory_path, self.sales_file
                        )
                        with open(sales_file_path, "r") as sales_file:
                            for line in sales_file:
                                sale_data = line.strip().split("; ")
                                if len(sale_data) < 3:
                                    continue
                                if sale_data[1] == str(car_id):
                                    sales_date = sale_data[2]
                                    sales_cost = float(sale_data[3])
                                    break

                    return CarFullInfo(
                        vin=vin,
                        car_model_name=model_name,
                        car_model_brand=model_brand,
                        price=price,
                        date_start=date_start,
                        status=status,
                        sales_date=sales_date,
                        sales_cost=sales_cost,
                    )

        return None

    # Задание 5. Обновление ключевого поля
    def update_vin(self, vin: str, new_vin: str) -> Car:
        """Обновляет VIN-код"""
        cars_file_path = os.path.join(self.root_directory_path, self.cars_file)
        car_index_path = os.path.join(self.root_directory_path, self.cars_index_file)

        updated_car = None
        car_line_number = None
        car_index = None
        for i, (car_vin, line_number) in enumerate(self.car_indices):
            if car_vin == vin:
                car_line_number = line_number
                car_index = i
                break
        if car_line_number is None:
            return None
        with open(cars_file_path, "r+") as file:
            file.seek(car_line_number * (self.FIXED_LINE_LENGTH + 1))
            car_line = file.read(self.FIXED_LINE_LENGTH).strip()
            car_data = car_line.split("; ")

        car_data[0] = new_vin
        updated_car_line = "; ".join(car_data)
        with open(cars_file_path, "r+") as file:
            file.seek(car_line_number * (self.FIXED_LINE_LENGTH + 1))
            file.write(updated_car_line + "\n")

        self.car_indices[car_index] = (new_vin, car_line_number)
        self._write_index(car_index_path, self.car_indices)

        updated_car = Car(
            vin=car_data[0],
            model=int(car_data[1]),
            price=Decimal(car_data[2]),
            date_start=datetime.fromisoformat(car_data[3]),
            status=CarStatus(car_data[4]),
        )
        return updated_car

    # Задание 6. Удаление продажи
    def revert_sale(self, sales_number: str) -> Car:
        """Удаляет запись о продаже и заменяет статус машины"""
        sale_to_remove = None
        for i, (sale_key, line_number) in enumerate(self.sales_indices):
            if sale_key == sales_number:
                sale_to_remove = (sale_key, line_number)
                del self.sales_indices[i]
                break

        if sale_to_remove is None:
            return None

        sales_file_path = os.path.join(self.root_directory_path, self.sales_file)
        with open(sales_file_path, "r") as file:
            sales_lines = file.readlines()

        del sales_lines[sale_to_remove[1]]

        with open(sales_file_path, "w") as file:
            file.writelines(sales_lines)

        car_vin = sale_to_remove[0].split("#")[1]
        car_to_update = None
        for i, (car_vin_index, car_line_number) in enumerate(self.car_indices):
            if car_vin_index == car_vin:
                car_to_update = car_line_number
                break

        if car_to_update is None:
            raise ValueError(f"Car with VIN {car_vin} not found.")

        cars_file_path = os.path.join(self.root_directory_path, self.cars_file)
        with open(cars_file_path, "r+") as file:
            file.seek(car_to_update * (self.FIXED_LINE_LENGTH + 1))
            car_line = file.read(self.FIXED_LINE_LENGTH).strip()
            car_data = car_line.split("; ")

            car_data[4] = "available"
            updated_car_line = "; ".join(car_data)

            file.seek(car_to_update * (self.FIXED_LINE_LENGTH + 1))
            file.write(updated_car_line + "\n")

        self._write_index(
            os.path.join(self.root_directory_path, self.sales_index_file),
            self.sales_indices,
        )
        self._write_index(
            os.path.join(self.root_directory_path, self.cars_index_file),
            self.car_indices,
        )
        updated_car = Car(
            vin=car_data[0],
            model=int(car_data[1]),
            price=Decimal(car_data[2]),
            date_start=datetime.fromisoformat(car_data[3]),
            status=CarStatus(car_data[4]),
        )
        return updated_car

    # Задание 7. Самые продаваемые модели

    def top_models_by_sales(self) -> list[ModelSaleStats]:
        """Выводит топ-3 модели по количеству продаж"""
        sales_count_dict: defaultdict[int] = defaultdict(int)
        sales_file_path = os.path.join(self.root_directory_path, self.sales_file)
        with open(sales_file_path, "r") as file:
            for line in file.readlines():
                sale_data = line.strip().split("; ")
                vin = sale_data[1]
                print(self.car_indices)
                car_to_update = None
                for car_vin_index, car_line_number in self.car_indices:
                    if car_vin_index == vin:
                        car_to_update = car_line_number
                        break
                if car_to_update is None:
                    continue
                cars_file_path = os.path.join(self.root_directory_path, self.cars_file)
                with open(cars_file_path, "r+") as file:
                    file.seek(car_to_update * (self.FIXED_LINE_LENGTH + 1))
                    car_line = file.read(self.FIXED_LINE_LENGTH).strip()
                    car_data = car_line.split("; ")
                model_id = car_data[1]
                sales_count_dict[model_id] += 1
        sorted_sales = sorted(sales_count_dict.items(), key=lambda x: (-x[1]))
        top_3_sales = sorted_sales[:3]
        print(top_3_sales)
        top_models = []
        for model_id, sales_count in top_3_sales:
            model_line_number = None
            for model_key, line_number in self.model_indices:
                if model_key == int(model_id):
                    model_line_number = line_number
                    break
            if model_line_number is None:
                continue
            models_file_path = os.path.join(self.root_directory_path, self.models_file)
            with open(models_file_path, "r") as file:
                file.seek(model_line_number * (self.FIXED_LINE_LENGTH + 1))
                model_line = file.read(self.FIXED_LINE_LENGTH).strip()
                model_data = model_line.split("; ")
            model_name = model_data[1]
            brand = model_data[2]
            top_models.append(
                ModelSaleStats(
                    car_model_name=model_name, brand=brand, sales_number=sales_count
                )
            )
        return top_models
