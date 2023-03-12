#!/bin/bash

ALIAS="alias ue='python3 $(pwd)/upcoming_events.py -p 2'"

echo $ALIAS >> ~/.bashrc
source ~/.bashrc
