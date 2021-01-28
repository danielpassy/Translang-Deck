# Translang-Deck
Backend for the Translang Deck project.
https://www.translang.live/
Written in Django, it allows user to utilize [AnkiTron](https://github.com/danielpassy/Anki-CardOTron) to automate the creation of Anki Deck to study Hebrew.

## Installation

Clone it 
```bash
git clone
```
$ pip install -r requirements.txt

# Faça as migrações
$ python manage.py migrate

# Inicialize em servidor local para testes
$ python manage.py runserver

# Gere um token de autenticação para realizar testes, 
curl -d "username=teste&password=teste" -X POST http://127.0.0.1:8000/api-token-auth


Create an 
```bash
pip install foobar
```



## Usage

```python
import foobar

foobar.pluralize('word') # returns 'words'
foobar.pluralize('goose') # returns 'geese'
foobar.singularize('phenomena') # returns 'phenomenon'
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
