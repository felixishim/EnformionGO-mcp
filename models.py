"""
Pydantic models for the EnformionGO API Wrapper
"""

from typing import List, Optional
from pydantic import BaseModel, Field, model_validator


class Address(BaseModel):
    """Represents an address for the person search."""
    address_line_1: Optional[str] = Field(None, alias="addressLine1")
    address_line_2: Optional[str] = Field(None, alias="addressLine2")
    county: Optional[str] = Field(None, alias="County")

class Name(BaseModel):
    """Represents a name, used for AKAs and relatives."""
    first_name: Optional[str] = Field(None, alias="FirstName")
    middle_name: Optional[str] = Field(None, alias="MiddleName")
    last_name: Optional[str] = Field(None, alias="LastName")

class PersonSearchRequest(BaseModel):
    """Defines the request body for the Person Search API."""
    first_name: Optional[str] = Field(None, alias="FirstName")
    middle_name: Optional[str] = Field(None, alias="MiddleName")
    last_name: Optional[str] = Field(None, alias="LastName")
    akas: Optional[List[Name]] = Field(None, alias="Akas")
    dob: Optional[str] = Field(None, alias="Dob")
    age: Optional[int] = Field(None, alias="Age")
    age_range_min_age: Optional[int] = Field(None, alias="AgeRangeMinAge")
    age_range_max_age: Optional[int] = Field(None, alias="AgeRangeMaxAge")
    age_range: Optional[str] = Field(None, alias="AgeRange")
    ssn: Optional[str] = Field(None, alias="Ssn")
    addresses: Optional[List[Address]] = Field(None, alias="Addresses")
    email: Optional[str] = Field(None, alias="Email")
    client_ip: Optional[str] = Field(None, alias="ClientIp")
    phone: Optional[str] = Field(None, alias="Phone")
    relatives: Optional[List[Name]] = Field(None, alias="Relatives")
    tahoe_ids: Optional[List[str]] = Field(None, alias="TahoeIds")
    first_name_char_offset: Optional[int] = Field(None, alias="FirstNameCharOffset")
    last_name_char_offset: Optional[int] = Field(None, alias="LastNameCharOffset")
    dob_format: Optional[str] = Field(None, alias="DobFormat")
    max_address_years: Optional[int] = Field(None, alias="MaxAddressYears")
    max_phone_years: Optional[int] = Field(None, alias="MaxPhoneYears")

    class Config:
        """Pydantic config to allow population by alias."""
        populate_by_name = True

class ContactEnrichmentAddress(BaseModel):
    """Represents an address specifically for Contact Enrichment."""
    address_line_1: Optional[str] = Field(None, alias="addressLine1")
    address_line_2: Optional[str] = Field(None, alias="addressLine2")

class ContactEnrichmentRequest(BaseModel):
    """Defines the request body for the Contact Enrichment API."""
    first_name: Optional[str] = Field(None, alias="FirstName")
    middle_name: Optional[str] = Field(None, alias="MiddleName")
    last_name: Optional[str] = Field(None, alias="LastName")
    dob: Optional[str] = Field(None, alias="Dob")
    age: Optional[int] = Field(None, alias="Age")
    address: Optional[ContactEnrichmentAddress] = Field(None, alias="Address")
    phone: Optional[str] = Field(None, alias="Phone")
    email: Optional[str] = Field(None, alias="Email")

    class Config:
        """Pydantic config to allow population by alias."""
        populate_by_name = True

class ReversePhoneSearchRequest(BaseModel):
    """Defines the request body for the Reverse Phone Search API."""
    phone_number: str = Field(
        ...,
        alias="PhoneNumber",
        description="The phone number to search for (e.g., '(123) 456-7890').",
    )
    page: Optional[int] = Field(1, alias="Page", description="The page of data to return.")
    results_per_page: Optional[int] = Field(
        10, alias="ResultsPerPage", description="The number of results to return per page."
    )

    class Config:
        """Pydantic config to allow population by alias."""
        populate_by_name = True

    @model_validator(mode="before")
    @classmethod
    def accept_legacy_phone_field(cls, data):
        """
        Accept legacy payloads that use 'Phone' instead of 'PhoneNumber'.
        """
        if isinstance(data, dict) and "Phone" in data and "PhoneNumber" not in data:
            data = {**data, "PhoneNumber": data["Phone"]}
        return data

class CallerIdRequest(BaseModel):
    """Defines the request body for the Caller ID API."""
    phone: str = Field(..., alias="Phone")

    class Config:
        populate_by_name = True

class EmailIdRequest(BaseModel):
    """Defines the request body for the Email ID API."""
    email: str = Field(..., alias="Email")

    class Config:
        populate_by_name = True

class ContactIdRequest(BaseModel):
    """Defines the request body for the Contact ID API."""
    person_id: str = Field(..., alias="PersonId")

    class Config:
        populate_by_name = True

class AddressIdRequest(BaseModel):
    """Defines the request body for the Address ID API."""
    address_line_1: str = Field(..., alias="addressLine1")
    address_line_2: str = Field(..., alias="addressLine2")
    exact_match: Optional[str] = Field(None, alias="ExactMatch", description="Can be 'CurrentOwner' or 'CurrentResident'.")

    class Config:
        populate_by_name = True

class AddressAutoCompleteRequest(BaseModel):
    """Defines the request body for the Address AutoComplete API."""
    input_str: str = Field(..., alias="Input")

    class Config:
        populate_by_name = True

class IdVerificationRequest(BaseModel):
    """Defines the request body for the ID Verification API."""
    first_name: Optional[str] = Field(None, alias="FirstName")
    middle_name: Optional[str] = Field(None, alias="MiddleName")
    last_name: Optional[str] = Field(None, alias="LastName")
    dob: Optional[str] = Field(None, alias="Dob")
    age: Optional[int] = Field(None, alias="Age")
    address_line_1: Optional[str] = Field(None, alias="AddressLine1")
    address_line_2: Optional[str] = Field(None, alias="AddressLine2")
    phones: Optional[List[str]] = Field(None, alias="Phones")
    emails: Optional[List[str]] = Field(None, alias="Emails")
    ssn: Optional[str] = Field(None, alias="Ssn")

    class Config:
        populate_by_name = True

class CensusAddress(BaseModel):
    city: Optional[str] = Field(None, alias="City")
    county: Optional[str] = Field(None, alias="County")
    state: Optional[str] = Field(None, alias="State")
    zip_code: Optional[str] = Field(None, alias="ZipCode")

class CensusSearchRequest(BaseModel):
    """Defines the request body for the Census Search API."""
    first_name: Optional[str] = Field(None, alias="FirstName")
    middle_name: Optional[str] = Field(None, alias="MiddleName")
    last_name: Optional[str] = Field(None, alias="LastName")
    dob: Optional[str] = Field(None, alias="DOB")
    age: Optional[str] = Field(None, alias="Age")
    addresses: Optional[CensusAddress] = Field(None, alias="Addresses")
    relatives: Optional[List[Name]] = Field(None, alias="Relatives")
    census_decades: Optional[List[int]] = Field(None, alias="CensusDecades")

    class Config:
        populate_by_name = True

    @model_validator(mode='after')
    def validate_state_presence(self) -> 'CensusSearchRequest':
        addresses = self.addresses
        if addresses and (addresses.city or addresses.county) and not addresses.state:
            raise ValueError("State is required if City or County is provided.")
        return self

class DivorceSearchRequest(BaseModel):
    """Defines the request body for the Divorce Search API."""
    first_name: Optional[str] = Field(None, alias="FirstName")
    middle_name: Optional[str] = Field(None, alias="MiddleName")
    last_name: Optional[str] = Field(None, alias="LastName")
    name_suffix: Optional[str] = Field(None, alias="NameSuffix")
    maiden_name: Optional[str] = Field(None, alias="MaidenName")
    spouse_first_name: Optional[str] = Field(None, alias="SpouseFirstName")
    spouse_middle_name: Optional[str] = Field(None, alias="SpouseMiddleName")
    spouse_last_name: Optional[str] = Field(None, alias="SpouseLastName")
    spouse_name_suffix: Optional[str] = Field(None, alias="SpouseNameSuffix")
    marriage_date: Optional[str] = Field(None, alias="MarriageDate")
    divorce_date: Optional[str] = Field(None, alias="DivorceDate")
    city: Optional[str] = Field(None, alias="City")
    county: Optional[str] = Field(None, alias="County")
    state: Optional[str] = Field(None, alias="State")
    poseidon_ids: Optional[List[str]] = Field(None, alias="PosiedonIds")
    tahoe_id: Optional[str] = Field(None, alias="TahoeId")
    ssn: Optional[str] = Field(None, alias="SSN")
    
    class Config:
        populate_by_name = True

    @model_validator(mode='after')
    def validate_state_presence(self) -> 'DivorceSearchRequest':
        if self.city and not self.state:
            raise ValueError("State is required when City is provided.")
        return self

class LinkedInIdRequest(BaseModel):
    """Defines the request body for the LinkedIn ID API."""
    profile_url: str = Field(..., alias="profileURL")

    class Config:
        populate_by_name = True

class BusinessSearchRequest(BaseModel):
    """Defines the request body for the Business Search API."""
    business_name: Optional[str] = Field(None, alias="businessName")
    first_name: Optional[str] = Field(None, alias="firstName")
    middle_name: Optional[str] = Field(None, alias="middleName")
    last_name: Optional[str] = Field(None, alias="lastName")
    creditor_name: Optional[str] = Field(None, alias="creditorName")
    address_line_1: Optional[str] = Field(None, alias="addressLine1")
    address_line_2: Optional[str] = Field(None, alias="addressLine2")
    county: Optional[str] = Field(None, alias="county")
    poseidon_id: Optional[str] = Field(None, alias="poseidonId")
    tahoe_id: Optional[str] = Field(None, alias="tahoeId")
    tax_id: Optional[str] = Field(None, alias="taxId")
    ssn: Optional[str] = Field(None, alias="ssn")
    business_type: Optional[str] = Field(None, alias="businessType")
    page: Optional[int] = Field(None, alias="Page")
    results_per_page: Optional[int] = Field(None, alias="ResultsPerPage")

    class Config:
        populate_by_name = True

class PropertySearchV2Request(BaseModel):
    """Defines the request body for the Property Search V2 API."""
    address_line_1: Optional[str] = Field(None, alias="addressLine1")
    address_line_2: Optional[str] = Field(None, alias="addressLine2")
    unit: Optional[str] = Field(None, alias="unit")
    city: Optional[str] = Field(None, alias="city")
    state: Optional[str] = Field(None, alias="state")
    zip_code: Optional[str] = Field(None, alias="zipCode")
    county: Optional[str] = Field(None, alias="county")
    apn: Optional[str] = Field(None, alias="apn")
    fips: Optional[str] = Field(None, alias="fips")
    owner_first_name: Optional[str] = Field(None, alias="ownerFirstName")
    owner_last_name: Optional[str] = Field(None, alias="ownerLastName")
    owner_middle_name: Optional[str] = Field(None, alias="ownerMiddleName")
    owner_name_suffix: Optional[str] = Field(None, alias="ownerNameSuffix")
    owner_business_name: Optional[str] = Field(None, alias="ownerBusinessName")
    search_type: Optional[str] = Field(None, alias="searchType")
    page: Optional[int] = Field(None, alias="Page")
    results_per_page: Optional[int] = Field(None, alias="ResultsPerPage")

    class Config:
        """Pydantic config to allow population by alias."""
        populate_by_name = True

class DomainSearchRequest(BaseModel):
    """Defines the request body for the Domain Search API."""
    domain: Optional[str] = Field(None, alias="domain")
    page: Optional[int] = Field(None, alias="Page")
    results_per_page: Optional[int] = Field(None, alias="ResultsPerPage")

    class Config:
        """Pydantic config to allow population by alias."""
        populate_by_name = True

class WorkplaceSearchRequest(BaseModel):
    """Defines the request body for the Workplace Search API."""
    business_name: Optional[str] = Field(None, alias="businessName")
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    city: Optional[str] = Field(None, alias="city")
    state: Optional[str] = Field(None, alias="state")
    page: Optional[int] = Field(None, alias="Page")
    results_per_page: Optional[int] = Field(None, alias="ResultsPerPage")

    class Config:
        """Pydantic config to allow population by alias."""
        populate_by_name = True

class BusinessIDRequest(BaseModel):
    """Defines the request body for the Business ID API."""
    business_id: str = Field(..., alias="businessId")
    page: Optional[int] = Field(None, alias="Page")
    results_per_page: Optional[int] = Field(None, alias="ResultsPerPage")

    class Config:
        """Pydantic config to allow population by alias."""
        populate_by_name = True