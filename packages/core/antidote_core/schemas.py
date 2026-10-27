"""Schemas for Antidote: label fields in, cited management card and medico-legal record out."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Cite(BaseModel):
    sid: str = Field(default="", description="The [S#] id of the numbered guideline sentence, for example S12.")
    doc: str = Field(default="", description="doc_id of the page holding that sentence")
    page: int = Field(default=0, description="page number of that sentence")
    quote: str = Field(default="", description="Leave empty when sid is given; code copies the exact sentence.")


class LabelRead(BaseModel):
    """Structured fields read from a pesticide container label (vision describes; nothing clinical)."""

    product_name: str | None = None
    active_ingredients: list[dict[str, str]] = Field(default_factory=list, description="[{name, percent}] as printed")
    formulation_code: str | None = None
    registration_number: str | None = None
    batch: str | None = None
    expiry: str | None = None
    manufacturer: str | None = None
    triangle_colour: str | None = None
    signal_word: str | None = None
    antidote_statement_text: str | None = Field(default=None, description="The antidote statement exactly as printed on the label, if any")
    visible_text: list[str] = Field(default_factory=list)
    languages_seen: list[str] = Field(default_factory=list)
    confidence: float = 0.0


class CardSentence(BaseModel):
    kind: Literal["quote", "explanation"] = Field(description="quote = a guideline sentence chosen by its [S#] id in cite.sid; explanation = connective plain sentence with NO drug names and NO numbers")
    text: str = Field(default="", description="For quote: leave empty, code fills the exact guideline sentence from cite.sid. For explanation: your plain sentence.")
    cite: Cite | None = None


class ManagementCard(BaseModel):
    """Bedside card for a trained clinician. Every clinical statement is a verbatim quote from a cited guideline page."""

    identity: list[CardSentence] = Field(description="What the chemical is and its group; explanation sentences allowed")
    expect: list[CardSentence] = Field(description="Toxidrome: what the poisoning looks like and when; quotes only")
    manage: list[CardSentence] = Field(description="Management and antidote guidance; quotes only; include the exact page for any dose text")
    cautions: list[CardSentence] = Field(description="Cautions and contraindications; quotes only")
    no_antidote: bool = Field(description="True if the cited guidance states there is no specific antidote for this group")


class AuditVerdict(BaseModel):
    index: int
    section: Literal["identity", "expect", "manage", "cautions"]
    verdict: Literal["approve", "reject"]
    reason: str


class AuditReport(BaseModel):
    """Independent audit of the card against the complete national module and the ISCCM statement."""

    verdicts: list[AuditVerdict]
    overall: Literal["approve", "approve_with_rejections", "reject"]
    notes: str = ""


class MLCRecord(BaseModel):
    """Medico-legal case register row (NHSRC fields). Patient identifiers are entered by staff, never inferred."""

    datetime: str
    brought_by: str | None = None
    alleged_history: str
    substance_product: str | None = None
    substance_active_ingredient: str | None = None
    registration_number: str | None = None
    who_class: str | None = None
    chemical_group: str | None = None
    banned_or_restricted: bool = False
    route: str | None = None
    time_since_exposure: str | None = None
    examination_findings: str = ""
    treatment_given: list[str] = Field(default_factory=list)
    referral: str | None = None
    doctor: str | None = None
    poison_centre_called: bool = False
    ai_trace_id: str
    label_photo_attached: bool = False
    locality: str | None = Field(default=None, description="Block or village, never a home address; used for cluster detection")
