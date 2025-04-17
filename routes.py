from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from controllers import (
    product_controller,
    inventory_controller
)

app = FastAPI()

def custom_openapi():
    if app.openapi_schema:  # Check if the OpenAPI schema is already created
        return app.openapi_schema
    
    # Define custom OpenAPI schema
    openapi_schema = get_openapi(
        title="We Rent API",
        version="1.0.0",
        description="An API for We Rent Project",
        routes=app.routes,
    )

    # Add global security definitions (if needed)
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    # Add global security requirements
    openapi_schema["security"] = [{"BearerAuth": []}]

    # Modify any additional OpenAPI details
    # openapi_schema["info"]["contact"] = {
    #     "name": "Support Team",
    #     "email": "support@example.com",
    #     "url": "https://example.com/support",
    # }

    # Cache the schema for future use
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Include all routers
app.include_router(product_controller.router)
app.include_router(inventory_controller.router)
