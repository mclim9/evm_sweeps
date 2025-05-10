import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
# from GUI_elements import select_list

class plotter():
    def __init__(self, filename=''):
        self.file_in = filename
        if filename == '':
            self.select_file()
        self.file_out = f'{self.file_in.split(".txt")[0]}'
        self.file_append = ''

    def select_file(self):
        root = tk.Tk()
        root.withdraw()  # Hides Tkinter window
        self.file_in = filedialog.askopenfilename(title="Select a file", filetypes=[("Text files", "*.txt")])

    def read_data(self):
        print(self.file_in)
        self.df = pd.read_csv(self.file_in, header=0, skiprows=3, sep=',')
        # asdf = select_list(list(self.df.columns), "Parmeters")
        print(f'Cols: {list(self.df.columns)}')                 # Col names

    def filter_data_bathtub(self):
        freq_array = self.df._series['Freq'].unique()
        for freq in freq_array:
            bathTub = self.df[self.df['Freq'].isin([freq])]         # filter data   | Up Lt
            # df = df[df['lvling'].str.contains('EVM')]             # filter data   | Up Lt
            self.Cols = ['Freq',  'Leveling']                       # Split Traces  | Up Rt
            self.Xval = ['Power [dBm]']                             # X Values      | Dn Lt
            self.Yval = ['EVM[dB]']                                 # Y Values      | Dn Rt
            self.aggg = 'mean'                                      # mean | sum
            self.table = pd.pivot_table(bathTub, values=self.Yval, index=self.Xval, columns=self.Cols, aggfunc=self.aggg)
            # print(f'Traces:{self.table.shape[1]} DataPts:{self.table.shape[0]}')
            self.file_append = f'bathtub_{freq / 1e9:.3f}GHz'
            self.plot_data()

    def filter_data_freqResp(self):
        pwr_arry = [-10, 5, 10, 12]
        for setPwr in pwr_arry:
            freqRespData = self.df[self.df['Power [dBm]'].isin([setPwr])]    # filter data   | Up Lt
            self.Cols = [ 'Leveling', 'Power [dBm]']                # Split Traces  | Up Rt
            self.Xval = ['Freq']                                    # X Values      | Dn Lt
            self.Yval = ['EVM[dB]']                                 # Y Values      | Dn Rt
            self.aggg = 'mean'                                      # mean | sum
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
        # plt.axis([-50, 10, -40, -20])                     # X, Y
        plt.ylim([-60, -30])
        plt.xlabel(self.Xval)
        plt.ylabel(self.Yval)

        plt.savefig(f'{self.file_out}_{self.file_append}.png')
        # plt.show()
        # time.sleep(1)
        plt.close()

    def main(self):
        self.read_data()
        # self.filter_data_freqResp()
        self.filter_data_bathtub()

if __name__ == '__main__':
    plotter().main()
