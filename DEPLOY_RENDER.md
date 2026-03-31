# Render Deployment Guide

This project can be deployed as a single web service on Render with MongoDB Atlas as the database.

## 1. Push the repo to GitHub

Make sure these files are in the repository:

- `render.yaml`
- `Dockerfile`
- `requirements.txt`
- `wsgi.py`
- `index.html`

Do not commit your real `.env` file.

## 2. Rotate exposed secrets first

If you ever stored real keys in `.env`, create new values before deploying:

- `GROQ_API_KEY`
- `TAVILY_API_KEY`
- `MONGODB_URI`
- `FAST2SMS_API_KEY`

## 3. Create a free MongoDB Atlas cluster

Create a free Atlas cluster and then:

- Create a database user
- In Atlas Network Access, allow the deployed app to reach the cluster
- Copy the connection string
- Replace username, password, and database name

For Render or other hosted platforms, do not whitelist only your laptop IP. Render outbound IPs are not your local machine IP, so Atlas access can fail after deploy. For a quick setup, allow `0.0.0.0/0`, or use a fixed egress setup if you need a tighter rule.

Use:

- `MONGODB_DB=healthbuddy`

## 4. Deploy on Render

In Render:

1. Click `New +`
2. Click `Blueprint`
3. Connect your GitHub repository
4. Select this repo
5. Render should detect `render.yaml`
6. Click `Apply`

Render will create one web service named `healthbuddy`.

## 5. Add environment variables

Set these in Render:

- `GROQ_API_KEY`
- `TAVILY_API_KEY`
- `MONGODB_URI`
- `MONGODB_DB`
- `FAST2SMS_API_KEY` only if SMS is required
- `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` if you want Google login
- `FACEBOOK_APP_ID` and `FACEBOOK_APP_SECRET` if you want Facebook login
- `MONGODB_APP_NAME=healthbuddy` optionally, if you want the Atlas client name to be explicit

These are already declared in `render.yaml`:

- `FLASK_SECRET_KEY`
- `PYTHON_VERSION`

## 6. Verify after deploy

Open your Render URL and test:

- Home page loads
- Register works
- Login works
- Symptom analysis works
- `/api/health` returns JSON

## 7. Free-tier behavior

On Render free instances, the app may sleep after inactivity and the first request can be slow.
