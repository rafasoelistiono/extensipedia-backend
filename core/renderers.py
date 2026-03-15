from rest_framework.renderers import JSONRenderer


class StandardJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        renderer_context = renderer_context or {}
        response = renderer_context.get("response")

        if response is None:
            return super().render(data, accepted_media_type, renderer_context)

        if isinstance(data, dict) and {"success", "message", "data"}.issubset(data.keys()):
            wrapped = data
        elif getattr(response, "exception", False):
            message = "Request failed"
            if isinstance(data, dict):
                message = data.get("message") or data.get("detail") or message
            wrapped = {
                "success": False,
                "message": str(message),
                "data": data,
            }
        else:
            wrapped = {
                "success": True,
                "message": getattr(response, "_message", "Request successful"),
                "data": data,
            }

        return super().render(wrapped, accepted_media_type, renderer_context)
