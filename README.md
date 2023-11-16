# PlantPAX Bypass Checker



## Description

This project checks if instances of PlantPAX AOI's are bypassed. If any are found, a list is printed of the tags in bypass

Below are the tag types being checked

P_AOut
P_AOutHART
P_D4SD
P_Dose
P_DOut
P_Intlk
P_IntlkAdv
P_LLS
P_Motor
P_Motor2Spd
P_MotorHO
P_MotorRev
P_nPos
P_PF52x
P_PF6000
P_PF7000
P_PF753
P_PF755
P_PIDE
P_SMC50
P_SMCFlex
P_ValveC
P_ValveMO
P_ValveMP
P_ValveSO
P_VSD

## Motivation

Rogue operators bypassing everything

## Reading tags from PLC

The tool requires a ommand line argument to work. a properly formatted command is shown below

```
bypchecker.py 10.10.17.10/1

```

10.10.17.10/1 is the PLC IP address and slot number of the PLC, without the slot number and just the IP address (like '10.10.17.10' it will default to slot 0)

The script will poke the PLC for the number of instances of each type. This then gets written to the "Setup" sheet in the workbook.

For each tag instance, a bulk read will be done to the PLC to get all the tag data. This then gets written to the spreadsheet for the AOI type.

## Installation

Please ensure you have the python packages installed as specified in the requirements.txt file.

Navigate to the directory where you cloned the repo and run the command below

```
pip3 install requirements.txt

```

## Troubleshooting

Can you ping the PLC you are trying to read from? Ensure you have network connectivity to the PLC before running this script.

If you do not know how to ping, run the command below, it should be the same for Mac/Unix and Windows. Replace the IP address with the PLC you wish to ping

```
ping 10.10.17.10

```

