from pycomm3 import LogixDriver
from sys import argv
from tqdm import trange, tqdm
from itertools import product
import argparse

# Define bypass and simulated tags

bypass_tags = ['.Sts_BypActive']

sim_tags    = ['.Sts_SubstPV']

bypass_aoi_types_v4 = ['P_AOut','P_AOutHART','P_D4SD','P_Dose','P_DOut',
               'P_Intlk','P_IntlkAdv','P_LLS','P_Motor','P_Motor2Spd',
               'P_MotorHO','P_MotorRev','P_nPos','P_PF52x','P_PF6000',
               'P_PF7000','P_PF753','P_PF755','P_PIDE','P_PID','P_SMC50','P_SMCFlex',
               'P_ValveC','P_ValveMO','P_ValveMP','P_ValveSO','P_VSD']

bypass_aoi_types_v5 = ['P_ANALOG_OUTPUT','P_DISCRETE_OUTPUT','P_DISCRETE_4STATE',
                'P_DISCRETE_MIX_PROOF','P_DISCRETE_N_POSITION','P_INTERLOCK','P_PERMISSIVE',
                'P_VARIABLE_SPEED_DRIVE','P_LEAD_LAG_STANDBY','P_MOTOR_DISCRETE','P_VALVE_DISCRETE']

bypass_aoi_types = bypass_aoi_types_v4 + bypass_aoi_types_v5

sim_aoi_types_v4 = ['P_AIn','P_AInDual','P_AInMulti','P_DIn']

sim_aoi_types_v5 = ['P_ANALOG_INPUT','P_DISCRETE_INPUT']

sim_aoi_types = sim_aoi_types_v4 + sim_aoi_types_v5

# append elements to instance of tag
def make_tag_list(base_tag,sub_tags):
    '''
    returns the full tag path of a given base tag and sub tags
    '''
    # concatenate base tag
    read_list = [base_tag + s for s in sub_tags]

    return read_list

# get all instances of a tag type
def get_aoi_tag_instances(plc, tag_type):
    """
    function returns list of tag names matching struct type
    """
    tag_list = []

    for tag, _def in plc.tags.items():
        if _def['data_type_name'] == tag_type:
            if _def['dim'] > 0:
                tag_list = tag_list + get_dim_list(tag,_def['dimensions'])
            else:
                tag_list.append(tag)

    return tag_list

def get_dim_list(base_tag, dim_list):
    '''
    function takes a list which has the array size and turns it into a list with all iterations
    '''
    # remove 0's
    filtered_list = list(filter(lambda num: num != 0, dim_list))

    temp = []

    for indices in product(*[range(dim) for dim in filtered_list]):
        temp.append(base_tag + ''.join(f'[{i}]' for i in indices))

    return temp

def check_for_bypass_tags():
    print('Checking for bypasses in ' + plc_name + ' PLC.')
    
    total_bypassed_tags   = []

    for aoi in bypass_aoi_types:
        base_tags = get_aoi_tag_instances(plc,aoi)
        num_instances = len(base_tags)

        if num_instances > 0:

            aoi_bypassed_tags = []

            # read tags 
            for i in tqdm(range(num_instances),"Checking instances of " + aoi):
                tag_list = make_tag_list(base_tags[i],bypass_tags)

                # read bypass tag list
                tag_data = plc.read(*tag_list)

                # second element is true/false flag. True means the .Sts_BypActive bit is on and add tag to list
                if tag_data[1]:
                    try: #v5 compatibility
                        tag_string = base_tags[i] + ' - ' + plc.read(base_tags[i] + '.Cfg_Desc')[1]
                    except:
                        tag_string = base_tags[i]
                    aoi_bypassed_tags.append(tag_string)

            num_aoi_bypassed = len(aoi_bypassed_tags)

            # output to command line and add tag to list
            if num_aoi_bypassed >= 1:
                print("Found " + str(num_aoi_bypassed) + " bypassed instances of " + aoi)

                total_bypassed_tags += aoi_bypassed_tags

        else:
            print("No instances of " + aoi + " found in " + plc_name + " PLC.")

    print('')
    print('Finished checking bypasses in ' + plc_name + ' PLC.')
    print('')
    print('Found ' + str(len(total_bypassed_tags)) + '.')
    print('')

    # print tag list
    if len(total_bypassed_tags) > 0:
        print('####################################')
        print('PERMISSIVE & INTERLOCK BYPASSED TAGS')
        print('')
        for tag in total_bypassed_tags:
            print(tag)
        print('')
        print('####################################')
        print('')  

def check_for_sim_tags():
    print('Checking for simulated tags in ' + plc_name + ' PLC.')
    
    total_simulated_tags   = []

    for aoi in sim_aoi_types:
        base_tags = get_aoi_tag_instances(plc,aoi)
        num_instances = len(base_tags)

        if num_instances > 0:

            aoi_simulated_tags = []

            # read tags 
            for i in tqdm(range(num_instances),"Checking instances of " + aoi):
                tag_list = make_tag_list(base_tags[i],sim_tags)

                # read bypass tag list
                tag_data = plc.read(*tag_list)

                # second element is true/false flag. True means the .Sts_BypActive bit is on and add tag to list
                if tag_data[1]:
                    try: #v5 compatibility
                        tag_string = base_tags[i] + ' - ' + plc.read(base_tags[i] + '.Cfg_Desc')[1]
                    except:
                        tag_string = base_tags[i]
                    aoi_simulated_tags.append(tag_string)

            num_aoi_simulated = len(aoi_simulated_tags)

            # output to command line and add tag to list
            if num_aoi_simulated >= 1:
                print("Found " + str(num_aoi_simulated) + " simulated instances of " + aoi)

                total_simulated_tags += aoi_simulated_tags
        else:
            print("No instances of " + aoi + " found in " + plc_name + " PLC.")

    print('')
    print('Finished checking for simulations in ' + plc_name + ' PLC.')
    print('')
    print('Found ' + str(len(total_simulated_tags)) + '.')
    print('')

    # print tag list
    if len(total_simulated_tags) > 0:
        print('####################################')
        print('######### SUBSTITUTED TAGS #########')
        print('')
        for tag in total_simulated_tags:
            print(tag)
        print('')
        print('####################################')
        print('')  


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Python-based PlantPAX tag bypass checker',
        epilog='This tool works on both Windows and Mac.')
    
    # Add command-line arguments
    parser.add_argument('commpath', help='Path to PLC')

    args = parser.parse_args()

    # Access the parsed arguments
    commpath = args.commpath

    # open connection to PLC

    plc = LogixDriver(commpath, init_tags=True,init_program_tags=True)

    print('Connecting to PLC.')
    try:
        plc.open()
        plc_name = plc.get_plc_name()

        print('Connected to ' + plc_name + ' PLC at ' + commpath)
    except:
        print('Unable to connect to PLC at ' + commpath)
        exit()

    # loop through list of tags and check if bypassed
    check_for_bypass_tags()

    check_for_sim_tags()
    
    plc.close()
