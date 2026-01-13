# Muster

Muster is a basic FastAPI application whose purpose is to provide an API target for automated checks of a [Phalanx](https://phalanx.lsst.io/) environment and to verify aspects of the environment only visible from a protected service.
This most notably includes verification of [Gafaelfawr](https://gafaelfawr.lsst.io/) ingress handling, authorization, token delegation, and service-facing API interactions.
It also tests [Repertoire](https://repertoire.lsst.io/) service discovery.

While Muster can be used via a web browser, it is intended for use with [mobu](https://mobu.lsst.io/).

Muster is developed with [FastAPI](https://fastapi.tiangolo.com) and [Safir](https://safir.lsst.io).
