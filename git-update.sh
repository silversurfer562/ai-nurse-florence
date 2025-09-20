#!/bin/bash
git add .
git commit -m "update: latest changes"
git pull --rebase origin main
git push origin main
