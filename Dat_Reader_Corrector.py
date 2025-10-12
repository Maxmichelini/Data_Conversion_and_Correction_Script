import numpy as np
import pandas as pd
import os

# Input, output, and correction folders
input_folder = r"C:\Users\Desktop\Base files"
output_folder = r"C:\Users\Desktop\Results"
correction_folder = r"C:\Users\Desktop\Corrector"
os.makedirs(output_folder, exist_ok=True)

# Common parameters for accelerometer calibration
sensitivity_g_default = 0.0004889999905824661  # LSB -> g
g_to_ms2 = 9.80665  # g -> m/s²

def parse_dat(file_path, filename):
    """Returns a DataFrame from the .dat file according to its specific format."""
    
    # --- Case 1: iis2dlpc accelerometer ---
    if filename == "iis2dlpc_acc.dat":
        sampling_rate = 50
        sensitivity_g = sensitivity_g_default

        # Read raw binary data (16-bit signed integers)
        raw_data = np.fromfile(file_path, dtype='<i2')
        n_samples = len(raw_data) // 3
        data = raw_data[:n_samples * 3].reshape(-1, 3)

        # Separate X, Y, Z components
        X_raw, Y_raw, Z_raw = data[:, 0], data[:, 1], data[:, 2]
        time = np.arange(n_samples) / sampling_rate

        # Convert: raw -> g -> m/s²
        X_acc = X_raw * sensitivity_g * g_to_ms2
        Y_acc = Y_raw * sensitivity_g * g_to_ms2
        Z_acc = Z_raw * sensitivity_g * g_to_ms2

        # Remove unrealistic acceleration spikes
        max_expected_acc = 18 * g_to_ms2
        X_acc[np.abs(X_acc) > max_expected_acc] = 0
        Y_acc[np.abs(Y_acc) > max_expected_acc] = 0
        Z_acc[np.abs(Z_acc) > max_expected_acc] = 0

        # Build final DataFrame
        df = pd.DataFrame({
            "time": time,
            "accX": X_acc,  
            "accY": Y_acc,
            "accZ": Z_acc
        })
        print("Number of samples:", n_samples)
        print("Estimated duration:", n_samples / sampling_rate)

    # --- Case 2: iis3dwb accelerometer (high frequency) ---
    elif filename == "iis3dwb_acc.dat":
        sampling_rate = 26800
        sensitivity_g = sensitivity_g_default

        raw_data = np.fromfile(file_path, dtype='<i2')
        n_samples = len(raw_data) // 3
        data = raw_data[:n_samples * 3].reshape(-1, 3)

        X_raw, Y_raw, Z_raw = data[:, 0], data[:, 1], data[:, 2]
        time = np.arange(n_samples) / sampling_rate

        # Conversion to m/s²
        X_acc = X_raw * sensitivity_g * g_to_ms2
        Y_acc = Y_raw * sensitivity_g * g_to_ms2
        Z_acc = Z_raw * sensitivity_g * g_to_ms2

        # Saturation threshold
        max_expected_acc = 4.1 * g_to_ms2
        X_acc[np.abs(X_acc) > max_expected_acc] = 0
        Y_acc[np.abs(Y_acc) > max_expected_acc] = 0
        Z_acc[np.abs(Z_acc) > max_expected_acc] = 0

        df = pd.DataFrame({
            "time": time,
            "X_acc": X_acc,
            "Y_acc": Y_acc,
            "Z_acc": Z_acc
        })

    # --- Case 3: iis2iclx accelerometer (2-axis) ---
    elif filename == "iis2iclx_acc.dat":
        sampling_rate = 835
        sensitivity_g = 0.0001218

        raw_data = np.fromfile(file_path, dtype='<i2')
        n_samples = len(raw_data) // 2
        data = raw_data[:n_samples * 2].reshape(-1, 2)

        X_raw, Y_raw = data[:, 0], data[:, 1]
        time = np.arange(n_samples) / sampling_rate

        X_acc = X_raw * sensitivity_g * g_to_ms2
        Y_acc = Y_raw * sensitivity_g * g_to_ms2

        max_expected_acc = 1.1 * g_to_ms2
        X_acc[np.abs(X_acc) > max_expected_acc] = 0
        Y_acc[np.abs(Y_acc) > max_expected_acc] = 0

        df = pd.DataFrame({
            "time": time,
            "X_acc": X_acc,
            "Y_acc": Y_acc
        })

    # --- Case 4: IMP23ABSU microphone ---
    elif filename == "imp23absu_mic.dat":
        sampling_rate = 16000  
        sensitivity_pa = 3.0517578125e-05  # Pa per LSB

        raw_data = np.fromfile(file_path, dtype='<i2')
        pressure_pa = raw_data * sensitivity_pa
        time = np.arange(len(pressure_pa)) / sampling_rate

        df = pd.DataFrame({
            "time": time,
            "pressure_Pa": pressure_pa
        })

    # --- Case 5: IIS2MDC magnetometer ---
    elif filename == "iis2mdc_mag.dat":
        sampling_rate = 101.91  
        sensitivity_g = 0.0015  

        raw_data = np.fromfile(file_path, dtype='<i2')
        n_samples = len(raw_data) // 3
        data = raw_data[:n_samples * 3].reshape(-1, 3)

        X_raw, Y_raw, Z_raw = data[:, 0], data[:, 1], data[:, 2]
        time = np.arange(n_samples) / sampling_rate

        # Convert to milliGauss (mG)
        X_mG = X_raw * sensitivity_g
        Y_mG = Y_raw * sensitivity_g
        Z_mG = Z_raw * sensitivity_g

        # Remove outliers
        max_expected_mG = 100
        X_mG[np.abs(X_mG) > max_expected_mG] = 0
        Y_mG[np.abs(Y_mG) > max_expected_mG] = 0
        Z_mG[np.abs(Z_mG) > max_expected_mG] = 0

        df = pd.DataFrame({
            "time": time,
            "X_mG": X_mG,
            "Y_mG": Y_mG,
            "Z_mG": Z_mG
        })

    # --- Default: generic float data ---
    else:
        data = np.fromfile(file_path, dtype=np.float32)
        df = pd.DataFrame(data, columns=["Value"])

    # Clean column names
    df.columns = [c.strip() for c in df.columns]
    return df


def apply_correction(df, base_filename, correction_folder):
    """
    Applies the correction by subtracting the vector columns (X, Y, Z) if present.
    Supports column names: X_g/Y_g/Z_g, AccX/AccY/AccZ, X_G/Y_G/Z_G, accX/accY/accZ.
    Uses the CSV file if available; otherwise, it tries a DAT file with the same name in the correction_folder.
    """
    csv_name = base_filename.replace(".dat", ".csv")
    corr_csv_path = os.path.join(correction_folder, csv_name)
    corr_dat_path = os.path.join(correction_folder, base_filename)

    corr_df = None
    if os.path.exists(corr_csv_path):
        corr_df = pd.read_csv(corr_csv_path)
    elif os.path.exists(corr_dat_path):
        # Convert the correction .dat
        corr_df = parse_dat(corr_dat_path, base_filename)

    if corr_df is None:
        print(f"No correction found for {base_filename}")
        return df

    corr_df.columns = [c.strip() for c in corr_df.columns]

    # Equivalent names for each axis
    name_sets = {
        'X': ['X_g', 'AccX', 'X_G', 'accX'],
        'Y': ['Y_g', 'AccY', 'Y_G', 'accY'],
        'Z': ['Z_g', 'AccZ', 'Z_G', 'accZ'],
    }

    applied = []
    for axis in ['X', 'Y', 'Z']:
        # Match corresponding columns between data and correction
        col_df = next((n for n in name_sets[axis] if n in df.columns), None)
        col_corr = next((n for n in name_sets[axis] if n in corr_df.columns), None)
        if col_df and col_corr:
            min_len = min(len(df[col_df]), len(corr_df[col_corr]))
            if min_len > 0:
                df.loc[:min_len-1, col_df] = (
                    df.loc[:min_len-1, col_df].values - corr_df.loc[:min_len-1, col_corr].values
                )
                applied.append(col_df)

    if applied:
        print(f"Correction applied to {base_filename} on columns: {', '.join(applied)}")
    else:
        print(f"No matching columns found for correction of {base_filename}")
    return df


# --- MAIN LOOP ---
for filename in os.listdir(input_folder):
    if not filename.endswith(".dat"):
        continue

    file_path = os.path.join(input_folder, filename)

    # Step 1: Convert .dat -> DataFrame
    df = parse_dat(file_path, filename)

    # Step 2: Apply correction (if matching file found in correction_folder)
    df = apply_correction(df, filename, correction_folder)

    # Step 3: Save to CSV in output folder
    csv_filename = filename.replace(".dat", ".csv")
    csv_path = os.path.join(output_folder, csv_filename)
    df.to_csv(csv_path, index=False)
    print(f"Converted and corrected: {filename} -> {csv_filename}")

