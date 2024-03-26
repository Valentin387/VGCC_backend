# VGCC_backend
Backend for my application. Using FastAPI, combining the google calendar and chatGPT API's


## Documentation for the integration with the frontend

The frontend must include:

1. A conversation chat.
   for that, use the endpoints /openAI/llm/response

2. Option for adding a google calendar account's events.
   for that, use the endpoints
   /calendar/authorize and
   /calendar/get-calendar-events
   it needs the start and end dates, use a calendr input. Watch out the format 2023-03-15T00:00:00Z

4. Option for resetting all the application context.
   for that, use the endpoints
   /calendar/delete-tokens
   /openAI/delete-text
   /openAI/create-text

Et voilà
