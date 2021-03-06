# -*- coding: utf-8 -*-
# !/usr/bin/env python

import numpy as np
import plotly
import plotly.io as pio
import plotly.plotly  as py
import plotly.graph_objs as go
from numpy import cos, sin, sqrt
from pymatgen.electronic_structure.core import Spin
from pymatgen.io.vasp import Vasprun


# 旋转函数
def rotation(cart, theta):
    rotation_matrix = np.array([[cos(theta), -sin(theta), 0],
                                [sin(theta), cos(theta), 0],
                                [0, 0, 1]])
    return np.matmul(rotation_matrix, cart)


if __name__ == "__main__":
    # 在生成kmesh脚本中，kpoints所分成的个数
    split_number = 24
    root = "/mnt/c/Users/a/OneDrive/Calculation_Data/Mg2C_Graphene/Paper_results/Nodal_Line/"

    # 将vasprun.xml转换成能够使用的数据
    vasp_data = []
    band_data = []
    for num_data in range(split_number):
        vasprun_file_name = 'vasprun_split_part_{}.xml'.format(num_data)
        kpoints_file_name = 'KPOINTS_split_part_{}.xml'.format(num_data)
        vasp_data.append(Vasprun("{}".format(root + vasprun_file_name)))
        band_data.append(vasp_data[num_data].get_band_structure(
            "{}".format(root + kpoints_file_name),
            efermi=vasp_data[num_data].efermi,
            line_mode=False))

    # 选取到空间坐标
    rec_coordinate = []
    for num_rec in range(len(vasp_data)):
        rec_coordinate.extend(vasp_data[num_rec].actual_kpoints)
    rec_coordinate = np.array(rec_coordinate)[:, 0:2]

    # 形变矩阵，将等腰直角三角形变成等边三角形
    shearing_matrix = np.array([[1, 1 / 2],
                                [0, sqrt(3) / 2]])
    rec_Position_shearing = []
    for rec_cart in rec_coordinate:
        rec_Position_shearing.append(np.matmul(shearing_matrix, rec_cart))
    rec_Position = np.array(rec_Position_shearing)

    # 能量数据采集，能带51和53
    Energy_Band_51 = []
    for energy_band in band_data:
        energy_data = energy_band.bands[Spin.up][51]
        Energy_Band_51.extend(energy_data.tolist())
    Energy_Band_51 = np.array(Energy_Band_51)

    Energy_Band_53 = []
    for energy_band in band_data:
        energy_data = energy_band.bands[Spin.up][53]
        Energy_Band_53.extend(energy_data.tolist())
    Energy_Band_53 = np.array(Energy_Band_53)
    # Energy_Band_tot = np.concatenate((Energy_Band_51, Energy_Band_53), axis=0)

    # 能量数据和位置数据合并
    data_51 = np.column_stack((rec_Position, Energy_Band_51))
    data_53 = np.column_stack((rec_Position, Energy_Band_53))

    data_tot = []
    for rot_num in range(6):
        rot_data = []
        for rot_cart in data_51:
            rot_data.append(rotation(rot_cart, rot_num * np.pi / 3))
        data_tot.extend(rot_data)
    data_tot = np.array(data_tot)

    # 使用plotly画图
    data_plot = data_tot
    plot_data = [
        go.Contour(
            x=data_plot[:, 0],
            y=data_plot[:, 1],
            z=data_plot[:, 2],
            #mode='markers',
            #marker={"size": 1, "showscale": True, "color": data_plot[:, 2]}

        )
    ]

    layout = go.Layout(
        width=800,
        height=700,
        autosize=False,
        title='Volcano dataset',
        scene=dict(
            xaxis=dict(
                gridcolor='rgb(255, 255, 255)',
                zerolinecolor='rgb(255, 255, 255)',
                showbackground=True,
                backgroundcolor='rgb(230, 230,230)',
                autorange=False,
                range=[-0.5, 0.5]
            ),
            yaxis=dict(
                gridcolor='rgb(255, 255, 255)',
                zerolinecolor='rgb(255, 255, 255)',
                showbackground=True,
                backgroundcolor='rgb(230, 230,230)',
                autorange=False,
                range=[-0.5, 0.5]
            ),
            zaxis=dict(
                gridcolor='rgb(255, 255, 255)',
                zerolinecolor='rgb(255, 255, 255)',
                showbackground=True,
                backgroundcolor='rgb(230, 230,230)'
            ),
            aspectratio=dict(x=1, y=1, z=0.7),
            aspectmode='manual'
        )
    )

    fig = dict(data=plot_data, layout=layout)
    #pio.write_image(fig, 'images/fig1.jpeg')
    plotly.offline.plot(fig, filename='/mnt/d/Nodal_Line_PLANAR_51.html')
