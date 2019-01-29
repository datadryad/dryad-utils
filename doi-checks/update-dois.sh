# Updates a list of DOIs in DataCite

# Takes a list of DOIs from the input stream, one per line, in the form "doi:xxxxxx"
# For each DOI:
# - if it is resolvable, the DOI metadata is updated
# - if it is not resolvable, the DOI is created

DOI_TOOL_LOCATION="/home/ubuntu/dryad-utils/doi_tool.py"

while read doi ; do
    resp=`curl -L -H "Accept: text/x-bibliography" -s -w "%{http_code}" -o /dev/null https://doi.org/"$doi"`
    if [ "$resp" -lt 400 ] ; then
        echo -e "$doi\tresolves, updating"
	resp=`$DOI_TOOL_LOCATION --doi=$doi --action=update`
	echo -e "$resp"
	echo ""
    else
	echo -e "$doi\tdoes not exist, creating"
        resp=`$DOI_TOOL_LOCATION --doi=$doi --action=create`
	echo -e "$resp"
	echo ""
    fi
done
