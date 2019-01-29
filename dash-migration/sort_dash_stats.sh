# Sorts a DASH-formatted stats log into monthly files

# It is assumed that the log is stored in a
# file in the current directory called dashStats.log,
# with one log entry per line.

set -e
echo Sorting DASH stats...

echo Putting stats into monthly files...
while read line; do
    # for each line, find the year-month at the beginning of line
    yearmo = `echo "$line" | egrep -o '[0-9]+-[0-9][0-9] | head -1'`
    
    echo "yearmo=|$yearmo|"
    # for each line, write it to the output file named by the year-month
done <dashStats.log

echo Sorting each monthly file...

echo
