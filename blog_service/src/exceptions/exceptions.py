class BlogException(Exception):
    status_code: int = 500
    detail: str = "Unexpected error"

    def __init__(self, detail: str | None = None):
        if detail:
            self.detail = detail
        super().__init__(self.detail)


class PostNotFoundException(BlogException):
    status_code = 404
    detail = "Post not found"


class PermissionErrorException(BlogException):
    status_code = 403
    detail = "You can only work with your own posts"


class PostAlreadyExistException(BlogException):
    status_code = 409
    detail = "Post already exists"


class UserNotFoundException(BlogException):
    status_code = 404
    detail = "User not found"


class ObjectNotFoundException(BlogException):
    status_code = 404
    detail = "Object not found"


class ObjectExistYet(BlogException):
    status_code = 409
    detail = "Object already exists"
