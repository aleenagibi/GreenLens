# GreenLens 

### Carbon-Aware AI Inference Orchestration

GreenLens is an AI inference orchestration project that helps make
language-model selection more transparent and resource-conscious.
Instead of treating every prompt as a reason to use the same model,
GreenLens evaluates available models against task requirements and
operational factors, selects a suitable candidate, executes the request,
and explains the routing decision.

The project brings **model selection, inference execution, and
sustainability-aware analysis** into one application.

## Why GreenLens?

Language models differ in capability, response time, availability, and
cost. Their computational demands and environmental impact can also
vary. Choosing a model without considering the task can lead to
unnecessary expense or resource use.

GreenLens explores how an inference-routing layer can make these
trade-offs more visible and help select an appropriate model for each
request.

## How It Works

A request moves through the GreenLens pipeline:

1.  **Understand the task** --- represent the prompt for downstream
    analysis.
2.  **Estimate task complexity** --- assess characteristics that
    influence the level of model capability required.
3.  **Evaluate candidate models** --- use the available model catalogue
    and capability signals.
4.  **Assess operational factors** --- consider available cost, latency,
    availability, and environmental estimates.
5.  **Select a model** --- rank eligible candidates according to the
    implemented routing objective.
6.  **Execute the request** --- send the prompt to the selected provider
    and retrieve its response.
7.  **Explain the decision** --- expose available information about the
    selected model and routing outcome.

The exact evidence available for each candidate depends on the provider
catalogue and the data accessible to the current implementation.

## Key Features

-   **Task-aware model routing** to avoid relying on one fixed model for
    every request.
-   **Inference execution** through the configured model provider.
-   **Routing transparency** with model-selection details and
    explanations when available.
-   **Sustainability-aware analysis** using available energy and carbon
    estimates.
-   **Cost and latency awareness** to help compare operational
    trade-offs.
-   **Model comparison** to inspect alternatives where comparison data
    is available.
-   **Chat interface** for submitting prompts and viewing generated
    responses.
-   **Insights dashboard** for reviewing available routing and usage
    records.
-   **Chat history** for revisiting previous interactions.
-   **Pipeline overview** explaining the stages behind a routing
    decision.

## Application

GreenLens provides separate experiences for interaction and analysis:

-   **Chat:** submit a task, receive the generated response, and inspect
    relevant model and routing information.
-   **Insights:** review available metrics and routing activity through
    a dedicated analytics view.
-   **History:** revisit saved requests and responses.
-   **How It Works:** explore the stages of the inference-routing
    pipeline.

The interface uses a dark charcoal and green visual identity inspired by
the project's focus on sustainability and AI infrastructure.

## Technology Stack

The project combines the following technologies, as configured in the
repository:

  -----------------------------------------------------------------------
  Layer                               Technologies
  ----------------------------------- -----------------------------------
  Frontend                            React, TypeScript, Vite, CSS

  API                                 Python, FastAPI, Uvicorn

  Model access                        OpenRouter with an
                                      OpenAI-compatible client

  Semantic representation             Sentence Transformers

  Similarity search                   FAISS and scikit-learn components

  Environmental estimation            EcoLogits-based estimation where
                                      supported

  Data and persistence                PostgreSQL and browser-local
                                      history where configured
  -----------------------------------------------------------------------

## Architecture at a Glance

``` text
User Prompt
    ↓
Task Representation
    ↓
Complexity and Capability Analysis
    ↓
Candidate Evaluation
    ↓
Routing and Model Selection
    ↓
Provider API
    ↓
Generated Response
    ↓
Routing Explanation and Available Impact Estimates
```

The React frontend communicates with the FastAPI backend. The backend
coordinates model evaluation, routing, provider execution, and the
response data returned to the interface.

## Getting Started

### Requirements

-   Node.js and npm
-   Python and the backend dependencies listed in the repository
-   The provider credentials required by your backend configuration

### Run the frontend

From the frontend project directory:

``` bash
npm install
npm run dev
```

### Run the backend

Activate the project's Python virtual environment, install the
dependencies listed in the backend requirements file, and start the
FastAPI application using the entry point configured in your repository.
For a typical setup, the command is:

``` bash
uvicorn app.main:app --reload
```

The frontend's current chat integration expects the backend at
`http://127.0.0.1:8000/chat`. Adjust the configuration if your local
setup uses a different address.

**Configuration note:** Set provider credentials in your local
environment. Do not commit API keys or `.env` files to version control.

## Sustainability and Evaluation Notes

GreenLens is designed to make environmental considerations part of model
routing, but the quality of its conclusions depends on the quality of
its input data.

-   Energy and carbon values may be estimates or fallbacks rather than
    direct measurements.
-   Model catalogues, pricing, availability, and provider restrictions
    can change.
-   A lower estimated environmental impact does not by itself establish
    that a response is sufficiently accurate or useful.
-   A routing decision is not proof of carbon savings unless it is
    evaluated against a suitable baseline using reliable measurements.

These distinctions are important when interpreting dashboard metrics and
comparing routing outcomes. The project provides a foundation for
testing sustainability-aware inference decisions; stronger controlled
evaluation and validated environmental measurements can improve the
reliability of future results.

## Project Goal

**GreenLens aims to make AI inference more deliberate: choose a suitable
model for the task, execute the request, and make the trade-offs behind
that decision visible.**
