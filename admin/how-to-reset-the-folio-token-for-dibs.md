
When folio is updated we need to regerate the token used by DIBs to access the "okapi".  The steps below are what we do at Caltech Library and may reflect a similar setup in your institution. The values in angle brackes should be replaced with your organization's values.

1. There is a <ADMIN_ACCOUNT> account that has access to Folio's dashboard. Use the URL: https://<YOUR_INSTITUION>.folio.ebsco.com/dashboard
2. On the dashboard login page in very tiny print (below the fold on my monitor) is a password reset link, the <ADMIN_ACCOUNT> account is just like any other library folio account in this regards (we always reset the password since we have access to the associated EMail account)
3. The Folio API DIBs uses os the okapi (I think that is the same as the foliage stuff generally). 
4. We have some tools in a private repository that automate generating the new token. They use the Folio API to generate the token. Our `get-api-token` script requires the <ADMIN_ACCOUNT> name and the tenant id found in the "settings.ini" of DIBs.  The resulting program generates a file called "okapi-login.json". It needs to have the appropriate permissions for the app to read it.
5. Copy the generated token displayed by `get-api-token` and update the line in DIB's `settings.ini` with  FOLIO_OKAPI_TOKEN
6. Restart Apache2 to make sure that DIBs is reloaded and the stale token isn't being used.
