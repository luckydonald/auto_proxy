#!/bin/bash
set -e;

CMD=python
ARGS="main.py"
echo "exec gosu $USER_UID:$GROUP_UID $CMD $ARGS";
set -ex;
exec gosu $USER_UID:$GROUP_UID $CMD $ARGS;
