#!/bin/bash
set -e

# == START: this is what we need to configure ==
# == END:   this is what we need to configure ==

case $ENV in
  prod)
    export TRUST_LEVEL=3
    export WORKER_SUFFIX=
    ;;
  fake-prod)
    export TRUST_LEVEL=t
    export WORKER_SUFFIX=
    ;;
  dev)
    export TRUST_LEVEL=1
    export WORKER_SUFFIX="-dev"
    ;;
  *)
    exit 1
    ;;
esac

case $COT_PRODUCT in
  firefox)
    export TRUST_DOMAIN=gecko
    case $ENV in
      fake-prod)
        ;;
      prod)
        ;;
      *)
        exit 1
        ;;
    esac
    ;;
  mobile)
    export TRUST_DOMAIN=mobile
    case $ENV in
      fake-prod)
        ;;
      prod)
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

    export GOOGLE_CREDENTIALS_FENIX_NIGHTLY_PATH=$CONFIGDIR/fenix_nightly.p12
    export GOOGLE_CREDENTIALS_FENIX_BETA_PATH=$CONFIGDIR/fenix_beta.p12
    export GOOGLE_CREDENTIALS_FENIX_PROD_PATH=$CONFIGDIR/fenix_prod.p12
    export GOOGLE_CREDENTIALS_FOCUS_PATH=$CONFIGDIR/focus.p12
    export GOOGLE_CREDENTIALS_REFERENCE_BROWSER_PATH=$CONFIGDIR/reference_browser.p12

    echo $GOOGLE_CREDENTIALS_FENIX_NIGHTLY | base64 -d >     $GOOGLE_CREDENTIALS_FENIX_NIGHTLY_PATH
    echo $GOOGLE_CREDENTIALS_FENIX_BETA | base64 -d >        $GOOGLE_CREDENTIALS_FENIX_BETA_PATH
    echo $GOOGLE_CREDENTIALS_FENIX_PROD | base64 -d >        $GOOGLE_CREDENTIALS_FENIX_PROD_PATH
    echo $GOOGLE_CREDENTIALS_FOCUS | base64 -d >             $GOOGLE_CREDENTIALS_FOCUS_PATH
    echo $GOOGLE_CREDENTIALS_REFERENCE_BROWSER | base64 -d > $GOOGLE_CREDENTIALS_REFERENCE_BROWSER_PATH
        ;;
      *)
        exit 1
        ;;
    esac
    ;;
  *)
    exit 1
    ;;
esac

export JARSIGNER_KEY_STORE="/app/mozilla-andoid-keystore"
