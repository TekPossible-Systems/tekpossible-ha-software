#!/bin/bash

echo "Setting up software baseline and moving installed software from staging to EFS store..."
mkdir -p /software/tekp-ha
mv /opt/installs/* /software/tekp-ha
unlink /opt/tekp-ha/current
ln -s /software/tekp-ha/$LATEST_SOFTWARE_VERSION/ /opt/tekp-ha/current

echo "The current version pointer has been set as such below"
ls -al /opt/tekp-ha/ | grep current

sudo systemctl enable --now tekpossible-ha.service
sudo systemctl restart tekpossible-ha.service

echo "The TekPossible HA Software has been started!"
