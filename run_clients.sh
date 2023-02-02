#!/bin/bash
for i in 0 1 2 3
do
    gnome-terminal --geometry=10x10+0+$((i*220)) -- 'minesweeper'
done