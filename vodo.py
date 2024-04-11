#!/usr/bin/env python3

import argparse
import time
import re
import os



TAB_SPACING = 3
parser = argparse.ArgumentParser(
        description='voDO! ')

    

def main():
    target = 'TODO'
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    text = ""
    HEADING = ""
    NEWLINE = "\n"
    ID = counter(target)
    statuses = ['1', '2', '3']



    interactive = parser.add_mutually_exclusive_group() 
    
    interactive.add_argument(
        '-i, --interactive', action='store_true', dest='interactive', 
        help="Spawns an interactive session.")

    parser.add_argument(
            'user_input', type=str, help='', metavar='task', nargs="?") 
    
    parser.add_argument(
            '-s, --status', type=str, choices=statuses, dest='status', metavar='status message', nargs="?", 
            help='status of Todo Task. Available Options = { 1: to-be-determined, 2: in-progress, 3: blocked }')

    parser.add_argument(
            '-d, --delete-preexisting', action='store_true', dest='delete',
            help='deletes TODO file if it exists in the current working directory')

    parser.add_argument(
            '-n, --notes', type=str, metavar='extra notes', dest='notes', 
            help="Add a note on todo task for better context.")    

    args = parser.parse_args()
    
    flags ={
        'ID': {
            'name': 'ID',
            'data': ID,
            'status': True,
        }, 
        'TASK': {
            'name': 'TASK',
            'data': args.user_input,
            'status': True,
        }, 
        'TIME': {
            'name': 'TIME',
            'data': timestamp,
            'status': True,
        },
        'STATUS':  {
            'name': 'STATUS',
            'data': setStatus(args.status, interactiveModeEnabled=args.interactive),
            'status': True,
        },
        'NOTES':  {
            'name': 'NOTES',
            'data': args.notes,
            'status': True,
        }

    }


    # Jumps to interactiveSession()
    if args.interactive:
        return interactiveSession(flags, target)


    if not args.interactive:
        if not args.status:
            if not args.user_input:
                parser.error("the following arguments are required: task, -s, --status")
            else:
                parser.error('the following argumens are required: -s, --status')



    # Checks if file decoding was successful
    if not ID or not isinstance(ID, int):
        parser.error('TODO File might\'ve been corrupted or tamperred with. '
                     'Please remove the file or specify the -d,--delete-existing flag to force deletion.')
    if args.delete:
        if os.path.exists(target):
            os.remove(target)


    
    # Iterates over flags dict to determine which flags will be appended
    # to the headers of the file
    columnWidth = {}



    for name,active in flags.items():
        if active['data'] is None:
            text += 'N/A' + '\t' + '\t' + '\t'


        elif active['status'] is True and type(active['status']) is bool:
            text += str(active['data']) + '\t' + '\t' + '\t'

        else:
            text += 'N/A' + '\t' + '\t' + '\t'

        HEADING += active['name'] + "\t" + '\t' + '\t'

    if not os.path.exists(target):
        print('No TODO file located. Generating new one...')


        # Creates new TODO file
        with open(target, 'w') as newfile:
            newfile.write(HEADING)
            newfile.write(NEWLINE)
            newfile.write(text)
            
            print('TODO file created in ' + os.getcwd() + '/' + target)


    else:

        # Works on preexisting TODO file
        with open(target, 'a') as file:
            file.write(NEWLINE)
            file.write(text)

        print('TODO file updated')

        todoCheckList(target)



''' Function called by todoCheckList() function to re-encode
    Todo file with changes that were made by todoCheckList().'''
def todoFileEncoder(file, objKeys, bit):
    with  open(file, bit) as f:
        column_widths = {}
        for key, items in objKeys.items():
            for idx, item in enumerate(items):
                column_widths[idx] = max(column_widths.get(idx, len(item)), len(item))
    
        # Write the formatted data to the file
        for key, items in objKeys.items():
            formattedRow = "\t".join([item.ljust(column_widths[idx]) for idx, item in enumerate(items)])
            f.write(formattedRow + '\n')

        print('done')



''' Function that sets status string'''
def setStatus(stdin, interactiveModeEnabled=False):

    if interactiveModeEnabled:
        return stdin

    match stdin:
        case '1':
            stdin = 'to-be-determined'
                    
        case '2':
            stdin = 'in-progress'

        case '3':
            stdin = 'blocked'

        case _:
            parser.error('--status only takes the following options: [1,2,3]')

    return stdin



''' Function that checks grabs each TODO task and asks
    user if updates have been made to task.'''
def todoCheckList(file):
    checklist = {}

    if os.path.exists(file):
        with open(file, 'r') as f:
            count = 0
    
            for line in f:
                lists = []
                count += 1
                entries = line.strip().split('\t')
    
                for entry in entries:
                    if entry != '':
                        regex = re.sub(r'\s+', ' ', entry.strip())

                        lists.append(regex)
                    
    
                    checklist[str(count)] = lists
   

        for key,items in checklist.items():
            
            if len(items) == 0:
                checklist.pop(key)
                break


            elif key == '1' or items[3] == 'COMPLETED':
               pass 
    
            else:


                # Step 1: Confirm if updates were made on task
                step1 = {
                    'done': False,
                    'response': None,
                }
    
                print(f'Task ID {items[0]}:')
                print(f'TODO: {items[1]}')
                print(f'Status: {items[3]}.')
                print(f'Have you made any updates on this task?')
    
                while step1['done'] is False:
                   user = input('(y/n):')
    
                   match user:
                       case 'y':
                            step1['response'] = True
                            step1['done'] = True
                       case 'n':
                           step1['response'] = False
                           step1['done'] = True
                       case _:
                           print('Please choose either \'y\' or \'n\'.')
    
    
                # Step 2: Ask if task is completed
                step2 = {
                    'done': False,
                    'response': None,
                    'previous': step1['response']
                }
    
                if step2['previous']:
                    print('Is this task done?')
                        
                    while step2['done'] is False:
                        user = input('(y/n):')
    
                        match user:
                            case 'y':
                               step2['done'] = True
                               items[3] = 'COMPLETED'
                               step2['response'] = True
    
    
                            case 'n':
                                step2['done'] = True
                                step2['response'] = False
    
                            case _:
                                print('Please choose either \'y\' or \'n\'.')
    
                # Step 3: Ask to update status if task not completed
                step3 = {
                    'done': False,
                    'response': None,
                    'previous': step2['response']
                }
                if not step3['previous']:
                    print('Would you like to update this task\'s status?')
                    print('Options:', 
                          '1) To Be Determined',
                          '2) In Progress',
                          '3) Blocked')
                    
                    while step3['done'] is False:
                        user = input('(1/2/3/n):')

                        match user:
                            case '1':
                                step3['done'] = True
                                items[3] = 'to-be-determined'
        
                            case '2':
                                step3['done'] = True
                                items[3] = 'in-progress'
                        
                            case '3':
                                step3['done'] = True
                                items[3] = 'blocked'
                        
                            case 'n':
                                step3['done'] = True
                
                            case _:
                                print('Please choose from the provided options or \'n\'.')


                # Step 4:  Ask to update notes
                    step4 = {
                        'done': False,
                        'response': None,
                        'previous': step3['response']
                    }
    
                    print('Do you wish to update this task\'s notes?')
    
                    while step4['done'] is False:
                        user = input('(y/n):')
    
                        match user:
                            case 'y':
                                updateNotes = input('Enter your new notes here... \n')
                                step4['done'] = True
                                items[4] = updateNotes
    
                            case 'n':
                                step4['done'] = True
    
                            case _:
                               print('Please choose either \'y\' or \'n\'.') 

        todoFileEncoder(file, checklist, 'w')



''' Function that handles the interactive session'''
def interactiveSession(flags, file):
    print('INTERACTIVE MODE ENABLED')
    NEWFILE = True if not os.path.exists(file) else False 
    

    if NEWFILE:
        print('Writing to new TODO file...')


    
    # Get task data
    flags['TASK']['data'] = input('Task: ')

    # Get status data
    flags['STATUS']['data'] = None

    
    while type(flags['STATUS']['data']) is not str:
        print('Give this task a status.')
        print('Options:', 
            '1) To Be Determined',
            '2) In Progress',
            '3) Blocked')

        user = input('(1/2/3): ')

        match user:
            case '1':
                 flags['STATUS']['data'] = 'to-be-determined'

            case '2':
                 flags['STATUS']['data'] = 'in-progress'

            case '3':
                flags['STATUS']['data'] = 'blocked'

            case _:
                print('Task status must be assigned!')
     

    # Get note data if user opts for it
    print('Would you like to add any additional notes ',
          'to this task?')

    note_options = None

    while note_options is None:
        user = input('(y/n): ')

        match user:
            case 'y':
                note_options = True

            case 'n':
                note_options = False

            case _:
                print('Please choose either y or n....')

    if note_options:
        print('Please enter any additional notes you may have...')

        flags['NOTES']['data'] = input('Notes: ')

    else:
        flags['NOTES']['data'] = 'N/A'

    payload = {
        'headers': [flag['name'] for key,flag in flags.items()],
        'data': [str(flag['data']) for key,flag in flags.items()] 
    }

    if not NEWFILE:
        payload.pop('headers') 
        todoFileEncoder(file, payload, 'a')
    else:
        todoFileEncoder(file, payload, 'w')

    todoCheckList(file)







''' Function that decodes the formatted TODO file 
    to get the next task ID'''
def counter(file):
    if os.path.exists(file):
        # Checks if the file is empty
        if os.path.getsize(file) == 0:
            return 1

        with open(file, 'r') as f:
            numbers = []
            for line in f:
                line = line.strip()
                if line:
                    # Extracts the first one or two digits from the line
                    digits = re.findall(r'^\d{1,2}', line)
                    if digits:
                        numbers.append(int(digits[0]))

            # Checks if the numbers are consecutive
            for i, n in enumerate(numbers, start=1):
                if n != i:
                    return False

            # Returns the next consecutive number
            return numbers[-1] + 1 if numbers else 1

    else:
        # Returns 1 if the file doesn't exist
        return 1
    




if __name__ == '__main__':
    main()  




    



