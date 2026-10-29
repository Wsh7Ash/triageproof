#!/bin/sh
# Sends a 512-byte header with a zero-length body to a local build.
printf 'POST /parse HTTP/1.1\r\nContent-Length: 512\r\n\r\n' | nc -q1 127.0.0.1 8080
