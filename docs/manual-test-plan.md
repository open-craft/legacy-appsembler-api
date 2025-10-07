# Manual test plan

This is a playbook to follow to manually test the api endpoints provided by this plugin.
This may also be useful as a reference for development.

It's written to be able to follow from top to bottom.
Some steps may use outputs from previous steps.

Prerequisites:

- This plugin installed in an Open edX environment.
  Follow the instructions in the README to install in a Tutor devstack if needed.
  The instructions here assume this is running in a local Tutor devstack.
- A superuser account to use for accessing the Django admin and calling the API endpoints.
  You can create one quickly via Tutor:
  ```sh
  tutor dev do createuser --staff --superuser user1 user1@example.com --password password
  ```
- An active course on the platform - the instructions below assume the default demo course is available.
  With Tutor, you can import the demo course with:
  ```sh
  tutor dev do importdemocourse
  ```
- A Bash-like shell, `curl`, and `jq` installed.

See also the [apidocs](./apidocs.md) for reference.
They may be a little outdated, but they give the general idea.

## Create an OAuth application

To start, you'll need to register an OAuth application in Open edX,
so you can authentication to the API.

1. As your superuser user, go to http://local.openedx.io:8000/admin/oauth2_provider/application/ (Django OAuth Toolkit > Applications)
2. Click "Add Application"
3. Choose your previously created superuser user for the user.
4. Choose `Confidential` Client Type
5. Choose `Client Credentials` for the Authorization Grant Type
6. Set a name for your application.
7. Save the "Client id" and "Client secret" for later.

## Retrieve a Bearer token

```sh
CLIENT_ID="the-client-id"
CLIENT_SECRET="the-client-secret"

curl -X POST 'http://local.openedx.io:8000/oauth2/access_token' \
  --header 'Content-Type: multipart/form-data' \
  --form "client_id=$CLIENT_ID" \
  --form "client_secret=$CLIENT_SECRET" \
  --form "token_type=bearer" \
  --form "grant_type=client_credentials" | jq
```

The output will look something like this:

```json
{
  "access_token": "DlfY7WqGjwQre7TbyMBIvmIYazgFHE",
  "expires_in": 36000,
  "token_type": "Bearer",
  "scope": "read write email profile"
}
```

Save the `access_token` value for use in testing the legacy-appsembler-api endpoints.

```sh
BEARER_TOKEN="the-access-token"
```

## Retrieve a CSRF token

Some API endpoints require a CSRF token. You can generate one with:

```sh
curl -X GET 'http://local.openedx.io:8000/csrf/api/v1/token' \
  --cookie-jar csrf_cookies.txt | jq
```

The output will look like:

```json
{
  "csrfToken": "WN33qvXlUEaz0GIvEinB2Df2JUtpeCr4flwN9wq3ngE1xdsyklq69A5f9waLBFz5"
}
```

Save the value of `csrfToken` for later:

```sh
CSRF_TOKEN="the-csrf-token"
```

This also saves cookies, which includes the CSRF token cookie.
Some endpoints require the cookie, while others may be happy with the `X-CSRFToken` header.

## Test the legacy-appsembler-api endpoints

Now you can test the functionality of this plugin!

You may find [./yaak-workspace.json](./yaak-workspace.json) helpful
if you use [Yaak](https://yaak.app/), a graphical API testing client.
This json file contains an export of a workspace with example requests
configured for all the relevant API endpoints, the auth API calls from above,
and request chaining to easily use them all together.

Either way, the requests provided below for testing are formatted as curl commands that can be copy/pasted.

### Create a user

Example:

```sh
curl -w "%{stderr}\nResponse code: %{http_code}\n" -X POST 'http://local.openedx.io:8000/appsembler_api/v0/accounts/create' \
  --header 'Content-Type: application/json' \
  --data '{
    "username": "apicreated4",
    "password": "mypassword",
    "email": "apicreated4@example.com",
    "name": "my name",
    "send_activation_email": "False"
}' \
  --header "Authorization: Bearer $BEARER_TOKEN" | jq
```

Expect a json response with with status 200, that looks like:

```json
{
  "user_id ": 5
}
```

### Use the custom login endpoint

This endpoint is a wrapper around the built-in `login_session` endpoint.
It sets a CSRF cookie that can be used cross-domain - see [CsrfCrossDomainCookieMiddleware](https://github.com/openedx/edx-platform/blob/open-release/sumac.master/openedx/core/djangoapps/cors_csrf/middleware.py#L85-L89) for more information on configuring that feature.

Requests to this endpoint require both the CSRF token cookie *and* the CSRF token header.
If you see CSRF errors in the response, regenerate the CSRF token cookie and header by repeating
the "Retrieve a CSRF token" step from earlier.

Test it by logging in:

```sh
curl -w "%{stderr}\nResponse code: %{http_code}\n" -X POST 'http://local.openedx.io:8000/appsembler_api/v0/account/login_session/' \
  --cookie csrf_cookies.txt \
  --header "x-CSRFToken: $CSRF_TOKEN" \
  --header 'Content-Type: multipart/form-data' \
  --form 'email=apicreated4@example.com' \
  --form 'password=mypassword' | jq
```

Expect a json response with status 200 and the following body:

```json
{
  "success": true,
  "redirect_url": "http://local.openedx.io:8000/dashboard"
}
```

Try again with an incorrect password.
First, repeat the "Retrieve a CSRF token" step from earlier to generate a new CSRF token,
then you can run:

```sh
curl -w "%{stderr}\nResponse code: %{http_code}\n" -X POST 'http://local.openedx.io:8000/appsembler_api/v0/account/login_session/' \
  --cookie csrf_cookies.txt \
  --header "x-CSRFToken: $CSRF_TOKEN" \
  --header 'Content-Type: multipart/form-data' \
  --form 'email=apicreated4@example.com' \
  --form 'password=notmypassword'
```

And verify you get a response with status 400 and the following json body:

```json
{
  "success": false,
  "value": "Email or password is incorrect.",
  "error_code": "incorrect-email-or-password",
  "context": {
    "failure_count": 0
  },
  "email": "apicreated4@example.com"
}
```

### Create a user without a password

This endpoint takes an email address and a name (and optionally some other user details),
and creates the user.
It generates a username based on the email address.

NOTE: This endpoint has a known bug where it messes up the authentication cookies.
You shouldn't encounter this when using Curl,
but if you use an API client that tracks cookies, please clear cookies after each request here.

```sh
curl -w "%{stderr}\nResponse code: %{http_code}\n" -X POST 'http://local.openedx.io:8000/appsembler_api/v0/accounts/user_without_password' \
  --header 'Content-Type: application/json' \
  --data '{
    "email": "user-without-password@example.com",
    "name": "Name 1"
}' \
  --header "Authorization: Bearer $BEARER_TOKEN" | jq
```

Verify the response has status 200 and the following json body:

```json
{
  "user_id": 7,
  "username": "userwithoutpassword"
}
```

Now try again with a subtly different email address to check that it can generate unique usernames:

```sh
curl -w "%{stderr}\nResponse code: %{http_code}\n" -X POST 'http://local.openedx.io:8000/appsembler_api/v0/accounts/user_without_password' \
  --header 'Content-Type: application/json' \
  --data '{
    "email": "user--without-password@example.com",
    "name": "Name 2"
}' \
  --header "Authorization: Bearer $BEARER_TOKEN" | jq
```

Verify the response has status 200, and a json body that looks like this
(the trailing digits on the username may be different):

```json
{
  "user_id": 9,
  "username": "userwithoutpassword732"
}
```

Finally, try again with the same email address to verify it blocks duplicate emails with a custom response code:

```sh
curl -w "%{stderr}%{stderr}\nResponse code: %{http_code}\n" -X POST 'http://local.openedx.io:8000/appsembler_api/v0/accounts/user_without_password' \
  --header 'Content-Type: application/json' \
  --data '{
    "email": "user--without-password@example.com",
    "name": "Name 2"
}' \
  --header "Authorization: Bearer $BEARER_TOKEN" | jq
```

Verify the response has status 409 (Conflict), and the following json body:

```json
{
  "user_message": "User already exists"
}
```

### Test the connect endpoint

Given a username, the connect endpoint can change the email, password, and name for the user.
Run this to update details for the `apicreated4` user you created in the first step to create a user:

```sh
curl -w "%{stderr}\nResponse code: %{http_code}\n" -X POST 'http://local.openedx.io:8000/appsembler_api/v0/accounts/connect' \
  --header 'Content-Type: application/json' \
  --data '{
    "username": "apicreated4",
    "password": "newpassword",
    "email": "newemail@example.com",
    "name": "my new name"
}' \
  --header "Authorization: Bearer $BEARER_TOKEN" | jq
```

Verify you get a response with status 200 and a json body that looks like:

```json
{
  "user_id": 5
}
```

Verify you can log in to the [devstack web ui](http://local.openedx.io:8000)
with the username and new password from above.

### Test getting a user

This endpoint is used for checking if a user exists:

```sh
curl -w "%{stderr}\nResponse code: %{http_code}\n" -X GET 'http://local.openedx.io:8000/appsembler_api/v0/accounts/get-user/apicreated4' \
  --header 'Content-Type: application/json' \
  --data '' \
  --header "Authorization: Bearer $BEARER_TOKEN" | jq
```

Verify the response has status 200 and the following json body:

```json
{
  "user_id": "apicreated4"
}
```

Test with a non-existing user:

```sh
curl -w "%{stderr}\nResponse code: %{http_code}\n" -X GET 'http://local.openedx.io:8000/appsembler_api/v0/accounts/get-user/doesnotexist' \
  --header 'Content-Type: application/json' \
  --data '' \
  --header "Authorization: Bearer $BEARER_TOKEN" | jq
```

Verify the status code is 404.

### Test updating a user's profile

The update user endpoint supports updating many fields from a user's profile:

```sh
curl -w "%{stderr}\nResponse code: %{http_code}\n" -X POST 'http://local.openedx.io:8000/appsembler_api/v0/accounts/update_user' \
  --header 'Content-Type: application/json' \
  --data '{
    "user_lookup": "apicreated4",
    "email": "apicreated1@example.com",
    "name": "my new name",
    "year_of_birth": "2001",
    "bio": "just another user",
    "country": "AU",
    "level_of_education": "a",
    "gender": "m",
    "language": "EN"
}' \
  --header "Authorization: Bearer $BEARER_TOKEN" | jq
```

Verify the response confirms the fields have been updated:

```json
{
  "success": "The following fields has been updated: email=apicreated1@example.com, name=my new name, level_of_education=a, gender=m, country=AU, bio=just another user, year_of_birth=2001, language=EN"
}
```

You can also log in to the web UI and view profile information on http://apps.local.openedx.io:1995/profile/u/apicreated4 .

### Test search courses

There is an endpoint to search for courses:

```sh
curl -w "%{stderr}\nResponse code: %{http_code}\n" -X GET 'http://local.openedx.io:8000/appsembler_api/v0/search_courses?search_term=demo&org=openedx' \
  --header 'Content-Type: application/json' \
  --data '' \
  --header "Authorization: Bearer $BEARER_TOKEN" | jq
```

Verify this search above returns the demo course:

```json
{
  "results": [
    {
      "blocks_url": "http://local.openedx.io:8000/api/courses/v2/blocks/?course_id=course-v1%3AOpenedX%2BDemoX%2BDemoCourse",
      "effort": null,
      "end": null,
      "enrollment_start": null,
      "enrollment_end": null,
      "id": "course-v1:OpenedX+DemoX+DemoCourse",
      "media": {
        "banner_image": {
          "uri": "/asset-v1:OpenedX+DemoX+DemoCourse+type@asset+block@images_course_image.jpg",
          "uri_absolute": "http://local.openedx.io:8000/asset-v1:OpenedX+DemoX+DemoCourse+type@asset+block@images_course_image.jpg"
        },
        "course_image": {
          "uri": "/asset-v1:OpenedX+DemoX+DemoCourse+type@asset+block@thumbnail_demox.jpeg"
        },
        "course_video": {
          "uri": null
        },
        "image": {
          "raw": "http://local.openedx.io:8000/asset-v1:OpenedX+DemoX+DemoCourse+type@asset+block@thumbnail_demox.jpeg",
          "small": "http://local.openedx.io:8000/asset-v1:OpenedX+DemoX+DemoCourse+type@asset+block@thumbnail_demox.jpeg",
          "large": "http://local.openedx.io:8000/asset-v1:OpenedX+DemoX+DemoCourse+type@asset+block@thumbnail_demox.jpeg"
        }
      },
      "name": "Open edX Demo Course",
      "number": "DemoX",
      "org": "OpenedX",
      "short_description": "Explore Open edX® capabilities in this demo course, covering platform tools, content creation, assessments, social learning, and community stories. Ideal for course developers, online learning newcomers, and community members. ",
      "start": "2020-01-01T00:00:00Z",
      "start_display": "Jan. 1, 2020",
      "start_type": "timestamp",
      "pacing": "self",
      "mobile_available": false,
      "hidden": false,
      "invitation_only": false,
      "course_id": "course-v1:OpenedX+DemoX+DemoCourse"
    }
  ],
  "pagination": {
    "next": null,
    "previous": null,
    "count": 1,
    "num_pages": 1
  }
}
```

Search for something that doesn't exist:

```sh
curl -w "%{stderr}\nResponse code: %{http_code}\n" -X GET 'http://local.openedx.io:8000/appsembler_api/v0/search_courses?search_term=demo&org=openedxnth' \
  --header 'Content-Type: application/json' \
  --data '' \
  --header "Authorization: Bearer $BEARER_TOKEN" | jq
```

Verify the response still has 200 status, but returns this json body:

```json
{
  "results": [],
  "pagination": {
    "next": null,
    "previous": null,
    "count": 0,
    "num_pages": 1
  }
}
```

NOTE: this endpoint also supports a `filter_` parameter for extra filtering (this is passed directly to [lms.djangoapps.course_api.api.list_courses](https://github.com/openedx/edx-platform/blob/198886d191d6cb1a73bed1260b5457dc3784f481/lms/djangoapps/course_api/api.py#L120),
and a `username` to filter by courses that are visible to that user.

### Test bulk enrollment


```sh
curl -w "%{stderr}\nResponse code: %{http_code}\n" -X POST 'http://local.openedx.io:8000/appsembler_api/v0/bulk-enrollment/bulk-enroll' \
  --header 'Content-Type: application/json' \
  --data '{
    "action": "enroll",
    "auto_enroll": true,
    "identifiers": "apicreated1@example.com,apicreated2@example.com",
    "email_students": true,
    "courses": "course-v1:OpenedX+DemoX+DemoCourse"
}' \
  --header "Authorization: Bearer $BEARER_TOKEN" | jq
```

Verify the response has status 200 and shows the results:

```json
{
  "auto_enroll": true,
  "email_students": true,
  "action": "enroll",
  "courses": {
    "course-v1:OpenedX+DemoX+DemoCourse": {
      "action": "enroll",
      "results": [
        {
          "identifier": "apicreated1@example.com",
          "before": {
            "user": true,
            "enrollment": false,
            "allowed": false,
            "auto_enroll": false
          },
          "after": {
            "user": true,
            "enrollment": true,
            "allowed": false,
            "auto_enroll": false
          }
        },
        {
          "identifier": "apicreated2@example.com",
          "before": {
            "user": false,
            "enrollment": false,
            "allowed": false,
            "auto_enroll": false
          },
          "after": {
            "user": false,
            "enrollment": false,
            "allowed": true,
            "auto_enroll": true
          }
        }
      ],
      "auto_enroll": true
    }
  }
}
```

Note that this works with user email address that don't exist too;
this is expected, and simply uses the edx-platform functions to perform the enrollments.
I think if a user doesn't exist, they'll receive an email inviting them to enroll.

### Test generating enrollment codes

This is functionality for providing a single-user code tied to a course,
allowing a user to be enrolled in that course by providing that code later.

```sh
curl -w "%{stderr}\nResponse code: %{http_code}\n" -X POST 'http://local.openedx.io:8000/appsembler_api/v0/enrollment-codes/generate' \
  --header 'Content-Type: application/json' \
  --data '{
    "total_registration_codes": "3",
    "course_id": "course-v1:OpenedX+DemoX+DemoCourse"
}' \
  --header "Authorization: Bearer $BEARER_TOKEN" | jq
```

Verify the response has status code 200 and json body with information about the course and the desired number of codes:

```json
{
  "codes": [
    "PY4ngLKw",
    "zbKy2BbR",
    "RDm6VkVd"
  ],
  "course_id": "course-v1:OpenedX+DemoX+DemoCourse",
  "course_url": "/courses/course-v1:OpenedX+DemoX+DemoCourse/about"
}
```

Save two codes for the next steps:

```sh
ENROLLMENT_CODE1="YOURCODE1"
ENROLLMENT_CODE2="YOURCODE2"
```

### Test enrolling users with enrollment codes

Now you can enroll a user in the demo course using one of those codes:

```sh
curl -w "%{stderr}\nResponse code: %{http_code}\n" -X POST 'http://local.openedx.io:8000/appsembler_api/v0/enrollment-codes/enroll-user' \
  --header 'Content-Type: application/json' \
  --data '{
    "email": "apicreated1@example.com",
    "enrollment_code": "'"$ENROLLMENT_CODE1"'"
}' \
  --header "Authorization: Bearer $BEARER_TOKEN" | jq
```

Verify a success response is returned:

```json
{
  "success": true
}
```

Log in to the web UI as the "apicreated1@example.com" user
(username "apicreated4"; sorry, that's confusing; password "newpassword"),
and verify the user is enrolled in the Open edX Demo Course.

**NOTE: This next test, for reusing an enrollment code, will fail. You will be able to reuse the code even though you should not be able to. See [this PR](https://github.com/open-craft/legacy-appsembler-api/pull/5) for details.**

Test enrolling again with the same code:

```sh
curl -w "%{stderr}\nResponse code: %{http_code}\n" -X POST 'http://local.openedx.io:8000/appsembler_api/v0/enrollment-codes/enroll-user' \
  --header 'Content-Type: application/json' \
  --data '{
    "email": "apicreated1@example.com",
    "enrollment_code": "'"$ENROLLMENT_CODE1"'"
}' \
  --header "Authorization: Bearer $BEARER_TOKEN" | jq
```

The code is single use, so verify the response has status 400, and the following json body:

```json
{
  "success": false,
  "reason": ""
}
```

NOTE: it may be a minor bug that the reason is empty here.

Try again with a code that does not exist:

```sh
curl -w "%{stderr}\nResponse code: %{http_code}\n" -X POST 'http://local.openedx.io:8000/appsembler_api/v0/enrollment-codes/enroll-user' \
  --header 'Content-Type: application/json' \
  --data '{
    "email": "apicreated1@example.com",
    "enrollment_code": "doesnotexist"
}' \
  --header "Authorization: Bearer $BEARER_TOKEN" | jq
```

Verify the response has status 400, and the following json body:

```json
{
  "success": false,
  "reason": "Enrollment code not found"
}
```

Finally, test the case where the user does not exist, but the enrollment code is valid
(pick one of the other unused enrollment codes):

```sh
curl -w "%{stderr}\nResponse code: %{http_code}\n" -X POST 'http://local.openedx.io:8000/appsembler_api/v0/enrollment-codes/enroll-user' \
  --header 'Content-Type: application/json' \
  --data '{
    "email": "doesnotexist@example.com",
    "enrollment_code": "'"$ENROLLMENT_CODE2"'"
}' \
  --header "Authorization: Bearer $BEARER_TOKEN" | jq
```

Verify the response has status 400 and the following json body:

```json
{
  "success": false,
  "reason": "User not found"
}
```


### Test changing enrollment code status

The enrollment-codes/status endpoint supports cancelling or restoring an enrollment code.

- "cancel": invalidate the code. Also unenroll the user from the course if the code was used.
- "restore": Make the code valid and ready to use again. Also unenroll the user from the course if the code was used.

Let's restore the enrollment code that was used earlier to enroll the "apicreated4" user:


```sh
curl -w "%{stderr}\nResponse code: %{http_code}\n" -X POST 'http://local.openedx.io:8000/appsembler_api/v0/enrollment-codes/status' \
  --header 'Content-Type: application/json' \
  --data '{
    "action": "restore",
    "enrollment_code": "'"$ENROLLMENT_CODE1"'"
}' \
  --header "Authorization: Bearer $BEARER_TOKEN" | jq
```

Verify the response has status 200 and the following json body:

```json
{
  "success": true
}
```

Visit the web UI as the "apicreated4" user again,
and verify the user is no longer enrolled in the demo course.

Enroll the user in the demo course again using the same (restored) code:

```sh
curl -w "%{stderr}\nResponse code: %{http_code}\n" -X POST 'http://local.openedx.io:8000/appsembler_api/v0/enrollment-codes/enroll-user' \
  --header 'Content-Type: application/json' \
  --data '{
    "email": "apicreated1@example.com",
    "enrollment_code": "'"$ENROLLMENT_CODE1"'"
}' \
  --header "Authorization: Bearer $BEARER_TOKEN" | jq
```

Verify a success response is returned:

```json
{
  "success": true
}
```

In the web UI, verify the user is enrolled again in the demo course.

Now cancel the enrollment code:

```sh
curl -w "%{stderr}\nResponse code: %{http_code}\n" -X POST 'http://local.openedx.io:8000/appsembler_api/v0/enrollment-codes/status' \
  --header 'Content-Type: application/json' \
  --data '{
    "action": "cancel",
    "enrollment_code": "'"$ENROLLMENT_CODE1"'"
}' \
  --header "Authorization: Bearer $BEARER_TOKEN" | jq
```

Verify the response has status 200 and the following json body:

```json
{
  "success": true
}
```

In the web UI, verify the user is once again no longer enrolled in the demo course.

One final time, attempt to enroll the user in the course using the same code:

```sh
curl -w "%{stderr}\nResponse code: %{http_code}\n" -X POST 'http://local.openedx.io:8000/appsembler_api/v0/enrollment-codes/enroll-user' \
  --header 'Content-Type: application/json' \
  --data '{
    "email": "apicreated1@example.com",
    "enrollment_code": "'"$ENROLLMENT_CODE1"'"
}' \
  --header "Authorization: Bearer $BEARER_TOKEN" | jq
```

Verify the response has status 400 and the following json body:

```json
{
  "success": false,
  "reason": "Enrollment code not found"
}
```

In the web UI, verify the user is still not enrolled in the demo course.

### Test the accounts analytics endpoint

This shows information about user accounts, and can filter by date joined.

You can get a list of all the users on the platform with:

```sh
curl -w "%{stderr}\nResponse code: %{http_code}\n" -X GET 'http://local.openedx.io:8000/appsembler_api/v0/analytics/accounts/batch' \
  --header 'Content-Type: application/json' \
  --data '' \
  --header "Authorization: Bearer $BEARER_TOKEN" | jq
```

Verify the response has status 200 and the body has a json list of all users:

```json5
[
  {
    "id": 2,
    "username": "login_service_user",
    "email": "login_service_user@fake.email",
    "is_active": true,
    "date_joined": "2025-09-29T06:35:08.751215Z"
  },
  {
    "id": 3,
    "username": "cms",
    "email": "cms@openedx",
    "is_active": true,
    "date_joined": "2025-09-29T06:36:27.318723Z"
  },
  {
    "id": 5,
    "username": "apicreated4",
    "email": "apicreated1@example.com",
    "is_active": true,
    "date_joined": "2025-09-29T07:05:03.092197Z"
  },
  // ...
]
```

You can also filter by date joined - for example (adjust the dates to suite when you run this):

```sh
curl -w "%{stderr}\nResponse code: %{http_code}\n" -X GET 'http://local.openedx.io:8000/appsembler_api/v0/analytics/accounts/batch?updated_max=2025-10-03&updated_min=2025-09-29' \
  --header 'Content-Type: application/json' \
  --data '' \
  --header "Authorization: Bearer $BEARER_TOKEN" | jq
```

Verify the response looks similar to the to the previous response,
but this time has only users who joined in the provided date range.

### Test the enrollments analytics endpoint

This endpoint returns information about enrollments,
and you can filter by `course_id`, `username`, `updated_min` (date), and `updated_max` (date).

For example to get all enrollments in the demo course:

```sh
curl -w "%{stderr}\nResponse code: %{http_code}\n" -X GET 'http://local.openedx.io:8000/appsembler_api/v0/analytics/enrollment/batch?course_id=course-v1%3AOpenedX%2BDemoX%2BDemoCourse' \
  --header 'Content-Type: application/json' \
  --data '' \
  --header "Authorization: Bearer $BEARER_TOKEN" | jq
```

Verify the response has status 200 and a json body that looks like:

```json
[
  {
    "enrollment_id": 1,
    "user_id": 5,
    "username": "apicreated4",
    "course_id": "course-v1:OpenedX+DemoX+DemoCourse",
    "date_enrolled": "2025-09-30T01:00:45.011099Z"
  }
]
```

An example that uses all the filters (modify as desired to test for applicable dates and usernames):

```sh
curl -w "%{stderr}\nResponse code: %{http_code}\n" -X GET 'http://local.openedx.io:8000/appsembler_api/v0/analytics/enrollment/batch?updated_max=2031-01-01&updated_min=2025-09-01&username=apicreated4&course_id=course-v1%3AOpenedX%2BDemoX%2BDemoCourse' \
  --header 'Content-Type: application/json' \
  --data '' \
  --header "Authorization: Bearer $BEARER_TOKEN" | jq
```

Verify the response returns results as expected.
