from app.celery_app import celery_app


@celery_app.task(name="add_numbers")
def add_numbers(a: int, b: int) -> int:
    """
    Celery task to add two numbers and print the result.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        The sum of a and b
    """
    result = a + b
    print(f"Adding {a} + {b} = {result}")
    return result
