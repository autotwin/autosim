#/bin/bash

# pytest --cov=center_of_geometry --cov-report=term-missing test_center_of_geometry.py -v
pytest --cov --cov-report=term-missing -v
