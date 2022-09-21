import ipyvuetify as v
import pandas as pd
from seeq import sdk
from seeq import spy

from ._SPy_functions import get_asset_trees_from_workbook_id
from ._SPy_functions import pull_signals_from_asset_tree
from ._SPy_functions import push_signals
from ._SPy_functions import saturation_treemap
from ._SPy_functions import push_metadata
from ._SPy_functions import get_start_end_display_range_from_ids
from ._SPy_functions import recalculate_change_short_gap_capsule
from .utils._sdl import get_workbook_worksheet_workstep_ids
from ._saturation_detection import generate_short_gap_capsule
from ._saturation_detection import saturation_detection
from ._saturation_detection import generate_metadata
from ._saturation_detection import generate_constraint_index_table
from ._saturation_detection import recalculate_saturation_index
from ._saturation_detection import recalculate_constraint_index_table


class HamburgerMenu(v.Menu):
    def __init__(self, **kwargs):
        """
        This class create an app bar for the UI with links to the GitHub issues page and to the
        Constraint Detection Add-on documentation.
        """
        self.hamburger_button = v.AppBarNavIcon(v_on='menuData.on')
        self.issue_button = v.ListItem(value='help',
                                       ripple=True,
                                       href='https://github.com/HAW-Process-Automation/Constraint-Detection/issues',
                                       target='_blank',
                                       children=[v.ListItemAction(class_='mr-2 ml-0',
                                                                  children=[v.Icon(color='#212529',
                                                                                   children=['fa-github'])]),
                                                 v.ListItemActionText(children=[f'Support'])
                                                 ])

        self.documentation_button = v.ListItem(value='help',
                                               ripple=True,
                                               href='https://constraint-detection.readthedocs.io/en/latest/index.html',
                                               target='_blank',
                                               children=[v.ListItemAction(class_='mr-2 ml-0',
                                                                          children=[v.Icon(color='#212529',
                                                                                           children=['fa-book'])]),
                                                         v.ListItemActionText(
                                                             children=[f'Documentation'])
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


class ConstraintDetection:
    """
    This class creates a user interface using ipyvuetify. All inputs required for the Constraint Detection Add-on
    can be specified in the UI.
    """

    def clear_button_clicked(self, widget, event, data):
        """
        This function clears input fields or resets them to the default values when the clear button is clicked.
        """
        self.text_field_start_time.v_model = start_display_range
        self.text_field_end_time.v_model = end_display_range
        self.select_asset_tree.v_model = ''
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
        self.select_time_short_gap.v_model = 'minute(s)'
        self.signal_table.items = []
        self.progress_bar.hide()

        self.clear_button.disabled = False
        self.execute_button.disabled = False
        self.export_button.disabled = True
        self.recalculate_button.disabled = True
        self.text_field_start_time.disabled = False
        self.text_field_end_time.disabled = False
        self.select_asset_tree.disabled = False
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

    def execute_button_clicked(self, widget, event, data):
        """
        This function executes the analysis with the user specified inputs from the UI when the execute button is
        clicked.
        """
        # Error messages for invalid specifications in the input fields
        if self.text_field_start_time.v_model == '' or self.text_field_end_time.v_model == '':
            raise RuntimeError(f'Please enter a start and end time for the analysis')
        if self.checkbox_OP.v_model == False and self.checkbox_PV.v_model == False and \
                self.checkbox_SP.v_model == False and self.checkbox_PV.v_model == False:
            raise RuntimeError(f'Please select signals for the analysis')
        if self.select_asset_tree.v_model == '':
            raise RuntimeError(f'Please select an asset tree')
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
        if int(self.text_field_short_capsule.v_model) < 0 or int(self.text_field_short_gap.v_model) < 0:
            raise RuntimeError(f'Please enter a value for short gap/capsule that is greater or equal to zero.')

        self.progress_bar.v_model = 0
        self.progress_bar.children = ["0%"]

        # start loading and disable UI while the analysis is running
        self.execute_button.loading = True
        self.clear_button.disabled = True
        self.export_button.disabled = True
        self.text_field_start_time.disabled = True
        self.text_field_end_time.disabled = True
        self.select_asset_tree.disabled = True
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

        self.progress_bar.v_model = 5
        self.progress_bar.children = ["5%"]

        # pull asset tree
        pulled_signals_df = pull_signals_from_asset_tree(workbook_id,
                                                         self.text_field_start_time.v_model,
                                                         self.text_field_end_time.v_model,
                                                         self.select_asset_tree.v_model)
        self.progress_bar.v_model = 25
        self.progress_bar.children = ["25%"]
        start = pulled_signals_df.index[0].isoformat()
        end = pulled_signals_df.index[-1].isoformat()

        pulled_signals_df.dropna(axis=1, how='all', inplace=True)

        if len(pulled_signals_df.columns) == 0:
            raise RuntimeError(f'There is no valid data in the asset tree in the selected time period.')

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

        self.progress_bar.v_model = 50
        self.progress_bar.children = ["50%"]

        # format constraint/saturation index dataframe to a dictionary for the signal table in th UI
        saturation_index_dict = generate_constraint_index_table(saturation_index_df,
                                                                self.text_field_asset_tree_copy.v_model)
        export_df = pd.DataFrame.from_dict(saturation_index_dict)
        export_df.to_csv('constraint_index_table.csv', index=False)
        self.progress_bar.v_model = 55
        self.progress_bar.children = ["55%"]

        # join pulled signals with saturation signals
        pulled_signals_reset_index_df = pulled_signals_df.reset_index()
        joined_signals = pd.concat([pulled_signals_reset_index_df, saturation_signals_df], axis=1)
        joined_signals_df = joined_signals.set_index('index')
        self.progress_bar.v_model = 60
        self.progress_bar.children = ["60%"]

        # generate metadata for the new asset tree
        metadata, joined_signals_correct_naming_df = generate_metadata(joined_signals_df,
                                                                       self.text_field_asset_tree_copy.v_model)
        self.progress_bar.v_model = 65
        self.progress_bar.children = ["65%"]

        # push all signals to workbook
        push_results_df = push_signals(workbook_id, joined_signals_correct_naming_df)
        self.progress_bar.v_model = 90
        self.progress_bar.children = ["90%"]

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
                                      self.checkbox_MV.v_model, )

        self.progress_bar.v_model = 95
        self.progress_bar.children = ["95%"]

        # push metadata
        push_metadata(workbook_id, build_df)

        self.progress_bar.v_model = 100
        self.progress_bar.children = ["100%"]

        # set items of signal table to the constraint index dictionary and enable UI
        self.signal_table.items = saturation_index_dict
        self.execute_button.loading = False
        self.execute_button.disabled = True
        self.clear_button.disabled = False
        self.export_button.disabled = False
        self.recalculate_button.disabled = False
        self.text_field_short_capsule.disabled = False
        self.select_time_short_capsule.disabled = False
        self.text_field_short_gap.disabled = False
        self.select_time_short_gap.disabled = False
        self.progress_bar.hide()

    def recalculate_button_clicked(self, widget, event, data):
        """
        This function recalculates the analysis with the new short gaps/capsules from the UI when the recalculate button
        is clicked.
        """

        # Error messages for invalid specifications in the input fields
        if int(self.text_field_short_capsule.v_model) < 0 or int(self.text_field_short_gap.v_model) < 0:
            raise RuntimeError(f'Please enter a value for short gap/capsule that is greater or equal to zero.')
        if int(self.text_field_short_capsule.v_model) < 0 or int(self.text_field_short_gap.v_model) < 0:
            raise RuntimeError(f'Please enter a value for short gap/capsule that is greater or equal to zero.')

        # start loading and disable UI while the analysis is running
        self.recalculate_button.loading = True
        self.clear_button.disabled = True
        self.export_button.disabled = True
        self.text_field_start_time.disabled = True
        self.text_field_end_time.disabled = True
        self.select_asset_tree.disabled = True
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

        self.progress_bar.v_model = 0
        self.progress_bar.children = ["0%"]

        # generate strings for short gaps/capsule e.g.'1min'
        short_gap, short_capsule = generate_short_gap_capsule(int(self.text_field_short_gap.v_model),
                                                              self.select_time_short_gap.v_model,
                                                              int(self.text_field_short_capsule.v_model),
                                                              self.select_time_short_capsule.v_model)

        self.progress_bar.v_model = 15
        self.progress_bar.children = ["15%"]

        # recalculate time capsules and time percentage in the treemap. pull saturation signals.
        pulled_signals_df = recalculate_change_short_gap_capsule(self.text_field_asset_tree_copy.v_model,
                                                                 self.select_asset_tree.v_model,
                                                                 self.text_field_start_time.v_model,
                                                                 self.text_field_end_time.v_model,
                                                                 workbook_id,
                                                                 short_gap,
                                                                 short_capsule)
        self.progress_bar.v_model = 50
        self.progress_bar.children = ["50%"]

        # recalculate time percentage for the signal table
        saturation_index_df = recalculate_saturation_index(pulled_signals_df,
                                                           int(self.text_field_short_capsule.v_model),
                                                           self.select_time_short_capsule.v_model,
                                                           int(self.text_field_short_gap.v_model),
                                                           self.select_time_short_gap.v_model)

        self.progress_bar.v_model = 75
        self.progress_bar.children = ["75%"]

        # format saturation_index_df to a dictionary for the signal table in th UI
        saturation_index_dict = recalculate_constraint_index_table(saturation_index_df)
        export_df = pd.DataFrame.from_dict(saturation_index_dict)
        export_df.to_csv('constraint_index_table.csv', index=False)

        self.progress_bar.v_model = 95
        self.progress_bar.children = ["95%"]

        # set items of signal table to the constraint index dictionary and enable UI
        self.signal_table.items = saturation_index_dict

        self.progress_bar.v_model = 100
        self.progress_bar.children = ["100%"]

        self.recalculate_button.loading = False
        self.clear_button.disabled = False
        self.export_button.disabled = False
        self.text_field_short_capsule.disabled = False
        self.select_time_short_capsule.disabled = False
        self.text_field_short_gap.disabled = False
        self.select_time_short_gap.disabled = False
        self.progress_bar.hide()

    def open_threshold_dialog(self, widget, event, data):
        """
        This function opens a dialog window with an explanation regarding the threshold visualization in treemap view.
        """
        self.threshold_dialog.v_model = True

    def open_constraint_detection_dialog(self, widget, event, data):
        """
        This function opens a dialog window with an explanation about the constraint detection add-on.
        """
        self.constraint_detection_dialog.v_model = True

    def on_close_button_clicked(self, widget, event, data):
        """
        This function closes all dialog windows.
        """
        self.threshold_dialog.v_model = False
        self.constraint_detection_dialog.v_model = False

    def ConstraintDetectionUI(self, jupyter_notebook_url):
        """
        This function contains the UI components.
        """
        global workbook_id
        workbook_id, worksheet_id, workstep_id = get_workbook_worksheet_workstep_ids(jupyter_notebook_url)

        # check for workbook owner and permissions of the acting user. The add-on only works if the acting user is the
        # workbook owner.
        workbooks_api = sdk.WorkbooksApi(spy.client)
        data = workbooks_api.get_workbook(id=workbook_id).to_dict()
        permissions = data['effective_permissions']['manage']
        workbook_owner = data['owner']['name']
        translation_key = data['ancestors'][0]['translation_key']

        if not permissions:
            raise RuntimeError(f'You need Read/Write/Manage access for the workbook to execute the add-on.')
        if translation_key == 'SHARED':
            raise RuntimeError(f'''Due to a SPy issue the add-on can only be executed if you are the workbook owner.
            The owner of this workbook is ''' + workbook_owner + '.')

        # get start and end of the display range
        global start_display_range
        global end_display_range
        start_display_range, end_display_range = get_start_end_display_range_from_ids(workbook_id, worksheet_id,
                                                                                      workstep_id)
        # get the names of all asset trees in the workbook
        asset_tree_name_list = get_asset_trees_from_workbook_id(workbook_id)

        # hamburger menu for appbar
        hamburger_menu = HamburgerMenu()

        # help icon for app bar
        self.help_constraint_detection = v.Btn(x_small=True, icon=True, class_='ma-2', children=[
            v.Icon(color='white', children=['mdi-help-circle'])])
        self.help_constraint_detection.on_event('click', self.open_constraint_detection_dialog)

        # close button for dialogs
        self.close_button = v.Btn(color='#00695C', dark=True, block=True, children=['Close'])
        self.close_button.on_event('click', self.on_close_button_clicked)

        self.add_on_explanation = f'''The Constraint Detection Add-on is a tool for control loop performance monitoring.
        It is used to find time periods when a control signal is constrained or saturated. This means that the signal 
        is at its minimum or maximum and only deviates from there for short time periods. Control signals include all 
        signals which are related to a control loop: Controller output (OP), setpoint (SP), process variable (PV), 
        manipulated variable (MV) and auto-manual mode. Saturation occurs in the OP whereas constraints exist in the PV
        and MV due to their physical limitations (e.g. measuring range, actuator range) or in the SP (e.g. when model 
        predictive control is applied). The Constraint Detection Add-on analyses the OP, SP, PV and MV and generates a 
        worksheet in treemap view where every controller panel is coloured according to the time-percentage a signal is
        constrained/saturated in the analysis time period.'''

        # dialog that opens from the appbar help icon
        self.constraint_detection_dialog = v.Dialog(width='500',
                                                    v_model='dialog',
                                                    children=[
                                                        v.Card(children=[
                                                            v.CardTitle(class_='headline gray lighten-2',
                                                                        primary_title=True,
                                                                        children=["Constraint Detection"]),
                                                            v.CardText(children=[
                                                                v.Row(lg=12, children=[self.add_on_explanation]),
                                                                v.Row(lg=12, children=[
                                                                    v.Spacer(),
                                                                    v.Col(lg=4, children=[self.close_button]),
                                                                ])
                                                            ])
                                                        ])
                                                    ])

        self.constraint_detection_dialog.v_model = False

        self.constraint_detection_dialog.on_event('keydown.stop', lambda *args: None)

        # AppBar
        self.AppBar = v.AppBar(color='#00695C', dense=True, dark=True, children=[
            v.ToolbarTitle(children=['Constraint Detection']), self.constraint_detection_dialog,
            self.help_constraint_detection, v.Spacer(), v.Divider(vertical=True), hamburger_menu])

        # Selection of start and end time. By default, the worksheet display range is entered for the start and end
        # time
        self.start_end_time = v.Html(tag='h4', class_='text-left', children=['Start and End Time'])
        self.text_field_start_time = v.TextField(class_='', color='#00695C', v_model='', disabled=False,
                                                 label='Start Time', hint='YYYY-MM-DDTHH:MM:SS')
        self.text_field_end_time = v.TextField(class_='', color='#00695C', v_model='', disabled=False,
                                               label='End Time', hint='YYYY-MM-DDTHH:MM:SS')
        self.text_field_start_time.v_model = start_display_range
        self.text_field_end_time.v_model = end_display_range

        # Checkboxes for signal selection for analysis
        self.checkbox_heading = v.Html(tag='h4', class_='text-left', children=['Select Signals for Analysis'])
        self.checkbox_OP = v.Checkbox(v_model=True, disabled=False, color='#00695C', label='Controller Output')
        self.checkbox_PV = v.Checkbox(v_model=False, disabled=False, color='#00695C', label='Process Variable')
        self.checkbox_SP = v.Checkbox(v_model=False, disabled=False, color='#00695C', label='Setpoint')
        self.checkbox_MV = v.Checkbox(v_model=False, disabled=False, color='#00695C', label='Manipulated Variable')

        # Selection of the asset tree for the analysis and name text field for asset tree copy. A list of all asset
        # trees which are scoped to the workbook is handed over to the dropdown menu.
        self.asset_tree_heading = v.Html(tag='h4', class_='text-left', children=['Select Asset Tree'])
        self.link_userguide = v.Btn(x_small=True, icon=True, target='_blank',
                                    href='https://constraint-detection.readthedocs.io/en/latest/userguide.html',
                                    attributes={"download": True}, children=[
                v.Icon(color='#00695C', children=['mdi-open-in-new'])])
        self.asset_tree_explanation = v.Html(tag='div', class_='text-left', children=[
            'The asset tree requires a specific layout, see User Guide for more information', self.link_userguide])

        self.select_asset_tree = v.Select(v_model=asset_tree_name_list[0], items=asset_tree_name_list, color='#00695C')
        self.text_field_asset_tree_copy = v.TextField(class_='', color='#00695C', v_model='',
                                                      label='Optional: Name for Asset Tree Copy',
                                                      hint='''The Add-on makes a copy of your asset tree. Give the copy
                                                       a name. By default, the word "Constraint Monitor" will be 
                                                       appended to the asset tree name.''')

        # Buttons
        self.execute_button = v.Btn(color='#00695C', class_='white--text', block=True, elevation=2,
                                    children=['Execute'], loading=False)
        self.execute_button.on_event('click', self.execute_button_clicked)

        self.clear_button = v.Btn(color='#00695C', block=True, outlined=True, elevation=2, children=['Clear'])
        self.clear_button.on_event('click', self.clear_button_clicked)

        self.export_button = v.Btn(color='#00695C', class_='white--text', disabled=True, block=True, elevation=2,
                                   href="constraint_index_table.csv", attributes={"download": True},
                                   children=['export table to csv', v.Icon(right=True, children=['mdi-download'])])

        self.recalculate_button = v.Btn(color='#00695C', class_='white--text', block=True, elevation=2,
                                        children=['Recalculate'], loading=False, disabled=True)
        self.recalculate_button.on_event('click', self.recalculate_button_clicked)

        # Selection of thresholds for the treemap
        self.priority_color_heading = v.Html(tag='h4', class_='text-left',
                                             children=['Select Thresholds for Priority Colors in Treemap'])

        # threshold help icon
        self.help_threshold = v.Btn(x_small=True, icon=True, children=[
            v.Icon(color='#00695C', children=['mdi-help-circle'])])
        self.help_threshold.on_event('click', self.open_threshold_dialog)

        self.red_color_heading = v.Html(tag='div', class_='text-left, pt-3', children=[
            'Constrained/Saturated Time %'])
        self.text_field_red_threshold = v.TextField(class_='', color='grey', background_color='white', suffix="%",
                                                    outlined=True, dense=True, type='number', v_model=50)
        self.yellow_color_heading = v.Html(tag='div', class_='text-left, pt-3', children=[
            'Constrained/Saturated Time %'])
        self.text_field_yellow_threshold = v.TextField(class_='', color='grey', background_color='white', suffix="%",
                                                       outlined=True, dense=True, type='number', v_model=10)

        self.threshold_explanation = f'''The 'Constrained Time %' or 'Saturated Time %' is the time-percentage a signal
        is constrained/saturated in the analysed time period. The term 'Constrained Time %' is used for constraints in 
        the setpoint, process variable and manipulated variable. The term 'Saturated Time %' is used for saturation in 
        the controller output. The 'Constrained/Saturated Time %' is used to set the colours in the treemap.'''

        # dialog that opens from the threshold help icon
        self.threshold_dialog = v.Dialog(width='500',
                                         v_model='dialog',
                                         children=[
                                             v.Card(children=[
                                                 v.CardTitle(class_='headline gray lighten-2', primary_title=True,
                                                             children=[
                                                                 "Constrained/Saturated Time %"
                                                             ]),
                                                 v.CardText(children=[
                                                     v.Row(lg=12, children=[self.threshold_explanation]),
                                                     v.Img(src='thresholds.PNG'),
                                                     v.Row(lg=12, children=[
                                                         v.Spacer(),
                                                         v.Col(lg=4, children=[self.close_button]),
                                                     ])
                                                 ])
                                             ])
                                         ])

        self.threshold_dialog.v_model = False

        self.threshold_dialog.on_event('keydown.stop', lambda *args: None)

        # select short gaps and capsules
        self.time_select_items = ['second(s)', 'minute(s)', 'hour(s)']
        self.short_capsule_heading = v.Html(tag='div', class_='pl-3', children=['Ignore capsules shorter than'])
        self.text_field_short_capsule = v.TextField(class_='', color='#00695C', outlined=True, dense=True,
                                                    type='number', v_model=0)
        self.select_time_short_capsule = v.Select(v_model='minute(s)', items=self.time_select_items, color='#00695C',
                                                  dense=True, outlined=True)

        self.short_gap_heading = v.Html(tag='div', class_='pl-3', children=['Ignore gaps shorter than'])
        self.text_field_short_gap = v.TextField(class_='', color='#00695C', outlined=True, dense=True, type='number',
                                                v_model=0)
        self.select_time_short_gap = v.Select(v_model='minute(s)', items=self.time_select_items, color='#00695C',
                                              outlined=True, dense=True)

        # progress bar that is shown during the excution and recalculation of the analysis
        self.progress_bar = v.ProgressLinear(class_='white--text', v_model=0, color='#00695C', striped=True, height=15,
                                             children=["0%"])
        self.progress_bar.hide()

        # Signal Table with Constrained Time % in descending order
        self.signal_table_headers = [
            {'text': 'Signal', 'value': 'Signal'},
            {'text': 'Path', 'value': 'Path'},
            {'text': 'Constrained/Saturated Time %', 'value': 'Index'}
        ]

        self.signal_table = v.DataTable(headers=self.signal_table_headers, dense=True, items=[])

        # Container for short gap/capsule selection
        self.short_capsules_gaps_container = v.Container(children=[
            v.Row(children=[self.short_capsule_heading]),
            v.Row(no_gutters=True, lg=12, children=[
                v.Col(lg=2, children=[self.text_field_short_capsule]),
                v.Col(lg=2, children=[self.select_time_short_capsule])
            ]),
            v.Row(children=[self.short_gap_heading]),
            v.Row(no_gutters=True, lg=12, children=[
                v.Col(lg=2, children=[self.text_field_short_gap]),
                v.Col(lg=2, children=[self.select_time_short_gap])
            ])
        ])

        # Expansion panel for short gap/capsules selection
        self.expansion_head_capsules_gaps = v.ExpansionPanelHeader(class_='white--text', color='#00695C',
                                                                   children=['Ignore Short Capsules/Gaps'])
        self.expansion_content_capsules_gaps = v.ExpansionPanelContent(color='white',
                                                                       children=[self.short_capsules_gaps_container])
        self.expansion_capsules_gaps = v.ExpansionPanels(children=[v.ExpansionPanel(
            children=[self.expansion_head_capsules_gaps, self.expansion_content_capsules_gaps])])

        # Container for start and end time selection
        self.time_container = v.Container(children=[
            v.Row(no_gutters=True, children=[self.start_end_time]),
            v.Row(lg=12, children=[
                v.Col(lg=6, children=[self.text_field_start_time]),
                v.Col(lg=6, children=[self.text_field_end_time])
            ])
        ])

        # Container for signal checkboxes
        self.checkbox_container = v.Container(children=[
            v.Row(no_gutters=True, children=[self.checkbox_heading]),
            v.Row(no_gutters=True, lg=12, children=[
                v.Col(lg=3, children=[self.checkbox_OP]),
                v.Col(lg=3, children=[self.checkbox_PV]),
                v.Col(lg=2, children=[self.checkbox_SP]),
                v.Col(lg=3, children=[self.checkbox_MV])
            ])
        ])

        # Container for asset tree selection
        self.asset_tree_container = v.Container(children=[
            v.Row(no_gutters=True, children=[
                v.Col(lg=2, children=[self.asset_tree_heading]),
                v.Col(lg=10, children=[self.asset_tree_explanation])
            ]),
            v.Row(lg=12, children=[
                v.Col(lg=6, children=[self.select_asset_tree]),
                v.Col(lg=6, children=[self.text_field_asset_tree_copy])
            ])
        ])

        # Container for the lower part of the UI
        self.lower_part_container = v.Container(children=[
            v.Row(no_gutters=True, children=[self.priority_color_heading, self.threshold_dialog, self.help_threshold]),
            v.Row(children=[
                v.Col(children=[
                    v.Card(height=65, color='red', children=[
                        v.Row(children=[
                            v.Spacer(),
                            v.Col(lg=6, children=[self.red_color_heading]),
                            v.Col(lg=3, children=[self.text_field_red_threshold]),
                            v.Spacer()
                        ])
                    ])
                ]),
                v.Col(children=[
                    v.Card(height=65, color='yellow', children=[
                        v.Row(children=[
                            v.Spacer(),
                            v.Col(lg=6, children=[self.yellow_color_heading]),
                            v.Col(lg=3, children=[self.text_field_yellow_threshold]),
                            v.Spacer()
                        ])
                    ])
                ])
            ]),
            v.Row(children=[v.Col(lg=12, children=[self.expansion_capsules_gaps])]),
            v.Row(children=[v.Col(lg=12, children=[self.signal_table])]),
            v.Row(lg=12, children=[
                v.Spacer(),
                v.Col(lg=2, children=[self.recalculate_button]),
                v.Col(lg=4, children=[self.export_button]),
                v.Col(lg=2, children=[self.clear_button]),
                v.Col(lg=2, children=[self.execute_button])
            ]),
            v.Row(children=[v.Col(lg=12, children=[self.progress_bar])])
        ])

        # FINAL CONTAINER
        self.final_container = v.Container(children=[
            self.AppBar,
            v.Card(no_gutters=True, color='grey lighten-4', children=[
                v.Row(no_gutters=True, children=[v.Col(children=[self.time_container])]),
                v.Row(no_gutters=True, children=[v.Col(children=[self.checkbox_container])]),
                v.Row(no_gutters=True, children=[v.Col(children=[self.asset_tree_container])]),
                v.Row(no_Gutters=True, children=[v.Col(children=[self.lower_part_container])]),
            ])
        ])
        return self.final_container
