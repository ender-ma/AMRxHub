from .signals import object_viewed_signal

class ObjectViewMixin:
    """
    Mixin to send a signal when an object is viewed successfully.
    Should be placed before the main view class in inheritance, e.g.,
    class MyDetailView(ObjectViewMixin, DetailView): ...
    """
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if (
            response.status_code == 200
            and hasattr(self, "object")
            and self.object is not None
            and request.user.is_authenticated
        ):
            object_viewed_signal.send(
                self.object.__class__, instance=self.object, request=request
            )
        return response