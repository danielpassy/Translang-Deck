cd ~/Translang-Deck/backend/decks/outputdeck
find . -mmin +1 -print0 | xargs -0 rm
cd ~/Translang-Deck/backend/
sqlite3 db.sqlite3 <<EOF
delete from backend_decks where timeStamp >= date('now', '-1 day');
delete from backend_correction where timeStamp >= date('now', '-1 day');
delete from backend_error where timeStamp >= date('now', '-1 day');