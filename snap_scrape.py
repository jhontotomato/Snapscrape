import csv
import pandas as pd
import asyncio
import aiohttp
from tqdm.asyncio import trange, tqdm
import aiofiles.os
import aiofiles.ospath
from io import StringIO
from typing import Optional,List
import os
import shutil
from dataclasses import dataclass,field,asdict,astuple

@dataclass
class UserInfo:
    username: str
    following: int
    followers: int
    media_count: int
    bio: str = ''
    pronouns: str = ''
    fullname: str = ''
    external_url: Optional[str] = ''
    category: Optional[str] = ''
    contact_phone_number: Optional[str] = ''
    public_email: Optional[str] = ''
    is_private: bool = False
    is_business: bool = False
    is_in_canada: bool = False
    is_verified: bool = False
    

@dataclass
class FileHandler:
    maindf_name: str = 'scrape_results.csv'
    users_dfs_folder: str = r"/media/jhawk/External ssd/Python folders/Snapscrape/users_to_scrape"
    scraped_users_folder: str = r'/media/jhawk/External ssd/Python folders/Snapscrape/scraped_df'

@dataclass
class SesHandler:
    url : str = f"https://gramsnap.com/api/ig/userInfoByUsername/"
    qued_wait: int = 5
    sesstimeout: int = 60


async def open_session()-> None:
    # init clasess
    file_handler = FileHandler()
    sess = SesHandler()
    
    # While there are files in users dataframes folders keep extracting users
    while len(os.listdir(file_handler.users_dfs_folder)) > 0:
        # Load both existing and new users 
        new_users_df = await load_new_users() 
        existing_users = await load_existing_users()
        
        # Users that will get requested 
        users_toscrape = [row['account'] for index, row in new_users_df.iterrows() if row['account'] not in existing_users]
        
        # progressbar on successfulls users requests
        progress_bar = tqdm(users_toscrape)
        
        timeout = aiohttp.ClientTimeout(sess.sesstimeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            tasks = []
            for index,row in new_users_df.iterrows():
                user_name = row["account"]
                if user_name not in existing_users:
                    task =  asyncio.create_task(request_account(session,user_name,progress_bar))
                    tasks.append(task)
                
                await asyncio.gather(*tasks)
            await move_scraped_files()

async def request_account(session,account:str,progress_bar:tqdm) -> None:
    # init clasess
    sess = SesHandler()
    file_handler = FileHandler()
    
    try:
        # Wait "time" between requests
        # The line `await asyncio.sleep(sess.qued_wait)` is causing the program to pause execution for
        # a specified amount of time. In this case, `sess.qued_wait` is the duration in seconds that
        # the program will wait before making the next request to the API. This is a way to introduce
        # a delay between API requests to prevent overwhelming the server with too many requests in a
        # short period of time.
        await asyncio.sleep(sess.qued_wait)
        async with session.get(f"{sess.url + account}") as response:
            # If the session is not "200" don't save user
            if response.status != 200:
                progress_bar.set_description(f'Fail processing {account}')
            else:
                # get response as a json 
                user_info = await response.json()
                
                # Extract user info
                parsed_user= await extract_user_info(user_info)
                await buffer(parsed_user)
                progress_bar.set_description(f'Saved user: {account}')
                progress_bar.update(1)
    except Exception as e:
        print(e)
        return

async def extract_user_info(user_info) -> tuple:
    user = user_info.get('result', {}).get('user', {})
    # Retrieve pronouns list, ensuring it's a list
    pronouns_list = user.get('pronouns', [])
    
    # Remove commas from each pronoun in the list
    cleaned_pronouns = [pronoun.replace(",", "") for pronoun in pronouns_list if isinstance(pronoun, str)]
    
    # Then you can join them or process as needed
    pronouns = "/".join(cleaned_pronouns)
    
    return UserInfo(
        username = user.get('username', ''),
        following = user.get('following_count', 0),
        followers = user.get('follower_count', 0),
        media_count = user.get('media_count', 0),
        bio = user.get('biography', '').replace(",","").replace('\n',''),
        pronouns = pronouns,
        fullname = user.get('full_name', '').replace(",",""),
        external_url = user.get('external_url', ''),
        category = user.get('category', ''),
        contact_phone_number = user.get('contact_phone_number', ''),
        public_email =  user.get('public_email', ''),
        is_private = user.get('is_private', False),
        is_business = user.get('is_business', False),
        is_in_canada = user.get('is_in_canada', False),
        is_verified = user.get('is_verified', False)
)

async def buffer(parsed_user)-> None:
    
    user_dict = asdict(parsed_user)
    file_handler = FileHandler()
    
    buffer = StringIO()
    writer = csv.DictWriter(buffer,fieldnames=user_dict.keys())
    
    if os.path.exists(file_handler.maindf_name):
        mode = 'a'
    else:
        mode = 'w'
        writer.writeheader()
        
    writer.writerow(user_dict)
    
    buffer.seek(0)
    # Save or append new data if the file exist
    async with aiofiles.open(file_handler.maindf_name,mode,encoding='utf-8') as csvfile:
        await csvfile.write(buffer.getvalue())
        
    buffer.close()

async def load_existing_users() -> set:
    file_handler = FileHandler()
    existing_users = set()
    if os.path.exists(file_handler.maindf_name):
        users_data = pd.read_csv(file_handler.maindf_name)
        for user in tqdm(users_data['username'],'Loading existing users'):
            existing_users.add(user)

    return existing_users

async def load_new_users() ->pd.DataFrame:
    file_handler = FileHandler()
    file_dir = await aiofiles.os.listdir(file_handler.users_dfs_folder)
    
    all_accounts = []
    
    for users_df in tqdm(file_dir,'Loading new users',colour='YELLOW',ascii=True):
        file_path = os.path.join(file_handler.users_dfs_folder,users_df)
        df = pd.read_csv(file_path)
        all_accounts.append(df['account'])
    concatenated_df = pd.concat(all_accounts, ignore_index=True)
    new_users_df = pd.DataFrame(concatenated_df, columns=['account'])
    
    return new_users_df

async def move_scraped_files() -> None:
        file_handler = FileHandler()
        # Move all files right after processing them
        file_dir = await aiofiles.os.listdir(file_handler.users_dfs_folder)
        
        for users_df in tqdm(file_dir,"Moving scraped files",colour='RED'):
            file_path = os.path.join(file_handler.users_dfs_folder, users_df)
            shutil.move(file_path, file_handler.scraped_users_folder)

async def main():
    # await open_session()
    await open_session()

if __name__ == "__main__":
    # pass
    asyncio.run(main())