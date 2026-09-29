from __future__ import annotations

from pytest_archon import archrule


def test_domain_isolation():
    (
        archrule("domain-isolation", comment="domain must not know outer layers")
        .match("arch_sample.domain*")
        .should_not_import("arch_sample.infrastructure*")
        .should_not_import("arch_sample.web*")
        .check("arch_sample")
    )


def test_domain_does_not_import_any_architecture_sibling():
    (
        archrule("domain-purity", comment="domain imports only its own package")
        .match("arch_sample.domain*")
        .should_not_import("arch_sample.services*")
        .should_not_import("arch_sample.infrastructure*")
        .should_not_import("arch_sample.web*")
        .check("arch_sample")
    )
