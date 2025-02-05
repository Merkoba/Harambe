#!/usr/bin/env bash
cd meltdown
clear &&
ruff format && ruff check &&
mypy --strict --strict --strict app.py &&
pyright