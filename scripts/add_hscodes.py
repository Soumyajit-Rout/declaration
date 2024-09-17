import os
import django
import sys
import openpyxl

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DeclarationManagement.settings')
django.setup()

from declaration.models import HsCode


def delete_hscode():
    hscode = HsCode.objects.filter()
    for i in hscode:
        print("deleting....")
        i.delete()


def load_hs_codes_from_xlsx():
    # Open the xlsx file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, 'hs_code.xlsx') 
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active

    
    for row in sheet.iter_rows(min_row=3, values_only=True):
        hs_code_value = str(row[5])  
        description = row[3]
        duty_fee = row[1]
        if description:
            keys = description.split()
            filtered_keys = [word.lower() for word in keys if word.isalpha() and len(word) >= 4]
            filtered_description = [word for word in keys if word.isalpha()]

            keywords = ','.join(filtered_keys)
            descriptions = ' '.join(filtered_description)

  
        hs_code_obj, created = HsCode.objects.get_or_create(
            hs_code=hs_code_value,
            defaults={
                'description': descriptions,
                'keywords': keywords,
                'duty_fee':duty_fee,
            }
        )

        if created:
            print(f"Added new HS code: {hs_code_value} - {description}")
        else:
            print(f"HS code {hs_code_value} already exists")

if __name__ == "__main__":
    load_hs_codes_from_xlsx()
    # delete_hscode()