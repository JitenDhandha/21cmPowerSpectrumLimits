from nicegui import ui
import plotly.graph_objects as go
import pandas as pd
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")
SNS_CB = sns.color_palette('colorblind').as_hex()

# Define all the data that exists
LimitNames = ['HERA_2022', 'HERA_2023',
              'AARTFAAC_2020', 
              'NenuFAR_2024',
              'PAPER_2019',
              'OVRO-LWA_2019', 'OVRO-LWA_2021',
              'LOFAR_2017', 'LOFAR_2019', 'LOFAR_2020', 'LOFAR_2024', 'LOFAR_2025',
              'GMRT_2013', 'GMRT_2021',
              'MWA_2015', 'MWA_2016a', 'MWA_2016b', 'MWA_2019a', 'MWA_2019b', 'MWA_2020', 'MWA_2021a', 'MWA_2021b', 'MWA_2023', 'MWA_2025']
ExperimentNames = ['HERA', 'AARTFAAC', 'NenuFAR', 'PAPER', 'OVRO-LWA', 'LOFAR', 'GMRT', 'MWA']
ColorsList = SNS_CB
MarkerStyles = ['circle', 'square', 'diamond', 'cross', 'x', 'triangle-up', 'triangle-down', 'triangle-left', 'triangle-right', 'star', 'hexagon']

# Function to read the data from the file
def get_limits(limit_name):
    file_path = f'data/{limit_name}.txt'
    with open(file_path, 'r') as f:
        lines = f.readlines()
        author = lines[0].split(':', 1)[0].replace('# ', '')
        ads_link = lines[0].split(':', 1)[1].strip()
    data = pd.read_csv(file_path, header=1, sep=',\s+')
    return author, ads_link, data

class GUI():
    
    def __init__(self):
        
        # Initialize non-GUI code variables
        self.checkbox_list = []
        self.function_of_z = True
        self.k_min = -2
        self.k_max = 1
        self.z_min = 5
        self.z_max = 30
        
        #Run the GUI
        self.run()
        
    def set_function_of_z(self, value):
        self.function_of_z = value
        self.update_plot()
    
    def set_k_min(self, value): 
        if value == '':
            value = -2
        else:
            try:
                value = float(value)
            except ValueError:
                value = -2
                ui.notify('Invalid input for k_min', color='negative')
        self.k_min = value
        self.update_plot()
        
    def set_k_max(self, value):
        if value == '':
            value = 1
        else:
            try:
                value = float(value)
            except ValueError:
                value = 1
                ui.notify('Invalid input for k_max', color='negative')
        self.k_max = value
        self.update_plot()
        
    def set_z_min(self, value):
        if value == '':
            value = 5
        else:
            try:
                value = float(value)
            except ValueError:
                value = 5
                ui.notify('Invalid input for z_min', color='negative')
        self.z_min = value
        self.update_plot()
    
    def set_z_max(self, value):
        if value == '':
            value = 30
        else:
            try:
                value = float(value)
            except ValueError:
                value = 30
                ui.notify('Invalid input for z_max', color='negative')
        self.z_max = value
        self.update_plot()
        
    def update_plot(self):
        # Get the data for the selected limit
        self.figure.data = []
        if self.function_of_z:
            xaxis = dict(type='linear', title='Redshift z', range=[5, 30], tickmode='linear')
        else:
            xaxis = dict(type='log', title='k [h/cMpc]', range=[-2, 1], exponentformat='e', tickmode='linear')
        for limit_name, chkbox in zip(LimitNames, self.checkbox_list):
            if chkbox.value:
                experiment_name = limit_name.split('_')[0]
                color = ColorsList[ExperimentNames.index(experiment_name)]
                marker_style = MarkerStyles[[x for x in LimitNames if x.startswith(experiment_name)].index(limit_name)]
                # Get the data for the selected limit
                author, ads_link, data = get_limits(limit_name)
                # Add the data to the plot
                z = data['z_center'].values
                k = data['k[h cMpc^-1]'].values
                x = z if self.function_of_z else k
                Dsq21 = data['Dsq21[mK^2]'].values
                Dsq21 = Dsq21[(k >= self.k_min) & (k <= self.k_max) & (z >= self.z_min) & (z <= self.z_max)]
                self.figure.add_trace(go.Scatter(
                    x=x,
                    y=Dsq21,
                    mode='markers',
                    marker=dict(color=color, symbol=marker_style, size=8),
                    name=author,)
                )
        self.figure.update_layout(
            xaxis=xaxis,
            yaxis=dict(type='log', title='Dsq21 [mK^2]', range=[2, 13], exponentformat='e', tickmode='linear'),
            legend=dict(title='Experiments'),
            showlegend=True,
            template='plotly_dark',
            title='21cm Power Spectrum Limits',
        )
        self.figure_ui.update()

    def run(self):
        
        #############################################
        #           Header of the GUI               #
        #############################################
        
        ui.dark_mode(True)
        ui.add_head_html('''
        <script>
        window.MathJax = {
            tex: {inlineMath: [['$', '$'], ['\\(', '\\)']]}
        };
        </script>
        <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
        ''')
        
        self.header = ui.header(
            ).classes('w-full h-[11%] items-center justify-center content-center bg-primary')
        with self.header:
            ui.label('21cmPSLimits'
                ).classes('text-5xl'
                ).style('font-family: Monaco')
            ui.label('by Jiten Dhandha').classes('mr-auto')
            ui.button(icon='code',
                on_click=lambda: ui.navigate.to('https://github.com/JitenDhandha/21cmPowerSpectrumLimits', new_tab=True)
                ).props('round'
                ).tooltip('GitHub')
                

            
        #############################################
        #            Experiments card               #
        #############################################
        
        with ui.row().classes('w-full items-center justify-center content-center'):
            
            with ui.card().classes('w-[45%]'):
                
                ui.label('Select the limits you want to plot:').classes('text-2xl')
                
                with ui.row().classes('w-full items-center'):
                    for experiment_name in ExperimentNames:
                        ui.label(experiment_name
                            ).classes('text-xl underline'
                            ).style(f'color: {ColorsList[ExperimentNames.index(experiment_name)]};')
                        experiment_limits = [x for x in LimitNames if x.startswith(experiment_name)]
                        for limit_name in experiment_limits:
                            author, ads_link, data = get_limits(limit_name)
                            chkbox = ui.checkbox(f'{author}', value=False,
                                on_change=self.update_plot
                                ).classes('text-l'
                                ).style(f'color: {ColorsList[ExperimentNames.index(experiment_name)]};')
                            self.checkbox_list.append(chkbox)
                    
            #############################################
            #                  Plot card                #
            #############################################
            
            with ui.card().classes('w-[53%]'):
                with ui.row().classes('w-full'):
                    self.figure = go.Figure()
                    self.figure_ui = ui.plotly(self.figure).classes('w-full h-350px')
                    self.update_plot()
                with ui.row().classes('w-full items-center justify-center content-center'):
                    with ui.column().classes('w-[31%]'):
                        self.function_z_button = ui.button('Function of z',
                            on_click=lambda: self.set_function_of_z(True)
                            ).style('background-color: bg-primary; color: white; font-size: 20px;')
                        self.function_k_button = ui.button('Function of k',
                            on_click=lambda: self.set_function_of_z(False)
                            ).style('background-color: bg-primary; color: white; font-size: 20px;')
                    with ui.column().classes('w-[31%]'):
                        self.k_min_input = ui.input('k_min',
                            on_change=lambda e: self.set_k_min(e.value)
                            ).classes('text-l'
                            ).style('background-color: bg-primary; color: white;')
                        self.k_max_input = ui.input('k_max', 
                            on_change=lambda e: self.set_k_max(e.value)
                            ).classes('text-l'
                            ).style('background-color: bg-primary; color: white;')
                    with ui.column().classes('w-[31%]'):
                        self.z_min_input = ui.input('z_min',
                            on_change=lambda e: self.set_z_min(e.value)
                            ).classes('text-l'
                            ).style('background-color: bg-primary; color: white;')
                        self.z_max_input = ui.input('z_max',
                            on_change=lambda e: self.set_z_max(e.value)
                            ).classes('text-l'
                            ).style('background-color: bg-primary; color: white;')
        
        ui.run()