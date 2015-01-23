dryad-utils
===========

Scripts for Dryad maintenance tasks.

## check_dataone_validation.py

There's a dataone validator script in dryad-repo: dspace/etc/dataone-mn-script/validator.py
it downloads the metadata for everything in D1, and runs xmllint on it. it writes to a csv file.
This script analyzes that csv file

## check_embargo.py

This was an investigation into embargo leaks in Fall of 2013.

Creates a report of items downloaded under embargo, targeting logs from Aug-Dec 2013 and
 files installed into Dryad around 2013-12-12.  Queries solr statistics and requires apache
 logs on the local filesystem

## fetch_get_urls.py

Used to fetch URLs via http. Used in both embargo investigation and DOI database load testing.

## fix_tasklistitems.py

This script adds or removes rows in the tasklistitem table, allowing "new" curators
to curate submissions that entered the workflow before they were added to the curators
group. It also removes epersons that are no longer in the curators group.

## item_ids.py

Part of the embargo leak investigation, extracted item ids, handles, etc.

## make_markup.py

Generates markup for journal cover image display. http://wiki.datadryad.org/Updating_Journal_Covers

## read_get_urls.py

Used to extract GET urls out of apache logs to send to fetch_get_urls

## read_httplogs.py

Reader of apache logs, to pull out metadata about requests

## replace_largefile_bitstream.py

Script to replace bitstreams, used for large files on the serve http://wiki.datadryad.org/Large_File_Technology

## resize_cover.py

Resizes journal cover images. http://wiki.datadryad.org/Updating_Journal_Covers

