# How to set up or reset the FOLIO credentials for DIBS

DIBS logs in to FOLIO with a service account. It uses the account's username and password to get short-lived access tokens from FOLIO, and logs in again when a token is about to expire or FOLIO rejects it. Nobody needs to create tokens by hand.

The steps below are what we do at Caltech Library and may reflect a similar setup in your institution. Replace the values in angle brackets with your organization's values.

1. Create a FOLIO user for DIBS (or use the existing one), named here <SERVICE_ACCOUNT>, in the tenant DIBS uses. Give it a password and a role with the permission `inventory.instances.collection.get`, which is all DIBS needs. Ask for a password that doesn't expire and an account that isn't subject to lockout or multi-factor login, since DIBS logs in on its own. The account doesn't need the FOLIO web interface.
2. In the `[folio]` section of DIBS's `settings.ini`, set:
   * `FOLIO_OKAPI_URL` to the FOLIO API URL (for example, `https://api-<YOUR_INSTITUTION>.folio.ebsco.com`)
   * `FOLIO_OKAPI_TENANT_ID` to the tenant ID
   * `FOLIO_OKAPI_USERNAME` to <SERVICE_ACCOUNT>
   * `FOLIO_OKAPI_PASSWORD` to its password
3. Make sure `settings.ini` can be read by the account that runs DIBS and not by other users, since it holds the password.
4. Run `admin/test-folio-token -v` with the Python environment DIBS uses, to check that the account can log in and look up instances.
5. Restart Apache so DIBS reads the new settings.

If the account's password is reset, or DIBS is moved to a different FOLIO tenant, repeat steps 2 through 5. Service accounts belong to a tenant, so a new tenant needs a new account.
