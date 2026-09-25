"""MARCO proof of concept: a locality-preserving coordinate for agent situations.

    from marco import primer, locus, world, generator

Public entry points:
    primer.expand()      seed -> Frame (the shared geometry)
    locus.Encoder(frame) observations -> Locus
    world.World          the fake world an agent is embedded in
    generator.Generator  the seed that asks its own questions
"""

from . import assignment, generator, locus, primer, world  # noqa: F401

__version__ = "0.1.0"
