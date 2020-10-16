import re
import numpy as np

import pytesseract
from Levenshtein import distance


class ReceiptProcessor:
    def __init__(self, goods, thr=0.45):
        self.goods = goods
        self.thr = thr

        self.reg_filters = [
            #  Есть хотя бы две буквы в тексте
            lambda x: len(re.findall(r'[a-zа-ё]', x)) > 2,
        ]
        self.reg_exps = [
            # убрать цифры в начале
            re.compile(r"^\d+ "),
            #  Сматчить лишние пробелы в один
            re.compile(r'\s+'),
        ]

    def _is_order(self, text):
        if all([func(text) for func in self.reg_filters]) is True:
            return True
        return False

    def _text_preproc(self, text):
        for reg_exp in self.reg_exps:
            text = reg_exp.sub(' ', text)
        return text.strip()

    def match_goods(self, texts, thr=0.45):
        """ Подбирает предполагаемым товарам товары из базы по
            расстоянию Ливенштейна.
        """
        result = []
        probs = []
        goods = []

        for text in texts:
            dists = []

            for label in self.goods:
                dists.append(distance(text, label))

            min_idx = np.argmin(dists)

            # HINT 3:
            # Если расстояние Ливенштейна больше или равно длине предполагаемого товара,
            # то плохо это мапить в существующий товар базы.
            if dists[min_idx] < len(text):
                # Вероятность ошибки, как число совпадающих букв с подобранным товаром.
                prob = 1 - dists[min_idx] / len(text)

                # HINT 4:
                # Больше половины букв должно совпадать с подобранным товаром
                if prob > self.thr:
                    result.append(min_idx)
                    probs.append(prob)

        if result:
            goods = self.goods[result]

        return result, goods, probs

    def text_process(self, text):
        """ text: str object """
        # Препроцессинг строки
        proc_texts = list(map(self._text_preproc, [text.lower()]))

        # Сопоставление с товарами из базы
        result, text, prob = self.match_goods(proc_texts)

        return result, text, prob

    def image_process(self, image):
        """ image: PIL object """
        # Извлечение текста OCR моделью
        text = pytesseract.image_to_string(image, lang='rus')

        # Оставить только строки, в которых может находиться товар из базы.
        # Препроцессинг строки.
        extracted_lines = text.lower().split('\n')
        extracted_orders = list(filter(self._is_order, extracted_lines))
        proc_texts = list(map(self._text_preproc, extracted_orders))

        # Сопоставление с товарами из базы
        result, text, prob = self.match_goods(proc_texts)

        return result, text, prob
