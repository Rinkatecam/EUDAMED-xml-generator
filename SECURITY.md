# Security policy

## Supported versions

Only the latest release receives fixes.

## Reporting a vulnerability

Please **do not open a public issue** for security problems. Use GitHub's private vulnerability reporting
("Security" tab -> "Report a vulnerability") on this repository.

Include what you found, how to reproduce it and, if possible, a suggested fix. Do not include real
credentials or real device data.

## What is in scope

* Anything that could make the application send data to a third party, or load code from one.
* Handling of the SRN, party ID and access token (the token is only persisted in the browser if the user
  explicitly asks for it).
* Cross-site scripting through workbook content (cell values are shown in the interface).
* Anything that could cause generated files to contain data the user did not enter.

## Things to keep in mind as a user

* Generated XML files contain your SRN and, if you entered it, your access token. Treat them as confidential
  and do not post them in issues.
* The application keeps SRN and party ID in your browser's `localStorage`; use *Clear saved credentials* on
  shared machines.
