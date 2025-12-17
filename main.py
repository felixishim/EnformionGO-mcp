from typing import Any
import logging
from enum import Enum
import httpx
from fastapi import Body, Depends, FastAPI, Header, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi_mcp import FastApiMCP

from config import Settings, settings
from error_handling import http_exception_handler, enformiongo_exception_handler
from exceptions import APIConnectionError, InvalidRequestError
from logging_config import setup_logging
from models import (
    PropertySearchV2Request,
    DomainSearchRequest,
    WorkplaceSearchRequest,
    BusinessIDRequest,
    PersonSearchRequest,
    ContactEnrichmentRequest,
    ReversePhoneSearchRequest,
    CallerIdRequest,
    EmailIdRequest,
    ContactIdRequest,
    AddressIdRequest,
    AddressAutoCompleteRequest,
    IdVerificationRequest,
    CensusSearchRequest,
    DivorceSearchRequest,
    LinkedInIdRequest,
    BusinessSearchRequest,
)

# --- Logging Setup ---
setup_logging()
logger = logging.getLogger(__name__)


# --- Configuration ---
def get_settings():
    return settings


# --- Enums ---
class PersonSearchType(str, Enum):
    person = "Person"
    teaser = "Teaser"


# --- Validation Dependencies ---
def validate_contact_enrichment_request(request: ContactEnrichmentRequest):
    """Dependency to validate that at least two search criteria are provided."""
    criteria_count = 0
    # A name counts as one criterion
    if request.first_name or request.middle_name or request.last_name:
        criteria_count += 1
    if request.phone:
        criteria_count += 1
    if request.address:
        criteria_count += 1
    if request.email:
        criteria_count += 1
    
    if criteria_count < 2:
        raise HTTPException(
            status_code=400,
            detail="Contact Enrichment requires at least two search criteria from: Name, Phone, Address, or Email."
        )
    return request

def validate_id_verification_request(request: IdVerificationRequest):
    """Dependency to validate that at least two ID verification criteria are provided."""
    criteria_count = 0
    if request.first_name or request.middle_name or request.last_name:
        criteria_count += 1
    if request.phones:
        criteria_count += 1
    if request.address_line_1 or request.address_line_2:
        criteria_count += 1
    if request.emails:
        criteria_count += 1
    if request.ssn:
        criteria_count +=1
    
    if criteria_count < 2:
        raise HTTPException(
            status_code=400,
            detail="ID Verification requires at least two criteria from: SSN, Name, Phone, Address, or Email."
        )
    return request


# --- API Helper Function ---
async def call_enformion_api(
    api_url: str,
    search_type: str,
    request_body: dict,
    settings: Settings,
    *,
    galaxy_ap_name: str | None = None,
    galaxy_ap_password: str | None = None,
    galaxy_client_session_id: str | None = None,
    galaxy_client_type: str | None = None,
):
    """Generic helper to call the EnformionGO API."""
    ap_name = galaxy_ap_name or settings.GALAXY_AP_NAME
    ap_password = galaxy_ap_password or (
        settings.GALAXY_AP_PASSWORD.get_secret_value() if settings.GALAXY_AP_PASSWORD else None
    )

    if not ap_name or not ap_password:
        raise APIConnectionError(
            "API credentials are not configured. Provide (GALAXY_AP_NAME, GALAXY_AP_PASSWORD) via env/.env, "
            "or pass them as request headers (galaxy-ap-name, galaxy-ap-password)."
        )

    headers = {
        "galaxy-ap-name": ap_name,
        "galaxy-ap-password": ap_password,
        "galaxy-search-type": search_type,
        "Content-Type": "application/json",
    }

    if galaxy_client_session_id:
        headers["galaxy-client-session-id"] = galaxy_client_session_id
    if galaxy_client_type:
        headers["galaxy-client-type"] = galaxy_client_type

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.post(api_url, json=request_body, headers=headers)
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise APIConnectionError(f"Request to EnformionGO API timed out: {exc}")
        except httpx.RequestError as exc:
            raise APIConnectionError(f"Error communicating with EnformionGO API: {exc}")
        except httpx.HTTPStatusError as exc:
            logger.error(
                f"Invalid request to EnformionGO API. Status: {exc.response.status_code}, Response: {exc.response.text}"
            )
            raise InvalidRequestError("The request to the upstream service failed.")
    return response.json()


# --- FastAPI Application ---
app = FastAPI(
    title="EnformionGO API Wrapper",
    description="A wrapper for the EnformionGO API Endpoints. With a Twist, MCP-enabled using FastMCP.",
    version="1.7.0",
)

# --- Static UI ---
# Served at /ui (no build step). Visit /ui/ for the search console.
app.mount("/ui", StaticFiles(directory="static", html=True), name="ui")

@app.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/ui/")

mcp = FastApiMCP(
    app,
    name="EnformionGO MCPServer",
    description="EnformionGO API Wrapped using FastAPI & converted into an http MCPServer using FastApiMCP **NOTE** This is a Bring your own API KEY tool which can be obtainedfrom http://api.enformiongo.com",
)

mcp.mount_http()

# --- Exception Handlers ---
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(APIConnectionError, enformiongo_exception_handler)
app.add_exception_handler(InvalidRequestError, enformiongo_exception_handler)


# --- Endpoints ---

# --- Dev APIs (Single Result) Endpoints ---
@app.post("/contact-enrichment", tags=["Dev APIs (Single Result)"])
async def contact_enrichment(
    search_request: ContactEnrichmentRequest = Depends(validate_contact_enrichment_request),
    settings: Settings = Depends(get_settings),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
    galaxy_search_type: str | None = Header(None, alias="galaxy-search-type"),
):
    """Performs a contact enrichment search. Requires at least two criteria."""
    request_body = search_request.model_dump(by_alias=True, exclude_none=True)
    return await call_enformion_api(
        settings.CONTACT_ENRICHMENT_API_URL,
        galaxy_search_type or "DevAPIContactEnrich",
        request_body,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )

@app.post("/caller-id", tags=["Dev APIs (Single Result)"])
async def caller_id(
    search_request: CallerIdRequest,
    settings: Settings = Depends(get_settings),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
    galaxy_search_type: str | None = Header(None, alias="galaxy-search-type"),
):
    """Retrieves information associated with a provided phone number."""
    request_body = search_request.model_dump(by_alias=True, exclude_none=True)
    return await call_enformion_api(
        settings.CALLER_ID_API_URL,
        galaxy_search_type or "DevAPICallerID",
        request_body,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )

@app.post("/email-id", tags=["Dev APIs (Single Result)"])
async def email_id(
    search_request: EmailIdRequest,
    settings: Settings = Depends(get_settings),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
    galaxy_search_type: str | None = Header(None, alias="galaxy-search-type"),
):
    """Retrieves information associated with a provided email address."""
    request_body = search_request.model_dump(by_alias=True, exclude_none=True)
    return await call_enformion_api(
        settings.EMAIL_ID_API_URL,
        galaxy_search_type or "DevAPIEmailID",
        request_body,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )

@app.post("/contact-id", tags=["Dev APIs (Single Result)"])
async def contact_id(
    search_request: ContactIdRequest,
    settings: Settings = Depends(get_settings),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
    galaxy_search_type: str | None = Header(None, alias="galaxy-search-type"),
):
    """Searches for contact information using a unique person ID."""
    request_body = search_request.model_dump(by_alias=True, exclude_none=True)
    return await call_enformion_api(
        settings.CONTACT_ID_API_URL,
        galaxy_search_type or "DevAPIContactID",
        request_body,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )

@app.post("/address-id", tags=["Dev APIs (Single Result)"])
async def address_id(
    search_request: AddressIdRequest,
    settings: Settings = Depends(get_settings),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
    galaxy_search_type: str | None = Header(None, alias="galaxy-search-type"),
):
    """Finds contact info for current owners or residents of a property."""
    request_body = search_request.model_dump(by_alias=True, exclude_none=True)
    return await call_enformion_api(
        settings.ADDRESS_ID_API_URL,
        galaxy_search_type or "DevAPIAddressID",
        request_body,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )

@app.post("/address-autocomplete", tags=["Dev APIs (Single Result)"])
async def address_autocomplete(
    search_request: AddressAutoCompleteRequest,
    settings: Settings = Depends(get_settings),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
    galaxy_search_type: str | None = Header(None, alias="galaxy-search-type"),
):
    """Provides address autocomplete functionality."""
    request_body = search_request.model_dump(by_alias=True, exclude_none=True)
    return await call_enformion_api(
        settings.ADDRESS_AUTOCOMPLETE_API_URL,
        galaxy_search_type or "AddressSearch",
        request_body,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )

# --- People Data Endpoints ---
@app.post("/person-search", tags=["People Data"])
async def person_search(
    search_request: PersonSearchRequest,
    settings: Settings = Depends(get_settings),
    galaxy_search_type: PersonSearchType = Header(
        PersonSearchType.person, alias="galaxy-search-type", description="Search type."
    ),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
):
    """Performs a person search by proxying the request to the EnformionGO API."""
    request_body = search_request.model_dump(by_alias=True, exclude_none=True)
    return await call_enformion_api(
        settings.PERSON_SEARCH_API_URL,
        galaxy_search_type.value,
        request_body,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )

@app.post("/reverse-phone-search", tags=["People Data"])
async def reverse_phone_search(
    search_request: ReversePhoneSearchRequest,
    settings: Settings = Depends(get_settings),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
    galaxy_search_type: str | None = Header(None, alias="galaxy-search-type"),
):
    """Performs a reverse phone search by proxying the request to the EnformionGO API."""
    request_body = search_request.model_dump(by_alias=True, exclude_none=True)
    return await call_enformion_api(
        settings.REVERSE_PHONE_API_URL,
        galaxy_search_type or "ReversePhoneSearch",
        request_body,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )

@app.post("/id-verification", tags=["People Data"])
async def id_verification(
    search_request: IdVerificationRequest = Depends(validate_id_verification_request),
    settings: Settings = Depends(get_settings),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
    galaxy_search_type: str | None = Header(None, alias="galaxy-search-type"),
):
    """Provides an identity score and verification flag. Requires at least two criteria."""
    request_body = search_request.model_dump(by_alias=True, exclude_none=True)
    return await call_enformion_api(
        settings.ID_VERIFICATION_API_URL,
        galaxy_search_type or "DevAPIIDVerification",
        request_body,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )

@app.post("/census-search", tags=["People Data"])
async def census_search(
    search_request: CensusSearchRequest,
    settings: Settings = Depends(get_settings),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
    galaxy_search_type: str | None = Header(None, alias="galaxy-search-type"),
):
    """Searches historical population data."""
    request_body = search_request.model_dump(by_alias=True, exclude_none=True)
    return await call_enformion_api(
        settings.CENSUS_SEARCH_API_URL,
        galaxy_search_type or "Census",
        request_body,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )

@app.post("/divorce-search", tags=["People Data"])
async def divorce_search(
    search_request: DivorceSearchRequest,
    settings: Settings = Depends(get_settings),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
    galaxy_search_type: str | None = Header(None, alias="galaxy-search-type"),
):
    """Searches for divorce records."""
    request_body = search_request.model_dump(by_alias=True, exclude_none=True)
    return await call_enformion_api(
        settings.DIVORCE_SEARCH_API_URL,
        galaxy_search_type or "Divorce",
        request_body,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )

@app.post("/linkedin-id", tags=["People Data"])
async def linkedin_id(
    search_request: LinkedInIdRequest,
    settings: Settings = Depends(get_settings),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
    galaxy_search_type: str | None = Header(None, alias="galaxy-search-type"),
):
    """Searches by a LinkedIn profile URL."""
    request_body = search_request.model_dump(by_alias=True, exclude_none=True)
    return await call_enformion_api(
        settings.LINKEDIN_ID_API_URL,
        galaxy_search_type or "LinkedInID",
        request_body,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )


# --- Property Data Endpoints ---
@app.post("/property-search-v2", tags=["Property Data"])
async def property_search_v2(
    search_request: PropertySearchV2Request,
    settings: Settings = Depends(get_settings),
    galaxy_search_type: str | None = Header(
        None, alias="galaxy-search-type", description="The galaxy-search-type for Property Search V2."
    ),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
):
    """
    Searches for property data.
    """
    request_body = search_request.model_dump(by_alias=True, exclude_none=True)
    return await call_enformion_api(
        settings.PROPERTY_SEARCH_V2_API_URL,
        galaxy_search_type or "PropertyV2Search",
        request_body,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )

# --- Business Data Endpoints ---
@app.post("/business-search", tags=["Business Data"])
async def business_search(
    search_request: BusinessSearchRequest,
    settings: Settings = Depends(get_settings),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
    galaxy_search_type: str | None = Header(None, alias="galaxy-search-type"),
):
    """
    Searches for business data using various criteria.
    """
    request_body = search_request.model_dump(by_alias=True, exclude_none=True)
    return await call_enformion_api(
        settings.BUSINESS_SEARCH_V2_API_URL,
        galaxy_search_type or "BusinessV2Search",
        request_body,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )

@app.post("/business-search-v2", tags=["Business Data"])
async def business_search_v2(
    search_request: BusinessSearchRequest,
    settings: Settings = Depends(get_settings),
    galaxy_search_type: str | None = Header(
        None, alias="galaxy-search-type", description="The galaxy-search-type for Business Search V2."
    ),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
):
    """
    Searches for business data using various criteria.
    """
    request_body = search_request.model_dump(by_alias=True, exclude_none=True)
    return await call_enformion_api(
        settings.BUSINESS_SEARCH_V2_API_URL,
        galaxy_search_type or "BusinessV2Search",
        request_body,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )

@app.post("/domain-search", tags=["Business Data"])
async def domain_search(
    search_request: DomainSearchRequest,
    settings: Settings = Depends(get_settings),
    galaxy_search_type: str | None = Header(
        None, alias="galaxy-search-type", description="The galaxy-search-type for Domain Search."
    ),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
):
    """
    Searches for domain data.
    """
    request_body = search_request.model_dump(by_alias=True, exclude_none=True)
    return await call_enformion_api(
        settings.DOMAIN_SEARCH_API_URL,
        galaxy_search_type or "DomainSearch",
        request_body,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )

@app.post("/workplace-search", tags=["Business Data"])
async def workplace_search(
    search_request: WorkplaceSearchRequest,
    settings: Settings = Depends(get_settings),
    galaxy_search_type: str | None = Header(
        None, alias="galaxy-search-type", description="The galaxy-search-type for Workplace Search."
    ),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
):
    """
    Searches for workplace data.
    """
    request_body = search_request.model_dump(by_alias=True, exclude_none=True)
    return await call_enformion_api(
        settings.WORKPLACE_SEARCH_API_URL,
        galaxy_search_type or "WorkplaceSearch",
        request_body,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )

@app.post("/business-id", tags=["Business Data"])
async def business_id(
    search_request: BusinessIDRequest,
    settings: Settings = Depends(get_settings),
    galaxy_search_type: str | None = Header(
        None, alias="galaxy-search-type", description="The galaxy-search-type for Business ID Search."
    ),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
):
    """
    Searches by business ID.
    """
    request_body = search_request.model_dump(by_alias=True, exclude_none=True)
    return await call_enformion_api(
        settings.BUSINESS_ID_API_URL,
        galaxy_search_type or "BusinessID",
        request_body,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )

# --- Enrich+/Id+ Endpoints ---
@app.post("/contact-enrichment-plus", tags=["Dev APIs (Single Result)"])
async def contact_enrichment_plus(
    payload: dict[str, Any] = Body(...),
    settings: Settings = Depends(get_settings),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
    galaxy_search_type: str | None = Header(None, alias="galaxy-search-type"),
):
    """Performs a contact enrichment (Enrich+) search."""
    return await call_enformion_api(
        settings.CONTACT_ENRICHMENT_PLUS_API_URL,
        galaxy_search_type or "ContactEnrichPlus",
        payload,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )

@app.post("/contact-id-plus", tags=["Dev APIs (Single Result)"])
async def contact_id_plus(
    payload: dict[str, Any] = Body(...),
    settings: Settings = Depends(get_settings),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
    galaxy_search_type: str | None = Header(None, alias="galaxy-search-type"),
):
    """Searches for contact information using a unique person ID (Id+)."""
    return await call_enformion_api(
        settings.CONTACT_ID_PLUS_API_URL,
        galaxy_search_type or "ContactIdPlus",
        payload,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )

@app.post("/caller-id-plus", tags=["Dev APIs (Single Result)"])
async def caller_id_plus(
    payload: dict[str, Any] = Body(...),
    settings: Settings = Depends(get_settings),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
    galaxy_search_type: str | None = Header(None, alias="galaxy-search-type"),
):
    """Retrieves information associated with a provided phone number (Enrich+)."""
    return await call_enformion_api(
        settings.CALLER_ID_PLUS_API_URL,
        galaxy_search_type or "PhoneEnrichPlus",
        payload,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )

@app.post("/email-id-plus", tags=["Dev APIs (Single Result)"])
async def email_id_plus(
    payload: dict[str, Any] = Body(...),
    settings: Settings = Depends(get_settings),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
    galaxy_search_type: str | None = Header(None, alias="galaxy-search-type"),
):
    """Retrieves information associated with a provided email address (Enrich+)."""
    return await call_enformion_api(
        settings.EMAIL_ID_PLUS_API_URL,
        galaxy_search_type or "EmailEnrichPlus",
        payload,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )

@app.post("/address-id-plus", tags=["Dev APIs (Single Result)"])
async def address_id_plus(
    payload: dict[str, Any] = Body(...),
    settings: Settings = Depends(get_settings),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
    galaxy_search_type: str | None = Header(None, alias="galaxy-search-type"),
):
    """Finds contact info for current owners or residents of a property (Id+)."""
    return await call_enformion_api(
        settings.ADDRESS_ID_PLUS_API_URL,
        galaxy_search_type or "AddressIdPlus",
        payload,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )

# --- Additional People/Property/Business Endpoints (documented in ReadMe) ---
@app.post("/criminal-search-v2", tags=["People Data"])
async def criminal_search_v2(
    payload: dict[str, Any] = Body(...),
    settings: Settings = Depends(get_settings),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
    galaxy_search_type: str | None = Header(None, alias="galaxy-search-type"),
):
    """Searches for criminal records (v2)."""
    return await call_enformion_api(
        settings.CRIMINAL_SEARCH_V2_API_URL,
        galaxy_search_type or "CriminalSearchV2",
        payload,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )

@app.post("/debt-v2", tags=["People Data"])
async def debt_v2(
    payload: dict[str, Any] = Body(...),
    settings: Settings = Depends(get_settings),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
    galaxy_search_type: str | None = Header(None, alias="galaxy-search-type"),
):
    """Searches for debt records (v2)."""
    return await call_enformion_api(
        settings.DEBT_SEARCH_V2_API_URL,
        galaxy_search_type or "DebtSearchV2",
        payload,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )

@app.post("/eviction-search", tags=["People Data"])
async def eviction_search(
    payload: dict[str, Any] = Body(...),
    settings: Settings = Depends(get_settings),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
    galaxy_search_type: str | None = Header(None, alias="galaxy-search-type"),
):
    """Searches eviction records."""
    return await call_enformion_api(
        settings.EVICTION_SEARCH_API_URL,
        galaxy_search_type or "EvictionSearch",
        payload,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )

@app.post("/marriage-search", tags=["People Data"])
async def marriage_search(
    payload: dict[str, Any] = Body(...),
    settings: Settings = Depends(get_settings),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
    galaxy_search_type: str | None = Header(None, alias="galaxy-search-type"),
):
    """Searches marriage records."""
    return await call_enformion_api(
        settings.MARRIAGE_SEARCH_API_URL,
        galaxy_search_type or "MarriageSearch",
        payload,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )

@app.post("/ofac-search", tags=["People Data"])
async def ofac_search(
    payload: dict[str, Any] = Body(...),
    settings: Settings = Depends(get_settings),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
    galaxy_search_type: str | None = Header(None, alias="galaxy-search-type"),
):
    """Searches OFAC records."""
    return await call_enformion_api(
        settings.OFAC_SEARCH_API_URL,
        galaxy_search_type or "OfacSearch",
        payload,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )

@app.post("/pre-foreclosure-search-v2", tags=["Property Data"])
async def pre_foreclosure_search_v2(
    payload: dict[str, Any] = Body(...),
    settings: Settings = Depends(get_settings),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
    galaxy_search_type: str | None = Header(None, alias="galaxy-search-type"),
):
    """Searches pre-foreclosure / foreclosure records (v2)."""
    return await call_enformion_api(
        settings.PRE_FORECLOSURE_SEARCH_V2_API_URL,
        galaxy_search_type or "ForeclosureV2Search",
        payload,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )

@app.post("/professional-license-search", tags=["People Data"])
async def professional_license_search(
    payload: dict[str, Any] = Body(...),
    settings: Settings = Depends(get_settings),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
    galaxy_search_type: str | None = Header(None, alias="galaxy-search-type"),
):
    """Searches professional license records."""
    return await call_enformion_api(
        settings.PRO_LICENSE_SEARCH_API_URL,
        galaxy_search_type or "ProLicense",
        payload,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )

@app.post("/vehicle-ownership-search", tags=["People Data"])
async def vehicle_ownership_search(
    payload: dict[str, Any] = Body(...),
    settings: Settings = Depends(get_settings),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
    galaxy_search_type: str | None = Header(None, alias="galaxy-search-type"),
):
    """Searches vehicle ownership / registration records."""
    return await call_enformion_api(
        settings.VEHICLE_OWNERSHIP_SEARCH_API_URL,
        galaxy_search_type or "VehicleRegistrationSearch",
        payload,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )

@app.post("/eleadverify", tags=["People Data"])
async def eleadverify(
    payload: dict[str, Any] = Body(...),
    settings: Settings = Depends(get_settings),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
    galaxy_search_type: str | None = Header(None, alias="galaxy-search-type"),
):
    """Performs eIDV eLeadVerify (documented in ReadMe)."""
    return await call_enformion_api(
        settings.ELEADVERIFY_API_URL,
        galaxy_search_type or "eLeadVerify",
        payload,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )

# --- Data Alerts Endpoints (documented in ReadMe) ---
@app.post("/data-alerts/add-subscription", tags=["Data Alerts"])
async def data_alerts_add_subscription(
    payload: dict[str, Any] = Body(...),
    settings: Settings = Depends(get_settings),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
    galaxy_search_type: str | None = Header(None, alias="galaxy-search-type"),
):
    """Adds a data alert subscription."""
    return await call_enformion_api(
        settings.DATA_ALERTS_ADD_SUBSCRIPTION_API_URL,
        galaxy_search_type or "DataAlertsAddSubscription",
        payload,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )

@app.post("/data-alerts/remove-subscription", tags=["Data Alerts"])
async def data_alerts_remove_subscription(
    payload: dict[str, Any] = Body(...),
    settings: Settings = Depends(get_settings),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
    galaxy_search_type: str | None = Header(None, alias="galaxy-search-type"),
):
    """Removes a data alert subscription."""
    return await call_enformion_api(
        settings.DATA_ALERTS_REMOVE_SUBSCRIPTION_API_URL,
        galaxy_search_type or "DataAlertsRemoveSubscription",
        payload,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )

@app.post("/data-alerts/get-subscription", tags=["Data Alerts"])
async def data_alerts_get_subscription(
    payload: dict[str, Any] = Body(...),
    settings: Settings = Depends(get_settings),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
    galaxy_search_type: str | None = Header(None, alias="galaxy-search-type"),
):
    """Retrieves a data alert subscription."""
    return await call_enformion_api(
        settings.DATA_ALERTS_GET_SUBSCRIPTION_API_URL,
        galaxy_search_type or "DataAlertsGetSubscription",
        payload,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )

@app.post("/data-alerts/count-alert", tags=["Data Alerts"])
async def data_alerts_count_alert(
    payload: dict[str, Any] = Body(...),
    settings: Settings = Depends(get_settings),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
    galaxy_search_type: str | None = Header(None, alias="galaxy-search-type"),
):
    """Counts alerts."""
    return await call_enformion_api(
        settings.DATA_ALERTS_COUNT_ALERT_API_URL,
        galaxy_search_type or "DataAlertsCountAlert",
        payload,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )

@app.post("/data-alerts/get-alert", tags=["Data Alerts"])
async def data_alerts_get_alert(
    payload: dict[str, Any] = Body(...),
    settings: Settings = Depends(get_settings),
    galaxy_ap_name: str | None = Header(None, alias="galaxy-ap-name"),
    galaxy_ap_password: str | None = Header(None, alias="galaxy-ap-password"),
    galaxy_client_session_id: str | None = Header(None, alias="galaxy-client-session-id"),
    galaxy_client_type: str | None = Header(None, alias="galaxy-client-type"),
    galaxy_search_type: str | None = Header(None, alias="galaxy-search-type"),
):
    """Retrieves an alert."""
    return await call_enformion_api(
        settings.DATA_ALERTS_GET_ALERT_API_URL,
        galaxy_search_type or "DataAlertsGetAlert",
        payload,
        settings,
        galaxy_ap_name=galaxy_ap_name,
        galaxy_ap_password=galaxy_ap_password,
        galaxy_client_session_id=galaxy_client_session_id,
        galaxy_client_type=galaxy_client_type,
    )


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


mcp.setup_server()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
