# Libraries
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import pydicom

# Class to handle DICOM files 
class DICOMHandler:
    def __init__(self, rtdose_path, rtss_path):
        self.rtdose = pydicom.dcmread(rtdose_path)
        self.rtss = pydicom.dcmread(rtss_path)
        self.dose_array, self.dose_origin, self.dose_spacing = self.extract_dose_data()
    #Extract the dose to obtain the max dose
    def extract_dose_data(self):
        dose_grid_scaling = (
            self.rtdose.DoseGridScaling if hasattr(self.rtdose, "DoseGridScaling") else 1.0
        )
        dose_array = self.rtdose.pixel_array * dose_grid_scaling  # Escalate the dose
        dose_origin = np.array(self.rtdose.ImagePositionPatient)  # Origin position
        dose_spacing = list(self.rtdose.PixelSpacing) + [
            self.rtdose.GridFrameOffsetVector[1] - self.rtdose.GridFrameOffsetVector[0]
        ]
        dose_spacing = np.array(dose_spacing)  # Convert to numpy
        return dose_array, dose_origin, dose_spacing
    #Extract structure data
    def extract_rtss_data(self):
        data = []
        for observation in self.rtss.RTROIObservationsSequence:
            roi_data = {
                "Observation Number": observation.ObservationNumber,
                "Referenced ROI Number": observation.ReferencedROINumber,
                "ROI Observation Label": observation.ROIObservationLabel,
                "RT ROI Interpreted Type": observation.RTROIInterpretedType,
                "ROI Interpreter": getattr(observation, "ROIInterpreter", "N/A"),
                "Physical Properties": [],
            }
            if hasattr(observation, "ROIPhysicalPropertiesSequence"):
                for prop in observation.ROIPhysicalPropertiesSequence:
                    roi_data["Physical Properties"].append(
                        {
                            "ROI Physical Property": prop.ROIPhysicalProperty,
                            "ROI Physical Property Value": prop.ROIPhysicalPropertyValue,
                        }
                    )
            data.append(roi_data)
        return data
    #Function to obtain the structure names and the contour points
    def extract_structures_and_contours(self):
        structures_data = []
        for roi_observation in self.rtss.RTROIObservationsSequence:
            structure_name = roi_observation.ROIObservationLabel
            contours = []
            for roi_contour in self.rtss.ROIContourSequence:
                if roi_contour.ReferencedROINumber == roi_observation.ReferencedROINumber:
                    if hasattr(roi_contour, "ContourSequence"):
                        for contour in roi_contour.ContourSequence:
                            contours.append(contour.ContourData)
            if contours:
                structures_data.append({"name": structure_name, "contours": contours})
        return structures_data
    #Extract the max dose
    def extract_rtdose_data(self):
        dose_data = self.rtdose.pixel_array * (
            self.rtdose.DoseGridScaling if hasattr(self.rtdose, "DoseGridScaling") else 1.0
        )
        return np.max(dose_data)
    # Extract the contour points for the doses of the structures
    def convert_to_dose_indices(self, contour_points):
        indices = []
        for point in contour_points:
            coord = np.array(point)
            index = np.round((coord - self.dose_origin) / self.dose_spacing).astype(int)
            indices.append(index)
        return indices
    #Calculate the max dose per structure
    def calculate_max_dose_per_structure(self, structures_data):
        max_doses = []
        for structure in structures_data:
            structure_name = structure["name"]
            contours = structure["contours"]
            max_dose = 0
            for contour in contours:
                contour_points = np.array(contour).reshape(-1, 3)  # Convert to x,y,z
                dose_indices = self.convert_to_dose_indices(contour_points)
                for x, y, z in dose_indices:
                    if 0 <= z < self.dose_array.shape[0] and 0 <= y < self.dose_array.shape[1] and 0 <= x < self.dose_array.shape[2]:
                        dose_value = self.dose_array[z, y, x]
                        max_dose = max(max_dose, dose_value)
            max_doses.append((structure_name, max_dose))
        return max_doses
    #Plot the structures
    def plot_structures(self, structure_names, doses):
        sns.set(style="whitegrid")
        plt.figure(figsize=(12, 8))
        sns.barplot(x=structure_names, y=doses, hue=structure_names, legend=False, palette="Blues_d")
        plt.xlabel("Nombre de las estructuras")
        plt.ylabel("Dosis máxima (Gy)")
        plt.title("Dosis máxima por estructura en el tratamiento")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.show()


# Class to handle Dynalog files
class DynalogHandler:
    def __init__(self, file_a_path, file_b_path):
        self.file_a_path = file_a_path
        self.file_b_path = file_b_path
        self.data_a = self.load_dynalog_data(self.file_a_path)
        self.data_b = self.load_dynalog_data(self.file_b_path)
    #Load and Parse the data
    def load_dynalog_data(self, file_path):
        header_data = []
        header_datab = []
        data_rows = []
        data_rowsb = []

        with open(file_path, "r") as file:
            lines = file.readlines()

        header_data = lines[1].strip().split(",")
        for line in lines[2:]:
            line_data = line.strip().replace(" ", "").split(",")
            data_rows.append(line_data)

        df_data = pd.DataFrame(data_rows)
        #We won´t be using the header, only the data
        #df_header = pd.DataFrame([header_data], columns=["Apellido1", "Apellido2", "Nombre", "ID"])

        return df_data
    #Extract the fluencies and calculate the error
    def calculate_fluency(self):
        fluencia_planificada_numeric = self.data_a.iloc[:, 1:].apply(pd.to_numeric, errors="coerce") #To clean the identifier
        fluencia_real_numeric = self.data_b.iloc[:, 1:].apply(pd.to_numeric, errors="coerce") #To clean the identifier
        fluencia_planificada_numeric = fluencia_planificada_numeric.fillna(0)
        fluencia_real_numeric = fluencia_real_numeric.fillna(0)
        fluencia_planificada_avg = fluencia_planificada_numeric.mean(axis=0)
        fluencia_real_avg = fluencia_real_numeric.mean(axis=0)
        error = fluencia_real_avg - fluencia_planificada_avg
        return fluencia_planificada_avg, fluencia_real_avg, error
    #Plot the fluencies
    def plot_fluency(self, fluencia_planificada_avg, fluencia_real_avg, error):
        plt.figure(figsize=(12, 6))
        plt.plot(fluencia_planificada_avg.index, fluencia_planificada_avg, label="Fluencia Planificada", marker="o")
        plt.plot(fluencia_real_avg.index, fluencia_real_avg, label="Fluencia Real", marker="x")
        plt.plot(error.index, error, label="Error", marker="s", linestyle="--", alpha=0.5)
        plt.title("Comparación de Fluencias")
        plt.xlabel("Posición de la Lámina")
        plt.ylabel("Fluencia Promedio")
        plt.legend()
        plt.grid(True)
        plt.show()


# Example usage:

# Load the data
rtdose_path = "./data/rtdose.dcm"
rtss_path = "./data/rtss.dcm"
file_a_path = "./data/DYNLOGA.042"
file_b_path = "./data/DYNLOGB.042"

# Iniciate the dicom class and functions
dicom_handler = DICOMHandler(rtdose_path, rtss_path)

#Get structure names and other data, aswell as the max dose
struct_data = dicom_handler.extract_rtss_data()
maximum_dose = dicom_handler.extract_rtdose_data()
print("Datos estructuras:", struct_data)
print(f"Dosis máxima {maximum_dose} Gy")
structures_data = dicom_handler.extract_structures_and_contours()
structure_doses = dicom_handler.calculate_max_dose_per_structure(structures_data)

#Define the structure names and doses for each one.
structure_names = [s[0] for s in structure_doses]
doses = [s[1] for s in structure_doses]

#Plot the structure names and doses.
dicom_handler.plot_structures(structure_names, doses)

#Iniciate the dynalog class and fuctions.
dynalog_handler = DynalogHandler(file_a_path, file_b_path)

#Calculate the fluencies.
fluencia_planificada_avg, fluencia_real_avg, error = dynalog_handler.calculate_fluency()

#Plot the fluencies.
dynalog_handler.plot_fluency(fluencia_planificada_avg, fluencia_real_avg, error)
