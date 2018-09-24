#!/usr/bin/perl

# Assumes input (stdin) is a list of "email address, number of submissions"
# Produces output as a list of "shortened domain name, number of submissions, email address"

use strict;

while(<>) {
    my @x = split(',', $_);

    my $fulladdress = $x[0];
    chomp($x[1]);
    my $count= $x[1];
    
    my @domainarr = split(/\@/,$fulladdress);
    my $fulldomain = $domainarr[1];
    
    my @domainparts = split('\.', $fulldomain);

    # If the domain has "ac" in the second-to-last spot, or is in the uk or au TLD, 
    # we need 3 parts to make a full institution name. Otherwise we only need 2 parts
    my $shortdomain;
    if( ($domainparts[-2] eq "edu") || ($domainparts[-2] eq "ac") || ($domainparts[-1] eq "uk") || ($domainparts[-1] eq "au")) {
	$shortdomain = "$domainparts[-3]\.$domainparts[-2]\.$domainparts[-1]";
    } else {
	$shortdomain = "$domainparts[-2]\.$domainparts[-1]";
    }
    
    print "$shortdomain, $count, $fulladdress\n";
}

