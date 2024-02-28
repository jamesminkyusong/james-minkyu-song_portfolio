#!/bin/bash

(( port=7005 ))

streamlit run app.py --server.port $port
