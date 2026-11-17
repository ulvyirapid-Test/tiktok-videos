#!/bin/bash
# Prepend a 0.1 s still (frame at $2 seconds, default 3) so TikTok's default cover (first frame) shows the title.
set -e
V=$1; T=${2:-3}; TMP=$(mktemp -d)
ffmpeg -v error -y -ss $T -i "$V" -frames:v 1 "$TMP/c.png"
ffmpeg -v error -y -i "$V" -loop 1 -t 0.1 -i "$TMP/c.png" -filter_complex \
 "[1:v]fps=30,scale=1080:1920,format=yuv420p,setsar=1[c];[0:v]fps=30,format=yuv420p,setsar=1[v];[c][v]concat=n=2:v=1:a=0[ov];[0:a]adelay=100|100[oa]" \
 -map "[ov]" -map "[oa]" -c:v libx264 -preset veryfast -crf 20 -c:a aac -b:a 160k -movflags +faststart "$TMP/out.mp4"
mv "$TMP/out.mp4" "$V"; rm -rf "$TMP"
