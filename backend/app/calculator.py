import math


class StringCalculator:
    """Калькулятор басовых струн"""

    @staticmethod
    def calculate_single(core_diameter: float, total_diameter: float, string_length: float) -> dict:
        """Расчет для одиночной навивки"""
        copper_diameter = (total_diameter - core_diameter) / 2
        copper_length = (core_diameter + copper_diameter * 2) * math.pi * string_length

        return {
            "copper_diameter": round(copper_diameter, 4),
            "copper_length": round(copper_length, 2)
        }

    @staticmethod
    def calculate_double(core_diameter: float, total_diameter: float, string_length: float) -> dict:
        """Расчет для двойной навивки"""
        total_copper = total_diameter - core_diameter

        primary_diameter = (total_copper * 0.3334) / 2
        secondary_diameter = (total_copper * 0.6667) / 2

        primary_length = (core_diameter + primary_diameter * 2) * math.pi * string_length - 50
        secondary_length = ((core_diameter + (primary_diameter * 2)) + (
                    secondary_diameter * 2)) * math.pi * string_length

        return {
            "primary_copper_diameter": round(primary_diameter, 4),
            "secondary_copper_diameter": round(secondary_diameter, 4),
            "primary_copper_length": round(primary_length, 2),
            "secondary_copper_length": round(secondary_length, 2)
        }

    @staticmethod
    def calculate(winding_type: str, core_diameter: float, total_diameter: float, string_length: float) -> dict:
        """Основной метод расчета"""
        if winding_type == "single":
            return StringCalculator.calculate_single(core_diameter, total_diameter, string_length)
        elif winding_type == "double":
            return StringCalculator.calculate_double(core_diameter, total_diameter, string_length)
        else:
            raise ValueError("Неизвестный тип навивки")