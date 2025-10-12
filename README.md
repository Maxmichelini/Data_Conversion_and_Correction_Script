# Data Conversion and Correction Script

##  Purpose

This Python script automates the process of:
1. **Reading and converting** binary `.dat` files from STMicroelectronics sensors (accelerometers, microphones, magnetometers, etc.) into human-readable `.csv` format;  
2. **Applying correction data** from matching files (`.csv` or `.dat`) located in a correction folder;  
3. **Saving the corrected results** in an output folder.

In short:  
➡️ **Input:** raw `.dat` files  
➡️ **Output:** corrected `.csv` files in physical units (m/s², Pa, mG, etc.)

---

##  Folder Structure

Make sure your folders are organized as follows:

```
📂 Desktop
 ┣ 📂 Base files       # folder containing the original .dat files
 ┣ 📂 Corrector        # folder containing correction files (.csv or .dat)
 ┗ 📂 Results          # folder where corrected CSVs will be saved
```

---

##  How It Works

For each `.dat` file in the input folder, the script performs the following steps:

1. **File Parsing**
   - Each sensor type (`iis2dlpc_acc.dat`, `iis3dwb_acc.dat`, `iis2iclx_acc.dat`, `imp23absu_mic.dat`, `iis2mdc_mag.dat`),
    corresponding respectively to accelerometer_2D, accelerometer_3D, accelerometer_6Axies, microphone and magnetometer is handled with its specific:
     - Sampling rate;
     - Sensitivity coefficient ([g] or [Pa] per [LSB]);
     - Conversion from raw data to physical units ([m/s²], [Pa], [mG]);
     - Filterinf process that remove unrealistic or saturated values.

3. **Correction Application**
   - The script looks for a correction file in the `correction_folder`:
     - If it finds a `.csv` or `.dat` file, with the same name as the sensors that must be converted, it **subtracts** the correction vectors (X, Y, Z) from the original data.
     - It automatically recognizes equivalent column names (e.g. `accX`, `AccX`, `X_g`, etc.).
     - If no compatible correction is found, the original data are kept unchanged.

4. **Data Export**
   - The corrected data are saved as `.csv` in the `output_folder`, keeping the same filename as the original `.dat`.

---

##  Dependencies

The script only relies on standard Python libraries:

```bash
pip install numpy pandas
```

---

##  Execution

1. Edit the folder paths at the beginning of the script:

```python
input_folder = r"C:\Users\...\Base Files"
output_folder = r"C:\Users\...\Results"
correction_folder = r"C:\Users\...\Corrector"
```

2. Run the script from your terminal or IDE:

```bash
python Dat_Reader_Corrector.py
```

3. Check the output folder for the converted and corrected `.csv` files.

---

##  Supported Sensors

| File | Sensor | Sampling rate | Conversion | Final units |
|------|---------|----------------|-------------|--------------|
| `iis2dlpc_acc.dat` | Low-power accelerometer | 50 Hz | raw → g → m/s² | m/s² |
| `iis3dwb_acc.dat` | Wideband accelerometer | 26.8 kHz | raw → g → m/s² | m/s² |
| `iis2iclx_acc.dat` | Inclinometer accelerometer | 835 Hz | raw → g → m/s² | m/s² |
| `imp23absu_mic.dat` | Microphone | 16 kHz | raw → Pa | Pa |
| `iis2mdc_mag.dat` | Magnetometer | 101.91 Hz | raw → mG | mG |

---

##  Additional Notes

- `.dat` files are interpreted as 16-bit integer arrays (`int16`, `<i2`).
- Conversion coefficients follow **official STMicroelectronics sensitivity constants**.
- Unrealistic peaks or saturation values are automatically set to zero.
- If no correction file is found, a message is printed and the original data are used.

---

##  Example Output

Example of a converted accelerometer CSV:

```csv
time,accX,accY,accZ
0.0000,-0.0117,0.0089,9.8123
0.0200,-0.0118,0.0087,9.8130
...
```

---

##  Author

**Developed by:** *Alessandro Gianluca Cazzaniga, Massimiliano Michelini, Riccardo Sibilia*  
**Purpose:** Data conversion and correction for sensor-based motion or impact analysis.  
