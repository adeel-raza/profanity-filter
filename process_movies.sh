#!/bin/bash
# Process both movies and generate summary

cd "/home/adeel/Link to html/wp_local/movie_cleaner"
source venv/bin/activate

echo "Processing Code_3.mkv..."
python clean.py "movies/Code_3.mkv" "movies/cleaned/Code_3_cleaned.mkv" \
    --fast --nsfw-threshold 0.3 --sample-rate 0.5 \
    --subs "movies/Code_3.srt" \
    2>&1 | tee /tmp/code3_clean.log

echo ""
echo "Processing argo.mp4..."
python clean.py "movies/argo/argo.mp4" "movies/cleaned/argo_cleaned.mp4" \
    --fast --nsfw-threshold 0.3 --sample-rate 0.5 \
    --subs "movies/argo/argo.srt" \
    2>&1 | tee /tmp/argo_clean.log

echo ""
echo "Generating summary..."
python generate_summary.py "movies" "movies/cleaned" 2>&1





