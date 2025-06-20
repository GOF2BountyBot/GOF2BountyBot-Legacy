#!/bin/bash
runbot="python3.8 main.py"
usegit=false
cfg=""

if [ "$#" -gt  0 ]; then
    if [ "$1" = "-g" ]; then
        echo "git mode enabled"
        usegit=true
    else
        cfg="$1"
        runbot="python3.8 main.py ${cfg}"
    fi

    if [ "$#" -gt  1 ]; then
        if [ "$2" = "-g" ]; then
            echo "git mode enabled"
            usegit=true
        else
            cfg="$2"
            runbot="python3.8 main.py ${cfg}"
        fi
    fi
fi


echo $runbot
$runbot

while [ "$?" -ne 1 ]; do
    echo "status code $?"
    if [ "$usegit" = true ] && [ "$?" -eq 2 ]; then
        git pull --no-commit --no-ff
        if [ "$?" -ne 0 ]; then
            echo "conflict occurred, aborting"
            git merge --abort
        else
            echo "no conflict, merging"
            git commit
        fi
    fi
    $runbot
done