#!/usr/bin/env bash
clear &&
ruff format && ruff check &&
mypy --strict --strict --strict app.py &&
pyright