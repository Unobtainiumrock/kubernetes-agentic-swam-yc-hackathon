#!/bin/bash

yes | ./cleanup.sh
./setup-cluster.sh
./deploy-demo-apps.sh
