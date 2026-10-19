from flask import Flask, request, jsonify
import re
from difflib import SequenceMatcher

app = Flask(__name__)

def split_sentences(text):
    if not text:
        return []
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]

@app.route('/api/compare', methods=['POST'])
def compare():
    data = request.get_json() or {}
    originals = data.get('originals', [])
    corrected = data.get('corrected', '')

    corr_sentences = split_sentences(corrected)
    results = []

    for orig_idx, original in enumerate(originals):
        orig_sentences = split_sentences(original)
        highlighted_sentences = []

        for i, o_sent in enumerate(orig_sentences):
            start_idx = max(0, i - 5)
            end_idx = min(len(corr_sentences), i + 6)
            window_corr = " ".join(corr_sentences[start_idx:end_idx])

            matcher = SequenceMatcher(None, o_sent, window_corr)
            blocks = matcher.get_matching_blocks()

            marked_chars = [False] * len(o_sent)
            for a, b, size in blocks:
                for k in range(size):
                    if o_sent[a + k].strip():
                        marked_chars[a + k] = True

            marked_sent = ""
            in_mark = False
            for j, char in enumerate(o_sent):
                if marked_chars[j] and not in_mark:
                    marked_sent += "<mark>" + char
                    in_mark = True
                elif not marked_chars[j] and in_mark:
                    marked_sent += "</mark>" + char
                    in_mark = False
                else:
                    marked_sent += char
            if in_mark:
                marked_sent += "</mark>"

            highlighted_sentences.append(marked_sent)

        results.append({
            "version": orig_idx + 1,
            "highlighted_text": " ".join(highlighted_sentences)
        })

    return jsonify({"results": results, "corrected": corrected})