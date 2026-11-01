# Private postcard publishing service — deployment required

The static `postcard-admin.html` page is a user interface only. It **cannot securely authenticate or publish photographs by itself** on GitHub Pages.

To activate it, deploy a server-side upload endpoint with:

- HTTPS, strict CORS limited to `https://dlongnecker2.github.io`, and server-side authentication using a salted password hash (never commit the password or hash to this repository).
- Rate limiting, maximum 5 MB upload, image MIME/signature validation, and metadata stripping.
- A scoped GitHub credential stored as a server-side secret with Contents write access only to `dlongnecker2/viking-river-watch`.
- Upload each photo to `photos/YYYY-MM-DD-<random>.jpg`, then update `journey-postcards.json` with `date`, `place`, `note`, `photo`, and `photo_alt`.
- Commit safely with GitHub contents API and retry on 409 conflicts; return success only after both photo and JSON are committed.
- Configure the endpoint URL in `postcard-admin.js` only after the service is live and verified.

**Do not put the publishing password or a GitHub token into JavaScript, HTML, or repository files.**

The page currently displays an honest 'not connected' message until the private service is deployed.
