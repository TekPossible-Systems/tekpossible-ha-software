#!/bin/bash

LATEST_SOFTWARE_VERSION=$(cat /etc/tekpossible-ha-release)
echo "Setting up software baseline and moving installed software from staging to EFS store..."
mkdir -p /software/tekp-ha
mkdir -p /opt/tekp-ha
\cp -r /opt/staging/* /software/tekp-ha
rm -rf /opt/staging
unlink /opt/tekp-ha/current
ln -s /software/tekp-ha/$LATEST_SOFTWARE_VERSION/ /opt/tekp-ha/current

echo "The current version pointer has been set as such below"
ls -al /opt/tekp-ha/ | grep current

sudo systemctl enable --now tekpossible-ha.service
sudo systemctl restart tekpossible-ha.service

echo "The TekPossible HA Software has been started!"
