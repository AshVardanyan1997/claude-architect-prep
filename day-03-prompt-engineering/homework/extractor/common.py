"""Shared pieces: the API client and the settings read from .env."""

import os

import anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = os.environ.get("MODEL", "claude-opus-5-5")
EFFORT = os.environ.get("EFFORT", "medium")


def make_client():
    return anthropic.Anthropic()
