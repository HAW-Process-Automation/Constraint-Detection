import ipyvuetify as v
import pandas as pd

from ._SPy_functions import get_start_end_display_range
from ._SPy_functions import pull_signals_from_asset_tree
from ._SPy_functions import push_signals
from ._SPy_functions import saturation_treemap
from ._SPy_functions import push_metadata
from ._SPy_functions import get_start_end_display_range_from_ids
from ._utils import get_workbook_id_from_url
from ._utils import get_worksheet_url
from ._utils import get_workbook_worksheet_workstep_ids
from ._saturation_detection import generate_short_gap_capsule
from ._saturation_detection import saturation_detection
from ._saturation_detection import generate_metadata
from ._saturation_detection import generate_constraint_index_table


class HamburgerMenu(v.Menu):
    def __init__(self, **kwargs):
        '''
        This class create an app bar for the UI with links to the GitHub issues page and to the
        Constraint Detection Add-on documentation.
        '''
        self.hamburger_button = v.AppBarNavIcon(v_on='menuData.on')
        self.issue_button = v.ListItem(value='help',
                                       ripple=True,
                                       href='https://github.com/HAW-Process-Automation/Constraint-Detection/issues',
                                       target='_blank',
                                       children=[v.ListItemAction(class_='mr-2 ml-0',
                                                                  children=[v.Icon(color='#212529',
                                                                                   children=['fa-github'])]),
                                                 v.ListItemActionText(children=[f'GitHub Issues'])
                                                 ])

        self.documentation_button = v.ListItem(value='help',
                                               ripple=True,
                                               href='https://haw-process-automation.github.io/Constraint-Detection/',
                                               target='_blank',
                                               children=[v.ListItemAction(class_='mr-2 ml-0',
                                                                          children=[v.Icon(color='#212529',
                                                                                           children=['fa-book'])]),
                                                         v.ListItemActionText(
                                                             children=[f'Constraint Detection Documentation'])
                                                         ])

        self.items = [v.Divider(), self.issue_button, v.Divider(), self.documentation_button, v.Divider()]

        super().__init__(offset_y=True,
                         offset_x=False,
                         left=True,
                         v_slots=[{
                             'name': 'activator',
                             'variable': 'menuData',
                             'children': self.hamburger_button,
                         }]
                         ,
                         children=[
                             v.List(children=self.items)
                         ]
                         , **kwargs)


class ConstraintDetection():
    '''
    This class creates a user interface using ipyvuetify. All inputs required for the Constraint Detection Add-on
    can be specified in the UI.
    '''
    
    def clear_button_clicked(self, widget, event, data):
        '''
        This function clears input fields or resets them to the default values when the clear button is clicked.
        '''
        self.text_field_start_time.v_model = start_display_range
        self.text_field_end_time.v_model = end_display_range
        self.text_field_asset_tree.v_model = ''
        self.text_field_asset_tree_copy.v_model = ''
        self.checkbox_OP.v_model = True
        self.checkbox_PV.v_model = False
        self.checkbox_SP.v_model = False
        self.checkbox_MV.v_model = False
        self.text_field_red_threshold.v_model = 50
        self.text_field_yellow_threshold.v_model = 10
        self.text_field_short_capsule.v_model = 0
        self.select_time_short_capsule.v_model = 'minute(s)'
        self.text_field_short_gap.v_model = 0
        self.select_time_short_gap = 'minute(s)'
        self.signal_table.items = []
        self.progress_bar.hide()
        self.export_button.disabled = True
    
    def execute_button_clicked(self, widget, event, data):
        '''
        This function executes the analysis with the user specified inputs from the UI when the execute button is 
        clicked.
        '''
        # check for empty fields and entries which don't make sense
        if self.text_field_start_time.v_model == '' or self.text_field_end_time.v_model == '':
            raise RuntimeError(f'Please enter a start and end time for the analysis')
        if self.checkbox_OP.v_model == False and self.checkbox_PV.v_model == False and self.checkbox_SP.v_model == False and self.checkbox_PV.v_model == False:
            raise RuntimeError(f'Please select signals for the analysis')
        if self.text_field_asset_tree.v_model == '':
            raise RuntimeError(f'Please insert the name of your asset tree')
        if self.text_field_yellow_threshold.v_model == '' or self.text_field_red_threshold.v_model == '':
            raise RuntimeError(f'Please enter thresholds for the visualization in Treemap')
        if int(self.text_field_yellow_threshold.v_model) > int(self.text_field_red_threshold.v_model):
            raise RuntimeError(f'The red threshold must be larger than the yellow threshold')
        if int(self.text_field_yellow_threshold.v_model) > 100 or int(self.text_field_yellow_threshold.v_model) < 0:
            raise RuntimeError(f'The thresholds must lie between 0 and 100 %')
        if int(self.text_field_red_threshold.v_model) > 100 or int(self.text_field_red_threshold.v_model) < 0:
            raise RuntimeError(f'The thresholds must lie between 0 and 100 %')
        if self.text_field_short_capsule.v_model == '' or self.text_field_short_gap.v_model == '':
            raise RuntimeError(f'Please enter a value for short gap/capsule')
        
        # start loading and disable UI while the analysis is running
        self.execute_button.loading = True
        self.clear_button.disabled = True
        self.export_button.disabled = True
        self.text_field_start_time.disabled=True
        self.text_field_end_time.disabled=True
        self.text_field_asset_tree.disabled = True
        self.text_field_asset_tree_copy.disabled = True
        self.checkbox_OP.disabled = True
        self.checkbox_PV.disabled = True
        self.checkbox_SP.disabled = True
        self.checkbox_MV.disabled = True
        self.text_field_red_threshold.disabled = True
        self.text_field_yellow_threshold.disabled = True
        self.text_field_short_capsule.disabled = True
        self.select_time_short_capsule.disabled = True
        self.text_field_short_gap.disabled = True
        self.select_time_short_gap.disabled = True
        self.progress_bar.show()
        
        self.progress_bar.v_model=0
        self.progress_bar.children=["0%"]
        
        # get workbook ID
        #workbook_id = get_workbook_id_from_url(url)
        #workbook_id = get_workbook_worksheet_workstep_ids(jupyter_notebook_url)
        self.progress_bar.v_model=5
        self.progress_bar.children=["5%"]
        
        # pull asset tree 
        pulled_signals_df = pull_signals_from_asset_tree(workbook_id, 
                                                         self.text_field_start_time.v_model, 
                                                         self.text_field_end_time.v_model, 
                                                         self.text_field_asset_tree.v_model)
        self.progress_bar.v_model=25
        self.progress_bar.children=["25%"]
        start = pulled_signals_df.index[0].isoformat()
        end = pulled_signals_df.index[-1].isoformat()
        
        # saturation detection: generates saturation signals and constraint/saturation index table
        saturation_signals_df, saturation_index_df = saturation_detection(pulled_signals_df, 
                                                                          self.checkbox_OP.v_model, 
                                                                          self.checkbox_PV.v_model, 
                                                                          self.checkbox_SP.v_model, 
                                                                          self.checkbox_MV.v_model, 
                                                                          int(self.text_field_yellow_threshold.v_model), 
                                                                          int(self.text_field_red_threshold.v_model),
                                                                          int(self.text_field_short_gap.v_model), 
                                                                          self.select_time_short_gap.v_model, 
                                                                          int(self.text_field_short_capsule.v_model), 
                                                                          self.select_time_short_capsule.v_model)
        
        self.progress_bar.v_model=50
        self.progress_bar.children=["50%"]
        
        # format contraint/saturation index dataframe to a dictionary for the signal table in th UI
        saturation_index_dict = generate_constraint_index_table(saturation_index_df, 
                                                                self.text_field_asset_tree_copy.v_model)
        export_df = pd.DataFrame.from_dict(saturation_index_dict)
        export_df.to_csv('constraint_index_table.csv', index=False)
        self.progress_bar.v_model=55
        self.progress_bar.children=["55%"]
        
        # join pulled signals with saturation signals
        pulled_signals_reset_index_df = pulled_signals_df.reset_index()
        joined_signals = pd.concat([pulled_signals_reset_index_df, saturation_signals_df], axis=1)
        joined_signals_df = joined_signals.set_index('index')
        self.progress_bar.v_model=60
        self.progress_bar.children=["60%"]
        
        # generate metadata for the new asset tree
        metadata, joined_signals_correct_naming_df = generate_metadata(joined_signals_df, 
                                                                       self.text_field_asset_tree_copy.v_model)
        self.progress_bar.v_model=65
        self.progress_bar.children=["65%"]
        
        # push all signals to workbook
        push_results_df = push_signals(workbook_id, joined_signals_correct_naming_df)
        self.progress_bar.v_model=90
        self.progress_bar.children=["90%"]
        
        # join metadata and push results for final metadata
        push_results_reset_index_df = push_results_df.reset_index()
        push_results_reset_index_df = push_results_reset_index_df.drop(['index'], axis=1)
        metadata_final = pd.concat([push_results_reset_index_df, metadata], axis=1)
        
        # generate strings for short gaps/capsule e.g.'1min'
        short_gap, short_capsule = generate_short_gap_capsule(int(self.text_field_short_gap.v_model), 
                                                              self.select_time_short_gap.v_model, 
                                                              int(self.text_field_short_capsule.v_model), 
                                                              self.select_time_short_capsule.v_model)
        # build asset tree and create treemap
        build_df = saturation_treemap(metadata_final, 
                                      start, 
                                      end, 
                                      short_gap, 
                                      short_capsule, 
                                      self.checkbox_OP.v_model, 
                                      self.checkbox_PV.v_model, 
                                      self.checkbox_SP.v_model, 
                                      self.checkbox_MV.v_model,)
        
        self.progress_bar.v_model=95
        self.progress_bar.children=["95%"]
        
        # push metadata
        push_metadata(workbook_id, build_df)
        
        self.progress_bar.v_model=100
        self.progress_bar.children=["100%"]
        
        # set items of signal table to the constraint index dictionary and enable UI
        self.signal_table.items = saturation_index_dict
        self.execute_button.loading = False
        self.clear_button.disabled = False
        self.export_button.disabled = False
        self.text_field_start_time.disabled = False
        self.text_field_end_time.disabled= False
        self.text_field_asset_tree.disabled = False
        self.text_field_asset_tree_copy.disabled = False
        self.checkbox_OP.disabled = False
        self.checkbox_PV.disabled = False
        self.checkbox_SP.disabled = False
        self.checkbox_MV.disabled = False
        self.text_field_red_threshold.disabled = False
        self.text_field_yellow_threshold.disabled = False
        self.text_field_short_capsule.disabled = False
        self.select_time_short_capsule.disabled = False
        self.text_field_short_gap.disabled = False
        self.select_time_short_gap.disabled = False
        self.progress_bar.hide()
        
    def ConstraintDetectionUI(self, jupyter_notebook_url):
        '''
        This function contains the UI components.
        '''
        global workbook_id
        workbook_id, worksheet_id, workstep_id = get_workbook_worksheet_workstep_ids(jupyter_notebook_url)
        #url = get_worksheet_url(jupyter_notebook_url)
        global start_display_range
        global end_display_range
        #start_display_range, end_display_range = get_start_end_display_range(url)
        start_display_range, end_display_range = get_start_end_display_range_from_ids(workbook_id, worksheet_id, workstep_id)
        
        hamburger_menu = HamburgerMenu()
        self.AppBar = v.AppBar(
        color='#00695C',
        dense=True,
        dark=True,
        children=[v.ToolbarTitle(children=['Constraint Detection']),
                    v.Spacer(),
                    v.Divider(vertical=True),
                    hamburger_menu])
        
        self.start_end_time = v.Html(tag='h4',class_='text-left',children=['Start and End Time'])  
        self.text_field_start_time = v.TextField(class_='',color='#00695C',v_model='',disabled=False, label='Start Time', hint='YYYY-MM-DDTHH:MM:SS')
        self.text_field_start_time.v_model = start_display_range
        self.text_field_end_time = v.TextField(class_='',color='#00695C',v_model='',disabled=False, label='End Time', hint='YYYY-MM-DDTHH:MM:SS')
        self.text_field_end_time.v_model = end_display_range
        
        self.checkbox_heading = v.Html(tag='h4',class_='text-left',children=['Select Signals for Analysis'])
        self.checkbox_OP = v.Checkbox(v_model=True,disabled=False,color='#00695C',label='Controller Output')
        self.checkbox_PV = v.Checkbox(v_model=False,disabled=False,color='#00695C',label='Process Variable')
        self.checkbox_SP = v.Checkbox(v_model=False,disabled=False,color='#00695C',label='Setpoint')
        self.checkbox_MV = v.Checkbox(v_model=False,disabled=False,color='#00695C',label='Manipulated Variable')
        
        self.asset_tree_heading = v.Html(tag='h4',class_='text-left',children=['Select Asset Tree'])
        self.asset_tree_explanation = v.Html(tag='div',class_='text-left',children=['(The asset tree requires a specific layout, see User Guide for more information)'])
        self.text_field_asset_tree = v.TextField(class_='',color='#00695C',v_model='', label='Asset Tree Name', hint='Highest level of your asset tree e.g. for the Example asset tree that would be "Example"')
        self.text_field_asset_tree_copy = v.TextField(class_='',color='#00695C',v_model='', label='Optional: Name for Asset Tree Copy', hint='The Add-on makes a copy of your asset tree. Give the copy a name. By default, the word "Copy" will be appended to the asset tree name.')
        
        self.explanation_head=v.ExpansionPanelHeader(class_="white--text",color='#00695C',children=['What is the Contraint Detection Add-on used for?'])
        self.explanation_expl=v.ExpansionPanelContent(color='white', children = [f'''The Constraint Detection Add-on is
        a tool for control loop performance monitoring. It is used to find time periods when a control signal is 
        constraint or saturated. This means that the signal is at its minimum or maximum and only deviates from there 
        for short time periods. Control signals include all signals which are related to a control loop: Controller 
        output (OP), setpoint (SP), process variable (PV), manipulated variable (MV) and auto-manual mode. Saturation 
        occurs in the OP whereas constraints occur in the PV and MV due to their physical limitations (e.g. measuring 
        range, actuator range) or in the SP (e.g. when model predictive control is applied). The Constraint Detection 
        Add-on analyses the OP, SP, PV and MV and visualizes the severity of contraints/saturation in Treemap View 
        using a Constraint/Saturation Index.'''])
        self.expansion_final=v.ExpansionPanels(children = [v.ExpansionPanel(children = [self.explanation_head, self.explanation_expl])])
        
        self.execute_button = v.Btn(color = '#00695C', dark=True, block=True, elevation=2, children = ['EXECUTE'],loading=False)
        self.execute_button.on_event('click', self.execute_button_clicked)
        self.clear_button = v.Btn(color = '#00695C', block=True, outlined=True, elevation=2, children = ['CLEAR'])
        self.clear_button.on_event('click', self.clear_button_clicked)
        self.export_button = v.Btn(color = '#00695C', disabled=True, block=True, elevation=2, href="constraint_index_table.csv", attributes={"download": True}, children = ['export table to csv', v.Icon(right=True, children=['mdi-download'])])
        
        self.priority_color_heading = v.Html(tag='h4',class_='text-left',children=['Select Thresholds for Priority Colors in Treemap'])
        self.red_color_heading = v.Html(tag='div',class_='text-right, pt-3',children=['Constraint Index [%] above'])
        self.text_field_red_threshold = v.TextField(class_='',color='grey', background_color='white',suffix="%", outlined=True, dense=True, type='number', v_model=50)
        self.yellow_color_heading = v.Html(tag='div',class_='text-left, pt-3',children=['Constraint Index [%] above'])
        self.text_field_yellow_threshold = v.TextField(class_='',color='grey', background_color='white', suffix="%", outlined=True, dense=True, type='number', v_model=10)
                                             
        self.time_select_items = ['second(s)', 'minute(s)', 'hour(s)']
        self.short_capsule_heading = v.Html(tag='div',class_='pl-3',children=['Ignore capsules shorter than'])
        self.text_field_short_capsule = v.TextField(class_='',color='#00695C', outlined=True, dense=True, type='number', v_model=0)
        self.select_time_short_capsule = v.Select(v_model='minute(s)', items = self.time_select_items, color='#00695C', dense=True, outlined=True)
        self.short_gap_heading = v.Html(tag='div',class_='pl-3',children=['Ignore gaps shorter than'])
        self.text_field_short_gap = v.TextField(class_='',color='#00695C', outlined=True, dense=True, type='number', v_model=0)
        self.select_time_short_gap = v.Select(v_model='minute(s)', items = self.time_select_items, color='#00695C', outlined=True, dense=True)

        self.progress_bar = v.ProgressLinear(v_model=0, color = '#00695C', striped=True, height=15, children=["0%"])
        self.progress_bar.hide()
        
        self.signal_table_headers = [
            { 'text': 'Signal', 'value': 'Signal'},
            { 'text': 'Path', 'value': 'Path' },
            { 'text': 'Constraint Index [%]', 'value': 'Index' }
        ]
        
        self.signal_table = v.DataTable(headers=self.signal_table_headers, dense=True, items=[])
        
        self.short_capsules_gaps_container = v.Container(children = [
            v.Row(children = [self.short_capsule_heading]),
            v.Row(no_gutters = True, lg=12, children = [
                v.Col(lg=2, children = [self.text_field_short_capsule]),
                v.Col(lg=2, children = [self.select_time_short_capsule])
            ]),
            v.Row(children = [self.short_gap_heading]),
            v.Row(no_gutters = True, lg=12, children = [
                v.Col(lg=2, children = [self.text_field_short_gap]),
                v.Col(lg=2, children = [self.select_time_short_gap])
            ])
        ])
        
        self.expansion_head_capsules_gaps = v.ExpansionPanelHeader(class_='white--text',color='#00695C',children=['Ignore Short Capsules/Gaps'])
        self.expansion_content_capsules_gaps=v.ExpansionPanelContent(color='white', children = [self.short_capsules_gaps_container])
        self.expansion_capsules_gaps=v.ExpansionPanels(children = [v.ExpansionPanel(children = [self.expansion_head_capsules_gaps, self.expansion_content_capsules_gaps])])
        
        
        self.time_container = v.Container(children = [
            v.Row(no_gutters=True, children = [self.start_end_time]),
            v.Row(lg=12, children = [
                v.Col(lg=6, children = [self.text_field_start_time]),
                v.Col(lg=6, children = [self.text_field_end_time])
            ])
        ])

        self.checkbox_container = v.Container(children = [
            v.Row(no_gutters=True, children = [self.checkbox_heading]),
            v.Row(no_gutters=True, lg=12, children = [
                v.Col(lg=3, children = [self.checkbox_OP]),
                v.Col(lg=3, children = [self.checkbox_PV]),
                v.Col(lg=2, children = [self.checkbox_SP]),
                v.Col(lg=3, children = [self.checkbox_MV])
            ])
        ])
        
        self.asset_tree_container = v.Container(children = [
            v.Row(no_gutters=True, children = [
                v.Col(lg=2, children = [self.asset_tree_heading]),
                v.Col(lg=10, children = [self.asset_tree_explanation])
            ]),
            v.Row(lg=12, children = [
                v.Col(lg=6, children = [self.text_field_asset_tree]),
                v.Col(lg=6, children = [self.text_field_asset_tree_copy])
            ])
        ])
                                           
        self.treemap_color_container = v.Container(children = [
            v.Row(no_gutters=True, children = [self.priority_color_heading]),
            v.Row(children = [
                v.Col(children = [
                    v.Card(height=65, color = 'red', children = [
                        v.Row(children = [
                            v.Spacer(lg=2),
                            v.Col(lg=5, children=[self.red_color_heading]),
                            v.Col(lg=3, children=[self.text_field_red_threshold]),
                            v.Spacer(lg=2)
                        ])
                    ])
                ]),
                v.Col(children = [
                    v.Card(height=65, color = 'yellow', children = [
                        v.Row(children = [
                            v.Spacer(),
                            v.Col(lg=5, children=[self.yellow_color_heading]),
                            v.Col(lg=3, children=[self.text_field_yellow_threshold]),
                            v.Spacer()
                        ])
                    ])
                ])
            ])
        ])
        
        self.lower_part_container = v.Container(children = [
            v.Row(children = [v.Col(lg=12, children = [self.signal_table])]),
            v.Row(lg=12, children = [
                v.Spacer(),
                v.Col(lg=2, children = [self.clear_button]),
                v.Col(lg=4, children = [self.export_button]),
                v.Col(lg=2, children = [self.execute_button])
            ]),
            v.Row(children = [v.Col(lg=12, children = [self.progress_bar])]),
            v.Row(children = [v.Col(lg=12, children = [self.expansion_capsules_gaps])]),
            v.Row(children = [v.Col(lg=12, children = [self.expansion_final])])
        ])
        
        self.final_container = v.Container(children = [
            self.AppBar,
            v.Card(no_gutters = True, color = 'grey lighten-4', children = [
                v.Row(no_gutters=True, children = [v.Col(children = [self.time_container])]),
                v.Row(no_gutters=True, children = [v.Col(children = [self.checkbox_container])]),
                v.Row(no_gutters=True, children = [v.Col(children = [self.asset_tree_container])]),
                v.Row(no_gutters=True, children = [v.Col(children = [self.treemap_color_container])]),
                v.Row(no_Gutters=True, children = [v.Col(children = [self.lower_part_container])]),
            ])
        ])
        return self.final_container