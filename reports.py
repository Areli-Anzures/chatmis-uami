import os, json, requests, xlsxwriter
#from rasa.nlu.training_data import load_data
#from rasa_nlu.converters import load_data
from rasa.shared.nlu.training_data.loading import load_data

parse_url = 'http://localhost:5021/model/parse'
nlu_directory = 'data/'
threshold = 0.6

messages = []

for filename in os.listdir(nlu_directory):
    if filename.startswith('nlu'):
        intents = load_data(nlu_directory + filename).sorted_intent_examples()
        for intent in intents:
            data = intent.as_dict()
            print(data['intent'], data['text'])
            # let's hit the parser and get the classifications
            headers = { 'content-type': 'application/json' }
            payload = '{ "text": "' + data['text'].replace("\"", "\\\"").strip() + '"}'
            r = requests.post(parse_url, data=payload.encode('utf-8'), headers = headers)
            if r.status_code != 200:
                print(payload)
                break
            results = json.loads(r.content.decode('utf8'))
            message = { 'expected_intent': data['intent'],
                'text': data['text'],
                'intent1': results['intent_ranking'][0]['name'],
                'accuracy1': float(results['intent_ranking'][0]['confidence']),
                'intent2': results['intent_ranking'][1]['name'],
                'accuracy2': float(results['intent_ranking'][1]['confidence']),
                'intent3': results['intent_ranking'][2]['name'],
                'accuracy3': float(results['intent_ranking'][2]['confidence']) }
            messages.append(message)

workbook = xlsxwriter.Workbook('Results.xlsx')
format_red = workbook.add_format({'font_color': 'white', 'bg_color': 'red'})
format_green = workbook.add_format({'bg_color': 'green'})
format_bold = workbook.add_format({'bold': True})
format_bold_percent = workbook.add_format({'bold': True, 'num_format': 10})
format_percent = workbook.add_format({'num_format': 10})
format_percent_red = workbook.add_format({'font_color': 'white', 'bg_color': 'red', 'num_format': 10})
format_percent_yellow = workbook.add_format({'bg_color': 'yellow', 'num_format': 10})
format_percent_green = workbook.add_format({'bg_color': 'green','num_format': 10})
format_center_green = workbook.add_format({'bg_color': 'green', 'align': 'center'})
format_center_red = workbook.add_format({'font_color': 'white', 'bg_color': 'red', 'align': 'center'})

#Add a spreadsheet and set up our column widths and headers:

worksheet = workbook.add_worksheet('Test results')
row = 1
worksheet.set_column('A:A', 30)
worksheet.set_column('B:B', 40)
worksheet.set_column('C:C', 5)
worksheet.set_column('D:D', 25)
worksheet.set_column('E:E', 10)
worksheet.set_column('F:F', 10)
worksheet.set_column('G:G', 5)
worksheet.set_column('H:H', 25)
worksheet.set_column('I:I', 10)
worksheet.set_column('J:J', 25)
worksheet.set_column('K:K', 10)
worksheet.set_column('L:L', 25)
worksheet.set_column('M:M', 10)

worksheet.write('A1', 'Expected intent', format_bold)
worksheet.write('B1', 'Text', format_bold)
worksheet.write('D1', 'Classified Intent', format_bold)
worksheet.write('E1', 'Accuracy', format_bold)
worksheet.write('H1', 'Ranking', format_bold)

#Now let's add all the results:

total_items = 0
correct_items = 0

for item in messages:
    worksheet.write(row, 0, item['expected_intent'])
    worksheet.write(row, 1, item['text'])
    if item['expected_intent'] == item['intent1']:
        worksheet.write(row, 3, item['intent1'], format_green)
        action_ok = True
    else:
        worksheet.write(row, 3, item['intent1'], format_red)
        action_ok = False
    if item['accuracy1'] > threshold + .1:
        worksheet.write(row, 4, item['accuracy1'], format_percent_green)
        accuracy_ok = True
    elif item['accuracy1'] >= threshold:
        worksheet.write(row, 4, item['accuracy1'], format_percent_yellow)
        accuracy_ok = True
    else:
        worksheet.write(row, 4, item['accuracy1'], format_percent_red)
        accuracy_ok = False
    if action_ok and accuracy_ok:
        worksheet.write(row, 5, 'OK', format_center_green)
        correct_items += 1
    else:
        worksheet.write(row, 5, 'BAD', format_center_red)
    total_items += 1
    worksheet.write(row, 7, item['intent1'])
    worksheet.write(row, 8, item['accuracy1'], format_percent)
    worksheet.write(row, 9, item['intent2'])
    worksheet.write(row, 10, item['accuracy2'], format_percent)
    worksheet.write(row, 11, item['intent3'])
    worksheet.write(row, 12, item['accuracy3'], format_percent)

    row += 1

#And finally add some overall stats and close the file:

if total_items > 0:
    worksheet.write(row + 1, 5, correct_items, format_bold)
    worksheet.write(row + 1, 6, 'correct examples', format_bold)
    worksheet.write(row + 2, 5, total_items, format_bold)
    worksheet.write(row + 2, 6, 'total examples', format_bold)
    worksheet.write(row + 3, 5, correct_items / total_items, format_bold_percent)
    worksheet.write(row + 3, 6, '%', format_bold)

workbook.close()