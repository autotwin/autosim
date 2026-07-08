from pipeline.postprocessing.strain import compute_mps, centroid_to_ijk

def test_uniaxial():
    result = compute_mps(0.05, 0, 0, 0, 0, 0)
    assert result == 0.05

def test_isotropic():
    result = compute_mps(0.03, 0.03, 0.03, 0, 0, 0)
    assert result == 0.03

def test_shear_is_halved():
    result = compute_mps(0, 0, 0, 0.10, 0, 0)                                                      
    assert result == 0.05  

def test_centroid_to_ijk_no_translation():
    coords = centroid_to_ijk(1.5, 2.5, 0.5, 0, 0, 0)
    assert coords == (0, 2, 1)

def test_centroid_to_ijk_with_translation():
    coords = centroid_to_ijk(11.5, 22.5, 5.5, 10, 20, 5)
    assert coords == (0, 2, 1)