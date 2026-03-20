# Agent Starter Pack - Quickstart Guide

Welcome to the Agent Starter Pack! Follow these instructions to test and deploy your agents locally or in production.

## 🚀 Local Testing

Follow these steps to run any of the agents locally:

1. **Authenticate with Google Cloud:**
   Make sure your account has at least logging access to your Google Cloud project, then run:
   ```bash
   gcloud auth application-default login
   ```

2. **Configure Environment Variables:**
   Create a `.env` file in the root directory of this repository with the following configuration:
   ```env
   GOOGLE_GENAI_USE_VERTEXAI=1
   GOOGLE_CLOUD_PROJECT=[your GCP project id]
   GOOGLE_CLOUD_LOCATION=global
   GH_TOKEN=[your github PAT ideally readonly]
   ```

3. **Install Dependencies:**
   Navigate to the specific agent's folder and run the enhancement command to install all necessary libraries:
   ```bash
   uvx agent-starter-pack enhance
   ```

4. **Launch the Playground:**
   Start the local Agent Development Kit (ADK) server:
   ```bash
   make playground
   ```

5. **Access the Interface:**
   Check your terminal for the port. By default, the interface should be available at:
   [http://127.0.0.1:8501](http://127.0.0.1:8501)

---

## 🌍 Production Testing & Deployment

Ready for real testing? Follow these steps to deploy your agent:

1. **Deploy the Agent:**
   Inside the agent's folder, run the following command to deploy it to the engine specified in your environment configuration:
   ```bash
   make deploy
   ```

2. **Register the Agent:**
   Register the agent in your preferred Agent Governance solution (e.g., Gemini Enterprise):
   ```bash
   make register-gemini-enterprise
   ```
