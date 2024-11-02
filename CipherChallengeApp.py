import os
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from flask import Flask

from ciphers import SubstitutionCipher, WordSegmenter  

# Initialize cipher and segmenter
cipher = SubstitutionCipher()
segmenter = WordSegmenter("/usr/share/dict/words", "special_words.txt")

# Directory to list files from
DIRECTORY = "./cipher_challenge"

# Initialize Dash app with Material Design theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MATERIA])
# app = dash.Dash(__name__, external_stylesheets=['/style.css'])

# Helper to list files in the cipher_challenge directory
def list_files():
    return [f for f in os.listdir(DIRECTORY) if os.path.isfile(os.path.join(DIRECTORY, f))]

app.layout = html.Div(
    style={"padding": "20px", "background-color": "#E8EAF6"},
    children=[
        html.H1("Cipher Challenge Interface", style={"color": "#3F51B5"}),

        # File selection and display areas
        html.Label("Select a file:", style={"color": "#3F51B5"}),
        dcc.Dropdown(
            id="file-selector",
            placeholder="Choose a file",
            style={"width": "50%", "margin-bottom": "20px"}
        ),
        html.Button("Load File", id="load-button", style={"background-color": "#FF4081", "color": "white"}),

        # Cipher options and alphabet display
        html.Div([
            html.Label("Cipher Type:", style={"color": "#3F51B5"}),
            dcc.Dropdown(
                id="cipher-type-selector",
                options=[
                    {"label": "Caesar", "value": "caesar"},
                    {"label": "Atbash", "value": "atbash"},
                    {"label": "Affine", "value": "affine"}
                ],
                value="caesar",
                style={"margin-bottom": "20px", "width": "50%"}
            ),
            html.Label("Current Decoding Alphabet:", style={"color": "#3F51B5"}),
            dcc.Textarea(id="alphabet-display", style={"width": "100%", "height": "50px", "background-color": "#E3F2FD"})
        ], style={"margin-bottom": "20px"}),

        # Operation selectors (encode/decode) and segmentation checkbox
        html.Label("Operation:", style={"color": "#3F51B5"}),
        dcc.RadioItems(
            id="operation-selector",
            options=[
                {"label": "Encode", "value": "encode"},
                {"label": "Decode", "value": "decode"}
            ],
            value="encode",
            labelStyle={"display": "block", "color": "#3F51B5"}
        ),
        dcc.Checklist(
            id="segmentation-check",
            options=[{"label": "Segment Text", "value": "segment"}],
            style={"margin-bottom": "20px", "color": "#3F51B5"}
        ),

        # Text buffer and result display
        html.Label("Input Buffer:", style={"color": "#3F51B5"}),
        dcc.Textarea(id="buffer-input", style={"width": "100%", "height": "100px", "background-color": "#E3F2FD"}),
        html.Label("Processed Output:", style={"color": "#3F51B5"}),
        dcc.Textarea(id="processed-output-display", style={"width": "100%", "height": "100px", "background-color": "#E3F2FD"}),

        html.Button("Process", id="process-button", style={"background-color": "#FF4081", "color": "white"})
    ]
)

# Store selected cipher type and create a substitution cipher instance
cipher_instance = SubstitutionCipher(cipher_type="caesar")

# Callback to update text buffer and alphabet display upon file load
@app.callback(
    Output("buffer-input", "value"),
    # Output("output-display", "value"),
    Input("load-button", "n_clicks"),
    State("file-selector", "value")
)
def load_file(n_clicks, filename):
    if n_clicks and filename:
        with open(f"./cipher_challenge/{filename}", "r") as file:
            text = file.read()
        return text
    return "input file"

# Callback for cipher type and alphabet display
@app.callback(
    Output("alphabet-display", "value"),
    Input("cipher-type-selector", "value")
)
def update_cipher_alphabet(cipher_type):
    global cipher_instance
    cipher_instance.set_cipher_alphabet(cipher_type)
    cipher_alphabet = cipher_instance.select_substitution_alphabet()
    return ' '.join(val for key, val in cipher_alphabet.items())

# Main processing callback
@app.callback(
    Output("processed-output-display", "value"),
    Input("process-button", "n_clicks"),
    State("buffer-input", "value"),
    State("operation-selector", "value"),
    State("segmentation-check", "value"),
    State("cipher-type-selector", "value")
)
def process_text(n_clicks, text, operation, segmentation, cipher_type):
    if not n_clicks:
        return ""
    
    cipher_instance.set_cipher_alphabet(cipher_type)
    result = text
    if operation == "encode":
        result = cipher_instance.encode(text)
    elif operation == "decode":
        result = cipher_instance.decode(text)
    if segmentation:
        result = " ".join(WordSegmenter("dictionary.txt").word_segmentation(result))
    
    return result

# Callback to populate file list
@app.callback(
    Output("file-selector", "options"),
    Input("load-button", "n_clicks")
)
def update_file_list(n_clicks):
    files = os.listdir('./cipher_challenge')
    return [{"label": file, "value": file} for file in files if file.endswith('.txt')]

if __name__ == "__main__":
    app.run_server(debug=True)
