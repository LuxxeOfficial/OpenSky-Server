# MIT License

# Copyright (c) 2023 Luxxe

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import re
import os
import json
from flask import Flask, request, jsonify
from translate import Translator

app = Flask(__name__)
TRANSLATIONS_FILE = 'translations.json'

regex = r"[@#$%^&*()_+={}\[\]\\:\";'<>]"

# Set the boolean setting to True to use JSON by default
use_json = False

@app.route('/translate', methods=['POST'])
def translate():
    try:
        data = request.get_json()
        target_lang = data['target_lang']
        from_lang = data['from_lang']
        text = data['text']
        # Sanitize inputs
        target_lang = re.sub(regex, '', target_lang)
        text = re.sub(regex, '', text)
        # Ensure security by limiting the length of input text
        if len(text) > 100:
            raise Exception('Text input is too long.')
        # Check if translation is already in the file
        if use_json:
            with open(TRANSLATIONS_FILE, 'r') as f:
                translations = json.load(f)
            key = f"{text.lower()}_{target_lang.lower()}"
            if key in translations:
                return jsonify({'translation': translations[key]})
        # If translation not in file or JSON not used, request and store it
        translator = Translator(to_lang=target_lang, from_lang=from_lang)
        translation = translator.translate(text)
        if use_json:
            translations[key] = translation
            with open(TRANSLATIONS_FILE, 'w') as f:
                json.dump(translations, f)
        return jsonify({'translation': translation})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    # Create translations file if it doesn't exist
    if use_json and not os.path.exists(TRANSLATIONS_FILE):
        with open(TRANSLATIONS_FILE, 'w') as f:
            json.dump({}, f)
    app.run(debug=True)
