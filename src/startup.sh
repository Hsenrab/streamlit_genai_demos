#!/bin/bash
set -e
python3 -m pip install --upgrade pip
pip3 install -r requirements.txt
python3.12 -m streamlit run Home.py --server.port 8000 --server.address 0.0.0.0