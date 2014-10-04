from django.conf.urls import patterns, include, url
from django.contrib import admin

from peacecorps.views import donation_payment_individual
from peacecorps.views import donation_payment_organization
from peacecorps.views import donation_payment_review

from peacecorps.views import donate_landing
from peacecorps.views import donate_issue
from peacecorps.views import donate_project

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^donate/?$', donate_landing, name='donate landing'),
    url(r'^donate/issue/(?P<slug>[a-zA-Z0-9_-]*)/?$',
        donate_issue, name='donate issue'),
    url(r'^donate/project/(?P<slug>[a-zA-Z0-9_-]*)/?$',
        donate_project, name='donate project'),
    url(
        r'^donations/contribute/individual$',
        donation_payment_individual, name='donations_individual'),
    url(
        r'^donations/contribute/organization$',
        donation_payment_organization, name='donations_organization'),
    url(
        r'^donations/review$',
        donation_payment_review, name='donations_review'),
)
