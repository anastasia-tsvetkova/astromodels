import pytest

import astropy.units as u
import numpy as np

from astromodels.sources.point_source import PointSource
from astromodels.spectral_component import SpectralComponent
from astromodels.sky_direction import SkyDirection
from astromodels.functions.functions import Powerlaw

__author__ = 'giacomov'


def test_constructor():

    # RA, Dec and L,B of the same point in the sky

    ra, dec = (125.6, -75.3)
    l, b = (288.44190139183564, -20.717313145391525)

    # Init with RA, Dec

    point_source1 = PointSource('my_source',ra, dec, Powerlaw())

    assert point_source1.position.get_ra() == ra
    assert point_source1.position.get_dec() == dec

    assert abs(point_source1.position.get_l() - l) < 1e-7
    assert abs(point_source1.position.get_b() - b) < 1e-7

    assert point_source1.position.ra.value == ra
    assert point_source1.position.dec.value == dec

    # Init with l,b

    point_source2 = PointSource('my_source', l=l, b=b, spectral_shape=Powerlaw())

    assert point_source2.position.get_l() == l
    assert point_source2.position.get_b() == b

    assert abs(point_source2.position.get_ra() - ra) < 1e-7
    assert abs(point_source2.position.get_dec() - dec) < 1e-7

    assert point_source2.position.l.value == l
    assert point_source2.position.b.value == b

    # Multi-component

    po1 = Powerlaw()
    po2 = Powerlaw()

    c1 = SpectralComponent("component1", po1)
    c2 = SpectralComponent("component2", po2)

    point_source3 = PointSource("test_source", ra, dec, components=[c1, c2])

    assert np.all(point_source3.spectrum.component1([1,2,3]) == po1([1,2,3]))
    assert np.all(point_source3.spectrum.component2([1,2,3]) == po2([1,2,3]))

    with pytest.raises(AssertionError):

        # Illegal RA

        _ = PointSource("test",720.0, -15.0, components=[c1,c2])

    with pytest.raises(AssertionError):
        # Illegal Dec

        _ = PointSource("test", 120.0, 180.0, components=[c1, c2])

    with pytest.raises(AssertionError):
        # Illegal l

        _ = PointSource("test", l=-195, b=-15.0, components=[c1, c2])

    with pytest.raises(AssertionError):
        # Illegal b

        _ = PointSource("test", l=120.0, b=-180.0, components=[c1, c2])


def test_call():

    # Multi-component

    po1 = Powerlaw()
    po2 = Powerlaw()

    c1 = SpectralComponent("component1", po1)
    c2 = SpectralComponent("component2", po2)

    point_source = PointSource("test_source", 125.4, -22.3, components=[c1, c2])

    assert np.all(point_source.spectrum.component1([1, 2, 3]) == po1([1, 2, 3]))
    assert np.all(point_source.spectrum.component2([1, 2, 3]) == po2([1, 2, 3]))

    one = point_source.spectrum.component1([1, 2, 3])
    two = point_source.spectrum.component2([1, 2, 3])

    assert np.all( np.abs(one + two - point_source([1,2,3])) == 0 )