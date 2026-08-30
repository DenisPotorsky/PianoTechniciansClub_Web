import math


class StringCalculator:
    RHO_COPPER = 0.00896  # г/мм³

    @staticmethod
    def calculate(winding_type, core, total, length, ratio=2.5, allowance=60.0):
        if total <= core: raise ValueError("Общий диаметр должен быть больше керна")

        copper_layer = (total - core) / 2

        if winding_type == 'single':
            d_cu = copper_layer
            turns = length / d_cu
            len_mm = turns * math.pi * (core + d_cu) + allowance
            weight = (math.pi / 4) * d_cu ** 2 * len_mm * StringCalculator.RHO_COPPER
            return {
                "type": "single", "d_cu": round(d_cu, 3), "turns": int(turns),
                "len_m": round(len_mm / 1000, 2), "weight_g": round(weight, 1)
            }
        else:
            d1 = copper_layer / (1 + ratio)
            d2 = ratio * d1
            t1 = length / d1
            l1_mm = t1 * math.pi * (core + d1) + allowance
            w1 = (math.pi / 4) * d1 ** 2 * l1_mm * StringCalculator.RHO_COPPER

            t2 = length / d2
            l2_mm = t2 * math.pi * (core + 2 * d1 + d2) + allowance
            w2 = (math.pi / 4) * d2 ** 2 * l2_mm * StringCalculator.RHO_COPPER

            return {
                "type": "double", "ratio": ratio,
                "d1": round(d1, 3), "d2": round(d2, 3),
                "t1": int(t1), "t2": int(t2),
                "l1_m": round(l1_mm / 1000, 2), "l2_m": round(l2_mm / 1000, 2),
                "w1_g": round(w1, 1), "w2_g": round(w2, 1), "total_w": round(w1 + w2, 1)
            }