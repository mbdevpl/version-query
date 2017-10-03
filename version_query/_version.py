"""Version of version_query package."""

from .query import predict_caller

VERSION = predict_caller().to_str()
