#!/bin/sh

infile="$1"
outfile="$2"

if [ -z "$infile" -o -z "$outfile" ]; then
  echo "usage: $0 input_file output_file" >&2
  exit 1
fi

osmium tags-filter "$infile" -o "$outfile" \
  /railway=station /railway=halt /railway=service_station
