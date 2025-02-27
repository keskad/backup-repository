Contributing
============

It would be fantastic if you would create an issue or better, create a PR, or do a code review. Contributions are always welcome!
Before doing a contribution please take a look at our guideline.

Architecture
------------

The architecture is module based, like in Golang projects. A little inspiration was taken from PHP and Python to use `Repository pattern`.

**Most of the modules are split into:**
- entity: Structs containing domain logic
- repository: Interaction with data store via `ConfigurationProvider` or `GORM` (only private methods there)
- service: Public methods performing actual actions on the model, repository. There are defined actions that aggregates logic as much as it is possible

**'http' module**

It is a special module that defines all routes, it's authentication and security logic for every endpoint.

- auth: Endpoints related to authorization and users management
- collection: Endpoints for operations on collections
- responses: HTTP responses format standardization
- utils: Various utils for validating user input, checking session etc.
- main: Registers all the endpoints to the router
