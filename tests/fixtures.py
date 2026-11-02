"""Synthetic EUDAMED DTX message builders.

They reproduce the *shapes* the generator emits (element order, indentation, namespaces) using
obviously fake data. Used by the tests and to produce the files in ``examples/messages``.
"""
from __future__ import annotations

T = "\t"

NS_URI = {
    "m": "https://ec.europa.eu/tools/eudamed/dtx/servicemodel/Message/v1",
    "s": "https://ec.europa.eu/tools/eudamed/dtx/servicemodel/Service/v1",
    "device": "https://ec.europa.eu/tools/eudamed/dtx/datamodel/Entity/Device/v1",
    "basicudi": "https://ec.europa.eu/tools/eudamed/dtx/datamodel/Entity/Device/BasicUDI/v1",
    "udidi": "https://ec.europa.eu/tools/eudamed/dtx/datamodel/Entity/UDIDI/v1",
    "commondi": "https://ec.europa.eu/tools/eudamed/dtx/datamodel/Entity/Device/CommonDevice/v1",
    "lsn": "https://ec.europa.eu/tools/eudamed/dtx/datamodel/Entity/Common/LanguageSpecific/v1",
    "marketinfo": "https://ec.europa.eu/tools/eudamed/dtx/datamodel/Entity/MktInfo/MarketInfo/v1",
    "links": "https://ec.europa.eu/tools/eudamed/dtx/datamodel/Entity/Links/v1",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}
# DEVICE.POST envelope declares every prefix; the UDI_DI.POST envelope only the ones it needs.
PREFIXES_DEVICE = ["m", "s", "device", "basicudi", "udidi", "commondi", "lsn", "marketinfo", "links", "xsi"]
PREFIXES_UDIDI = ["m", "s", "device", "udidi", "commondi", "lsn", "marketinfo", "xsi"]

SRN = "DE-MF-000000000"            # obviously fake manufacturer SRN
TOKEN_PLACEHOLDER = "&lt;!-- TOKEN --&gt;"   # what the generator writes when no token was entered


def _ns(prefixes):
    return "".join(f' xmlns:{p}="{NS_URI[p]}"' for p in prefixes)


def lang_block(tag, en, indent=4, lang="EN"):
    t = T * indent
    return (f"{t}<{tag}>\n{t}{T}<lsn:name>\n{t}{T}{T}<lsn:language>{lang}</lsn:language>\n"
            f"{t}{T}{T}<lsn:textValue>{en}</lsn:textValue>\n{t}{T}</lsn:name>\n{t}</{tag}>\n")


def comment_block(text, lang, indent=6):
    t = T * indent
    return (f"{t}<commondi:comments>\n{t}{T}<lsn:name>\n{t}{T}{T}<lsn:language>{lang}</lsn:language>\n"
            f"{t}{T}{T}<lsn:textValue>{text}</lsn:textValue>\n{t}{T}</lsn:name>\n{t}</commondi:comments>\n")


def storage_block(low="10", high="25", lang="ANY", code="SHC008"):
    return (f"{T*4}<udidi:storageHandlingConditions>\n{T*5}<commondi:condition>\n"
            + comment_block(f"Store at {low}-{high} °C", lang)
            + f"{T*6}<commondi:storageHandlingConditionValue>{code}</commondi:storageHandlingConditionValue>\n"
            f"{T*5}</commondi:condition>\n{T*4}</udidi:storageHandlingConditions>\n")


def warnings_block(texts=("Example warning text.",), lang="EN", code="CW999"):
    x = f"{T*4}<udidi:criticalWarnings>\n"
    for txt in texts:
        x += (f"{T*5}<commondi:warning>\n" + comment_block(txt, lang)
              + f"{T*6}<commondi:warningValue>{code}</commondi:warningValue>\n{T*5}</commondi:warning>\n")
    return x + f"{T*4}</udidi:criticalWarnings>\n"


def market_block(countries=("DE", "AT"), original="DE", start="2026-01-01"):
    x = f"{T*4}<udidi:marketInfos>\n"
    for c in countries:
        x += (f"{T*5}<marketinfo:marketInfo>\n{T*6}<marketinfo:country>{c}</marketinfo:country>\n"
              f"{T*6}<marketinfo:originalPlacedOnTheMarket>{'true' if c == original else 'false'}"
              f"</marketinfo:originalPlacedOnTheMarket>\n{T*6}<marketinfo:startDate>{start}</marketinfo:startDate>\n"
              f"{T*5}</marketinfo:marketInfo>\n")
    return x + f"{T*4}</udidi:marketInfos>\n"


def basic_udi_xml(budi, issuing="HIBCC", srn=SRN, model="Example product family"):
    return (f'{T*3}<device:MDRBasicUDI xsi:type="device:MDRBasicUDIType">\n'
            f"{T*4}<basicudi:riskClass>CLASS_IIA</basicudi:riskClass>\n"
            f"{T*4}<basicudi:model>{model}</basicudi:model>\n"
            f"{T*4}<basicudi:identifier>\n{T*5}<commondi:DICode>{budi}</commondi:DICode>\n"
            f"{T*5}<commondi:issuingEntityCode>{issuing}</commondi:issuingEntityCode>\n{T*4}</basicudi:identifier>\n"
            f"{T*4}<basicudi:animalTissuesCells>false</basicudi:animalTissuesCells>\n"
            f"{T*4}<basicudi:humanTissuesCells>false</basicudi:humanTissuesCells>\n"
            f"{T*4}<basicudi:MFActorCode>{srn}</basicudi:MFActorCode>\n"
            f"{T*4}<basicudi:deviceCertificateLinks>\n{T*5}<links:deviceCertificateLink>\n"
            f"{T*6}<links:certificateNumber>CERT-EXAMPLE-0001</links:certificateNumber>\n"
            f"{T*6}<links:expiryDate>2030-12-31</links:expiryDate>\n"
            f"{T*6}<links:NBActorCode>0000</links:NBActorCode>\n"
            f"{T*6}<links:certificateType>MDR_QUALITY_MANAGEMENT_SYSTEM</links:certificateType>\n"
            f"{T*5}</links:deviceCertificateLink>\n{T*4}</basicudi:deviceCertificateLinks>\n"
            f"{T*4}<basicudi:humanProductCheck>false</basicudi:humanProductCheck>\n"
            f"{T*4}<basicudi:medicinalProductCheck>false</basicudi:medicinalProductCheck>\n"
            f"{T*4}<basicudi:type>DEVICE</basicudi:type>\n"
            f"{T*4}<commondi:active>false</commondi:active>\n"
            f"{T*4}<commondi:administeringMedicine>false</commondi:administeringMedicine>\n"
            f"{T*4}<commondi:implantable>false</commondi:implantable>\n"
            f"{T*4}<commondi:measuringFunction>false</commondi:measuringFunction>\n"
            f"{T*4}<commondi:reusable>false</commondi:reusable>\n"
            f"{T*3}</device:MDRBasicUDI>\n")


def udidi_content(udi, budi, issuing="HIBCC", *, storage="", warnings="", markets="", ref="REF-0001"):
    return (f"{T*4}<udidi:identifier>\n{T*5}<commondi:DICode>{udi}</commondi:DICode>\n"
            f"{T*5}<commondi:issuingEntityCode>{issuing}</commondi:issuingEntityCode>\n{T*4}</udidi:identifier>\n"
            f"{T*4}<udidi:status>\n{T*5}<commondi:code>ON_THE_MARKET</commondi:code>\n{T*4}</udidi:status>\n"
            f"{T*4}<udidi:basicUDIIdentifier>\n{T*5}<commondi:DICode>{budi}</commondi:DICode>\n"
            f"{T*5}<commondi:issuingEntityCode>{issuing}</commondi:issuingEntityCode>\n{T*4}</udidi:basicUDIIdentifier>\n"
            f"{T*4}<udidi:MDNCodes>Q010699</udidi:MDNCodes>\n"
            f"{T*4}<udidi:productionIdentifier>BATCH_NUMBER</udidi:productionIdentifier>\n"
            f"{T*4}<udidi:referenceNumber>{ref}</udidi:referenceNumber>\n"
            f"{T*4}<udidi:sterile>false</udidi:sterile>\n"
            f"{T*4}<udidi:sterilization>false</udidi:sterilization>\n"
            + lang_block("udidi:tradeNames", f"Example trade name {ref}")
            + storage + warnings
            + f"{T*4}<udidi:numberOfReuses>-1</udidi:numberOfReuses>\n"
            + markets
            + f"{T*4}<udidi:baseQuantity>1</udidi:baseQuantity>\n"
            f"{T*4}<udidi:latex>false</udidi:latex>\n"
            f"{T*4}<udidi:reprocessed>false</udidi:reprocessed>\n")


def device_entity(udi, budi, **kw):
    """One device:Device = Basic UDI + UDI-DI (DEVICE.POST)."""
    return (f'{T*2}<device:Device xsi:type="device:MDRDeviceType">\n' + basic_udi_xml(budi)
            + f'{T*3}<device:MDRUDIDIData xsi:type="device:MDRUDIDIDataType">\n'
            + udidi_content(udi, budi, **kw) + f"{T*3}</device:MDRUDIDIData>\n{T*2}</device:Device>\n")


def udidi_entity(udi, budi, **kw):
    """One standalone device:UDIDIData (UDI_DI.POST)."""
    return (f'{T*2}<device:UDIDIData xsi:type="udidi:MDRUDIDIDataType">\n'
            + udidi_content(udi, budi, **kw) + f"{T*2}</device:UDIDIData>\n")


def push(payload, service=("DEVICE", "POST"), *, version="3.0.30", token=TOKEN_PLACEHOLDER,
         sender_service=None, narrow=False):
    sid, sop = service
    ssid, ssop = sender_service or service
    ns = _ns(PREFIXES_UDIDI if narrow else PREFIXES_DEVICE)
    return (f'<?xml version="1.0" encoding="utf-8"?>\n<m:Push{ns} version="{version}">\n'
            f"{T}<m:conversationID>00000000-0000-4000-8000-000000000001</m:conversationID>\n"
            f"{T}<m:correlationID>00000000-0000-4000-8000-000000000002</m:correlationID>\n"
            f"{T}<m:creationDateTime>2026-01-01T00:00:00Z</m:creationDateTime>\n"
            f"{T}<m:messageID>00000000-0000-4000-8000-000000000003</m:messageID>\n"
            f"{T}<m:recipient>\n{T*2}<m:node>\n{T*3}<s:nodeActorCode>EUDAMED</s:nodeActorCode>\n"
            f"{T*3}<s:nodeID>eDelivery:EUDAMED</s:nodeID>\n{T*2}</m:node>\n{T*2}<m:service>\n"
            f"{T*3}<s:serviceAccessToken>{token}</s:serviceAccessToken>\n{T*3}<s:serviceID>{sid}</s:serviceID>\n"
            f"{T*3}<s:serviceOperation>{sop}</s:serviceOperation>\n{T*2}</m:service>\n{T}</m:recipient>\n"
            f"{T}<m:payload>\n{payload}{T}</m:payload>\n"
            f"{T}<m:sender>\n{T*2}<m:node>\n{T*3}<s:nodeActorCode>{SRN}</s:nodeActorCode>\n"
            f"{T*3}<s:nodeID>eDelivery:{SRN}</s:nodeID>\n{T*2}</m:node>\n{T*2}<m:service>\n"
            f"{T*3}<s:serviceID>{ssid}</s:serviceID>\n{T*3}<s:serviceOperation>{ssop}</s:serviceOperation>\n"
            f"{T*2}</m:service>\n{T}</m:sender>\n</m:Push>\n")


def rich_kwargs():
    """Storage + warning + market data in the form the generator writes it (valid language rules)."""
    return dict(storage=storage_block(), warnings=warnings_block(), markets=market_block())


def example_device_post():
    """Two NEW Basic UDI families, one UDI-DI each -> what folder 1_DEVICE_POST/ contains."""
    return push(device_entity("+EXAMPLE000011X", "++EXAMPLE00001AA", ref="REF-0001", **rich_kwargs())
                + device_entity("+EXAMPLE000021Y", "++EXAMPLE00002BB", ref="REF-0002", **rich_kwargs()))


def example_udi_di_post():
    """Further UDI-DIs of the first family -> what folder 2_UDI_DI_POST/ contains."""
    return push(udidi_entity("+EXAMPLE000012Y", "++EXAMPLE00001AA", ref="REF-0003", **rich_kwargs())
                + udidi_entity("+EXAMPLE000013Z", "++EXAMPLE00001AA", ref="REF-0004", **rich_kwargs())
                + udidi_entity("+EXAMPLE000022Z", "++EXAMPLE00002BB", ref="REF-0005", **rich_kwargs()),
                service=("UDI_DI", "POST"), narrow=True)
