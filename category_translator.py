import asyncio
import csv
import os
import random
import time
from dataclasses import asdict, dataclass
from io import StringIO
import aiofiles
from googletrans import Translator
from tqdm import tqdm


@dataclass
class FileHandler:
    traslations_df: str = 'category_translations.csv'
    scrape_results_df: str = 'scrape_results.csv'
    dictionary_df: str = 'OPTED-Dictionary.csv'

@dataclass
class TransDict:
    category: str 
    src_lang: str 
    translation: str
    target_lang: str 

def translate(text: str)-> TransDict:
    translator = Translator()
    response = translator.translate(text)
    return TransDict(category=text, src_lang=response.src, translation=response.text, target_lang=response.dest)
    
async def translate_category(category) -> dict:
    translated_word = translate(category)
    trans_dict = asdict(translated_word)
    return await buffer([trans_dict])
    
async def buffer(transdict:dict):
    f = FileHandler()
    filename = f.traslations_df
    # Field names (keys)
    fieldnames = transdict[0].keys()
    # create file object
    buffer = StringIO()
    writer = csv.DictWriter(buffer,fieldnames=fieldnames)
    
    # Write buffer
    if os.path.exists(filename):
        mode = 'a' #Append new data to existing file
    else:
        mode = 'w' #write new file with headers
        writer.writeheader()
        
    for row in transdict:
        writer.writerow(row)
    
    buffer.seek(0)
    # Save or append content to file
    await save(filename,buffer.getvalue(),mode)
    
    buffer.close()
    
async def save(filename,content,mode):
    # Save translated category
    async with aiofiles.open(filename,mode,encoding='utf-8') as dict:
        await dict.write(content)

async def load_dataframe_column(dataframe:str,column:str,dictionary: str = False,results_categories: set = None)-> set:
    column_set = set()
    # Asynchronous reading of file
    async with aiofiles.open(dataframe,'r',encoding='utf-8') as csv_file:
        dataframe = await csv_file.read()
    # Use StringIO to transform the file to an object file
    with StringIO(dataframe) as object_file:
        csv_dataframe = csv.DictReader(object_file)
        # if is not the dictionary load the columns that are not empty
        if not dictionary:
            for line in csv_dataframe:
                load_column = line[column].strip()
                if load_column:
                    column_set.add(load_column)
        # load and check non english words from scraped results
        else:
            dictionary_words = set(line[column] for line in csv_dataframe)  # Collect all words in a set for efficient lookup
            for word in results_categories:
                if word not in dictionary_words:
                    column_set.add(word)
    return column_set
    
async def main():
    df = FileHandler()
    tasks = []
    
    scrape_results_df = await load_dataframe_column(df.scrape_results_df,column='category')
    
    translations_df = await load_dataframe_column(df.traslations_df,column='category')
    
    non_english_words = await load_dataframe_column(df.dictionary_df,column='Word',
                                                    dictionary=True,
                                                    results_categories=scrape_results_df)
        
    for category in tqdm(non_english_words,colour='MAGENTA',ascii=True):
        if category in translations_df:
            continue
        else:
            task =  asyncio.create_task(translate_category(category))
            tasks.append(task)
            await asyncio.sleep(random.uniform(5,10))
            
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())

