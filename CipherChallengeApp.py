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

# Helper to list files in the cipher_challenge directory
def list_files():
    return [f for f in os.listdir(DIRECTORY) if os.path.isfile(os.path.join(DIRECTORY, f))]

# Define layout with input fields, file selection, text areas, and buttons
app.layout = dbc.Container([
    html.H1("Cipher Challenge Interface", style={'textAlign': 'center'}),

    dbc.Row([
        dbc.Col([
            html.Label("Select a File"),
            dcc.Dropdown(
                id='file-dropdown',
                options=[{'label': f, 'value': f} for f in list_files()],
                placeholder="Select a file",
                clearable=False,
                style={'marginBottom': '10px'}
            ),
            dbc.Button("Load File", id='load-file-btn', color="primary", style={'width': '100%', 'marginBottom': '20px'}),
            
            html.Label("File Content (Editable)"),
            dcc.Textarea(id='file-content', style={'width': '100%', 'height': '200px', 'marginBottom': '20px'}),

            html.Label("Cipher Type"),
            dcc.Dropdown(
                id='cipher-type-dropdown',
                options=[
                    {'label': 'Caesar', 'value': 'caesar'},
                    {'label': 'Affine', 'value': 'affine'}
                ],
                value='caesar',
                clearable=False,
                style={'marginBottom': '10px'}
            ),
            html.Label("Cipher Parameters"),
            dcc.Input(id='parameter-a', type='number', placeholder="a", value=5, style={'marginRight': '5px'}),
            dcc.Input(id='parameter-b', type='number', placeholder="b", value=3),
            dbc.Button("Set Cipher", id='set-cipher-btn', color="primary", style={'width': '100%', 'marginTop': '10px', 'marginBottom': '20px'}),
        ], width=4),
        
        dbc.Col([
            html.Label("Text Buffer"),
            dcc.Textarea(id='text-buffer', style={'width': '100%', 'height': '150px', 'marginBottom': '20px'}),
            
            dbc.Button("Encode", id='encode-btn', color="success", style={'width': '48%', 'marginRight': '4%'}),
            dbc.Button("Decode", id='decode-btn', color="danger", style={'width': '48%'}),
            html.Br(), html.Br(),
            dbc.Button("Segment Text", id='segment-btn', color="warning", style={'width': '100%', 'marginBottom': '20px'}),
            
            html.H5("Output"),
            html.Div(id='output-display', style={'whiteSpace': 'pre-line', 'border': '1px solid #ddd', 'padding': '10px', 'height': '150px'}),
            
            html.H5("Substitution Alphabet"),
            html.Div(id='alphabet-display', style={'whiteSpace': 'pre-line', 'border': '1px solid #ddd', 'padding': '10px', 'height': '50px'}),
        ], width=8)
    ])
])

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
    Output('alphabet-display', 'children'),
    Input('set-cipher-btn', 'n_clicks'),
    [State('cipher-type-dropdown', 'value'), State('parameter-a', 'value'), State('parameter-b', 'value')]
)
def update_cipher(n_clicks, cipher_type, a, b):
    if cipher_type == 'caesar':
        cipher.reset_cipher_alphabet(cipher_type='caesar', b=b)
    elif cipher_type == 'affine':
        cipher.reset_cipher_alphabet(cipher_type='affine', a=a, b=b)
    substitution_alphabet = cipher.create_substitution_alphabet()
    alphabet_str = ' '.join(substitution_alphabet.values())
    return f"Substitution Alphabet:\n{alphabet_str}"

# Callback to encode the text buffer
@app.callback(
    Output('encode-output-display', 'children'),
    Input('encode-btn', 'n_clicks'),
    State('text-buffer', 'value')
)
def encode_text(n_clicks, text):
    if text:
        encoded_text = cipher.encode(text)
        return f"Encoded Text:\n{encoded_text}"
    return "No text provided to encode."

# Callback to decode the text buffer
@app.callback(
    Output('decode-output-display', 'children'),
    Input('decode-btn', 'n_clicks'),
    State('text-buffer', 'value')
)
def decode_text(n_clicks, text):
    if text:
        decoded_text = cipher.decode(text)
        return f"Decoded Text:\n{decoded_text}"
    return "No text provided to decode."

# Callback to segment the text buffer
@app.callback(
    Output('buffer-output-display', 'children'),
    Input('segment-btn', 'n_clicks'),
    State('text-buffer', 'value')
)
def segment_text(n_clicks, text):
    if text:
        segmented_words = segmenter.word_segmentation(text)
        return f"Segmented Text:\n{' '.join(segmented_words)}"
    return "No text provided for segmentation."

# Callback to show the substitution alphabet
@app.callback(
    Output('alphabet-display', 'value'),
    Input('cipher-dropdown', 'value') 
)
def update_alphabet_display(cipher_type):
    if cipher_type:
        cipher = SubstitutionCipher(cipher_type=cipher_type)
        alphabet_dict = cipher.create_substitution_alphabet()
        alphabet_str = ' '.join([f"{k}->{v}" for k, v in alphabet_dict.items()])
        return alphabet_str
    return "Select a cipher to view its alphabet."


# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
