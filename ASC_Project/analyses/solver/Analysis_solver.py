from __future__ import absolute_import, unicode_literals      
from .Darcy_CVFEM import Darcy_CVFEM
from ..models import (BC, Analysis, Connectivity, Mesh, Nodes, Preform, Resin,
                     Section, Step, Results)
from time import sleep          
import numpy as np
from celery import shared_task

@shared_task (bind=True)
def solve_darcy(progress,_id):
    '''
    This function creates an instance for the Darcy_FEM solver class
    based on the database information 
    '''
    """
### ProgressBar
    for i in range(100):
        sleep(0.2)
        self.update_state(state="PROGRESS",  meta={'current': i, 'total': 100, 'percent':i/100})
        print(i)
    self.update_state(state='COMPLETE',  meta={'current': i, 'total': 100, 'percent':i/100})
    """
    _analysis = Analysis.objects.get(id=_id)
    resin = _analysis.resin
    viscosity = resin.viscosity

    FaceList = {}
    for item in Nodes.objects.filter(mesh_id=_analysis.mesh).values():
        if item['FaceGroup'] not in FaceList.keys():
            FaceList[item['FaceGroup']] = []
        FaceList[item['FaceGroup']].append(item['NodeNum'])

    KXX = {}
    KXY = {}
    KYY = {}
    H = {}
    phi = {}
    section_names = _analysis.section.values('name').distinct()
    for section in section_names:
        H[section['name']] = 0.0
        KXX[section['name']] = 0.0
        KXY[section['name']] = 0.0
        KYY[section['name']] = 0.0
        phi[section['name']] = 0.0
        preform_ids_rotate = Section.objects.filter(analysis = _analysis, name=section['name']).values('preform_id', 'rotate')
        for item in preform_ids_rotate:
            preform = Preform.objects.get(id = item['preform_id'])
            radian_rot = np.deg2rad(item['rotate'])
            T = np.array([[np.cos(radian_rot), np.sin(radian_rot)], [-np.sin(radian_rot), np.cos(radian_rot)]])
            H[section['name']] = H[section['name']] + preform.thickness
            phi[section['name']] = phi[section['name']] + preform.phi*preform.thickness
            k = T * np.array([[preform.K11, preform.K12], [preform.K12, preform.K22]])
            KXX[section['name']] = KXX[section['name']] + preform.thickness * k[0][0]
            KXY[section['name']] = KXY[section['name']] + preform.thickness * k[0][1]
            KYY[section['name']] = KYY[section['name']] + preform.thickness * k[1][1]
            KXX[section['name']] = KXX[section['name']]/H[section['name']]
            KXY[section['name']] = KXY[section['name']]/H[section['name']]
            KYY[section['name']] = KYY[section['name']]/H[section['name']]
            phi[section['name']] = phi[section['name']]/H[section['name']]

    analysis = {
        'analysis_id':_analysis.id,
        'folder_address':("media/" + str(_analysis.id))
    }

    resin = {
        'viscosity':viscosity
    }
    section_data = {}
    section_id = 1
    for section in section_names:
        section_data[section['name']]={
            'marker': section_id,
            'K11':KXX[section['name']],
            'K12':KXY[section['name']],
            'K22':KYY[section['name']],
            'thickness':H[section['name']],
            'volume_fraction':phi[section['name']],
            'nodes':FaceList[section['name']],
        }
        section_id = section_id + 1

    step = _analysis.step

    step_data = {
        'termination_type':step.typ,
        'termination_time':step.endtime,
        'output_steps':step.outputstep,
        'maximum_itrations':step.maxiterations,
        'maximum_consequtive_steps':step.maxhaltsteps, 
        'minimum_change_of_saturation':step.minchangesaturation,
        'time_scaling_parameter':step.timescaling,
        'filling_threshold':step.fillthreshold,
    }

    EdgeList = {}
    for item in Nodes.objects.filter(mesh_id=_analysis.mesh).values():
        if item['EdgeGroup'] not in EdgeList.keys():
            EdgeList[item['EdgeGroup']] = []
        EdgeList[item['EdgeGroup']].append(item['NodeNum'])
    del EdgeList["_None"]

    Inlets = {}
    Outlets = {}
    Walls = {}
    boundary_marker = 1
    for item in BC.objects.filter(analysis_id=_analysis.id):
        if item.typ == 'Inlet':
            Inlets[item.name] = {
                'marker':boundary_marker,
                'condition':item.condition,
                'value':item.value,
                'nodes':EdgeList[item.name],
            }
            boundary_marker += 1

        elif item.typ == 'Outlet':
            Outlets[item.name] = {
                'marker':boundary_marker,
                'condition':'Pressure',
                'value':item.value,
                'nodes':EdgeList[item.name],
            }
            boundary_marker += 1
            
        else:
            Walls[item.name] = {
                'marker':boundary_marker,
                'condition':'None',
                'value':0.0,
                'nodes':EdgeList[item.name],
            }
            boundary_marker += 1

    BCs = {
        'inlets':Inlets,
        'outlets':Outlets,
        'walls':Walls,
    }

    InputData = {
        'analysis': analysis,
        'resin':resin,
        'sections':section_data,
        'step':step_data,
        'BCs':BCs,
#        'ICs':InitialConditions,
#        'loads':Loads,
#        'output':Output
    }

    problem=Darcy_CVFEM(InputData)
    problem.solve(progress) 

