import pandas as pd
import numpy as np


def generate_short_gap_capsule(short_gap_number, short_gap_unit, short_capsule_number, short_capsule_unit):
    """
    This function creates string that specify the short gaps and capsules for the High/Medium Constraint Conditions.

    Parameters
    ----------
    short_gap_number: int
        Integer which specifies the length of the gaps that should be closed in the High/Medium Contraint Conditions
    short_gap_unit: str
        Unit (seconds. minutes, hours) of the short gaps
    short_capsule_number: int
        Integer which specifies the length of the capsules that should be ignored in the High/Medium Contraint
        Conditions
    short_capsule_unit: str
        Unit (seconds. minutes, hours) of the short capsules

    Returns
    -------
    short_gap: str
        String that contains the length and unit of the short gaps e.g. '2min'
    short_capsule: str
        String that contains the length and unit of the short capsules e.g. '2min'
    """
    if short_gap_unit == 'second(s)':
        short_gap = str(short_gap_number) + 's'
    elif short_gap_unit == 'minute(s)':
        short_gap = str(short_gap_number) + 'min'
    elif short_gap_unit == 'hour(s)':
        short_gap = str(short_gap_number) + 'h'

    if short_capsule_number == 0:
        short_capsule = str(0.1) + 's'
    if short_capsule_number > 0:
        if short_capsule_unit == 'second(s)':
            short_capsule = str(short_capsule_number) + 's'
        elif short_capsule_unit == 'minute(s)':
            short_capsule = str(short_capsule_number) + 'min'
        elif short_capsule_unit == 'hour(s)':
            short_capsule = str(short_capsule_number) + 'h'

    return short_gap, short_capsule


def saturation_detection(pulled_signals_df, checkbox_op, checkbox_pv, checkbox_sp, checkbox_mv, lower_threshold,
                         upper_threshold, short_gap_number, short_gap_unit, short_capsule_number, short_capsule_unit):
    """
    This function analyzes every signal in the pulled_signals_df for saturation/constraints and adds the saturation
    signal to the saturation_signals_df and the saturation/constraint index to the saturation_index_df.

    Parameters
    ----------
    pulled_signals_df: pd.DataFrame
        The dataframe with all signals in the original asset tree
    checkbox_op: bool
        True if OP checkbox is checked. False if OP checkbox is not checked.
    checkbox_pv: bool
        True if PV checkbox is checked. False if PV checkbox is not checked.
    checkbox_sp: bool
        True if SP checkbox is checked. False if SP checkbox is not checked.
    checkbox_mv: bool
        True if MV checkbox is checked. False if MV checkbox is not checked.
    lower_threshold: float
        The threshold which is used to set the yellow priority colour in treemap and to create the Medium Constraint
        Condition.
    upper_threshold: float
        The threshold which is used to set the red priority colour in treemap and to create the High Constraint
        Condition.
    short_gap_number: int
        Integer which specifies the length of the gaps that should be closed
    short_gap_unit: str
        Unit (seconds. minutes, hours) of the short gaps
    short_capsule_number:int
        Integer which specifies the length of the capsule that should be ignored
    short_capsule_unit: str
        Unit (seconds. minutes, hours) of the short capsules

    Returns
    -------
    saturation_signals_df: pd.DataFrame
        The dataframe which contains all saturation signals.
    saturation_index_df: pd.DataFrame
        The dataframe which contains signal name and contraint index
    """
    signals_for_analysis = []
    if checkbox_op:
        signals_for_analysis = signals_for_analysis + ['Controller Output']
    if checkbox_pv:
        signals_for_analysis = signals_for_analysis + ['Process Variable']
    if checkbox_sp:
        signals_for_analysis = signals_for_analysis + ['Setpoint']
    if checkbox_mv:
        signals_for_analysis = signals_for_analysis + ['Manipulated Variable']

    if short_capsule_number == 0:
        short_capsule = 0
    elif short_capsule_number > 0:
        if short_capsule_unit == 'second(s)':
            short_capsule = short_capsule_number
        elif short_capsule_unit == 'minute(s)':
            short_capsule = short_capsule_number * 60
        elif short_capsule_unit == 'hour(s)':
            short_capsule = short_capsule_number * 60 * 60

    if short_gap_number == 0:
        short_gap = 0
    elif short_gap_number > 0:
        if short_gap_unit == 'second(s)':
            short_gap = short_gap_number
        elif short_gap_unit == 'minute(s)':
            short_gap = short_gap_number * 60
        elif short_gap_unit == 'hour(s)':
            short_gap = short_gap_number * 60 * 60

    # initiate empty dataframe for saturation signals saturation/constraint index
    saturation_signals_df = pd.DataFrame()
    saturation_index_df = pd.DataFrame(columns=['Signal Name and Path', 'Signal', 'Path', 'Index'])

    # extended period of saturation: at least 3 consecutive samples have to be saturated to detect saturation
    ext_length = 3

    # Loop goes through all signals in the pull_data dataframe
    for x in range(len(pulled_signals_df.columns)):

        if 'Mode' in pulled_signals_df.columns[x]:
            # auto manual mode data should not be analysed by the saturation detection
            # mode columns are skipped and the loop starts with the next column
            continue

        if 'Controller Output' in pulled_signals_df.columns[x]:
            if 'Controller Output' in signals_for_analysis:
                pass
            else:
                continue

        if 'Process Variable' in pulled_signals_df.columns[x]:
            if 'Process Variable' in signals_for_analysis:
                pass
            else:
                continue

        if 'Setpoint' in pulled_signals_df.columns[x]:
            if 'Setpoint' in signals_for_analysis:
                pass
            else:
                continue

        if 'Manipulated Variable' in pulled_signals_df.columns[x]:
            if 'Manipulated Variable' in signals_for_analysis:
                pass
            else:
                continue

        if 'Process Variable' not in pulled_signals_df.columns[x] and 'Controller Output' not in \
                pulled_signals_df.columns[x] and 'Setpoint' not in pulled_signals_df.columns[
            x] and 'Manipulated Variable' not in pulled_signals_df.columns[x] and 'Mode' not in \
                pulled_signals_df.columns[x]:
            raise RuntimeError(
                f'''Check if your asset tree has the required layout. Accepted signal names are "Controller Output", 
                "Process Variable", "Setpoint", "Manipulated Variable" and "Mode". See User Guide for more 
                information on the required layout''')

            # format the current column as a numpy array
        df_column = np.asarray(pulled_signals_df.iloc[:, x])
        # get length of the column
        df_column_length = len(df_column)
        # calculate derivative of the column data
        df_column_derivative = np.gradient(df_column)

        # calculate minimum and maximum of the column data
        df_column_min = min(df_column)
        df_column_max = max(df_column)

        # delta_sat is the width of the saturation band
        delta_sat = 0.005 * (abs(df_column_max - df_column_min))

        # initiate variables for saturation counters, extended saturation periods and saturation signal
        max_sat_counter = 0
        min_sat_counter = 0
        sat_signal = np.zeros([df_column_length, 1])

        # initiate variables for gap and capsule counters
        capsule = 0
        gap = 0
        capsule_counter = 0
        gap_counter = 0

        # Loop for saturation detection: Loop goes through every value and checks whether its is in the upper or lower
        # saturation band and if the derivative is zero. If 3 consecutive values are in the same saturation band,
        # then saturation is detected.
        for i in range(len(df_column)):

            if df_column[i] > df_column_max - delta_sat and df_column_derivative[i] == 0:
                # current value is in the max saturation band
                # start max_sat_counter
                max_sat_counter = max_sat_counter + 1

                if max_sat_counter == ext_length:
                    # saturation detected if 3 consecutive samples were saturated --> extended saturation period
                    # set max_sat_signal to 1
                    sat_signal[i - ext_length:i, 0] = 1

                elif max_sat_counter > ext_length:
                    # set sat_signal to 1
                    sat_signal[i, 0] = 1

            elif df_column[i] < df_column_min + delta_sat and df_column_derivative[i] == 0:
                # current value is in the min saturation band
                # start min_sat_counter
                min_sat_counter = min_sat_counter + 1

                if min_sat_counter == ext_length:
                    # saturation detected if 3 consecutive samples were saturated --> extended saturation period
                    # set sat_signal to 1
                    sat_signal[i - ext_length:i, 0] = 1

                elif min_sat_counter > ext_length:
                    # set min_sat_signal to 1
                    sat_signal[i, 0] = 1

            else:
                # no saturation, reset counters
                max_sat_counter = 0
                min_sat_counter = 0

        sat_signal_copy = sat_signal.copy()
        for a in range(len(sat_signal_copy)):
            if sat_signal_copy[a, 0] == 0 and sat_signal_copy[a - 1, 0] == 1:
                gap = 30
                gap_counter = 1
            elif sat_signal_copy[a, 0] == 0 and sat_signal_copy[a - 1, 0] == 0:
                gap = gap + 30
                gap_counter = gap_counter + 1
            elif sat_signal_copy[a, 0] == 1 and sat_signal_copy[a - 1, 0] == 0:
                gap = gap + 30
                gap_counter = gap_counter + 1
                if gap < short_gap:
                    sat_signal_copy[a - gap_counter:a, 0] = 1
            elif sat_signal_copy[a, 0] == 1 and sat_signal_copy[a - 1, 0] == 1:
                gap = 0
                gap_counter = 0

        for a in range(len(sat_signal_copy)):
            if sat_signal_copy[a, 0] == 0 and sat_signal_copy[a - 1, 0] == 1:
                capsule_counter = capsule_counter + 1
                if capsule < short_capsule:
                    sat_signal_copy[a - capsule_counter:a, 0] = 0
            elif sat_signal_copy[a, 0] == 0 and sat_signal_copy[a - 1, 0] == 0:
                capsule = 0
                capsule_counter = 0
            elif sat_signal_copy[a, 0] == 1 and sat_signal_copy[a - 1, 0] == 0:
                capsule = 0
                capsule_counter = 0
            elif sat_signal_copy[a, 0] == 1 and sat_signal_copy[a - 1, 0] == 1:
                capsule = capsule + 30
                capsule_counter = capsule_counter + 1

        # saturation index in % is calculated
        saturation_index = float(sum(sat_signal_copy) / df_column_length * 100)

        # the saturation index is compared to the thresholds. the saturation signal is multiplied with a factor if
        # the index lies above the thresholds. the factors are used for the conditions/colors in treemap
        # 2 = yellow
        # 3 = red
        if lower_threshold < saturation_index < upper_threshold:
            sat_signal = 2 * sat_signal
        elif saturation_index >= upper_threshold:
            sat_signal = 3 * sat_signal

        # sat_signal is converted into a dataframe
        sat_signal_df = pd.DataFrame(sat_signal)
        # renaming the dataframe so that every saturation signal has a unique name
        signal_name = pulled_signals_df.columns[x] + ' Saturation'
        sat_signal_df.rename(columns={0: signal_name}, inplace=True)
        # join the saturation dataframes to saturation_signals_df
        saturation_signals_df = saturation_signals_df.join(sat_signal_df, how='outer')

        data = [{'Signal Name and Path': pulled_signals_df.columns[x], 'Index': round(saturation_index, 1)}]
        current_saturation_index_df = pd.DataFrame(data)
        saturation_index_df = pd.concat([saturation_index_df, current_saturation_index_df], ignore_index=True)

    return saturation_signals_df, saturation_index_df


pd.options.mode.chained_assignment = None


def generate_constraint_index_table(saturation_index_df, new_asset_tree_name):
    """
    This functions generates a dictionary with signal name, signal path and constraint index data which is handed over
    to v.DataTable.

    Parameters
    ----------
    saturation_index_df: pd.DataFrame
        The dataframe that contains the unformatted signal names and constraint index
    new_asset_tree_name: str
        User specified name for the new asset tree

    Returns
    --------
    saturation_index_dict: dictionary
        The dictionary that contains the signal names, signal paths and constraint index
    """

    saturation_index_df = saturation_index_df.sort_values(by=['Index'], ascending=False, ignore_index=True)
    saturation_index_df = saturation_index_df.head(30)

    for i in range(len(saturation_index_df.index)):
        # split 'Signal Name and Path' colum and get the length
        split_index = saturation_index_df['Signal Name and Path'][i].split(" >> ")
        split_index_length = len(split_index)

        # new column name is the asset name + signal name
        new_signal_name = split_index[split_index_length - 1]
        saturation_index_df['Signal'][i] = new_signal_name

        # loop creates the path column
        for x in range(split_index_length - 1):
            if x == 0:
                if new_asset_tree_name == '':
                    # highest level of the path. The word "Copy" is appended if the user has not specified a name for
                    # the asset tree copy.
                    new_path_name_part = split_index[x] + ' Copy >> '
                    saturation_index_df['Path'][i] = new_path_name_part
                elif new_asset_tree_name != '':
                    # highest level of the path. The user specified name for the asset tree copy is used.
                    new_path_name_part = new_asset_tree_name + ' >> '
                    saturation_index_df['Path'][i] = new_path_name_part

            elif x < split_index_length - 2:
                # intermediate levels of the path
                new_path_name_part = split_index[x] + ' >> '
                saturation_index_df['Path'][i] = saturation_index_df['Path'][i] + new_path_name_part

            elif x == split_index_length - 2:
                # lowest level of the path
                new_path_name_part = split_index[x]
                saturation_index_df['Path'][i] = saturation_index_df['Path'][i] + new_path_name_part

    saturation_index_df_final = saturation_index_df.drop(['Signal Name and Path'], axis=1)
    saturation_index_dict = saturation_index_df_final.to_dict('records')

    return saturation_index_dict


def generate_metadata(joined_signals_df, new_asset_tree_name):
    """
    This function generates metadata for the new asset tree and formats the column names in the joined_signals_df.

    Parameters
    ----------
    joined_signals_df: pd.DataFrame
        The dataframe that contains the pulled signals from the original asset tree and the saturation/constraint
        signals
    new_asset_tree_name: str
        User specified name for the new asset tree

    Returns
    --------
    metadata: pd.DataFrame
        The dataframe that contains the 'Build Asset' and 'Build Path' column
    joined_signals_df: pd.DataFrame
        The dataframe that contains the pulled signals from the original asset tree and the saturation/constraint
        signals with formatted names so that the dataframe can be pushed to the workbook
    """
    # initiate dataframe with name, asset and path to create metadata for signals
    metadata = pd.DataFrame(columns=['Build Asset', 'Build Path'], index=range(len(joined_signals_df.columns)))

    # loop iterates through all signal names and gets the name, asset, and path
    # the signals names in joined_signals_df are changed so that spy.push doesn't get confused
    for i in range(len(joined_signals_df.columns)):
        # split current column name and get the length
        split_index = joined_signals_df.columns[i].split(" >> ")
        split_index_length = len(split_index)

        # new column name is the asset name + signal name
        new_column_name = split_index[split_index_length - 2] + ' ' + split_index[split_index_length - 1]
        joined_signals_df.rename(columns={joined_signals_df.columns[i]: new_column_name}, inplace=True)
        # metadata asset is the second last value of the split_index
        metadata['Build Asset'][i] = split_index[split_index_length - 2]
        # loop creates the path column
        for x in range(split_index_length - 2):
            if x == 0:
                if split_index_length > 3:
                    if new_asset_tree_name == '':
                        # highest level of the path. The word "Copy" is appended if the user has not specified a name
                        # for the asset tree copy.
                        new_path_name_part = split_index[x] + ' Copy >> '
                        metadata['Build Path'][i] = new_path_name_part
                    elif new_asset_tree_name != '':
                        # highest level of the path. The user specified name for the asset tree copy is used.
                        new_path_name_part = new_asset_tree_name + ' >> '
                        metadata['Build Path'][i] = new_path_name_part

                elif split_index_length == 3:
                    if new_asset_tree_name == '':
                        # highest level of the path. The word "Copy" is appended if the user has not specified a name
                        # for the asset tree copy.
                        new_path_name_part = split_index[x] + ' Copy'
                        metadata['Build Path'][i] = new_path_name_part
                    elif new_asset_tree_name != '':
                        # highest level of the path. The user specified name for the asset tree copy is used.
                        new_path_name_part = new_asset_tree_name
                        metadata['Build Path'][i] = new_path_name_part

            elif x < split_index_length - 3:
                # intermediate levels of the path
                new_path_name_part = split_index[x] + ' >> '
                metadata['Build Path'][i] = metadata['Build Path'][i] + new_path_name_part

            elif x == split_index_length - 3:
                # lowest level of the path
                new_path_name_part = split_index[x]
                metadata['Build Path'][i] = metadata['Build Path'][i] + new_path_name_part

    return metadata, joined_signals_df
