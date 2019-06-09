'''
DO NOT EDIT THIS FILE

This file is generated from the CDP definitions. If you need to make changes,
edit the generator and regenerate all of the modules.

Domain: security
Experimental: False
'''

from dataclasses import dataclass, field
import typing


class CertificateId(int):
    '''
    An internal certificate ID value.
    '''
    @classmethod
    def from_response(cls, response):
        return cls(response)

    def __repr__(self):
        return 'CertificateId({})'.format(int.__repr__(self))



class MixedContentType:
    '''
    A description of mixed content (HTTP resources on HTTPS pages), as defined by
    https://www.w3.org/TR/mixed-content/#categories
    '''
    BLOCKABLE = "blockable"
    OPTIONALLY_BLOCKABLE = "optionally-blockable"
    NONE = "none"


class SecurityState:
    '''
    The security level of a page or resource.
    '''
    UNKNOWN = "unknown"
    NEUTRAL = "neutral"
    INSECURE = "insecure"
    SECURE = "secure"
    INFO = "info"


class CertificateErrorAction:
    '''
    The action to take when a certificate error occurs. continue will continue processing the
    request and cancel will cancel the request.
    '''
    CONTINUE = "continue"
    CANCEL = "cancel"


@dataclass
class SecurityStateExplanation:
    '''
    An explanation of an factor contributing to the security state.
    '''
    #: Security state representing the severity of the factor being explained.
    security_state: SecurityState

    #: Title describing the type of factor.
    title: str

    #: Short phrase describing the type of factor.
    summary: str

    #: Full text explanation of the factor.
    description: str

    #: The type of mixed content described by the explanation.
    mixed_content_type: MixedContentType

    #: Page certificate.
    certificate: typing.List

    #: Recommendations to fix any issues.
    recommendations: typing.List

    @classmethod
    def from_response(cls, response):
        return cls(
            security_state=SecurityState.from_response(response.get('securityState')),
            title=str(response.get('title')),
            summary=str(response.get('summary')),
            description=str(response.get('description')),
            mixed_content_type=MixedContentType.from_response(response.get('mixedContentType')),
            certificate=[str(i) for i in response.get('certificate')],
            recommendations=[str(i) for i in response.get('recommendations')],
        )


@dataclass
class InsecureContentStatus:
    '''
    Information about insecure content on the page.
    '''
    #: Always false.
    ran_mixed_content: bool

    #: Always false.
    displayed_mixed_content: bool

    #: Always false.
    contained_mixed_form: bool

    #: Always false.
    ran_content_with_cert_errors: bool

    #: Always false.
    displayed_content_with_cert_errors: bool

    #: Always set to unknown.
    ran_insecure_content_style: SecurityState

    #: Always set to unknown.
    displayed_insecure_content_style: SecurityState

    @classmethod
    def from_response(cls, response):
        return cls(
            ran_mixed_content=bool(response.get('ranMixedContent')),
            displayed_mixed_content=bool(response.get('displayedMixedContent')),
            contained_mixed_form=bool(response.get('containedMixedForm')),
            ran_content_with_cert_errors=bool(response.get('ranContentWithCertErrors')),
            displayed_content_with_cert_errors=bool(response.get('displayedContentWithCertErrors')),
            ran_insecure_content_style=SecurityState.from_response(response.get('ranInsecureContentStyle')),
            displayed_insecure_content_style=SecurityState.from_response(response.get('displayedInsecureContentStyle')),
        )
