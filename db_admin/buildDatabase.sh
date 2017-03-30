# Get Datapath from user input
DATAPATH = $1

# Get psql credentials from data/creds.json
HOST=`/usr/local/bin/jq-osx-amd64 .host data/creds.json`
DBNAME=`/usr/local/bin/jq-osx-amd64 .dbname data/creds.json`
USER=`/usr/local/bin/jq-osx-amd64 .user data/creds.json`
PASSWORD=`/usr/local/bin/jq-osx-amd64 .password data/creds.json`

# Strip start and ending double quotes to be able to pass through the psql command
HOST=`sed -e 's/^"//' -e 's/"$//' <<<"$HOST"`
DBNAME=`sed -e 's/^"//' -e 's/"$//' <<<"$DBNAME"`
USER=`sed -e 's/^"//' -e 's/"$//' <<<"$USER"`
PASSWORD=`sed -e 's/^"//' -e 's/"$//' <<<"$PASSWORD"`

# Run Python Script to build insert queries
python buildDB.py -datapath $DATAPATH

# Execute all insert queries
echo 'Inserting Meta'
for file in /Users/Levittation/Desktop/MSAN/Module4/AppDev/prefer/db_admin/data/meta_inserts/meta_insert_*; do
    psql "dbname='$DBNAME' user='$USER' host='$HOST' password='$PASSWORD'" -f "$file"
    echo -n '.'
done

echo 'Inserting Review'
for file in /Users/Levittation/Desktop/MSAN/Module4/AppDev/prefer/db_admin/data/review_inserts/review_insert_*; do
    psql "dbname='$DBNAME' user='$USER' host='$HOST' password='$PASSWORD'" -f "$file"
    echo -n '.'
done
