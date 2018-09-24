#!/usr/bin/perl

# Assumes input is a list of "shortened domain name, number of submissions, possibly other stuff...."
# Assumes input is sorted, so all instances of a shortened domain name are on adjacent lines.
# Produces output as "shortened domain name, total submissions from that domain"


use strict;

my $previousdomain = "";
my $currenttotal = 0;

while(<>) {
    my @x = split(',', $_);

    my $shortdomain = $x[0];
    my $count= $x[1];
    
    if( $shortdomain eq $previousdomain ) {
	$currenttotal = $currenttotal + $count;
    } else {
	print "$previousdomain, $currenttotal\n";
	$currenttotal = $count;
	$previousdomain = $shortdomain;
    }
}

print "$previousdomain, $currenttotal\n";
