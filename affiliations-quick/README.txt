Quick and dirty report of Dryad submissions by university.

```
The base report is a Postgres query to list submitter email addresses and counts of submissions:
\copy (select email, count(item_id) from eperson, item where
eperson.eperson_id = item.submitter_id and item.in_archive=true and
item.owning_collection=2 group by eperson.eperson_id order by count
desc;) to 'authorReport.csv' with CSV; 
```

Then the report is processed using the perl scripts in this directory
to parse out the "university" portion of the email address and sum by
university:

```
perl report.pl <authorReport.csv >authorReportDomains.csv
sort authorReportDomains.csv >authorReportDomainsSort.csv
perl report2.pl <authorReportDomainsSort.csv >reportByEmail.csv
```
