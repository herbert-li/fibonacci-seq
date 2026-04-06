from flask import Flask, jsonify, request
import logging
import time

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def fibonacci(n):
    """
    Calculate the nth Fibonacci number.
    F(0) = 0, F(1) = 1, F(n) = F(n-1) + F(n-2) for n > 1

    Uses iterative approach for O(n) time complexity and O(1) space complexity.
    """
    if n < 0:
        raise ValueError("n must be a non-negative integer")

    if n == 0:
        return 0
    elif n == 1:
        return 1

    prev, curr = 0, 1
    for _ in range(2, n + 1):
        prev, curr = curr, prev + curr

    return curr


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint for monitoring."""
    return jsonify({"status": "healthy"}), 200


@app.route("/fibonacci", methods=["GET"])
def get_fibonacci():
    """
    GET /fibonacci?n=<number>
    Returns the nth Fibonacci number.
    """
    start_time = time.time()

    try:
        n = request.args.get("n")

        if n is None:
            logger.warning("Request missing parameter 'n'")
            return (
                jsonify(
                    {
                        "error": "Missing parameter 'n'",
                        "message": "Please provide a non-negative integer n as a query parameter",
                    }
                ),
                400,
            )

        try:
            n = int(n)
        except ValueError:
            logger.warning(f"Invalid parameter value: {n}")
            return (
                jsonify(
                    {
                        "error": "Invalid parameter",
                        "message": "Parameter 'n' must be an integer",
                    }
                ),
                400,
            )

        if n < 0:
            logger.warning(f"Negative parameter value: {n}")
            return (
                jsonify(
                    {
                        "error": "Invalid parameter",
                        "message": "Parameter 'n' must be a non-negative integer",
                    }
                ),
                400,
            )

        # Limit n to prevent excessive computation
        if n > 10000:
            logger.warning(f"Parameter value too large: {n}")
            return (
                jsonify(
                    {
                        "error": "Parameter too large",
                        "message": "Parameter 'n' must be <= 10000",
                    }
                ),
                400,
            )

        result = fibonacci(n)
        elapsed_time = time.time() - start_time

        logger.info(f"Computed F({n}) = {result} in {elapsed_time:.4f}s")

        return (
            jsonify(
                {
                    "n": n,
                    "result": result,
                    "computation_time_seconds": round(elapsed_time, 4),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error", "message": str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return (
        jsonify(
            {"error": "Not found", "message": "The requested endpoint does not exist"}
        ),
        404,
    )


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}")
    return (
        jsonify(
            {
                "error": "Internal server error",
                "message": "An unexpected error occurred",
            }
        ),
        500,
    )


if __name__ == "__main__":
    # For development only - use a proper WSGI server in production
    app.run(host="0.0.0.0", port=5000, debug=False)
