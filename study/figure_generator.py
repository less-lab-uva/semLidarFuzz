import csv
import itertools
import argparse
import json
import glob
import math
import os
import sys
from collections import defaultdict
from itertools import combinations

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from matplotlib.transforms import ScaledTranslation


def parse_args():
    p = argparse.ArgumentParser(
        description='Figure Generator')
    p.add_argument("-full_data",
                   help="Path to the data directory produced by the tool",
                   nargs='?')

    return p.parse_args()


def getModelComboKeys(models):
    combos = []
    for n in range(1, len(models) + 1):
        combos += list(combinations(models, n))

    comboKeys = []
    for combo in combos:
        comboKeys.append("_".join(combo))

    return comboKeys


def normalize_name(mut_name):
    parts = mut_name.split('_')
    new_name = ''
    for part in parts:
        if part == 'SCENE':
            continue
        new_name += part[0] + part[1:].lower() + ' '
    return new_name[:-1]


def set_bar_text(ax, bar, zero_height=0.8):
    height = bar.get_height()
    label = str(int(height))
    for _ in range(1 * (3 - len(label))):
        label = ' ' + label
    y = zero_height if height == 0 else height * 1.02  # mult becomes add in log scale
    ax.text(bar.get_x() + bar.get_width() * 0.2, y, label, va='bottom', rotation=90)


def set_barh_text(ax, bar, zero_height=0.8, bar_height_factor=0.1):
    width = bar.get_width()
    label = str(int(width))
    for _ in range(1 * (3 - len(label))):
        label = ' ' + label
    x = zero_height if width == 0 else width * 1.02  # mult becomes add in log scale
    ax.text(x, bar.get_y() + bar.get_height() * bar_height_factor, label, va='bottom')


def set_bar_text_no_log(ax, bar, zero_height=0.8):
    height = bar.get_height()
    label = '%0.2f' % height
    for _ in range(1 * (3 - len(label))):
        label = ' ' + label
    y = zero_height if height == 0 else height + .05
    ax.text(bar.get_x() + bar.get_width() * 0.2, y, label, va='bottom')


def format_amount(amount, total):
    # return '%d (%d\\%%)' % (amount, 100 * amount / total) if amount > 0 else '---'
    return '%d' % amount if amount > 0 else '---'


def format_amount_perc_only(amount, total):
    return '(%d\\%%)' % (round(100 * amount / total)) if amount > 0 else '~'


def fix_names(combo, model_name):
    for model in model_name:
        combo = combo.replace(model, model_name[model])
    combo = combo.replace('_', ', ')
    return combo


if __name__ == '__main__':
    print("\n\n------------------------------")
    print("\n\nStarting Figure Generator\n\n")
    os.makedirs('figures', exist_ok=True)
    args = parse_args()
    full_data_dir = args.full_data
    mutation_folders = list(glob.glob(full_data_dir + os.sep + '*'))
    acc_failure_counts = {}
    jacc_failure_counts = {}
    acc_overlap_counts = {}
    jacc_overlap_counts = {}
    mut_names = []
    bucketKeysInvariant = None
    modelsInvariant = None
    mut_order = [
        'ADD_ROTATE',
        'ADD_MIRROR_ROTATE',
        'SCENE_REMOVE',
        'VEHICLE_INTENSITY',
        'VEHICLE_DEFORM',
        'VEHICLE_SCALE',
        'SIGN_REPLACE'
    ]
    bucket_labels = {
        'bucket_0': '<0.1',
        'bucket_1': '(0.1, 1]',
        'bucket_2': '(1, 2]',
        'bucket_3': '(2, 3]',
        'bucket_4': '(3, 4]',
        'bucket_5': '(4, 5]',
        'bucket_6': '(5, 100]',
    }
    model_order = ['cyl', 'spv', 'js3c_gpu', 'sal', 'spv']
    model_name = {
        'cyl': 'Cylinder3D',
        'spv': 'SPVNAS',
        'js3c_gpu': 'JSC3-Net',
        'sal': 'SalsaNext',
        'sq3': 'SqueezeSegV3'
    }
    model_short_name = {
        'cyl': 'Cyl',
        'spv': 'SPV',
        'js3c_gpu': 'JSC3',
        'sal': 'Salsa',
        'sq3': 'Squeeze'
    }
    mutation_count = {}
    duplicate_counts = {}
    acc_overlap_ignoring_salsa_and_squeeze = {mut_name: 0 for mut_name in mut_order}
    jacc_overlap_ignoring_salsa_and_squeeze = {mut_name: 0 for mut_name in mut_order}
    all_combos = getModelComboKeys(model_short_name.keys())
    all_combos = [fix_names(combo, model_short_name) for combo in all_combos]
    acc_overlap_by_group = {i+1: defaultdict(int) for i in range(len(model_short_name))}
    jacc_overlap_by_group = {i+1: defaultdict(int) for i in range(len(model_short_name))}
    acc_overlap_2_suts = {model: defaultdict(int) for model in model_short_name}
    jacc_overlap_2_suts = {model: defaultdict(int) for model in model_short_name}
    total_time = {}
    sut_time = {}
    time_per_model = {model: defaultdict(int) for model in model_short_name}
    for mut_fol in mutation_folders:
        if not os.path.isdir(mut_fol):
            continue
        print('Looking in folder:', mut_fol)
        mut_name = mut_fol[mut_fol.rfind(os.sep)+1:-20]  # the timestamp at the end is 20 chars, remove
        mut_names.append(mut_name)
        print('Gathering data for', normalize_name(mut_name))

        final_data_file = glob.glob(mut_fol + '%s**%sfinalData.json' % (os.sep, os.sep))[0]
        print("Getting data from {}".format(final_data_file))
        # Opening JSON file
        f = open(final_data_file)
        # returns JSON object as a dictionary
        data = json.load(f)
        mutation_count[mut_name] = data['count']
        # Get mutation keys and bucket keys
        mutations = data["mutations"]
        bucketKeys = list(sorted(data["buckets"], reverse=False))  # ensure they are in sorted order, highest to lowest
        if bucketKeysInvariant is None:
            bucketKeysInvariant = bucketKeys
        elif not bucketKeys == bucketKeysInvariant:
            raise RuntimeError('The data in this folder contains differing bucket counts per mutation, aborting')
        models = data["models"]
        if modelsInvariant is None:
            modelsInvariant = models
        elif not models == modelsInvariant:
            raise RuntimeError('The data in this folder contains differing models per mutation, aborting')
        total_time[mut_name] = data['seconds']
        time_per_model[mut_name] = data['modelTime']
        sut_time[mut_name] = sum(data['modelTime'].values())
        modelCombos = getModelComboKeys(models)
        acc_failure_counts[mut_name] = {model: {} for model in models}
        jacc_failure_counts[mut_name] = {model: {} for model in models}
        acc_overlap_counts[mut_name] = defaultdict(int)
        jacc_overlap_counts[mut_name] = defaultdict(int)
        for mutationKey in mutations:  # each of the files only actually has one mutation
            duplicate_counts[mut_name] = data[mutationKey]['duplicates']
            acc_data = data[mutationKey]["accuracy"]
            jacc_data = data[mutationKey]["jaccard"]
            acc_total_per_model = {}
            jacc_total_per_model = {}
            for model in models:
                acc_total = 0
                jacc_total = 0
                for bucket in bucketKeys:
                    acc_failure_counts[mut_name][model][bucket] = acc_data[bucket]['total_' + model]
                    acc_total += acc_data[bucket]['total_' + model]
                    jacc_failure_counts[mut_name][model][bucket] = jacc_data[bucket]['total_' + model]
                    jacc_total += jacc_data[bucket]['total_' + model]
                acc_total_per_model[model] = acc_total
                jacc_total_per_model[model] = jacc_total
            if len(set(acc_total_per_model.values())) != 1:
                raise RuntimeError('The data in this folder contains differing number of acc results per model, aborting')
            if len(set(jacc_total_per_model.values())) != 1:
                raise RuntimeError('The data in this folder contains differing number of acc results per model, aborting')
            if acc_total_per_model == jacc_total_per_model:
                mutation_count[mut_name] = list(acc_total_per_model.values())[0]
            else:
                raise RuntimeError('The data in this folder contains differing results for acc and jacc, aborting')
            last_bucket = bucketKeys[-1]
            for combo, amount in acc_data[last_bucket]['model_overlap'].items():
                adj = combo.replace('js3c_', 'js3c-')
                suts = adj.split('_')
                for i in range(len(suts)):
                    if 'js3c-' in suts[i]:
                        suts[i] = suts[i].replace('-', '_')
                count = len(suts)
                acc_overlap_counts[mut_name][count] += amount
                acc_overlap_by_group[count][fix_names(combo, model_short_name)] += amount
                if count == 2 and ('sal' in combo and 'sq3' in combo):
                    acc_overlap_ignoring_salsa_and_squeeze[mut_name] += amount
                if count >= 2:
                    for sut1, sut2 in itertools.combinations(suts, 2):
                        acc_overlap_2_suts[sut1][sut2] += amount
                        acc_overlap_2_suts[sut2][sut1] += amount

            for combo, amount in jacc_data[last_bucket]['model_overlap'].items():
                adj = combo.replace('js3c_', 'js3c-')
                suts = adj.split('_')
                for i in range(len(suts)):
                    if 'js3c-' in suts[i]:
                        suts[i] = suts[i].replace('-', '_')
                count = len(suts)
                jacc_overlap_counts[mut_name][count] += amount
                jacc_overlap_by_group[count][fix_names(combo, model_short_name)] += amount
                if count == 2 and ('sal' in combo and 'sq3' in combo):
                    jacc_overlap_ignoring_salsa_and_squeeze[mut_name] += amount
                if count >= 2:
                    for sut1, sut2 in itertools.combinations(suts, 2):
                        jacc_overlap_2_suts[sut1][sut2] += amount
                        jacc_overlap_2_suts[sut2][sut1] += amount

    mut_names = [mut_name for mut_name in mut_order if mut_name in mut_names]  # reorder to be consistent
    longest_mut_name_len = max([len(normalize_name(mut_name)) for mut_name in mut_names])
    acc_all_failure_counts = {model: {} for model in modelsInvariant}
    jacc_all_failure_counts = {model: {} for model in modelsInvariant}
    for model in modelsInvariant:
        for bucket in bucketKeysInvariant:
            acc_all_failure_counts[model][bucket] = sum([acc_failure_counts[mut_name][model][bucket] for mut_name in mut_names])
            jacc_all_failure_counts[model][bucket] = sum([jacc_failure_counts[mut_name][model][bucket] for mut_name in mut_names])
    acc_all_overlap_counts = defaultdict(int)
    jacc_all_overlap_counts = defaultdict(int)
    for mut_name in mut_names:
        for count, amount in acc_overlap_counts[mut_name].items():
            acc_all_overlap_counts[count] += amount
        for count, amount in jacc_overlap_counts[mut_name].items():
            jacc_all_overlap_counts[count] += amount

    # https://stackoverflow.com/questions/3899980/how-to-change-the-font-size-on-a-matplotlib-plot
    font = {'weight': 'bold', 'size': 14}

    matplotlib.rc('font', **font)
    print('Generating figures for all mutations')
    hatches = ['x', '*', '.', '-', '/', '+', '\\']
    colors = ['tab:cyan', 'tab:olive', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:red']
    row_count = 8
    subfig_count = (len(mut_names) + 1)
    column_count = int(math.ceil(subfig_count / row_count))
    fig = plt.figure(figsize=(12, 24), constrained_layout=True)
    # fig, axes = plt.subplots(row_count, column_count)
    subfigs = fig.subfigures(row_count, column_count, wspace=0.05, hspace=0.05, squeeze=False)
    bucket_offset = 2  # since the first two buckets are very low values, skip them in the figure
    X = np.arange((len(bucketKeysInvariant) - bucket_offset))
    width = 1.0 / (len(modelsInvariant) + 1)
    for sub_idx in range(0, subfig_count):
        mut_ind = sub_idx
        row = sub_idx // column_count
        column = sub_idx % column_count
        subfig = subfigs[row, column]
        axes = subfig.subplots(1, 2, sharey=True)
        if mut_ind < len(mut_names):
            mut_name = mut_names[mut_ind]
            title = normalize_name(mut_name)
            cur_counts = [acc_failure_counts[mut_name], jacc_failure_counts[mut_name]]
        else:  # do total
            title = 'Total'
            cur_counts = [acc_all_failure_counts, jacc_all_failure_counts]
        print('Generating figures for', title)
        subfig.suptitle(title, fontweight='bold')
        ind_fig = plt.figure(figsize=(12.8, 9.6))
        # ind_fig.suptitle(title, fontweight='bold')
        ind_axes = ind_fig.subplots(1, 2, sharey=True)
        # ylim_top = None
        for in_idx, (name, all_failure_counts) in enumerate(zip(['Accuracy', 'Jaccard'], cur_counts)):
            # Bar chart style adapted from https://www.tutorialspoint.com/matplotlib/matplotlib_bar_plot.htm
            for ax in [axes[in_idx], ind_axes[in_idx]]:
                for index, model in enumerate(modelsInvariant):
                    amounts = [all_failure_counts[model][bucket] for bucket in bucketKeysInvariant[bucket_offset:]]
                    bars = ax.bar(X + width * index, amounts, width=width, hatch=hatches[index], color=colors[index], log=True)
                    for bar in bars:
                        set_bar_text(ax, bar)
                # ax.set_title('Failures found for different levels of $\\epsilon$ ' + name)
                ax.set_ylabel('Number of Failures (Log)')
                ax.set_xlabel(name + ' drop threshold (%)')
                # ax.set_ylim(bottom=0.5, top=ylim_top)
                ax.set_title(name)
                # _, ylim_top = ax.get_ylim()
                ax.set_xticks([x + width * (len(modelsInvariant) - 1) / 2.0 for x in X])  # move tick to center
                ax.set_xticklabels([bucket_labels[bucket] for bucket in bucketKeysInvariant[bucket_offset:]])
                ax.legend(labels=[model_name[model] for model in modelsInvariant])
        ind_fig.tight_layout()
        ind_fig.savefig('./figures/%s.png' % title, bbox_inches='tight', dpi=100)
        plt.close(ind_fig)
    # fig.savefig('outname.png', bbox_inches='tight', dpi=100)
    fig.savefig('./figures/failure_counts.png', dpi=100)
    plt.close(fig)

    print('Generating figures for all mutations horiz')
    fig = plt.figure(figsize=(12, 24), constrained_layout=True)
    # fig, axes = plt.subplots(row_count, column_count)
    subfigs = fig.subfigures(row_count, column_count, wspace=0.05, hspace=0.05, squeeze=False)
    X = -np.arange((len(bucketKeysInvariant) - bucket_offset))
    for sub_idx in range(0, subfig_count):
        mut_ind = sub_idx
        row = sub_idx // column_count
        column = sub_idx % column_count
        subfig = subfigs[row, column]
        axes = subfig.subplots(1, 2, sharey=True)
        if mut_ind < len(mut_names):
            mut_name = mut_names[mut_ind]
            title = normalize_name(mut_name)
            cur_counts = [acc_failure_counts[mut_name], jacc_failure_counts[mut_name]]
        else:  # do total
            title = 'Total'
            cur_counts = [acc_all_failure_counts, jacc_all_failure_counts]
        print('Generating figures for', title)
        subfig.suptitle(title, fontweight='bold')
        ind_fig = plt.figure(figsize=(16, 10))
        # ind_fig.suptitle(title, fontweight='bold')
        ind_axes = ind_fig.subplots(1, 2)
        # ylim_top = None
        for in_idx, (name, all_failure_counts) in enumerate(zip(['Accuracy', 'Jaccard'], cur_counts)):
            # Bar chart style adapted from https://www.tutorialspoint.com/matplotlib/matplotlib_bar_plot.htm
            for ax in [axes[in_idx], ind_axes[in_idx]]:
                for index, model in enumerate(modelsInvariant):
                    amounts = [all_failure_counts[model][bucket] for bucket in bucketKeysInvariant[bucket_offset:]]
                    bars = ax.barh(X + width * index, amounts, height=width, hatch=hatches[index], color=colors[index], log=True)
                    for bar in bars:
                        set_barh_text(ax, bar)
                # ax.set_title('Failures found for different levels of $\\epsilon$ ' + name)
                ax.set_xlabel('Number of Failures (Log)')
                ax.set_ylabel(name + ' drop threshold (%)')
                # ax.set_ylim(bottom=0.5, top=ylim_top)
                ax.set_title(name)
                # _, ylim_top = ax.get_ylim()
                ax.set_yticks([x + width * (len(modelsInvariant) - 1) / 2.0 for x in X])  # move tick to center
                ax.set_yticklabels([bucket_labels[bucket] for bucket in bucketKeysInvariant[bucket_offset:]])
                # https://stackoverflow.com/questions/28615887/how-to-move-a-tick-label-in-matplotlib
                # apply offset transform to all x ticklabels.
                dy = 5 / 72.
                dx = 0 / 72.
                offset = ScaledTranslation(dx, dy, fig.dpi_scale_trans)
                for label in ax.yaxis.get_majorticklabels():
                    label.set_transform(label.get_transform() + offset)
                ax.legend(labels=[model_name[model] for model in modelsInvariant])
        ind_fig.tight_layout()
        ind_fig.savefig('./figures/%s_horiz.png' % title, bbox_inches='tight', dpi=100)
        plt.close(ind_fig)
    # fig.savefig('outname.png', bbox_inches='tight', dpi=100)
    fig.savefig('./figures/failure_counts_horiz.png', dpi=100)
    plt.close(fig)


    print('Generating figure for only largest failures')
    # Only bucket 6
    fig = plt.figure(figsize=(20, 10))
    axes = fig.subplots(1, 2, sharey=True)
    X = np.arange(len(mut_names))
    for in_idx, (name, failure_counts) in \
        enumerate(zip(['Accuracy', 'Jaccard'], [acc_failure_counts, jacc_failure_counts])):
        ax = axes[in_idx]
        for index, model in enumerate(modelsInvariant):
            amounts = [failure_counts[mut_name][model][bucketKeysInvariant[-1]] for mut_name in mut_names]
            bars = ax.bar(X + width * index, amounts, width=width, hatch=hatches[index], color=colors[index],
                          log=True)
            for bar in bars:
                set_bar_text(ax, bar)
            ax.set_ylabel('Number of Failures (Log)')
            ax.set_xlabel(name)
            # ax.set_ylim(bottom=0.5, top=ylim_top)
            ax.set_title(name)
            # _, ylim_top = ax.get_ylim()
            ax.set_xticks([x + width * (len(modelsInvariant) - 1) / 2.0 for x in X])  # move tick to center
            ax.set_xticklabels([normalize_name(mut_name) for mut_name in mut_names], rotation=15)
            ax.legend(labels=[model_name[model] for model in modelsInvariant])
    fig.savefig('./figures/biggest_failures.png', bbox_inches='tight', dpi=100)
    plt.close(fig)

    print('Generating figure for only largest failures')
    # Only bucket 6
    fig = plt.figure(figsize=(16, 10))
    axes = fig.subplots(1, 2, sharey=True)
    X = -np.arange(len(mut_names))
    for in_idx, (name, failure_counts) in \
        enumerate(zip(['Accuracy', 'Jaccard'], [acc_failure_counts, jacc_failure_counts])):
        ax = axes[in_idx]
        for index, model in enumerate(modelsInvariant):
            amounts = [failure_counts[mut_name][model][bucketKeysInvariant[-1]] for mut_name in mut_names]
            bars = ax.barh(X + width * index, amounts, height=width, hatch=hatches[index], color=colors[index],
                          log=True)
            for bar in bars:
                set_barh_text(ax, bar, bar_height_factor=0)
            ax.set_xlabel('Number of Failures (Log)')
            # ax.set_ylabel(name)
            # ax.set_ylim(bottom=0.5, top=ylim_top)
            ax.set_title(name)
            # _, ylim_top = ax.get_ylim()
            ax.set_yticks([x + width * (len(modelsInvariant) - 1) / 2.0 for x in X])  # move tick to center
            # ax.set_yticks([x for x in X])  # move tick to center
            ax.set_yticklabels([normalize_name(mut_name) for mut_name in mut_names], rotation=45)
            # https://stackoverflow.com/questions/28615887/how-to-move-a-tick-label-in-matplotlib
            # apply offset transform to all x ticklabels.
            dy = 5 / 72.
            dx = 0 / 72.
            offset = ScaledTranslation(dx, dy, fig.dpi_scale_trans)
            for label in ax.yaxis.get_majorticklabels():
                label.set_transform(label.get_transform() + offset)
            ax.legend(labels=[model_name[model] for model in modelsInvariant])
    fig.savefig('./figures/biggest_failures_horiz.png', bbox_inches='tight', dpi=100)
    plt.close(fig)

    print('Generating figures for false positive rates')
    subfig_count = (len(mut_names) + 1)
    row_count = 8
    column_count = int(math.ceil(subfig_count / row_count))
    fig = plt.figure(figsize=(12, 24), constrained_layout=True)
    # fig, axes = plt.subplots(row_count, column_count)
    subfigs = fig.subfigures(row_count, column_count, wspace=0.05, hspace=0.05, squeeze=False)
    overlap_table_row = {'Accuracy': {},
                         'Jaccard': {}}
    overlap_table_cutoff_row = {'Accuracy': {},
                         'Jaccard': {}}
    cutoff_V = 3
    for sub_idx in range(0, subfig_count):
        mut_ind = sub_idx
        row = sub_idx // column_count
        column = sub_idx % column_count
        subfig = subfigs[row, column]
        axes = subfig.subplots(1, 2, sharey=True)
        if mut_ind < len(mut_names):
            mut_name = mut_names[mut_ind]
            title = normalize_name(mut_name)
            cur_counts = [acc_overlap_counts[mut_name], jacc_overlap_counts[mut_name]]
        else:  # do total
            title = 'Total'
            cur_counts = [acc_all_overlap_counts, jacc_all_overlap_counts]
        print('Generating overlap figures for', title)
        subfig.suptitle(title, fontweight='bold')
        ind_fig = plt.figure(figsize=(12.8, 6.2))
        # ind_fig = plt.figure()
        ind_fig.suptitle(title, fontweight='bold')
        ind_axes = ind_fig.subplots(1, 2, sharey=True)
        # ylim_top = None
        pie_hatches = ['.', '/', 'x', '*', 'O.']
        for in_idx, (name, overlap_counts) in enumerate(zip(['Accuracy', 'Jaccard'], cur_counts)):
            # Bar chart style adapted from https://www.tutorialspoint.com/matplotlib/matplotlib_bar_plot.htm
            for ax in [axes[in_idx], ind_axes[in_idx]]:
                if len(overlap_counts) == 0:
                    labels = ['No Failures Found']
                    amounts = [1]
                    total = 0
                    overlap_table_row[name][title] = '0 & --- & --- & --- & --- & ---'
                    overlap_table_cutoff_row[name][title] = '--- & ---'

                    ax.pie(amounts, shadow=False, startangle=90, labels=labels, colors=['tab:gray'],
                           labeldistance=0,
                           textprops=dict(rotation_mode='anchor', va='center', ha='left'))  # https://stackoverflow.com/questions/52020474/matplotlib-pie-chart-how-to-center-label
                else:
                    counts = sorted(overlap_counts.keys())
                    # print(overlap_counts)
                    amounts = [overlap_counts[count] for count in counts]
                    total = sum(amounts)
                    overlap_table_row[name][title] = \
                        '%d & %s & %s & %s & %s & %s' % \
                        (total,
                         format_amount(overlap_counts[1], total),
                         format_amount(overlap_counts[2], total),
                         format_amount(overlap_counts[3], total),
                         format_amount(overlap_counts[4], total),
                         format_amount(overlap_counts[5], total))
                    overlap_table_cutoff_row[name][title] = \
                        '%s & %s' % \
                        (
                         format_amount(
                             sum([overlap_counts[i] for i in range(len(overlap_counts)+1) if 1 <= i < cutoff_V]), total),
                         format_amount(
                             sum([overlap_counts[i] for i in range(len(overlap_counts)+1) if i >= cutoff_V]), total))
                    if title == 'Total':
                        overlap_table_row[name]['\\%'] = \
                            '~ & %s & %s & %s & %s & %s' % \
                            (format_amount_perc_only(overlap_counts[1], total),
                             format_amount_perc_only(overlap_counts[2], total),
                             format_amount_perc_only(overlap_counts[3], total),
                             format_amount_perc_only(overlap_counts[4], total),
                             format_amount_perc_only(overlap_counts[5], total))
                        overlap_table_cutoff_row[name]['\\%'] = \
                            '%s & %s' % \
                            (format_amount_perc_only(
                                sum([overlap_counts[i] for i in range(len(overlap_counts)+1) if 1 <= i < cutoff_V]), total),
                             format_amount_perc_only(
                                 sum([overlap_counts[i] for i in range(len(overlap_counts)+1) if i >= cutoff_V]), total))
                    labels = ['%s SUT%s\n%d (%0.2f)' %
                              (count, 's' if count > 1 else '', overlap_counts[count],
                               100 * overlap_counts[count] / total)
                              if overlap_counts[count] > 0 else ''
                              for count in counts]
                    explode = None if overlap_counts == 1 else \
                        [0.1 if index == 0 else 0 for index in range(len(counts))]
                    patches, _ = ax.pie(amounts, shadow=False,
                                           startangle=90, labels=labels, explode=explode, counterclock=False,
                                           colors=[colors[count - 1] for count in counts])
                    cur_hatches = [pie_hatches[count - 1] for count in counts]
                    # https://towardsdatascience.com/how-to-fill-plots-with-patterns-in-matplotlib-58ad41ea8cf8
                    for i in range(len(patches)):
                        patches[i].set(hatch=cur_hatches[i])
                # ax.axis('equal')
                ax.set_title('%s\n%d Total' % (name, total))
                # ax.legend(labels=labels)
        ind_fig.tight_layout()
        ind_fig.savefig('./figures/%s Overlap.png' % title, bbox_inches='tight', dpi=100)
        plt.close(ind_fig)
    # fig.savefig('outname.png', bbox_inches='tight', dpi=100)
    fig.savefig('./figures/overlap_counts.png', dpi=100)
    plt.close(fig)

    print('Generating Overlap By SUT Figures')
    subfig_count = 5
    row_count = 5
    column_count = int(math.ceil(subfig_count / row_count))
    fig = plt.figure(figsize=(12, 24), constrained_layout=True)
    # fig, axes = plt.subplots(row_count, column_count)
    subfigs = fig.subfigures(row_count, column_count, wspace=0.05, hspace=0.05, squeeze=False)
    for sub_idx in range(0, subfig_count):
        mut_ind = sub_idx
        row = sub_idx // column_count
        column = sub_idx % column_count
        subfig = subfigs[row, column]
        axes = subfig.subplots(1, 2, sharey=True)
        count = sub_idx + 1
        title='%d SUT%s' % (count, 's' if count > 1 else '')
        subfig.suptitle(title)
        ind_fig = plt.figure(figsize=(12.8, 6.2))
        # ind_fig = plt.figure()
        ind_fig.suptitle(title, fontweight='bold')
        ind_axes = ind_fig.subplots(1, 2, sharey=True)
        # ylim_top = None
        pie_hatches = ['.', '/', 'x', '*', 'O.']
        bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
        kw = dict(arrowprops=dict(arrowstyle="-"),
                  bbox=bbox_props, zorder=0, va="center")
        for in_idx, (name, overlap_counts) in enumerate(zip(['Accuracy', 'Jaccard'],
                                                            [acc_overlap_by_group[count], jacc_overlap_by_group[count]])):
            for ax in [axes[in_idx], ind_axes[in_idx]]:
                if len(overlap_counts) == 0:
                    labels = ['No Failures Found']
                    amounts = [1]
                    total = 0
                    ax.pie(amounts, shadow=False, startangle=90, labels=labels, colors=['tab:gray'],
                           labeldistance=0,
                           textprops=dict(rotation_mode='anchor', va='center', ha='left'))  # https://stackoverflow.com/questions/52020474/matplotlib-pie-chart-how-to-center-label
                else:
                    groups = sorted(overlap_counts.keys())
                    amounts = [overlap_counts[group] for group in groups]
                    total = sum(amounts)
                    labels = ['%s\n%d (%d%%)' %
                              (group, overlap_counts[group], 100 * overlap_counts[group] / total) for group in groups]
                    patches, _ = ax.pie(amounts, shadow=False,
                                        startangle=90, counterclock=False,
                                        colors=[colors[all_combos.index(group) % len(colors)] for group in groups])
                    cur_hatches = [pie_hatches[all_combos.index(group) % len(pie_hatches)] for group in groups]
                    # https://towardsdatascience.com/how-to-fill-plots-with-patterns-in-matplotlib-58ad41ea8cf8
                    for i, p in enumerate(patches):
                        patches[i].set(hatch=cur_hatches[i])
                    ax.legend(patches, labels)
                # ax.axis('equal')
                ax.set_title('%s\n%d Total' % (name, total))
                # ax.legend(labels=labels)
        ind_fig.tight_layout()
        ind_fig.savefig('./figures/%s_overlap.png' % title, bbox_inches='tight', dpi=100)
        # fig.savefig('outname.png', bbox_inches='tight', dpi=100)
    fig.savefig('./figures/overlap_by_sut.png', dpi=100)


    print('Printing LaTeX Overlap Table')
    print('------ Accuracy -----')
    overlap_table = '''
\\begin{table}[htbp]
\\caption{TITLE False Positive Thresholds}
    \\centering
    \\begin{tabular}{|r|c|c|c|c|c|c|}
    \\hline
    Mutation & Total & 1 SUT & 2 SUTs & 3 SUTs & 4 SUTs & 5 SUTs \\\\ \\hline
    DATA
    \\end{tabular}
    \\label{tab:SHORT_false_positive}
\\end{table}
'''
    acc_string = ''
    for title, row in overlap_table_row['Accuracy'].items():
        if title == 'Total':
            acc_string += '\\hline ' + title + '&' + row + ' \\\\ \n'
        else:
            acc_string += title + '&' + row + ' \\\\ \\hline \n'
    print(overlap_table.replace('DATA', acc_string).replace('SHORT', 'acc').replace('TITLE', 'Accuracy'))
    print('----- Jaccard -----')
    jacc_string = ''
    for title, row in overlap_table_row['Jaccard'].items():
        if title == 'Total':
            jacc_string += '\\hline ' + title + '&' + row + ' \\\\ \n'
        else:
            jacc_string += title + '&' + row + ' \\\\ \\hline \n'
    print(overlap_table.replace('DATA', jacc_string).replace('SHORT', 'jacc').replace('TITLE', 'Jaccard'))

    overlap_both_table = '''
\\begin{table*}[htbp]
\\caption{False Positive Thresholds}
    \\centering
    \\begin{tabular}{|r|c|c|c|c|c|c||c|c|c|c|c|c|}
    \\hline
    ~ & \\multicolumn{6}{c||}{Accuracy} & \\multicolumn{6}{c|}{Jaccard} \\\\ 
    Mutation & Total & 1 SUT & 2 SUTs & 3 SUTs & 4 SUTs & 5 SUTs & Total & 1 SUT & 2 SUTs & 3 SUTs & 4 SUTs & 5 SUTs\\\\ \\hline
    DATA
    \\end{tabular}
    \\label{tab:SHORT_false_positive}
\\end{table*}
    '''
    print('----- Both -----')
    both_string = ''
    for title in overlap_table_row['Accuracy']:
        if title == 'Total':
            both_string += '\\hline ' + title + '&' + overlap_table_row['Accuracy'][title] + '&' \
                       + overlap_table_row['Jaccard'][title] + ' \\\\  \n'
        else:
            both_string += title + '&' + overlap_table_row['Accuracy'][title] + '&' \
                       + overlap_table_row['Jaccard'][title] + ' \\\\ \\hline \n'
    print(overlap_both_table.replace('DATA', both_string).replace('SHORT', 'both'))

    print('Printing LaTeX Overlap by SUT Table')

    overlap_both_table_reduced = '''
    \\begin{table}[htbp]
    \\caption{False Positive Counts, V=CUTOFF_V}
        \\centering
        \\begin{tabular}{|r|c|c||c|c|c|}
        \\hline
        ~ & \\multicolumn{2}{c||}{Accuracy} & \\multicolumn{2}{c|}{Jaccard} \\\\ 
        Mutation & TP & FP & TP & FP\\\\ \\hline \\hline
        DATA
        \\end{tabular}
        \\label{tab:SHORT_false_positive_reduced}
    \\end{table}
        '''
    print('----- Both Reduced -----')
    both_string = ''
    for title in overlap_table_cutoff_row['Accuracy']:
        if title == 'Total':
            both_string += '\\hline ' + title + '&' + overlap_table_cutoff_row['Accuracy'][title] + '&' \
                           + overlap_table_cutoff_row['Jaccard'][title] + ' \\\\  \n'
        else:
            both_string += title + '&' + overlap_table_cutoff_row['Accuracy'][title] + '&' \
                           + overlap_table_cutoff_row['Jaccard'][title] + ' \\\\ \\hline \n'
    print(overlap_both_table_reduced.replace('DATA', both_string).replace('SHORT', 'both')
          .replace('CUTOFF_V', '%d' % cutoff_V))

    print('Printing LaTeX Overlap by SUT Table')

    vote_together_table = '''
\\begin{table}[htbp]
\\caption{Number of times SUTs Voted Together: TITLE}
    \\centering
    \\begin{tabular}{|r|c|c|c|c|}
    \\hline
    DATA
    \\end{tabular}
    \\label{tab:SHORT_voting_together}
\\end{table}
'''
    for short, long, overlap in zip(['acc', 'jacc'],
                                    ['Accuracy', 'Jaccard'],
                                    [acc_overlap_2_suts, jacc_overlap_2_suts]):
        tog_string = '~'
        header = list(reversed(list(model_name.keys())[1:]))
        rows = list(list(model_name.keys())[:-1])
        for model in header:
            tog_string += ' & %s' % model_name[model]
        tog_string += '\\\\ \\hline \n'
        total = 0
        for ind1, model1 in enumerate(rows):  # row
            for ind2, model2 in enumerate(header):  # column
                total += overlap[model1][model2]
        for ind1, model1 in enumerate(rows):  # row
            tog_string += '%s' % model_name[model1]
            for ind2, model2 in enumerate(header):  # column
                if ind1 + ind2 >= len(header):
                    tog_string += ' & ~'
                else:
                    tog_string += ' & %d (%d\\%%)' % (overlap[model1][model2], round(100*overlap[model1][model2] / total))
            tog_string += '\\\\ \\hline \n'
        print('----- %s SUT Voting Together -----' % long)
        print(vote_together_table.replace('DATA', tog_string).replace('SHORT', short).replace('TITLE', long))

    print('----- False Positive Rate ignoring Sal and Sq3 together')
    cur_counts = [acc_all_overlap_counts, jacc_all_overlap_counts]
    cur_ignore = [acc_overlap_ignoring_salsa_and_squeeze, jacc_overlap_ignoring_salsa_and_squeeze]
    for counts, (ignore, name) in zip(cur_counts, zip(cur_ignore, ['Accuracy', 'Jaccard'])):
        total = sum(counts.values())
        new_single = counts[1] + sum(ignore.values())
        print('New True Positive Rate for V=2 under %s metric: %d/%d (%d%%)' %
              (name, new_single, total, round(100*new_single / total)))

    print('----- Timing Information -----')
    timing_table = '''
\\begin{table*}[htbp]
\\caption{Time taken for SUT and Tool per mutation (seconds)}
    \\centering
    \\begin{tabular}{|r|c|c|c|c|c|c|c|}
    \\hline
    DATA
    \\end{tabular}
    \\label{tab:time_taken}
\\end{table*}
    '''
    time_string = '~'
    for mut_name in mut_order:
        time_string += ' & ' + normalize_name(mut_name)
    time_string += '\\\\ \\hline\n'
    for model in model_order:
        time_string += model_name[model]
        for mut_name in mut_order:
            time_string += ' & %0.2f' % (time_per_model[mut_name][model] / mutation_count[mut_name])
        time_string += '\\\\ \\hline\n'
    time_string += '\hline\n Generation'
    generation_times = []
    labels = ['']
    for mut_name in mut_order:
        generation_time = (total_time[mut_name] - sut_time[mut_name]) / mutation_count[mut_name]
        generation_times.append(generation_time)
        labels.append(normalize_name(mut_name))
        time_string += ' & %0.2f' % generation_time
    labels.append('')
    time_string += '\\\\ \\hline\n'
    # ind_fig = plt.figure(figsize=(12.8, 6.2))
    ind_fig = plt.figure()
    ind_fig.suptitle('Average Time to Generate per Mutation', fontweight='bold')
    ax = plt.gca()
    X = np.arange(len(mut_order))
    bars = ax.bar(X, generation_times, color=colors[:len(generation_times)], hatch=hatches[:len(generation_times)])
    for bar in bars:
        set_bar_text_no_log(ax, bar)
    # https://stackoverflow.com/questions/63723514/userwarning-fixedformatter-should-only-be-used-together-with-fixedlocator
    ticks_loc = ax.get_xticks().tolist()
    ax.xaxis.set_major_locator(mticker.FixedLocator(ticks_loc))
    ax.set_xticklabels(labels, rotation=15)
    ax.set_xlabel('Mutation')
    ax.set_ylabel('Average Time per Test Case (s)')
    ind_fig.tight_layout()
    ind_fig.savefig('./figures/time_per_mutation.png', bbox_inches='tight', dpi=100)
    print(timing_table.replace('DATA', time_string))

    print('----- Average Time per SUT -----')
    for model in model_order:
        print('%s: %0.2f seconds' % (model_name[model].rjust(20, ' '), sum([time_per_model[mut_name][model] for mut_name in mut_names]) / sum([mutation_count[mut_name] for mut_name in mut_names])))
    print()

    print('----- Average Time per Mutation -----')
    for mut_name in mut_order:
        print('%s: %0.2f seconds' % (normalize_name(mut_name).rjust(longest_mut_name_len, ' '),
                                     (total_time[mut_name] - sut_time[mut_name]) / mutation_count[mut_name]))
    print()

    print('----- Duplicate Counts -----')
    for mut_name in mut_order:
        print('%s: %d' % (normalize_name(mut_name).rjust(longest_mut_name_len, ' '), duplicate_counts[mut_name]))
    print()
