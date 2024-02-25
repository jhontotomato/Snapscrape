import asyncio
import csv
import aiofiles
from io import StringIO


async def modify_and_save_csv(input_file: str, output_file: str, column: str, replacement_dict: dict):
    modified_rows = []
    async with aiofiles.open(input_file, 'r', encoding='utf-8') as file:
        csv_file = await file.read()

    # Read and modify each row
    with StringIO(csv_file) as object_file:
        reader = csv.DictReader(object_file)
        fieldnames = reader.fieldnames

        for row in reader:
            # Replace the column value based on the replacement dictionary
            if row[column] in replacement_dict:
                row[column] = replacement_dict[row[column]]
            modified_rows.append(row)

    # Prepare the modified data for writing
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for row in modified_rows:
        writer.writerow(row)

    # Move back to the start of the StringIO buffer
    output.seek(0)

    # Write the modified data to the output file asynchronously
    async with aiofiles.open(output_file, 'w', encoding='utf-8', newline='') as file:
        await file.write(output.getvalue())

    # Close the StringIO buffer
    output.close()

async def file_opener(file:str,column:str,tr_column:str) -> set:
    categories = {}
    async with aiofiles.open(file,'r',encoding='utf-8') as file:
        csv_file = await file.read()

    with StringIO(csv_file) as object_file:
        file = csv.DictReader(object_file)
        for line in file:
            category = line[column]
            translation = line[tr_column]
            categories[category] = translation
                
    return categories

async def main():
    replacement_dict = await file_opener('category_translations.csv','category','translation') 
    
    input_file = 'scrape_results.csv'
    output_file = 'translated_scrape_results.csv'
    
    await modify_and_save_csv(input_file, output_file, 'category', replacement_dict)

if __name__ == '__main__':
    asyncio.run(main())