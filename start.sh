#!/bin/bash

cat db_part_* > db.zip

unzip -o db.zip

python bot.py
