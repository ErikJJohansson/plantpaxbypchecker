from pycomm3 import LogixDriver
from sys import argv
from tqdm import trange, tqdm

'''
    argv 1 PLC path
'''

bypass_tags = ['.Sts_BypActive']

aoi_types   = ['P_AOut','P_AOutHART','P_D4SD','P_Dose','P_DOut',
               'P_Intlk','P_IntlkAdv','P_LLS','P_Motor','P_Motor2Spd',
               'P_MotorHO','P_MotorRev','P_nPos','P_PF52x','P_PF6000',
               'P_PF7000','P_PF753','P_PF755','P_PIDE','P_SMC50','P_SMCFlex',
               'P_ValveC','P_ValveMO','P_ValveMP','P_ValveSO','P_VSD']

def make_tag_list(base_tag,sub_tags):
    '''
    returns the full tag path of a given base tag and sub tags
    '''
    # concatenate base tag
    read_list = [base_tag + s for s in sub_tags]

    return read_list

def get_aoi_tag_instances(plc, tag_type):
    """
    function returns list of tag names matching struct type
    """
    #return tag_list

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

    # this can totally be better, my brain just started hurting
    # idea is to get a single dimension list of strings with all the indexes so that can be concatenated with base tag

    if len(filtered_list) == 1: # one dimension
        for i in range(dim_list[0]):
            temp.append(base_tag + '[' + str(i) + ']')
    elif len(filtered_list) == 2: # two dimension
        for i in range(dim_list[0]):
            for j in range(dim_list[1]):
                temp.append(base_tag + '[' + str(i) + '][' + str(j) + ']')
    elif len(filtered_list) == 3: # three dimension
        for i in range(dim_list[0]):
            for j in range(dim_list[1]):
                for k in range(dim_list[2]):
                    temp.append(base_tag + '[' + str(i) + '][' + str(j) + '][' + str(k) + ']')

    return temp

def read_plc_row(plc, tag_list):
    '''
    reads data from plc, returns list of tuples (tag_name, tag_value)
    '''
    
    if plc.connected:
        tag_data = plc.read(*tag_list)

    # tuple of tag name, data
    tag_data_formatted = []

    # hardcoded but it works
    for s in tag_data:
        if s[2] == 'BOOL':
            data = int(s[1])
        elif s[2] == 'REAL':
            if 'e' in str(s[1]):
                data = float(format(s[1],'.6e'))
            elif s[1].is_integer():
                data = int(s[1])
            else:
                data = float(format(s[1], '.6f'))                  
        else:
            data = s[1]

        tag_data_formatted.append((s[0],data))

    return tag_data_formatted

if __name__ == "__main__":

    # Arguments checking
   
    if len(argv) == 2:
        commpath = str(argv[1])
    else:
        print('Cannot run script. Invalid number of arguments.')
        exit()

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

    # loop through list of tags
    print('Checking for bypasses in ' + plc_name + ' PLC.')
    
    total_bypassed_tags   = []

    for aoi in aoi_types:
        base_tags = get_aoi_tag_instances(plc,aoi)
        num_instances = len(base_tags)

        if num_instances > 0:

            aoi_bypassed_tags = []

            # read tags 
            for i in tqdm(range(num_instances),"Checking instances of " + aoi):
                tag_list = make_tag_list(base_tags[i],bypass_tags)

                # data for one tag and all sub tags
                tag_data = plc.read(*tag_list)

                if tag_data[1]:
                    aoi_bypassed_tags.append(base_tags[i])

            num_aoi_bypassed = len(aoi_bypassed_tags)

            if num_aoi_bypassed >= 1:
                print("Found " + str(num_aoi_bypassed) + " bypassed instances of " + aoi)

                total_bypassed_tags += aoi_bypassed_tags

        else:
            print("No instances of " + aoi + " found in " + plc_name + " PLC.")

    print('Finished checking bypasses in ' + plc_name + ' PLC.')
    print('Found ' + str(len(total_bypassed_tags)) + '.')
    for tag in total_bypassed_tags:
        print(tag)

    plc.close()
