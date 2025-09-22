# pylint: disable=line-too-long,

from django.urls import re_path
from django.db import transaction

from openedx.core.djangoapps.user_authn.views import login
from openedx.core.djangoapps.cors_csrf.decorators import ensure_csrf_cookie_cross_domain

from shoppingcart import views

urlpatterns = [
    # provide a wrapped cross-domain csrf version of user_api/v1/account/login_session
    # use an Nginx redirect from that to
    # /appsembler_api/v0/account/login_session if you want to use this one:
    # override of login_session from openedx.core.djangoapps.user_authn.urls_common
    re_path(r'^account/login_session/$', ensure_csrf_cookie_cross_domain(login.LoginSessionView.as_view()),
        kwargs={"api_version": "v1"}, name="user_api_login_session"
    ),

    # user API
    re_path(
        r'^accounts/user_without_password',
        transaction.non_atomic_requests(views.CreateUserAccountWithoutPasswordView.as_view()),
        name="create_user_account_without_password_api"
    ),
    re_path(r'^accounts/create',
        transaction.non_atomic_requests(views.CreateUserAccountView.as_view()),
        name="create_user_account_api"
    ),
    re_path(r'^accounts/connect', views.UserAccountConnect.as_view(), name="user_account_connect_api"),
    re_path(r'^accounts/update_user', views.UpdateUserAccount.as_view(), name="user_account_update_user"),
    re_path(r'^accounts/get-user/(?P<username>[\w.+-]+)', views.GetUserAccountView.as_view(), name="get_user_account_api"),

    # Just like CourseListView API, but with search
    re_path(r'^search_courses', views.CourseListSearchView.as_view(), name="course_list_search"),

    # bulk enrollment API
    re_path(r'^bulk-enrollment/bulk-enroll', views.BulkEnrollView.as_view(), name="bulk_enrollment_api"),

    # enrollment codes API
    re_path(r'^enrollment-codes/generate', views.GenerateRegistrationCodesView.as_view(), name="generate_registration_codes_api"),  # pylint: disable=line-too-long
    re_path(r'^enrollment-codes/enroll-user', views.EnrollUserWithEnrollmentCodeView.as_view(), name="enroll_use_with_code_api"),  # pylint: disable=line-too-long
    re_path(r'^enrollment-codes/status', views.EnrollmentCodeStatusView.as_view(), name="enrollment_code_status_api"),

    # enrollment analytics API
    re_path(r'^analytics/accounts/batch', views.GetBatchUserDataView.as_view(), name="get_batch_user_data"),
    re_path(r'^analytics/enrollment/batch', views.GetBatchEnrollmentDataView.as_view(), name="get_batch_enrollment_data"),
]
