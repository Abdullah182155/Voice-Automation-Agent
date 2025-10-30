# Voice Automation Agent App

The Voice Automation Agent is an intelligent voice-based assistant that allows users to interact naturally through speech to view or book schedules.
It uses speech recognition, natural language understanding (LLM), and text-to-speech to provide a smooth, hands-free scheduling experience.

Users can speak in English to ask questions like:

“List my upcoming appointments.”

“Book a meeting with Dr. Abdullah tomorrow at 3 PM.”

The agent understands these commands using a Large Language Model (LLM) and converts them into structured actions that trigger API calls to a scheduling backend.


## Requirements

- python 3.10 

### Install Python using MiniConda

1) Download and install MiniConda from [here](https://docs.anaconda.com/free/miniconda/#quick-command-line-install)
2) Create a new environment using the following command:
```bash
$ conda create -n  voice_agent python=3.10
```
3) Activate the environment:
```bash
$ conda activate voice_agent
```

### (Optional) Setup you command line interface for better readability

```bash
export PS1="\[\033[01;32m\]\u@\h:\w\n\[\033[00m\]\$ "
```


## Installation

### Install the required packages

```bash
$ pip install -r requirements.txt
```

### Setup the environment variables

```bash
$ cp .env.example .env
```

## Access Services

- **FastAPI**: http://localhost:8000

## Run the FastAPI server (Development Mode)

```bash
$ uvicorn main:app --reload --host 0.0.0.0 --port 5000
```
