import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
# from GUI_elements import select_list
headerRows = 3

class plotter():
    def __init__(self, filename=''):
        self.file_in = filename
        self.df = pd.DataFrame([])
        if filename == '':
            self.select_file()
        self.file_out = f'{self.file_in.split(".txt")[0]}'
        self.file_append = ''

    def convert_column_to_float(self, df, column_name):
        if column_name not in df.columns:
            print(f"Column '{column_name}' not found")
            return df
        try:
            df[column_name] = df[column_name].astype(float)
            return df
        except ValueError as e:
            print(f"Error converting column '{column_name}' to float: {e}")
            print("Possible issues: Invalid characters, missing values, or values that are not numeric.")
        return df

    def select_file(self):
        root = tk.Tk()
        root.withdraw()  # Hides Tkinter window
        # self.file_in = filedialog.askopenfilename(title="Select a file", filetypes=[("Text files", "*.txt")]) # Single file
        self.file_paths = filedialog.askopenfilenames(title="Select a file", filetypes=[("Text files", "*.txt")])
        for file in self.file_paths:
            self.file_in = file
            self.read_data()

    def read_data(self):
        print(self.file_in)
        self.hdr = pd.read_csv(self.file_in, nrows=headerRows, header=None)
        df_now = pd.read_csv(self.file_in, header=0, skiprows=headerRows, sep=',')
        df_now = df_now.assign(VSA=f'{self.hdr[1][0]}_{self.hdr[2][0]}')        # VSA+Serial
        df_now = df_now.assign(VSG=f'{self.hdr[1][1]}_{self.hdr[2][1]}')        # VSG+Serial
        df_now = df_now.assign(VSA=f'{self.hdr[1][0]}')                         # VSA Model only
        df_now = df_now.assign(VSG=f'{self.hdr[1][1]}')                         # VSG Model only
        df_now = df_now.assign(wave=f'{self.hdr[0][2]}')                        # Waveform
        df_now = df_now.replace(r'^\s*nan', -9999.99, regex=True)               # Replace NaN with -9999
        df_now = self.convert_column_to_float(df_now, 'EVM[dB]')                # EVM[dB] to float
        df_now = self.convert_column_to_float(df_now, 'ChPwr[dBm]')             # ChPwr[dBm] to float
        self.df = pd.concat([self.df, df_now], ignore_index=True)
        print(f'Cols: {list(self.df.columns)}')                                 # Col names
        # self.df.iloc[2, self.df.columns.get_loc['VSG']]                       # Get VSG in row 2

    def filter_data_bathtub_per_freq(self):
        freq_array = self.df._series['Freq'].unique()
        for freq in freq_array:
            bathTub = self.df[self.df['Freq'].isin([freq])]                     # filter data   | Up Lt
            # df = df[df['lvling'].str.contains('EVM')]                         # filter data   | Up Lt
            self.Cols = ['Freq', 'Leveling', 'VSG', 'VSA']                      # Split Traces  | Up Rt
            self.Xval = ['Power [dBm]']                                         # X Values      | Dn Lt
            self.Yval = ['EVM[dB]']                                             # Y Values      | Dn Rt
            self.aggg = 'mean'                                                  # mean | sum
            self.table = pd.pivot_table(bathTub, values=self.Yval, index=self.Xval, columns=self.Cols, aggfunc=self.aggg)
            # print(f'Traces:{self.table.shape[1]} DataPts:{self.table.shape[0]}')
            self.file_append = f'bathtub_{freq / 1e9:.3f}GHz'
            self.plot_data()

    def filter_data_bathtub(self):
        bathTub = self.df
        # df = df[df['lvling'].str.contains('EVM')]                               # filter data   | Up Lt
        self.Cols = ['Freq', 'Leveling', 'VSG', 'VSA']                          # Split Traces  | Up Rt
        self.Xval = ['Power [dBm]']                                             # X Values      | Dn Lt
        self.Yval = ['EVM[dB]']                                                 # Y Values      | Dn Rt
        self.aggg = 'mean'                                                      # mean | sum
        self.table = pd.pivot_table(bathTub, values=self.Yval, index=self.Xval, columns=self.Cols, aggfunc=self.aggg)
        # print(f'Traces:{self.table.shape[1]} DataPts:{self.table.shape[0]}')
        self.file_append = f'bathtub'
        self.plot_data()

    def filter_data_freqResp(self):
        pwr_arry = [-10, 5, 10, 12]
        for setPwr in pwr_arry:
            freqRespData = self.df[self.df['Power [dBm]'].isin([setPwr])]       # filter data   | Up Lt
            self.Cols = ['Leveling', 'Power [dBm]', 'VSG', 'VSA']               # Split Traces  | Up Rt
            self.Xval = ['Freq']                                                # X Values      | Dn Lt
            self.Yval = ['EVM[dB]']                                             # Y Values      | Dn Rt
            self.aggg = 'mean'                                                  # mean | sum
            self.table = pd.pivot_table(freqRespData, values=self.Yval, index=self.Xval, columns=self.Cols, aggfunc=self.aggg)
            self.file_append = f'freqResp_{setPwr}'
            self.plot_data()

    def plot_data(self):
        markers = ['o', 's', '^', 'v', 'D', '|', 'X', 'p', '4', '*', '+', 'x', '.', '>']
        print(f'Traces:{self.table.shape[1]:2d} DataPts:{self.table.shape[0]:3d} {self.file_append}')

        fig, ax = plt.subplots(figsize=(10, 8))  # Create figure and axes

        for i in range(self.table.shape[1]):
            self.table.iloc[:, i].plot(ax=ax, legend=True, marker=markers[i % len(markers)], linewidth=2.0) # Use iloc for column selection

        ax.grid(True)
        ax.set_title(f'{self.Yval} {self.file_append}')
        ax.set_ylim([-55, -30])
        ax.set_xlabel(self.Xval)
        ax.set_ylabel(self.Yval)

        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=2) # Move legend after plotting all traces
        plt.tight_layout(pad=2)

        plt.savefig(f'{self.file_out}_{self.file_append}.png')
        # plt.show()
        # time.sleep(1)
        # plt.close()

    def main(self):
        # self.read_data()
        # self.filter_data_freqResp()
        self.filter_data_bathtub()
        # self.filter_data_bathtub_per_freq()

if __name__ == '__main__':
    # plotter('EVM_Sweep_Simple_2025.09.09-163900-WLAN.txt').main()               # Explicitly name file
    plotter().main()                                                            # GUI will prompt for file
