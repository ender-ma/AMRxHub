"""Branded error page, shown for every HTTP error the site produces.

The page is rendered without a request, so no context processors run and it
never touches the database. It has to keep working during a database outage.
"""
from django.http import HttpResponse
from django.template.loader import render_to_string

ERROR_MESSAGES = {
    400: ("Bad request", "We couldn't understand that request. Please check the link or try again."),
    403: ("Access denied", "You don't have permission to view this page."),
    404: ("Page not found", "The page you're looking for doesn't exist or may have moved."),
    405: ("Action not allowed", "This page can't be used that way. Please go back and try again."),
    429: ("Too many requests", "You've made a lot of requests in a short time. Please wait a moment and try again."),
    500: ("Something went wrong", "An unexpected error occurred on our side. Please try again in a few minutes."),
}
DEFAULT_MESSAGE = ("Something went wrong", "We couldn't complete your request. Please try again.")
CSRF_MESSAGE = ("Session expired", "Your form couldn't be verified. Please refresh the page and try again.")


def render_error_html(status, title_and_message=None):
    title, message = title_and_message or ERROR_MESSAGES.get(status, DEFAULT_MESSAGE)
    return render_to_string("errors/error.html", {"status": status, "title": title, "message": message})


def error_response(status, title_and_message=None):
    return HttpResponse(render_error_html(status, title_and_message), status=status)


def bad_request(request, exception):
    return error_response(400)


def permission_denied(request, exception):
    return error_response(403)


def page_not_found(request, exception):
    return error_response(404)


def server_error(request):
    return error_response(500)


def csrf_failure(request, reason=""):
    return error_response(403, CSRF_MESSAGE)


def error_preview(request, status):
    """DEBUG-only: Django shows its debug pages instead of the handlers above."""
    return error_response(status)


class ErrorPageMiddleware:
    """Fill in empty error responses, such as the 405 from @require_POST.

    These never reach the handlers above, so a browser would show a blank page.
    fetch() callers don't send text/html in Accept and are left alone. Must sit
    after CommonMiddleware, which sets Content-Length from the final body.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if (
            response.status_code >= 400
            and not response.streaming
            and not response.content
            and "text/html" in request.headers.get("Accept", "")
        ):
            response.content = render_error_html(response.status_code)
            response["Content-Type"] = "text/html; charset=utf-8"
        return response
