# VGCC_backend
Backend for my application. Using FastAPI, combining the google calendar and chatGPT API's

Just run the main.py file and that's it

## Caution
In the file calendar.py I call a file named credentials.json, you have to add your own google calendar credentials there, nevertheless, sometimes it works with the path "credentials.json" and sometimes with the path "src/credentials.json"

Also, it does not have a mean to interrupt the authentication flow once it's started, which might be annoying for the user experience.



## Documentation for the integration with the frontend

The frontend must include:

1. A conversation chat.
   for that, use the endpoints /openAI/llm/response

2. Option for adding a google calendar account's events.
   for that, use the pipeline of endpoints:
   /calendar/authorize and
   /calendar/get-calendar-events
   /calendar/credentials-info
   it needs the start and end dates, use a calendar input in the HTML for doing so. Watch out the format 2023-03-15T00:00:00Z

4. Option for resetting all the application context.
   for that, use pipeline of endpoints:
   /calendar/delete-tokens
   /openAI/delete-text
   /openAI/create-text

Et voilà
