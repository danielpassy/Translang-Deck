# Translang-Deck
Backend for the Translang Deck project.<br>
https://www.translang.live/
Written in Django, it allows user to utilize [AnkiTron](https://github.com/danielpassy/Anki-CardOTron) to automate the creation of Anki Deck to study Hebrew.

## Installation

Clone it 
```bash
git clone
```
Create an virtual enviroment
```bash
python3 -m venv venv
```
Initialize the virtual environ
```bash
$ on Linux
source ./venv/bin/activate
$ On Windows
/venv/Scripts/activate.exe
```
Install the required dependencies
```bash
pip install -r requirements.txt
```
Cd into backend
```bash
cd backend
```
Apply the migrations
```bash
python manage.py migrate
```
Start the developer server
```python
python manage.py runserver
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
