def log(logger):
    def decorator(func):
        def decorated(*args, **kwargs):
            res = func(*args, **kwargs)
            logger.debug(f'Log: {func.__name__}({args},{kwargs}) = {res}')
            return res
        return decorated
    return decorator
