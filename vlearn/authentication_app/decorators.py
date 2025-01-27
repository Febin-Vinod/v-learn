from django.http import HttpResponseForbidden
from functools import wraps
def instructor_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.profile.isInstructor:  # Assuming you have Profile linked with the user
            return HttpResponseForbidden("You are not authorized to view this page.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
