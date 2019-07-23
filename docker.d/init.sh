#!/bin/bash
set -e

# == START: This system variables are set by cloudops ==
test $PROJECT_NAME
test $ENV  # ENV should be set to "dep", "prod"
test $COT_PRODUCT  # either "firefox" or "mobile"
test $TASKCLUSTER_CLIENT_ID
test $TASKCLUSTER_ACCESS_TOKEN
#test $ED25519_PRIVKEY  # optional since on staging we don't sign CoT files
# == END ==

TEMPLATEDIR=/app/docker.d/configs
CONFIGDIR=/app/configs
CONFIGLOADER=/app/bin/configloader
SCRIPTWORKER=/app/bin/scriptworker

if [ "COT_PRODUCT" == "mobile"]; then
  if [ "ENV" == "prod" ]; then
    test $GOOGLE_PLAY_SERVICE_ACCOUNT_FENIX_NIGHTLY
    test $GOOGLE_CREDENTIALS_FENIX_NIGHTLY
    test $GOOGLE_PLAY_SERVICE_ACCOUNT_FENIX_BETA
    test $GOOGLE_CREDENTIALS_FENIX_BETA
    test $GOOGLE_PLAY_SERVICE_ACCOUNT_FENIX_PROD
    test $GOOGLE_CREDENTIALS_FENIX_PROD
    test $GOOGLE_PLAY_SERVICE_ACCOUNT_FOCUS
    test $GOOGLE_CREDENTIALS_FOCUS
    test $GOOGLE_PLAY_SERVICE_ACCOUNT_REFERENCE_BROWSER
    test $GOOGLE_CREDENTIALS_REFERENCE_BROWSER
    echo $GOOGLE_CREDENTIALS_FENIX_NIGHTLY | base64 -d > $CONFIGDIR/fenix_nightly.p12
    echo $GOOGLE_CREDENTIALS_FENIX_BETA | base64 -d > $CONFIGDIR/fenix_beta.p12
    echo $GOOGLE_CREDENTIALS_FENIX_PROD | base64 -d > $CONFIGDIR/fenix_prod.p12
    echo $GOOGLE_CREDENTIALS_FOCUS | base64 -d > $CONFIGDIR/focus.p12
    echo $GOOGLE_CREDENTIALS_REFERENCE_BROWSER | base64 -d > $CONFIGDIR/reference_browser.p12
  elif [ "ENV" == "dep" ]; then
    test $GOOGLE_CREDENTIALS_FENIX
    test $GOOGLE_CREDENTIALS_FOCUS
    test $GOOGLE_CREDENTIALS_REFERENCE_BROWSER
    echo $GOOGLE_CREDENTIALS_FENIX | base64 -d > $CONFIGDIR/fenix.p12
    echo $GOOGLE_CREDENTIALS_FOCUS | base64 -d > $CONFIGDIR/focus.p12
    echo $GOOGLE_CREDENTIALS_REFERENCE_BROWSER | base64 -d > $CONFIGDIR/reference_browser.p12
  fi
elif [ "COT_PRODUCT"] == "firefox"; then
  if [ "ENV" == "prod" ]; then
    test $GOOGLE_PLAY_SERVICE_ACCOUNT_AURORA
    test $GOOGLE_CREDENTIALS_AURORA
    test $GOOGLE_PLAY_SERVICE_ACCOUNT_BETA
    test $GOOGLE_CREDENTIALS_BETA
    test $GOOGLE_PLAY_SERVICE_ACCOUNT_RELEASE
    test $GOOGLE_CREDENTIALS_RELEASE
    echo $GOOGLE_CREDENTIALS_AURORA | base64 -d > $CONFIGDIR/aurora.p12
    echo $GOOGLE_CREDENTIALS_BETA | base64 -d > $CONFIGDIR/beta.p12
    echo $GOOGLE_CREDENTIALS_RELEASE | base64 -d > $CONFIGDIR/release.p12
  elif [ "ENV" == "dep" ]; then
    test $GOOGLE_CREDENTIALS_DEP
    echo $GOOGLE_CREDENTIALS_DEP | base64 -d > $CONFIGDIR/dep.p12
  fi
fi

mkdir -p -m 700 $CONFIGDIR

# Eval JSON-e expressions in the config templates
$CONFIGLOADER --worker-id-prefix=${PROJECT_NAME}script-${ENV}- $TEMPLATEDIR/scriptworker.yaml $CONFIGDIR/scriptworker.json
$CONFIGLOADER $TEMPLATEDIR/worker.json $CONFIGDIR/worker_config.json

echo $ED25519_PRIVKEY > $CONFIGDIR/ed25519_privkey
chmod 600 $CONFIGDIR/ed25519_privkey

exec $SCRIPTWORKER $CONFIGDIR/scriptworker.json
