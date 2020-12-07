import random


class Model:
    def predict(self, calced_data: dict):
        is_buy = random.randint(1, 10) > 5
        sell_seconds = -1
        if is_buy:
            sell_seconds = random.randint(1, 5)
        return is_buy, sell_seconds
