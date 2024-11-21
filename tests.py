import pytest
import pandas as pd
from analyzer import DICOMHandler, DynalogHandler

# Test for DICOMHandler class
@pytest.fixture
def dicom_handler():
    rtdose_path = "./data/rtdose.dcm"
    rtss_path = "./data/rtss.dcm"
    return DICOMHandler(rtdose_path, rtss_path)

def test_extract_dose_data(dicom_handler):
    # Verify the dose is being passed
    assert dicom_handler.dose_array is not None, "La dosis no debería ser None."
    assert dicom_handler.dose_origin is not None, "El origen de la dosis no debería ser None."
    assert dicom_handler.dose_spacing is not None, "El espaciamiento de la dosis no debería ser None."
    
def test_calculate_max_dose_per_structure(dicom_handler):
    # Verify that the calculations of contours and max dose works properly
    structures_data = dicom_handler.extract_structures_and_contours()
    structure_doses = dicom_handler.calculate_max_dose_per_structure(structures_data)
    
    # Verify that the dose is not none or less than 0
    for structure_name, dose in structure_doses:
        assert dose > 0, f"La dosis máxima para {structure_name} debería ser mayor que cero."

# Test for DynalogHandler class
@pytest.fixture
def dynalog_handler():
    file_a_path = "./data/DYNLOGA.042"
    file_b_path = "./data/DYNLOGB.042"
    return DynalogHandler(file_a_path, file_b_path)

def test_load_dynalog_data(dynalog_handler):
    # Verify that the datasets are loaded properly
    assert not dynalog_handler.data_a.empty, "Los datos AQA deberían ser cargados correctamente."
    assert not dynalog_handler.data_b.empty, "Los datos BQA deberían ser cargados correctamente."
    
def test_calculate_fluency_error(dynalog_handler):
    # Verify that the calculations for the fluencies and errors aren´t 0
    fluencia_planificada_avg, fluencia_real_avg, error = dynalog_handler.calculate_fluency()
    assert not fluencia_planificada_avg.isna().any(), "La fluencia planificada no debería tener valores NaN."
    assert not fluencia_real_avg.isna().any(), "La fluencia real no debería tener valores NaN."
    assert not error.isna().any(), "El error no debería tener valores NaN."

# Test for DynalogHandler's plot method with mocking plt.show()
def test_fluency_plot(dynalog_handler, mocker):
    fluencia_planificada_avg, fluencia_real_avg, error = dynalog_handler.calculate_fluency()
    mock_show = mocker.patch('matplotlib.pyplot.show')
    dynalog_handler.plot_fluency(fluencia_planificada_avg, fluencia_real_avg, error)    
    mock_show.assert_called_once()

#To run it locally
if __name__ == "__main__":
    pytest.main(["-v", "tests.py"])

    