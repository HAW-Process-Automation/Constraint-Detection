from contextlib import contextmanager

from seeq import spy
from seeq import sdk
from seeq.spy.assets import Asset
import datetime

import pytz
import json


def get_asset_trees_from_workbook_id(workbook_id):
    items = spy.search({
        'Type': 'Signal'
    }, workbook=workbook_id, quiet=True)
    items = items[items['Path'].notnull()]
    items.reset_index(inplace=True)
    asset_tree_name_list = []
    for i in range(len(items.index)):
        split_index = items['Path'][i].split(" >> ")
        asset_tree_name = split_index[0]
        if asset_tree_name not in asset_tree_name_list:
            asset_tree_name_list.append(asset_tree_name)

    return asset_tree_name_list


def get_start_end_display_range(url):
    """
    Parameters
    ----------
    url: str
        The url from the active worksheet

    Returns
    -------
    start: str
        The start of the display range of the active worksheet
    end: str
        The end of the display range of the active worksheet
    """

    worksheet = spy.utils.get_analysis_worksheet_from_url(url, quiet=True)
    start = worksheet.display_range['Start']
    start = start.isoformat(timespec="seconds")
    end = worksheet.display_range['End']
    end = end.isoformat(timespec="seconds")

    return start, end


def get_start_end_display_range_from_ids(workbook_id, worksheet_id, workstep_id):
    """
    This function gets the start and end of the worksheet display range.

    Parameters
    ----------
    workbook_id: str
        The ID of the workbook
    worksheet_id: str
        The ID of the worksheet
    workstep_id: str
        The ID of the workstep

    Returns
    -------
    start_time: str
        The start of the display range of the active worksheet
    end_time: str
        The end of the display range of the active worksheet
    """
    workbooks_api = sdk.WorkbooksApi(spy.client)
    data = workbooks_api.get_workstep(workbook_id=workbook_id, worksheet_id=worksheet_id, workstep_id=workstep_id).to_dict()['data']
    data_dict = json.loads(data)
    tz = data_dict['state']['stores']['sqExportODataPanelStore']['exportTimeZone']['name']
    start = data_dict['state']['stores']['sqDurationStore']['displayRange']['start']
    end = data_dict['state']['stores']['sqDurationStore']['displayRange']['end']
    start_time = datetime.datetime.fromtimestamp(start/1000).astimezone(pytz.timezone(tz))
    end_time = datetime.datetime.fromtimestamp(end/1000).astimezone(pytz.timezone(tz))
    start_time = start_time.strftime('%Y-%m-%dT%H:%M:%S')
    end_time = end_time.strftime('%Y-%m-%dT%H:%M:%S')
    
    return start_time, end_time


def pull_signals_from_asset_tree(workbook_id, start_time, end_time, asset_tree_name):
    """
    This function pulls all signals between start_time and end_time from the original asset tree in the specified
    workbook.

    Parameters
    ----------
    workbook_id: str
        The ID of the workbook
    start_time: str
        The start time for the analysis
    end_time: str
        The end time for the analysis
    asset_tree_name: str
        The name of the original asset tree

    Returns
    -------
    pulled_signals_df: pd.DataFrame
        The dataframe that contains all signals from the original asset tree
    """
    # search for asset tree by defining the path and workbook
    items = spy.search({
        'Path': asset_tree_name,
        'Type': 'Signal'
    }, workbook=workbook_id, quiet=True)

    # pull the signals from the search results
    pulled_signals_df = spy.pull(items, start=start_time, end=end_time, grid='30 s', quiet=True)

    return pulled_signals_df


def push_signals(workbook_id, joined_signals_correct_naming_df):
    """
    This function pushes all signals from the original asset tree and the saturation/constraint signals to the
    workbook.

    Parameters
    ----------
    workbook_id: str
        The ID of the workbook
    joined_signals_correct_naming_df: pd.DataFrame
        The dataframe that contains the pulled signals from the original asset tree and the saturation/constraint
        signals with formatted signal names

    Returns
    -------
    push_results: pd.DataFrame
        The dataframe with the push results.
    """
    # push joined_signals_correct_naming_df dataframe to workbench
    # dataframe contains the pulled signals and the saturation signals for the analysed time interval
    push_results = spy.push(data=joined_signals_correct_naming_df, workbook=workbook_id, quiet=True)
    return push_results

class OnlyPushWorksheetsPatch:
    """
    This class is used when pushing the metadata with push_metadata(). It prevents all existing worksheets in the
    workbook from getting archived.
    """
    original_pull_worksheet_ids = spy.workbooks.Workbook._pull_worksheet_ids
    original_worksheet_push = spy.workbooks.Worksheet.push

    def patched_pull_worksheet_ids(self, *args, **kwargs):
        return []

    def patched_worksheet_push(self, session, pushed_workbook_id, item_map,
                               datasource_output, existing_worksheet_ids, *args, **kwargs):
        return OnlyPushWorksheetsPatch.original_worksheet_push(
                self, session, pushed_workbook_id, item_map, datasource_output, {}, *args, **kwargs)

    @classmethod
    def on(cls):
        spy.workbooks.Workbook._pull_worksheet_ids = cls.patched_pull_worksheet_ids
        spy.workbooks.Worksheet.push = cls.patched_worksheet_push

    @classmethod
    def off(cls):
        spy.workbooks.Workbook._pull_worksheet_ids = cls.original_pull_worksheet_ids
        spy.workbooks.Worksheet.push = cls.original_worksheet_push


def saturation_treemap(metadata, start, end, short_gap, short_capsule, checkbox_op, checkbox_pv, checkbox_sp,
                       checkbox_mv):
    """
    This function generates the new asset tree with all signals, High Constraint Condition, Medium Constraint Condition
    and Contraint/Saturation Indices. Controller Outputs will be referred to as OP, Process Variables will be referred
    to as PV, Setpoints will be referred to as SP and Manipulated Variables will be referred to as MV. The function also
    generates a new worksheet called "Constraint Detection Treemap View".

    Parameters
    ----------
    metadata: pd.DataFrame
        The dataframe that contains the push results and the 'Build Asset' and 'Build Path' column
    start: str
        The start time for the analysis
    end: str
        The end time for the analysis
    short_gap: str
        String that specifies short gaps which should be closed in the High/Medium Contraint Condition
    short_capsule: str
        String that specifies short capsules which should be ignored in the High/Medium Contraint Condition
    checkbox_op: bool
        True if OP checkbox is checked. False if OP checkbox is not checked.
    checkbox_pv: bool
        True if PV checkbox is checked. False if PV checkbox is not checked.
    checkbox_sp: bool
        True if SP checkbox is checked. False if SP checkbox is not checked.
    checkbox_mv: bool
        True if MV checkbox is checked. False if MV checkbox is not checked.

    Returns
    -------
    spy.assets.build(Treemap_AssetStructure, metadata=metadata, quiet=True): pd.DataFrame
        The dataframe with the metadata for the new asset tree with all signals, conditions and constraint indices
    """

    time_capsule = '$condition = condition(capsule("' + start + '", "' + end + '"))'
    medium_saturation_condition = '($sat==2).merge(' + short_gap + ').removeShorterThan(' + short_capsule + ')'
    high_saturation_condition = '($sat==3).merge(' + short_gap + ').removeShorterThan(' + short_capsule + ')'
    saturation_index_condition = '$saturation = ($sat>0).merge(' + short_gap + ').removeShorterThan(' + short_capsule + ')'

    class Treemap_AssetStructure(Asset):
        """
        This class creates all signal (OP, PV, SP, MV), the corresponding constraint/saturation signals and the
        constraint/saturation indices. It also creates the High Constraint Condition and Medium Constraint Condition.
        The signals and conditions are arranged in an asset tree using the metadata. The asset tree is visualized in
        treemap in a new worksheet.
        """

        @Asset.Attribute()
        def OP(self, metadata):
            return metadata[metadata['Name'].str.endswith('Controller Output')]

        @Asset.Attribute()
        def PV(self, metadata):
            return metadata[metadata['Name'].str.endswith('Process Variable')]

        @Asset.Attribute()
        def SP(self, metadata):
            return metadata[metadata['Name'].str.endswith('Setpoint')]

        @Asset.Attribute()
        def MV(self, metadata):
            return metadata[metadata['Name'].str.endswith('Manipulated Variable')]

        @Asset.Attribute()
        def Mode(self, metadata):
            return metadata[metadata['Name'].str.endswith('Mode')]

        @Asset.Attribute()
        def OP_Saturation_Signal(self, metadata):
            return metadata[metadata['Name'].str.contains('Controller Output Saturation')]

        @Asset.Attribute()
        def PV_Constraint_Signal(self, metadata):
            return metadata[metadata['Name'].str.contains('Process Variable Saturation')]

        @Asset.Attribute()
        def SP_Constraint_Signal(self, metadata):
            return metadata[metadata['Name'].str.contains('Setpoint Saturation')]

        @Asset.Attribute()
        def MV_Constraint_Signal(self, metadata):
            return metadata[metadata['Name'].str.contains('Manipulated Variable Saturation')]

        @Asset.Attribute()
        def Medium_OP_Saturation(self, metadata):
            return {
                'Type': 'Condition',
                'Formula': medium_saturation_condition,
                'Formula Parameters': {
                    '$sat': self.OP_Saturation_Signal(metadata),
                }
            }

        @Asset.Attribute()
        def High_OP_Saturation(self, metadata):
            return {
                'Type': 'Condition',
                'Formula': high_saturation_condition,
                'Formula Parameters': {
                    '$sat': self.OP_Saturation_Signal(metadata),
                }
            }

        @Asset.Attribute()
        def Medium_PV_Constraint(self, metadata):
            return {
                'Type': 'Condition',
                'Formula': medium_saturation_condition,
                'Formula Parameters': {
                    '$sat': self.PV_Constraint_Signal(metadata),
                }
            }

        @Asset.Attribute()
        def High_PV_Constraint(self, metadata):
            return {
                'Type': 'Condition',
                'Formula': high_saturation_condition,
                'Formula Parameters': {
                    '$sat': self.PV_Constraint_Signal(metadata),
                }
            }

        @Asset.Attribute()
        def Medium_SP_Constraint(self, metadata):
            return {
                'Type': 'Condition',
                'Formula': medium_saturation_condition,
                'Formula Parameters': {
                    '$sat': self.SP_Constraint_Signal(metadata),
                }
            }

        @Asset.Attribute()
        def High_SP_Constraint(self, metadata):
            return {
                'Type': 'Condition',
                'Formula': high_saturation_condition,
                'Formula Parameters': {
                    '$sat': self.SP_Constraint_Signal(metadata),
                }
            }

        @Asset.Attribute()
        def Medium_MV_Constraint(self, metadata):
            return {
                'Type': 'Condition',
                'Formula': medium_saturation_condition,
                'Formula Parameters': {
                    '$sat': self.MV_Constraint_Signal(metadata),
                }
            }

        @Asset.Attribute()
        def High_MV_Constraint(self, metadata):
            return {
                'Type': 'Condition',
                'Formula': high_saturation_condition,
                'Formula Parameters': {
                    '$sat': self.MV_Constraint_Signal(metadata),
                }
            }

        @Asset.Attribute()
        def OP_Saturated_Time_Percentage(self, metadata):
            return {
                'Type': 'Signal',
                'Formula': time_capsule + saturation_index_condition + f'''$saturation.aggregate(percentDuration(), 
                $condition, middleKey(), 0s)''',
                'Formula Parameters': {
                    '$sat': self.OP_Saturation_Signal(metadata),
                }
            }

        @Asset.Attribute()
        def PV_Constrained_Time_Percentage(self, metadata):
            return {
                'Type': 'Signal',
                'Formula': time_capsule + saturation_index_condition + f'''$saturation.aggregate(percentDuration(), 
                $condition, middleKey(), 0s)''',
                'Formula Parameters': {
                    '$sat': self.PV_Constraint_Signal(metadata),
                }
            }

        @Asset.Attribute()
        def SP_Constrained_Time_Percentage(self, metadata):
            return {
                'Type': 'Signal',
                'Formula': time_capsule + saturation_index_condition + f'''$saturation.aggregate(percentDuration(), 
                $condition, middleKey(), 0s)''',
                'Formula Parameters': {
                    '$sat': self.SP_Constraint_Signal(metadata),
                }
            }

        @Asset.Attribute()
        def MV_Constrained_Time_Percentage(self, metadata):
            return {
                'Type': 'Signal',
                'Formula': time_capsule + saturation_index_condition + f'''$saturation.aggregate(percentDuration(), 
                $condition, middleKey(), 0s)''',
                'Formula Parameters': {
                    '$sat': self.MV_Constraint_Signal(metadata),
                }
            }

        @Asset.Display()
        def Ambient_Conditions(self, metadata, analysis):

            if checkbox_op:
                worksheet = analysis.worksheet('OP Saturation Detection Treemap')
                workstep = worksheet.workstep('OP_Treemap')
                workstep.view = 'Treemap'
                workstep.display_range = {
                    'Start': start,
                    'End': end
                }

                workstep.display_items = [{
                    'Item': self.OP()
                }, {
                    'Item': self.OP_Saturation_Signal()
                }, {
                    'Item': self.OP_Saturated_Time_Percentage(),
                    'Samples Display': 'Bars',
                    'Line Width': 20
                }, {
                    'Item': self.High_OP_Saturation(),
                    'Color': '#ff0000'
                }, {
                    'Item': self.Medium_OP_Saturation(),
                    'Color': '#ffdd52'
                }]

            if checkbox_pv:
                worksheet = analysis.worksheet('PV Constraint Detection Treemap')
                workstep = worksheet.workstep('PV_Treemap')
                workstep.view = 'Treemap'
                workstep.display_range = {
                    'Start': start,
                    'End': end
                }

                workstep.display_items = [{
                    'Item': self.PV()
                }, {
                    'Item': self.PV_Constraint_Signal()
                }, {
                    'Item': self.PV_Constrained_Time_Percentage(),
                    'Samples Display': 'Bars',
                    'Line Width': 20
                }, {
                    'Item': self.High_PV_Constraint(),
                    'Color': '#ff0000'
                }, {
                    'Item': self.Medium_PV_Constraint(),
                    'Color': '#ffdd52'
                }]

            if checkbox_sp:
                worksheet = analysis.worksheet('SP Constraint Detection Treemap')
                workstep = worksheet.workstep('SP_Treemap')
                workstep.view = 'Treemap'
                workstep.display_range = {
                    'Start': start,
                    'End': end
                }

                workstep.display_items = [{
                    'Item': self.SP()
                }, {
                    'Item': self.SP_Constraint_Signal()
                }, {
                    'Item': self.SP_Constrained_Time_Percentage(),
                    'Samples Display': 'Bars',
                    'Line Width': 20
                }, {
                    'Item': self.High_SP_Constraint(),
                    'Color': '#ff0000'
                }, {
                    'Item': self.Medium_SP_Constraint(),
                    'Color': '#ffdd52'
                }]

            if checkbox_mv:
                worksheet = analysis.worksheet('MV Constraint Detection Treemap')
                workstep = worksheet.workstep('MV_Treemap')
                workstep.view = 'Treemap'
                workstep.display_range = {
                    'Start': start,
                    'End': end
                }

                workstep.display_items = [{
                    'Item': self.MV()
                }, {
                    'Item': self.MV_Constraint_Signal()
                }, {
                    'Item': self.MV_Constrained_Time_Percentage(),
                    'Samples Display': 'Bars',
                    'Line Width': 20
                }, {
                    'Item': self.High_MV_Constraint(),
                    'Color': '#ff0000'
                }, {
                    'Item': self.Medium_MV_Constraint(),
                    'Color': '#ffdd52'
                }]
            return workstep

    return spy.assets.build(Treemap_AssetStructure, metadata=metadata, quiet=True)


@contextmanager
def patching():
    OnlyPushWorksheetsPatch.on()
    try:
        yield
    finally:
        OnlyPushWorksheetsPatch.off()


def push_metadata(workbook_id, build_df):
    """
    This function pushes the metadata for the new asset structure to the workbook.

    Parameters
    ----------
    workbook_id: str
        The ID of the workbook
    build_df: pd.DataFrame
        The dataframe with the metadata for the new asset tree
    """

    # push build_df with asset structure to the workbench
    # controller signals and saturation detection results are now arranged as in the original asset tree.
    # A copy asset tree was generated to not clutter the original asset tree with random signals and conditions
    with patching():
        spy.push(metadata=build_df, workbook=workbook_id, quiet=True)


def recalculate_change_short_gap_capsule(asset_tree_name, original_asset_tree_name, start_time, end_time, workbook_id,
                                         short_gap, short_capsule):
    """
    This function recalculates the formula for the High/Medium Constraint Condition and the Constrained/Saturated Time
    Percentage. It pulls all saturation/constraint signals from the new asset tree, so that the Constrained/Saturated
    Time Percentage for the table in the UI can be recalculated as well.

    Parameters
    ----------
    asset_tree_name: str
        User specified name for the new asset tree
    original_asset_tree_name: str
        Selected asset tree for the analysis
    start_time: str
        The start time for the analysis
    end_time: str
        The end time for the analysis
    workbook_id: str
        The ID of the workbook
    short_gap: str
        String that specifies short gaps which should be closed in the High/Medium Constraint Condition
    short_capsule: str
        String that specifies short capsules which should be ignored in the High/Medium Constraint Condition

    Returns
    -------
    pulled_signals_df: pd.DataFrame
        A dataframe with all saturation/constraint signals in the new asset tree
    """
    if asset_tree_name == '':
        asset_tree_name = original_asset_tree_name + ' Constraint Monitor'

    saturation_signal_df = spy.search({
        'Path': asset_tree_name,
        'Name': 'Signal',
        'Type': 'Signal'
    }, workbook=workbook_id, all_properties=True, quiet=True)

    pulled_signals_df = spy.pull(saturation_signal_df, start=start_time, end=end_time, grid='30 s', quiet=True)

    index_df = spy.search({
        'Path': asset_tree_name,
        'Name': 'Time Percentage'
    }, workbook=workbook_id, all_properties=True, quiet=True)

    start = pulled_signals_df.index[0].isoformat()
    end = pulled_signals_df.index[-1].isoformat()

    time_capsule = '$condition = condition(capsule("' + start + '", "' + end + '"))'
    saturation_index_condition = '$saturation = ($sat>0).merge('+short_gap+').removeShorterThan('+short_capsule+')'
    index_formula = time_capsule + saturation_index_condition + f'''$saturation.aggregate(percentDuration(), 
    $condition, middleKey(), 0s)'''
    index_df['Formula'] = index_formula

    conditions_df = spy.search({
        'Path': asset_tree_name,
        'Type': 'Condition'
    }, workbook=workbook_id, all_properties=True, quiet=True)

    for i in range(len(conditions_df.index)):
        if 'High' in conditions_df['Name'][i]:
            conditions_df['Formula'][i] = '($sat==3).merge(' + short_gap + ').removeShorterThan(' + short_capsule + ')'
        elif 'Medium' in conditions_df['Name'][i]:
            conditions_df['Formula'][i] = '(($sat==2).intersect($sat.derivative()==0)).merge(' + short_gap + \
                                          ').removeShorterThan(' + short_capsule + ') '

    spy.push(metadata=conditions_df, workbook=workbook_id, quiet=True)
    spy.push(metadata=index_df, workbook=workbook_id, quiet=True)

    return pulled_signals_df
