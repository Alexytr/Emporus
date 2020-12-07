import time


def execution_timer(func):
    """
    Decorator: Used to print runtime of the decorated function
    """
    def timer_wrapper(*args, **kwargs):

        start = time.perf_counter()
        returned = func(*args, **kwargs)
        end = time.perf_counter()
        run_time = end - start
        print(f"Finished {func.__name__} in {run_time:.2f} secs")
        return returned

    return timer_wrapper

