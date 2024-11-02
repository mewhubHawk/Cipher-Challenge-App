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

        # File selection and in buffer display
        dbc.Button("Load File", id='load-button', color="primary", style={'marginTop': '10px', 'marginBottom': '10px'}),
        dcc.Dropdown(
            id="file-selector",
            placeholder="Choose a file",
            style={"width": "50%", "margin-bottom": "10px"}
        ),
        dcc.Textarea(id="buffer-input", style={"width": "100%", "height": "100px", "background-color": "#E3F2FD"}),

        # Cipher and alphabet display
        dbc.Button("Set Cipher", id='set-cipher-btn', color="primary", style={'marginTop': '10px', 'marginBottom': '10px'}),

        dcc.Dropdown(
            id="cipher-type-selector",
            options=[
                {"label": "Caesar", "value": "caesar"},
                {"label": "Atbash", "value": "atbash"},
                {"label": "Affine", "value": "affine"}
            ],
            value="caesar",
            style={"margin-bottom": "5px", "width": "50%"}
        ),
        dcc.Input(id='parameter-a', type='number', placeholder="a", value=5, style={'marginLeft': '5px'}),
        dcc.Input(id='parameter-b', type='number', placeholder="b", value=3, style={'marginLeft': '5px'}),


        # Encode/decode and segmentation selection
        dcc.RadioItems(
            id="operation-selector",
            options=[
                {"label": "Decode", "value": "decode"},
                {"label": "Encode", "value": "encode"}
            ],
            value="decode",
            labelStyle={"display": "block", "color": "#3F51B5"}
        ),
        dcc.Checklist(
            id="segmentation-check",
            options=[{"label": "Segment Text", "value": "segment"}],
            style={"margin-bottom": "5px", "color": "#3F51B5"}
        ),
        dcc.Textarea(id="alphabet-display", style={"width": "75%", "height": "50px", "background-color": "#E3F2FD"}),

        # Display output results
        html.H4("Processed Output", style={"color": "#3F51B5"}),
        dcc.Textarea(id="processed-output-display", style={"width": "100%", "height": "100px", "background-color": "#E3F2FD"}),
    ]
)

# Callback to populate file list
@app.callback(
    Output("file-selector", "options"),
    Input("load-button", "n_clicks")
)
def update_file_list(n_clicks):
    files = os.listdir('./cipher_challenge')
    return [{"label": file, "value": file} for file in files if file.endswith('.txt')]

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

# Callback to set cipher parameters and display substitution alphabet
@app.callback(
    Output('alphabet-display', 'value'),
    Input('set-cipher-btn', 'n_clicks'),
    [State('cipher-type-selector', 'value'), State('parameter-a', 'value'), State('parameter-b', 'value')]
)
def update_cipher(n_clicks, cipher_type, a, b):
    if cipher_type == 'caesar':
        cipher.set_cipher_alphabet(cipher_type='caesar', b=b)
    elif cipher_type == 'affine':
        cipher.set_cipher_alphabet(cipher_type='affine', a=a, b=b)
    substitution_alphabet = cipher.select_substitution_alphabet()
    alphabet_str = ' '.join(substitution_alphabet.values())
    # return f"Substitution Alphabet:\n{alphabet_str}"
    return ' '.join(val for key, val in substitution_alphabet.items())

# Main processing callback
@app.callback(
    Output("processed-output-display", "value"),
    # Input("process-button", "n_clicks"),
    Input('set-cipher-btn', 'n_clicks'),
    State("buffer-input", "value"),
    State("operation-selector", "value"),
    State("segmentation-check", "value"),
    State("cipher-type-selector", "value")
)
def process_text(n_clicks, text, operation, segmentation, cipher_type):
    if not n_clicks:
        return ""
    
    cipher.set_cipher_alphabet(cipher_type)
    result = text
    if operation == "encode":
        result = cipher.encode(text)
    elif operation == "decode":
        result = cipher.decode(text)
    if segmentation:
        result = " ".join(WordSegmenter("dictionary.txt").word_segmentation(result))
    
    return result


if __name__ == "__main__":
    app.run_server(debug=True)
