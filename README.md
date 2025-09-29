# appsembler_api

NOTE: the app is called `shoppingcart` to hack in the old shoppingcart tables from pre-Juniper.

Provide legacy (Hawthorn and earlier) appsembler_api as an LMS Django app plugin
for use in Juniper and later (possibly).

This API is deprecated though and ideally its functionality will be refactored to
openedx.core.djangoapps.appsembler.api in our forks of edx-platform, or as moved to
another service.

Currently maintained for standalone customers.

Primary authors were @johnbaldwin, @melvinsoft

Updated for standalone, Juniper/Py3 by @bryanlandia

See [apidocs.md](./appsembler_api/apidocs.md) for details on usage/the API

## Testing

For some tests you need to run them from within a working Open edX environment.
Install in a Tutor devstack, then shell into the lms:

```sh
tutor dev exec lms -- bash
```

In the LMS shell, cd to the plugin directory:

```sh
cd /mnt/legacy-appsembler-api
```

Then you can run the unit tests (no unit tests yet):

```sh
pytest
python ./manage.py makemigrations shoppingcart --check --dry-run --verbosity 3
```
