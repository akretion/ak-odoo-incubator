Fix OAuth login redirection by including in the frontend the redirect URL fragment in the final redirect URL.

It can't be done in the backend because URL fragments are not sent to the server.
