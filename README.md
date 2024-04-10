# VGCC_backend
Backend for my application. Using FastAPI, combining the google calendar and chatGPT API's

Just run the main.py file and that's it

## Caution
In the file calendar.py I call a file named credentials.json, you have to add your own google calendar credentials there, nevertheless, sometimes it works with the path "credentials.json" and sometimes with the path "src/credentials.json"

Also, it does not have a mean to interrupt the authentication flow once it's started, which might be annoying for the user experience.

