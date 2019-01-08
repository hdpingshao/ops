#!/bin/bash

OLD_PWD=$PWD
cd /usr/local/tomcat/webapps/ROOT

if [ "${GIT_TAG_MESSAGE}" == "dev" ]; then
    touch dev
elif [ "${GIT_TAG_MESSAGE}" == "test" ]; then
    touch test
elif [ "${GIT_TAG_MESSAGE}" == "prod" ]; then
    touch prod
fi

cd $OLD_PWD
exec "$@"
