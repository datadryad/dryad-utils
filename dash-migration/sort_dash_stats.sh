# Sorts a DASH-formatted stats log into monthly files

# It is assumed that the log is stored in a
# file in the current directory called dashStats.log,
# with one log entry per line.

set -e
echo Sorting DASH stats...

echo Putting stats into monthly files...
while read line; do
    # for each line, find the year-month at the beginning of line
    yearmo=`echo "$line" | egrep -o '[0-9]+-[0-9][0-9]' | head -1`

    # for each line, write it to the output file named by the year-month
    echo "$line" >> "counter_$yearmo"
done <dashStats.log

echo Sorting each monthly file...
find . -name 'counter_[0-9][0-9][0-9][0-9]-[0-9][0-9]' -exec sh -c 'sort {} > {}.log' \;

echo "Removing \"junk\" file that contains the lines from the original log file which are not in the counter format"
rm counter_

echo
