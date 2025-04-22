#!/bin/bash

CLINGO_OPT_STRATEGY="bb"
CLINGO_TIME_LIMIT="180"
CLINGO_OPT_MODE="optN"

PARALLEL_COMMAND="clingo --opt-strategy=$CLINGO_OPT_STRATEGY --time-limit=$CLINGO_TIME_LIMIT --outf=3 --models=0 --opt-mode=$CLINGO_OPT_MODE --project=project encodings/*"

PARALLEL_FILE_PATTERN=medium-finegrained-instances/instances/*.lp
PARALLEL_OUTPUT_FOLDER=medium-finegrained-bb-results

PARALLEL_JOBS=8

mkdir -p $PARALLEL_OUTPUT_FOLDER

export PARALLEL_COMMAND

parallel --progress -j $PARALLEL_JOBS "$PARALLEL_COMMAND {} > $PARALLEL_OUTPUT_FOLDER/{/.}.out 2> $PARALLEL_OUTPUT_FOLDER/{/.}.err" ::: $PARALLEL_FILE_PATTERN
