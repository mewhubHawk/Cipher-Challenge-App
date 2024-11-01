import tkinter as tk
from tkinter import filedialog, messagebox
import argparse
import string
import cmd
import os


class SubstitutionCipher:
    def __init__(self, cipher_type='affine', a=5, b=8):
        self.cipher_type = cipher_type
        self.a = a  # Multiplier for Affine Cipher
        self.b = b  # Shift for both Affine and Caesar Ciphers
        self.alphabet = string.ascii_uppercase
        self.precomputed_alphabets = self.precompute_all_substitution_alphabets()

    def precompute_all_substitution_alphabets(self):
        """Precompute alphabets for all possible Caesar and Affine ciphers."""
        caesar_alphabets = {b: self._caesar_shift(b) for b in range(26)}
        affine_alphabets = {(a, b): self._affine_shift(a, b) for a in range(1, 26, 2) for b in range(26) if self._gcd(a, 26) == 1}
        return {'caesar': caesar_alphabets, 'affine': affine_alphabets}

    def _caesar_shift(self, b):
        """Helper to calculate Caesar shift alphabet for a given b."""
        return self.alphabet[b:] + self.alphabet[:b]

    def _affine_shift(self, a, b):
        """Helper to calculate Affine shift alphabet for given a and b."""
        return ''.join(self.alphabet[(a * i + b) % 26] for i in range(26))

    def _gcd(self, a, b):
        """Helper to compute the greatest common divisor."""
        while b != 0:
            a, b = b, a % b
        return a
    
    def select_substitution_alphabet(self):
        if self.cipher_type == 'caesar':
            shifted_alphabet = self.precomputed_alphabets['caesar'][self.b]
        elif self.cipher_type == 'affine':
            shifted_alphabet = self.precomputed_alphabets['affine'][(self.a,self.b)]
        else:
            raise ValueError(f"Unknown cipher type: {self.cipher_type}")
        return dict(zip(self.alphabet, shifted_alphabet))

    def encode(self, plaintext):
        substitution_dict = self.select_substitution_alphabet()
        plaintext = plaintext.upper()
        return ''.join(substitution_dict.get(char, char) for char in plaintext)

    def decode(self, ciphertext):
        substitution_dict = self.select_substitution_alphabet()
        reverse_dict = {v: k for k, v in substitution_dict.items()}
        ciphertext = ciphertext.upper()
        return ''.join(reverse_dict.get(char, char) for char in ciphertext)

    def brute_force_decode(self, ciphertext):
        """Try all Caesar and Affine cipher parameters to brute-force decode."""
        brute_force_results = {}

        # Try all Caesar shifts
        self.cipher_type = 'caesar'
        for b in range(26):
            self.b = b
            decoded_text = self.decode(ciphertext)
            brute_force_results[f"Caesar b={b}"] = decoded_text

        # Try all valid Affine (a, b) pairs
        self.cipher_type = 'affine'
        for a in range(1, 26, 2):
            if self._gcd(a, 26) == 1:
                for b in range(26):
                    self.a = a
                    self.b = b
                    decoded_text = self.decode(ciphertext)
                    brute_force_results[f"Affine a={a} b={b}"] = decoded_text
        return brute_force_results

    def reset_cipher_alphabet(self, cipher_type=None, a=None, b=None):
        """Reset cipher type and parameters."""
        if cipher_type:
            self.cipher_type = cipher_type
        if a is not None:
            self.a = a
        if b is not None:
            self.b = b
        self.precomputed_alphabets = self.precompute_all_substitution_alphabets()


class WordSegmenter:
    def __init__(self, dictionary_path, special_words_path=None):
        self.valid_words = self.load_dictionary(dictionary_path)
        self.special_words = self.load_special_words(special_words_path)

    def load_dictionary(self, file_path):
        with open(file_path, 'r') as file:
            valid_words = set(word.strip().lower() for word in file)
        return valid_words

    def load_special_words(self, file_path=None):
        if file_path:
            with open(file_path, 'r') as file:
                special_words = set(word.strip().lower() for word in file)
        else:
            special_words = {"babbage", "lovelace", "palmerstone", "ada", "charles", "lord"}
        return special_words

    def load_text_from_file(self, file_path):
        with open(file_path, 'r') as file:
            return file.read().replace("\n", "").replace("\r", "").strip().lower()

    def word_segmentation(self, text):
        cleaned_text = ''.join(char for char in text.lower() if char in string.ascii_lowercase)
        n = len(cleaned_text)
        dp = [None] * (n + 1)
        dp[0] = []

        for i in range(1, n + 1):
            for j in range(i):
                word = cleaned_text[j:i]
                if word in self.special_words and dp[j] is not None:
                    if dp[i] is None or len(dp[j]) + 1 < len(dp[i]):
                        dp[i] = dp[j] + [word]
                elif word in self.valid_words and dp[j] is not None:
                    if dp[i] is None or len(dp[j]) + 1 < len(dp[i]):
                        dp[i] = dp[j] + [word]

        return dp[n] if dp[n] is not None else []


# Helper function to list available cipher challenge files
def list_files(directory):
    return [f for f in os.listdir(directory) if f.endswith('.txt')]
