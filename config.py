"""Configuration for the EnformionGO API wrapper."""

from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Credentials are optional at startup so the server can boot without env vars;
    # requests will fail at runtime if credentials are missing.
    GALAXY_AP_NAME: str | None = None
    GALAXY_AP_PASSWORD: SecretStr | None = None  # Use SecretStr for sensitive values

    PERSON_SEARCH_API_URL: str = "https://devapi.enformion.com/PersonSearch"
    REVERSE_PHONE_API_URL: str = "https://devapi.enformion.com/ReversePhoneSearch"
    CONTACT_ENRICHMENT_API_URL: str = "https://devapi.enformion.com/Contact/Enrich"
    CALLER_ID_API_URL: str = "https://devapi.enformion.com/Phone/Enrich"
    EMAIL_ID_API_URL: str = "https://devapi.enformion.com/Email/Enrich"
    CONTACT_ID_API_URL: str = "https://devapi.enformion.com/Contact/Id"
    ADDRESS_ID_API_URL: str = "https://devapi.enformion.com/Address/Id"
    ADDRESS_AUTOCOMPLETE_API_URL: str = "https://devapi.enformion.com/Address/AutoComplete"
    ID_VERIFICATION_API_URL: str = "https://devapi.enformion.com/Identity/Verify_Id"
    CENSUS_SEARCH_API_URL: str = "https://devapi.enformion.com/CensusSearch"
    DIVORCE_SEARCH_API_URL: str = "https://devapi.enformion.com/DivorceSearch"
    LINKEDIN_ID_API_URL: str = "https://devapi.enformion.com/LinkedIn/Id"
    PROPERTY_SEARCH_V2_API_URL: str = "https://devapi.enformion.com/PropertyV2Search"
    BUSINESS_SEARCH_V2_API_URL: str = "https://devapi.enformion.com/BusinessV2Search"
    DOMAIN_SEARCH_API_URL: str = "https://devapi.enformion.com/DomainSearch"
    WORKPLACE_SEARCH_API_URL: str = "https://devapi.enformion.com/WorkplaceSearch"
    BUSINESS_ID_API_URL: str = "https://devapi.enformion.com/Business/Id"

    # Enrich+ / Id+ endpoints (documented in ReadMe)
    CONTACT_ENRICHMENT_PLUS_API_URL: str = "https://devapi.enformion.com/Contact/EnrichPlus"
    CONTACT_ID_PLUS_API_URL: str = "https://devapi.enformion.com/Contact/IdPlus"
    CALLER_ID_PLUS_API_URL: str = "https://devapi.enformion.com/Phone/EnrichPlus"
    EMAIL_ID_PLUS_API_URL: str = "https://devapi.enformion.com/Email/EnrichPlus"
    ADDRESS_ID_PLUS_API_URL: str = "https://devapi.enformion.com/Address/IdPlus"

    # Additional data endpoints (documented in ReadMe)
    CRIMINAL_SEARCH_V2_API_URL: str = "https://devapi.enformion.com/CriminalSearch/V2"
    DEBT_SEARCH_V2_API_URL: str = "https://devapi.enformion.com/DebtSearch/V2"
    EVICTION_SEARCH_API_URL: str = "https://devapi.enformion.com/EvictionSearch"
    MARRIAGE_SEARCH_API_URL: str = "https://devapi.enformion.com/MarriageSearch"
    OFAC_SEARCH_API_URL: str = "https://devapi.enformion.com/OfacSearch"
    PRE_FORECLOSURE_SEARCH_V2_API_URL: str = "https://devapi.enformion.com/ForeclosureV2Search"
    PRO_LICENSE_SEARCH_API_URL: str = "https://devapi.enformion.com/ProLicenseSearch"
    VEHICLE_OWNERSHIP_SEARCH_API_URL: str = "https://devapi.enformion.com/VehicleRegistrationSearch"
    ELEADVERIFY_API_URL: str = "https://devapi.enformion.com/eIDV/eLeadVerify"

    # Data Alerts endpoints (documented in ReadMe)
    DATA_ALERTS_ADD_SUBSCRIPTION_API_URL: str = "https://devapi.enformion.com/DataAlerts/AddSubscription"
    DATA_ALERTS_REMOVE_SUBSCRIPTION_API_URL: str = "https://devapi.enformion.com/DataAlerts/RemoveSubscription"
    DATA_ALERTS_GET_SUBSCRIPTION_API_URL: str = "https://devapi.enformion.com/DataAlerts/GetSubscription"
    DATA_ALERTS_COUNT_ALERT_API_URL: str = "https://devapi.enformion.com/DataAlerts/CountAlert"
    DATA_ALERTS_GET_ALERT_API_URL: str = "https://devapi.enformion.com/DataAlerts/GetAlert"

    class Config:
        """Pydantic settings configuration."""

        env_file = ".env"


settings = Settings()