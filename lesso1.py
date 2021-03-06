import time
import json
import requests

class Parser5ka:
    _params = {
        'records_per_page': 50,
    }
    _headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0"
    }

    def __init__(self, start_url):
        self.start_url = start_url

    def _get(*args, **kwargs):
        while True:
            try:
                response = requests.get(*args, **kwargs)
                if response.status_code != 200:
                    raise Exception
                time.sleep(0.1)
                return response
            except Exception:
                time.sleep(0.3)

    def run(self):
        for products in self.parse(self.start_url):
            for product in products:
                self.save_to_json_file(product, product['id'])
            time.sleep(0.1)


    def parse(self, url):
        if not url:
            url = self.start_url
        params = self._params
        while url:
            response = self._get(url, params=params, headers=self._headers)
            if params:
                params = {}
            data: dict = response.json()
            url = data.get('next')

            yield data.get('results')

    def save_to_json_file(data: dict, file_name):
        with open(f'products/{file_name}.json', 'w', encoding='UTF-8') as file:
            json.dump(data, file, ensure_ascii=False)


class ParserCatalog(Parser5ka):

    def __init__(self, start_url, category_url):
        self.category_url = category_url
        super().__init__(start_url)

    def get_categories(self, url):
        response = self._get(url, headers=self._headers)
        return response.json()

    def run(self):
        for category in self.get_categories(self.category_url):
            data = {
                "name": category['parent_group_name'],
                'code': category['parent_group_code'],
                "products": [],
            }

            self._params['categories'] = category['parent_group_code']

            for products in self.parse(self.start_url):
                data["products"].extend(products)
            self.save_to_json_file(
                data,
                category['parent_group_code']
            )


if __name__ == '__main__':
    parser = ParserCatalog('https://5ka.ru/api/v2/special_offers/', 'https://5ka.ru/api/v2/categories/')
    parser.run()
