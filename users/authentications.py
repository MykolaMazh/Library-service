from rest_framework_simplejwt.authentication import JWTAuthentication


class CustomJWTAuthentication(JWTAuthentication):
    def get_header(self, request):
        header = request.META.get("HTTP_AUTHORIZE")
        if header is None:
            return None
        return header.encode("utf-8")
