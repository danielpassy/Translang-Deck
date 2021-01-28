# Translang-Deck
Backend for the Translang Deck project.<br>
https://www.translang.live/ <br>
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

There're just three end points
```python
    api/upload_file/
    api/upload_list/
    api/correct/
```
First you need to input the Hebrew words that you wish to turn into Flash cards. You may choose one of the two options: <br> 
- The first option, 'api/upload_file/', accepts a .csv with one word per cell.<br>
- The second, 'api/upload_list/', accepts a list of words. <br>

After the first step, the response will contain either a deck ready to use, or, in case there's any mistake, a list of errors. <br>
In the latter, you should redirect the response to 'api/correct/' inserting the appropiate corrections in the corretion field. <br>
The mandatory fields are the Deck Id, the error list with the corrections as the response from the first step exemplifies.<br>
To discard a word, just left the correction entry blank. If everything turns out fine, you're get the deck link as response, otherwise you may need to do extra corrections <br>



## Contribuindo
Contribuições são bem vindas.
Apenas certifique de escrever os testes apropiados.

## License
[MIT](https://choosealicense.com/licenses/mit/)
