#! /usr/bin/env bash
# blackscholes, dedup, ferret, freqmine, swaptions
package=swaptions
sys=mlp
threads=80
inputsize=native
outfile=$sys'_'$package.time$threads
parsec=~/parsec-benchmark/bin/parsecmgmt
echo $outfile

$parsec -a run -p $package -n $threads -i $inputsize >> $outfile && echo '.'
$parsec -a run -p $package -n $threads -i $inputsize >> $outfile && echo '.'
$parsec -a run -p $package -n $threads -i $inputsize >> $outfile && echo '.'
$parsec -a run -p $package -n $threads -i $inputsize >> $outfile && echo '.'
$parsec -a run -p $package -n $threads -i $inputsize >> $outfile && echo '.'
$parsec -a run -p $package -n $threads -i $inputsize >> $outfile && echo '.'
$parsec -a run -p $package -n $threads -i $inputsize >> $outfile && echo '.'
$parsec -a run -p $package -n $threads -i $inputsize >> $outfile && echo '.'
$parsec -a run -p $package -n $threads -i $inputsize >> $outfile && echo '.'
$parsec -a run -p $package -n $threads -i $inputsize >> $outfile && echo '.'
