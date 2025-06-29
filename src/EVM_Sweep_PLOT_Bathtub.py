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
        self.df = pd.concat([self.df, df_now], ignore_index=True)
        print(f'Cols: {list(self.df.columns)}')                                 # Col names
        # self.df.iloc[2, self.df.columns.get_loc['VSG']]                       # Get VSG in row 2

    def filter_data_bathtub(self):
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
        print(f'Traces:{self.table.shape[1]:2d} DataPts:{self.table.shape[0]:3d} {self.file_append}')
        self.table.plot(legend=True)
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=2)
        plt.tight_layout(pad=2)
        plt.grid()
        plt.title(f'{self.Yval} {self.file_append}')
        # plt.axis([-50, 10, -40, -20])                                         # X, Y
        plt.ylim([-60, -30])
        plt.xlabel(self.Xval)
        plt.ylabel(self.Yval)

        plt.savefig(f'{self.file_out}_{self.file_append}.png')
        # plt.show()
        # time.sleep(1)
        # plt.close()

    def main(self):
        # self.read_data()
        # self.filter_data_freqResp()
        self.filter_data_bathtub()

if __name__ == '__main__':
    # plotter('EVM_Sweep_Simple_2025.05.09-214057.txt').main()                  # Explicitly name file
    plotter().main()                                                            # GUI will prompt for file
