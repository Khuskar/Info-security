#!/bin/bash
CURRENT_TIME=$(date +%H:%M)
END_TIME="17:00"

CURRENT_MINUTES=$(( $(date +%H) * 60 + $(date +%M) ))
END_MINUTES=$(( 17 * 60 ))

REMAINING=$(( END_MINUTES - CURRENT_MINUTES ))

if [ $REMAINING -gt 0 ]; then
  HOURS=$(( REMAINING / 60 ))
  MINUTES=$(( REMAINING % 60 ))
  echo "Current time: $CURRENT_TIME"
  echo "Work day ends after $HOURS hours and $MINUTES minutes."
else
  echo "Current time: $CURRENT_TIME"
  echo "The work day has already ended."
fi

