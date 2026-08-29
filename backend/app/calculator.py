import math


class StringCalculator:
    """Калькулятор басовых струн.

    Воспроизводит старую (порванную) струну по измерениям мастера:
    по диаметру керна и общему диаметру вычисляет диаметр медной
    проволоки и её длину для изготовления новой струны.

    Правило двойной навивки: соотношение выбирается мастером.
    Медный слой делится на (1 + ratio) частей:
    1 часть — первичка (тонкая), ratio частей — вторичка (толстая).
    """

    RHO_COPPER = 0.00896  # плотность меди, г/мм³

    @staticmethod
    def calculate_single(core_diameter: float, total_diameter: float,
                         winding_length: float, end_allowance: float = 60.0) -> dict:
        """Расчёт для одиночной навивки."""
        if total_diameter <= core_diameter:
            raise ValueError("Общий диаметр должен быть больше диаметра керна")
        if winding_length <= 0:
            raise ValueError("Длина обмотки должна быть положительной")

        copper_diameter = (total_diameter - core_diameter) / 2
        turns = winding_length / copper_diameter
        copper_length_mm = turns * math.pi * (core_diameter + copper_diameter) + end_allowance
        weight_g = (math.pi / 4) * copper_diameter ** 2 * copper_length_mm * StringCalculator.RHO_COPPER

        return {
            "copper_diameter": round(copper_diameter, 3),
            "turns": int(round(turns)),
            "copper_length_m": round(copper_length_mm / 1000, 2),
            "weight_g": round(weight_g, 1)
        }

    @staticmethod
    def calculate_double(core_diameter: float, total_diameter: float,
                         winding_length: float, ratio: float = 2.5,
                         end_allowance: float = 60.0) -> dict:
        """Расчёт для двойной навивки.

        ratio — отношение вторички к первичке (по умолчанию 2.5).
        Медный слой d_меди = (общий − керн) / 2 делится на (1 + ratio) частей:
        первичка (тонкая, нижняя) = d_меди / (1 + ratio)
        вторичка (толстая, верхняя) = ratio × d_меди / (1 + ratio)
        """
        if total_diameter <= core_diameter:
            raise ValueError("Общий диаметр должен быть больше диаметра керна")
        if winding_length <= 0:
            raise ValueError("Длина обмотки должна быть положительной")
        if ratio <= 0:
            raise ValueError("Соотношение должно быть положительным числом")

        copper_layer = (total_diameter - core_diameter) / 2
        divisor = 1.0 + ratio

        primary_diameter = copper_layer / divisor
        secondary_diameter = ratio * primary_diameter

        # 1-я навивка: спираль по осевой линии (керн + d1)
        turns1 = winding_length / primary_diameter
        primary_length_mm = turns1 * math.pi * (core_diameter + primary_diameter) + end_allowance

        # 2-я навивка: осевая линия (керн + 2·d1 + d2)
        turns2 = winding_length / secondary_diameter
        secondary_length_mm = turns2 * math.pi * (core_diameter + 2 * primary_diameter + secondary_diameter) + end_allowance

        weight1 = (math.pi / 4) * primary_diameter ** 2 * primary_length_mm * StringCalculator.RHO_COPPER
        weight2 = (math.pi / 4) * secondary_diameter ** 2 * secondary_length_mm * StringCalculator.RHO_COPPER

        return {
            "ratio": ratio,
            "primary_copper_diameter": round(primary_diameter, 3),
            "secondary_copper_diameter": round(secondary_diameter, 3),
            "primary_turns": int(round(turns1)),
            "secondary_turns": int(round(turns2)),
            "primary_copper_length_m": round(primary_length_mm / 1000, 2),
            "secondary_copper_length_m": round(secondary_length_mm / 1000, 2),
            "weight_g": round(weight1 + weight2, 1)
        }

    @staticmethod
    def calculate(winding_type: str, core_diameter: float, total_diameter: float,
                  winding_length: float, ratio: float = 2.5,
                  end_allowance: float = 60.0) -> dict:
        """Основной метод расчёта."""
        if winding_type == "single":
            return StringCalculator.calculate_single(
                core_diameter, total_diameter, winding_length, end_allowance)
        elif winding_type == "double":
            return StringCalculator.calculate_double(
                core_diameter, total_diameter, winding_length, ratio, end_allowance)
        else:
            raise ValueError("Неизвестный тип навивки")