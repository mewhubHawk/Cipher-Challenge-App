import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import os
from ciphers import SubstitutionCipher, WordSegmenter  # Ensure these are defined elsewhere

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

# Define layout with input fields, file selection, text areas, and buttons
app.layout = html.Div(
    style={"padding": "20px", "background-color": "#E8EAF6"},  # Indigo-light background
    children=[
        html.H1("Cipher Challenge Interface", style={"color": "#3F51B5"}),  # Primary Indigo

        # File selection dropdown and display area
        html.Label("Select a file:", style={"color": "#3F51B5"}),
        dcc.Dropdown(
            id="file-selector",
            placeholder="Choose a file",
            style={"width": "50%", "margin-bottom": "20px"}
        ),
        html.Button("Load File", id="load-button", style={"background-color": "#FF4081", "color": "white"}),  # Secondary Pink

        # Radio options for Encode/Decode and Segmentation Checkbox
        html.Div([
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
        ], style={"margin-top": "10px", "margin-bottom": "20px"}),

        # Text buffer and result display areas
        html.Label("Input Buffer:", style={"color": "#3F51B5"}),
        dcc.Textarea(id="buffer-input", style={"width": "100%", "height": "100px", "background-color": "#E3F2FD"}),  # Light Indigo
        html.Label("Processed Output:", style={"color": "#3F51B5"}),
        dcc.Textarea(id="output-display", style={"width": "100%", "height": "100px", "background-color": "#E3F2FD"}),  # Light Indigo

        # Process button
        html.Button("Process", id="process-button", style={"background-color": "#FF4081", "color": "white"})
    ]
)

# Callback to load the selected file and display contents
@app.callback(
    Output('file-content', 'value'),
    Output('text-buffer', 'value'),
    Input('load-file-btn', 'n_clicks'),
    State('file-dropdown', 'value')
)
def load_file(n_clicks, filename):
    if n_clicks and filename:  # Only proceed if button is clicked and filename is valid
        try:
            path = os.path.join(DIRECTORY, filename)
            with open(path, 'r') as file:
                content = file.read()
            return content, content  # Load content to both 'file-content' and 'text-buffer'
        except Exception as e:
            print(f"Error loading file: {e}")
            return "Error loading file. Please check if the file exists and is readable.", ""
    return "", ""

# Callback to set cipher parameters and display substitution alphabet
@app.callback(
    Output('alphabet-display', 'value'),
    Input('set-cipher-btn', 'n_clicks'),
    [State('cipher-type-dropdown', 'value'), State('parameter-a', 'value'), State('parameter-b', 'value')]
)
def update_cipher(n_clicks, cipher_type, a, b):
    if cipher_type == 'caesar':
        cipher.reset_cipher_alphabet(cipher_type='caesar', b=b)
    elif cipher_type == 'affine':
        cipher.reset_cipher_alphabet(cipher_type='affine', a=a, b=b)
    substitution_alphabet = cipher.select_substitution_alphabet()
    alphabet_str = ' '.join(substitution_alphabet.values())
    # return f"Substitution Alphabet:\n{alphabet_str}"
    return alphabet_str


@app.callback(
    Output("output-display", "value"),
    Input("process-button", "n_clicks"),
    State("buffer-input", "value"),
    State("operation-selector", "value"),
    State("segmentation-check", "value")
)
def process_text(n_clicks, text, operation, segmentation):
    if not n_clicks:
        return ""
    result = text
    if operation == "encode":
        result = SubstitutionCipher().encode(text)
    elif operation == "decode":
        result = SubstitutionCipher().decode(text)
    if segmentation:
        result = " ".join(WordSegmenter("dictionary.txt").word_segmentation(result))
    return result

# Populate file list
@app.callback(
    Output("file-selector", "options"),
    Input("load-button", "n_clicks")
)
def update_file_list(n_clicks):
    files = os.listdir('./cipher_challenge')
    return [{"label": file, "value": file} for file in files if file.endswith('.txt')]

if __name__ == "__main__":
    app.run_server(debug=True)


# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
