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

## Installing in a devstack

This assumes a [Tutor dev devstack](https://docs.tutor.edly.io/dev.html) set up.

```
git clone https://github.com/open-craft/legacy-appsembler-api
tutor mounts add ./legacy-appsembler-api

# This directory won't be autodetected for build-time mount by Tutor,
# so we need to manually configure Tutor for it.
TUTOR_PLUGINS_ROOT="$(tutor plugins printroot)"
mkdir -p "$TUTOR_PLUGINS_ROOT"
echo 'from tutor import hooks; hooks.Filters.MOUNTED_DIRECTORIES.add_item(("openedx", "legacy-appsembler-api"))' > "$TUTOR_PLUGINS_ROOT/legacy-appsembler-api.py"
tutor plugins enable legacy-appsembler-api

tutor images build openedx-dev
tutor dev launch
```

## Developing

Before committing, be sure to run the code formatter:

```
make format
```

## Testing

### Quality lints

Quality tests (runs within tox, so you can run it directly on your workstation):

```
make quality
```

### Manual integration tests

There is also a manual test plan to follow at [./docs/manual-test-plan.md](./docs/manual-test-plan.md).
Install this in a Tutor devstack following the instructions above, then you can run through the test plan.

### Migration tests

For some migration tests,
you need to run them from within a working Open edX environment.

Install in a Tutor devstack following the instructions above, then shell into the lms:

```sh
tutor dev exec lms -- bash
```

In the LMS shell, cd to the plugin directory:

```sh
cd /mnt/legacy-appsembler-api
```

Then you can run the migrations test:

```
make test_migrations
```

From this environment, you can also:

```sh
# upgrade dependencies
make upgrade

# make migrations
python ./manage.py makemigrations shoppingcart
```

## License

This repository is licensed under AGPLv3. Please see [LICENSE.txt](./LICENSE.txt) for more information.
